"""Pytest configuration and fixtures for Norway Alerts tests."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock(spec=HomeAssistant)
    hass.config_entries = MagicMock()
    hass.data = {}
    hass.states = MagicMock()
    hass.services = MagicMock()
    return hass


@pytest.fixture
def mock_aiohttp_session():
    """Create a reusable mock aiohttp ClientSession setup.
    
    Returns a function that creates a properly configured mock session
    given one or more mock responses.
    
    Usage:
        mock_session_class = mock_aiohttp_session(mock_response)
        # Or for multiple calls:
        mock_session_class = mock_aiohttp_session(mock_response1, mock_response2)
    """
    def _create_mock_session(*responses):
        """Create mock session with given response(s)."""
        # Create context managers for each response
        mock_get_cms = []
        for response in responses:
            mock_get_cm = MagicMock()
            mock_get_cm.__aenter__ = AsyncMock(return_value=response)
            mock_get_cm.__aexit__ = AsyncMock(return_value=None)
            mock_get_cms.append(mock_get_cm)
        
        # Create mock session
        mock_session = MagicMock()
        if len(mock_get_cms) == 1:
            mock_session.get = MagicMock(return_value=mock_get_cms[0])
        else:
            mock_session.get = MagicMock(side_effect=mock_get_cms)
        
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        # Create mock session class
        mock_session_class = MagicMock()
        mock_session_class.return_value = mock_session
        
        return mock_session_class
    
    return _create_mock_session


@pytest.fixture
def mock_county_api_response():
    """Mock response from NVE county-based API (landslide/flood)."""
    return [
        {
            "Id": 123456,
            "MasterId": 789,
            "ActivityLevel": "2",
            "DangerLevel": "Level 2",
            "DangerTypeName": "Jordskred",
            "MainText": "Moderat fare for jordskred",
            "RegionName": "Vestland",
            "ValidFrom": "2024-01-01T00:00:00+01:00",
            "ValidTo": "2024-01-02T00:00:00+01:00",
            "PublishTime": "2024-01-01T08:00:00+01:00",
            "MunicipalityList": [
                {"Name": "Bergen", "Id": 4601}
            ]
        }
    ]


@pytest.fixture
def mock_avalanche_api_response():
    """Mock response from NVE avalanche API."""
    return [
        {
            "RegionId": 3022,
            "RegionName": "Voss",
            "DangerLevel": 3,
            "ValidFrom": "2024-01-01T00:00:00+01:00",
            "ValidTo": "2024-01-02T00:00:00+01:00",
            "MainText": "Betydelig snøskredfare",
            "CountyList": [{"Name": "Vestland"}],
            "MunicipalityList": [{"Name": "Voss", "CountyId": 46}],
            "AvalancheProblems": []
        }
    ]


@pytest.fixture
def mock_metalerts_api_response():
    """Mock response from Met.no MetAlerts API."""
    return {
        "features": [
            {
                "properties": {
                    "id": "2.49.0.1.578.0.20240101121500",
                    "title": "Orange level for rain, 2024-01-01T12:00:00+01:00, 2024-01-02T00:00:00+01:00",
                    "description": "Heavy rainfall expected",
                    "event": "rain",
                    "area": "Vestland",
                    "awareness_level": "2; orange; Moderate",
                    "awareness_type": "2; moderate",
                    "certainty": "Likely",
                    "severity": "Moderate",
                    "instruction": "Be prepared",
                    "resources": [
                        {"uri": "https://example.com/map.png", "mimeType": "image/png"}
                    ]
                }
            }
        ]
    }
