"""Config flow for Purple Air integration."""
import logging
import voluptuous as vol
import socket  # Used to validate IP address

from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_IP_ADDRESS, CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, LOCAL_URL_FORMAT, PMS_SENSOR, BME_SENSOR, MODEL_PA_1, MODEL_PA_2, MODEL_PA_FLEX

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """

    json = {}
    client = async_get_clientsession(hass)
    name = data['name']
    ip_address = data['ip_address']
    url = LOCAL_URL_FORMAT.format(ip_address)
    _LOGGER.debug('Using ip_address: %s. URL: %s', (ip_address, url))

    try:
        socket.inet_aton(ip_address)
    except socket.error:
        raise InvalidIp("The IP Address provided is not valid")

    async with client.get(url) as resp:
        if not resp.status == 200:
            raise InvalidIp(resp)

        json = await resp.json()

    config = {
        'title': name,
        'place': json['place'],
        'id': str(json['SensorId']),
        'ip_address': ip_address,
        'sw_version': json['version'],
        'hw_version': json['hardwareversion'],
        'model': get_model_name(json['hardwarediscovered']),
        'is_dual': ('pm2.5_aqi_b' in json)
    }

    _LOGGER.debug('generated config data: %s', config)
    return config


def get_model_name(hardwarediscovered):
    if hardwarediscovered.count(PMS_SENSOR) == 1:
        return MODEL_PA_1

    if hardwarediscovered.count(BME_SENSOR) > 1:
        return MODEL_PA_FLEX

    return MODEL_PA_2


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PurpleAir."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                await self.async_set_unique_id(info['id'])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=info)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidIp:
                errors["base"] = "invalid_ip_address"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_IP_ADDRESS): str,
                vol.Required(CONF_NAME): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""

class InvalidIp(exceptions.HomeAssistantError):
    """Error to indicate there is invalid config IP Address."""

    def __init__(self, response):
        self.response = response

class InvalidResponse(exceptions.HomeAssistantError):
    """Error to indicate a bad HTTP response."""

    def __init__(self, response):
        self.response = response
