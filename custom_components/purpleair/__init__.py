"""The (Local) PurpleAir integration."""
import asyncio
import logging

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .PurpleAirApi import PurpleAirApi

PLATFORMS = ["sensor"]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the PurpleAir component."""
    session = async_get_clientsession(hass)

    hass.data[DOMAIN] = PurpleAirApi(hass, session)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up PurpleAir from a config entry."""

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )

    return unload_ok
