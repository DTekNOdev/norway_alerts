"""Simplified coordinator using API classes."""

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import WARNING_TYPE_LANDSLIDE, WARNING_TYPE_FLOOD, WARNING_TYPE_AVALANCHE, WARNING_TYPE_BOTH, WARNING_TYPE_ALL
from .api import WarningAPIFactory

import logging
_LOGGER = logging.getLogger(__name__)


class VarsomAlertsCoordinator(DataUpdateCoordinator):
    """Simplified coordinator using modular API classes."""

    def __init__(self, hass, county_id, county_name, warning_type, lang, test_mode=False):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="varsom",
            update_interval=timedelta(minutes=30),
        )
        self.county_id = county_id
        self.county_name = county_name
        self.warning_type = warning_type
        self.lang = lang
        self.test_mode = test_mode

    async def _async_update_data(self):
        """Fetch data using API classes."""
        all_warnings = []
        
        try:
            # Inject test alert if test mode is enabled
            if self.test_mode:
                test_alert = {
                    "Id": 999999,
                    "ActivityLevel": "3",
                    "DangerLevel": "Moderate", 
                    "DangerTypeName": "Jordskred",
                    "MainText": "Test Alert - Orange Landslide Warning for Testville",
                    "_warning_type": "landslide"
                }
                all_warnings.append(test_alert)
                _LOGGER.info("Test mode: Injected fake alert")
            
            # Determine which API clients to use
            warning_types_to_fetch = []
            
            if self.warning_type == WARNING_TYPE_LANDSLIDE:
                warning_types_to_fetch = ["landslide"]
            elif self.warning_type == WARNING_TYPE_FLOOD:
                warning_types_to_fetch = ["flood"]
            elif self.warning_type == WARNING_TYPE_AVALANCHE:
                warning_types_to_fetch = ["avalanche"]
            elif self.warning_type == WARNING_TYPE_BOTH:
                warning_types_to_fetch = ["landslide", "flood"]
            elif self.warning_type == WARNING_TYPE_ALL:
                warning_types_to_fetch = ["landslide", "flood", "avalanche"]
            
            # Fetch warnings from each API
            for wtype in warning_types_to_fetch:
                _LOGGER.info("Fetching %s warnings", wtype)
                
                api_client = WarningAPIFactory.create_api(
                    wtype, self.county_id, self.county_name, self.lang
                )
                
                warnings = await api_client.fetch_warnings()
                
                # Tag warnings with their type
                for warning in warnings:
                    warning["_warning_type"] = wtype
                
                all_warnings.extend(warnings)
                _LOGGER.info("Added %d %s warnings", len(warnings), wtype)
            
            _LOGGER.info("Total warnings fetched: %d", len(all_warnings))
            
            # Debug: log warning types breakdown
            warning_types = {}
            for warning in all_warnings:
                wtype = warning.get("_warning_type", "unknown")
                warning_types[wtype] = warning_types.get(wtype, 0) + 1
            _LOGGER.info("Warning types breakdown: %s", warning_types)
            
            return all_warnings
            
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}")