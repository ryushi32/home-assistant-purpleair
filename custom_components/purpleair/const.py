"""Constants for the Purple Air integration."""
from homeassistant.const import UnitOfTemperature, UnitOfPressure
from homeassistant.components.sensor import SensorDeviceClass

AQI_BREAKPOINTS = {
    'pm2_5': [
        { 'pm_low': 500.5, 'pm_high': 999.9, 'aqi_low': 501, 'aqi_high': 999 },
        { 'pm_low': 350.5, 'pm_high': 500.4, 'aqi_low': 401, 'aqi_high': 500 },
        { 'pm_low': 250.5, 'pm_high': 350.4, 'aqi_low': 301, 'aqi_high': 400 },
        { 'pm_low': 150.5, 'pm_high': 250.4, 'aqi_low': 201, 'aqi_high': 300 },
        { 'pm_low':  55.5, 'pm_high': 150.4, 'aqi_low': 151, 'aqi_high': 200 },
        { 'pm_low':  35.5, 'pm_high':  55.4, 'aqi_low': 101, 'aqi_high': 150 },
        { 'pm_low':  12.1, 'pm_high':  35.4, 'aqi_low':  51, 'aqi_high': 100 },
        { 'pm_low':     0, 'pm_high':  12.0, 'aqi_low':   0, 'aqi_high':  50 },
    ],
}
PARTICLE_PROPS = ['pm1_0_atm', 'pm2_5_atm', 'pm10_0_atm', 'pm1_0_cf_1', 'pm2_5_cf_1', 'pm10_0_cf_1']

# Map of sensors to create entities for
SENSORS_MAP = {
    'sensor_confidence':       {'key': 'pm2_5_raw_conf',   'uom': None, 'device_class': None, 'icon': 'mdi:seal'},
    'pm1_0_raw':               {'key': 'pm1_0_raw',        'uom': 'µg/m³', 'device_class': SensorDeviceClass.PM1,  'icon': 'mdi:blur'},
    'pm2_5_raw':               {'key': 'pm2_5_raw',        'uom': 'µg/m³', 'device_class': SensorDeviceClass.PM25, 'icon': 'mdi:blur'},
    'pm2_5_epa':               {'key': 'pm2_5_epa',        'uom': 'µg/m³', 'device_class': SensorDeviceClass.PM25, 'icon': 'mdi:blur'},
    'pm2_5_alt':               {'key': 'pm2_5_alt',        'uom': 'µg/m³', 'device_class': SensorDeviceClass.PM25, 'icon': 'mdi:blur'},
    'pm10_0_raw':              {'key': 'pm10_0_raw',       'uom': 'µg/m³', 'device_class': SensorDeviceClass.PM10, 'icon': 'mdi:blur'},
    'aqi_epa_raw_pm':          {'key': 'aqi_epa_raw_pm',   'uom': None, 'device_class': SensorDeviceClass.AQI, 'icon': 'mdi:weather-hazy'},
    'aqi_epa_cor_pm':          {'key': 'aqi_epa_cor_pm',   'uom': None, 'device_class': SensorDeviceClass.AQI, 'icon': 'mdi:weather-hazy'},
    'aqi_epa_alt_pm':          {'key': 'aqi_epa_alt_pm',   'uom': None, 'device_class': SensorDeviceClass.AQI, 'icon': 'mdi:weather-hazy'},
    'rh_operating':            {'key': 'rh_operating',     'uom': '%', 'device_class': SensorDeviceClass.HUMIDITY, 'icon': 'mdi:water-percent'},
    'rh_estimated':            {'key': 'rh_estimated',     'uom': '%', 'device_class': SensorDeviceClass.HUMIDITY, 'icon': 'mdi:water-percent'},
    'temp_operating':          {'key': 'temp_operating',   'uom': UnitOfTemperature.FAHRENHEIT, 'device_class': SensorDeviceClass.TEMPERATURE, 'icon': 'mdi:thermometer'},
    'temp_estimated':          {'key': 'temp_estimated',   'uom': UnitOfTemperature.FAHRENHEIT, 'device_class': SensorDeviceClass.TEMPERATURE, 'icon': 'mdi:thermometer'},
    'dewpoint':                {'key': 'current_dewpoint', 'uom': UnitOfTemperature.FAHRENHEIT, 'device_class': SensorDeviceClass.TEMPERATURE, 'icon': 'mdi:water-outline'},
    'pressure':                {'key': 'pressure',         'uom': UnitOfPressure.HPA, 'device_class': SensorDeviceClass.PRESSURE, 'icon': 'mdi:gauge'},
    'rssi':                    {'key': 'rssi',             'uom': 'dBm', 'device_class': SensorDeviceClass.SIGNAL_STRENGTH, 'icon': 'mdi:wifi'}
}

MANUFACTURER = 'Purple Air'
DISPATCHER_PURPLE_AIR = 'dispatcher_purple_air'
DOMAIN = "purpleair"

LOCAL_SCAN_INTERVAL = 30
LOCAL_URL_FORMAT = "http://{0}/json?live=false"

# Models
PMS_SENSOR = 'PMS'
BME_SENSOR = 'BME'
MODEL_PA_1 = 'PA-I'
MODEL_PA_2 = 'PA-II'
MODEL_PA_FLEX = 'PA-II-FLEX'
