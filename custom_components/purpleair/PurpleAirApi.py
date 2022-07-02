from datetime import timedelta
import logging

from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval, async_track_point_in_utc_time
from homeassistant.util import dt

from .const import AQI_BREAKPOINTS, DISPATCHER_PURPLE_AIR, PARTICLE_PROPS, LOCAL_SCAN_INTERVAL, LOCAL_URL_FORMAT

_LOGGER = logging.getLogger(__name__)


def calc_aqi(value, index):
    if index not in AQI_BREAKPOINTS:
        _LOGGER.debug('calc_aqi requested for unknown type: %s', index)
        return None

    bp = next((bp for bp in AQI_BREAKPOINTS[index] if bp['pm_low'] <= value <= bp['pm_high']), None)
    if not bp:
        _LOGGER.debug('value %s did not fall in valid range for type %s', value, index)
        return None

    aqi_range = bp['aqi_high'] - bp['aqi_low']
    pm_range = bp['pm_high'] - bp['pm_low']
    c = value - bp['pm_low']
    return round((aqi_range/pm_range) * c + bp['aqi_low'])


# LRAPA conversion using the same formula as used by PurpleAir's map as of 2020-09-06
def lrapa(value):
    return max(0, 0.5 * value - 0.66)


def process_readings(json_result, is_dual = False):
    readings = {'pm2_5_aqi_original': json_result['pm2.5_aqi']}
    if is_dual:
        readings['pm2_5_aqi_b_original'] = json_result['pm2.5_aqi_b']

    for prop in PARTICLE_PROPS:
        if prop not in json_result:
            readings[prop] = None
            continue

        a = float(json_result[prop])
        prop_b = prop + '_b'  # Property name for sensor B
        if is_dual and prop_b in json_result:
            b = float(json_result[prop_b])
        else:
            b = a
        readings[prop] = round((a + b) / 2, 1)
        readings[f'{prop}_confidence'] = 'Good' if abs(a - b) < 45 else 'Questionable'

    readings['aqi_epa'] = calc_aqi(readings['pm2_5_atm'], 'pm2_5')
    readings['aqi_lrapa'] = calc_aqi(lrapa(readings['pm2_5_atm']), 'pm2_5')
    return readings


class PurpleAirApi:
    def __init__(self, hass, session):
        self._hass = hass
        self._session = session
        self._nodes = {}
        self._data = {}
        self._scan_interval = timedelta(seconds=LOCAL_SCAN_INTERVAL)
        self._shutdown_interval = None

    def is_node_registered(self, pa_sensor_id):
        return pa_sensor_id in self._data

    def get_reading(self, pa_sensor_id, prop):
        if pa_sensor_id not in self._data:
            return None

        node = self._data[pa_sensor_id]
        return node[prop] if prop in node else None

    def register_node(self, pa_sensor_id, ip_address):
        if pa_sensor_id in self._nodes:
            _LOGGER.debug('detected duplicate registration: %s', pa_sensor_id)
            return

        self._nodes[pa_sensor_id] = { 'ip_address': ip_address }
        _LOGGER.debug('registered new node: %s', pa_sensor_id)

        if not self._shutdown_interval:
            _LOGGER.debug('starting background poll: %s', self._scan_interval)
            self._shutdown_interval = async_track_time_interval(
                self._hass,
                self._update,
                self._scan_interval
            )

            async_track_point_in_utc_time(
                self._hass,
                self._update,
                dt.utcnow() + timedelta(seconds=5)
            )

    def unregister_node(self, pa_sensor_id):
        if pa_sensor_id not in self._nodes:
            _LOGGER.debug('detected non-existent unregistration: %s', pa_sensor_id)
            return

        del self._nodes[pa_sensor_id]
        _LOGGER.debug('unregistered node: %s', pa_sensor_id)

        if not self._nodes and self._shutdown_interval:
            _LOGGER.debug('no more nodes, shutting down interval')
            self._shutdown_interval()
            self._shutdown_interval = None


    async def _fetch_data(self, local_node_ips):
        if not local_node_ips:
            _LOGGER.debug('no nodes provided')
            return []

        urls =  map(LOCAL_URL_FORMAT.format, local_node_ips)
        _LOGGER.debug('fetch url list: %s', urls)

        results = []
        for url in urls:
            _LOGGER.debug('fetching url: %s', url)

            async with self._session.get(url) as response:
                if response.status != 200:
                    _LOGGER.warning('bad API response for %s: %s', url, response.status)

                json = await response.json()
                results.append(json)

        return results

    async def _update(self, now=None):
        local_node_ips = [n['ip_address'] for n in self._nodes.values()]
        _LOGGER.debug('nodes: %s', local_node_ips)

        results = await self._fetch_data(local_node_ips)

        nodes = {}
        for result in results:
            pa_sensor_id = result['SensorId']
            is_dual = 'pm2.5_aqi_b' in result
            nodes[pa_sensor_id] = {
                'device_location': result['place'],
                'rssi': result['rssi'],
                'current_temp': result['current_temp_f'],
                'current_humidity': result['current_humidity'],
                'current_dewpoint': result['current_dewpoint_f'],
                'pressure': result['pressure'],
                'is_dual': is_dual
            }
            nodes[pa_sensor_id].update(process_readings(result, is_dual))
            _LOGGER.debug('json results %s <===> readings: %s', result, nodes[pa_sensor_id])

        self._data = nodes
        async_dispatcher_send(self._hass, DISPATCHER_PURPLE_AIR)
