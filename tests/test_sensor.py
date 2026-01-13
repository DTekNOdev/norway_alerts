"""Unit tests for Norway Alerts sensor platform."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from custom_components.norway_alerts.const import CONF_WARNING_TYPE, WARNING_TYPE_LANDSLIDE


class TestNorwayAlertsSensor:
    """Test Norway Alerts sensor entity."""

    @pytest.mark.asyncio
    async def test_sensor_update_with_alerts(self, mock_hass, mock_county_api_response):
        """Test sensor update when alerts exist."""
        from custom_components.norway_alerts.sensor import NorwayAlertsSensor
        
        config = {
            "county_id": "46",
            "county_name": "Vestland",
            CONF_WARNING_TYPE: WARNING_TYPE_LANDSLIDE,
            "lang": "en",
        }
        
        sensor = NorwayAlertsSensor(mock_hass, config, "test_sensor")
        
        with patch.object(sensor._api, "fetch_warnings", return_value=mock_county_api_response):
            await sensor.async_update()
        
        assert sensor.native_value == 1  # One alert
        assert sensor.state_attributes["alert_count"] == 1
        assert sensor.state_attributes["highest_level"] == "yellow"

    @pytest.mark.asyncio
    async def test_sensor_update_no_alerts(self, mock_hass):
        """Test sensor update when no alerts exist."""
        from custom_components.norway_alerts.sensor import NorwayAlertsSensor
        
        config = {
            "county_id": "46",
            "county_name": "Vestland",
            CONF_WARNING_TYPE: WARNING_TYPE_LANDSLIDE,
            "lang": "en",
        }
        
        sensor = NorwayAlertsSensor(mock_hass, config, "test_sensor")
        
        with patch.object(sensor._api, "fetch_warnings", return_value=[]):
            await sensor.async_update()
        
        assert sensor.native_value == 0
        assert sensor.state_attributes["alert_count"] == 0

    def test_sensor_icon_selection(self):
        """Test icon selection based on alert level."""
        from custom_components.norway_alerts.sensor import NorwayAlertsSensor
        
        config = {
            "county_id": "46",
            "county_name": "Vestland",
            CONF_WARNING_TYPE: WARNING_TYPE_LANDSLIDE,
            "lang": "en",
        }
        
        sensor = NorwayAlertsSensor(MagicMock(), config, "test_sensor")
        
        # Test with no alerts
        sensor._active_alerts = []
        assert sensor.entity_picture is None
        
        # Test with yellow alert
        sensor._active_alerts = [{"ActivityLevel": "2"}]
        sensor._highest_level_numeric = 2
        assert sensor.entity_picture is not None

    @pytest.mark.asyncio
    async def test_notification_sending(self, mock_hass, mock_county_api_response):
        """Test notification is sent for new alert."""
        from custom_components.norway_alerts.sensor import NorwayAlertsSensor
        
        config = {
            "county_id": "46",
            "county_name": "Vestland",
            CONF_WARNING_TYPE: WARNING_TYPE_LANDSLIDE,
            "lang": "en",
            "enable_notifications": True,
            "notification_severity": "yellow_plus",
        }
        
        sensor = NorwayAlertsSensor(mock_hass, config, "test_sensor")
        
        with patch.object(sensor._api, "fetch_warnings", return_value=mock_county_api_response):
            with patch.object(sensor, "_send_new_alert_notification") as mock_notify:
                await sensor.async_update()
                
                # Should send notification for yellow+ alert
                assert mock_notify.call_count > 0
