"""Switch platform for Norway Alerts."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Norway Alerts switch."""
    _LOGGER.debug("Setting up Norway Alerts switch for entry: %s", entry.entry_id)
    
    # Get config to construct the same name as the sensor
    config = entry.options if entry.options else entry.data
    warning_type = config.get("warning_type") or entry.data.get("warning_type")
    county_id = config.get("county_id") or entry.data.get("county_id")
    latitude = config.get("latitude") or entry.data.get("latitude")
    longitude = config.get("longitude") or entry.data.get("longitude")
    
    # Construct the same base name as the sensor
    warning_type_label = warning_type.replace("_", " ").title() if warning_type else "Alerts"
    
    if county_id:
        county_name = config.get("county_name") or entry.data.get("county_name", "Unknown")
        base_name = f"Norway Alerts {warning_type_label} {county_name}"
    else:
        location_name = f"({latitude:.2f}, {longitude:.2f})" if latitude and longitude else "Unknown"
        base_name = f"Norway Alerts {warning_type_label} {location_name}"
    
    async_add_entities([NorwayAlertsCompactViewSwitch(entry, base_name)], True)


class NorwayAlertsCompactViewSwitch(SwitchEntity, RestoreEntity):
    """Switch to toggle compact view for Norway Alerts."""

    def __init__(self, entry: ConfigEntry, base_name: str) -> None:
        """Initialize the switch."""
        self._entry = entry
        # Use the same base name as the sensor for consistent entity_id generation
        self._attr_name = f"{base_name} Compact View"
        # Match the sensor's unique_id pattern: {entry_id}_alerts_compact_view
        self._attr_unique_id = f"{entry.entry_id}_alerts_compact_view"
        self._attr_icon = "mdi:view-compact"
        self._is_on = False

    async def async_added_to_hass(self) -> None:
        """Restore previous state when entity is added to hass."""
        await super().async_added_to_hass()
        
        # Restore previous state, default to False (full view)
        if (last_state := await self.async_get_last_state()) is not None:
            self._is_on = last_state.state == "on"
            _LOGGER.debug("Restored compact view switch state: %s", self._is_on)
        else:
            self._is_on = False
            _LOGGER.debug("No previous state found, defaulting to full view")

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on (compact view)."""
        return self._is_on

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on (enable compact view)."""
        self._is_on = True
        self.async_write_ha_state()
        _LOGGER.debug("Compact view enabled")

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off (disable compact view, show full details)."""
        self._is_on = False
        self.async_write_ha_state()
        _LOGGER.debug("Compact view disabled, showing full details")

    @property
    def device_info(self):
        """Return device info to group with the sensor."""
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._entry.title,
            "manufacturer": "Norway Alerts",
            "model": "Alert Monitor",
        }
