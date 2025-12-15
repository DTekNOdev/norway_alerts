# Varsom Alerts Integration - Development Summary

**Created**: December 15, 2025  
**Author**: Jeremy Cook  
**Branch**: Initial development (to be committed to no.varsom repo)

## Overview

A brand new Home Assistant custom integration for fetching landslide and flood warnings from NVE (Norwegian Water Resources and Energy Directorate) via the Varsom.no API.

## Key Design Decisions

### ✅ Single Sensor Pattern
Unlike the older `met_alerts` integration which creates 4 sensors (_1, _2, _3, _4), this integration follows modern HA best practices:
- **One sensor per configuration** (e.g., `sensor.varsom_landslide_vestland`)
- **All alerts in attributes array** - scalable from 0 to 100+ alerts
- **State = highest alert level** (1-4) for easy automation triggers
- **Rich structured data** in attributes for template sensors

### API Integration
- **Landslide API**: `https://api01.nve.no/hydrology/forecast/landslide/v1.0.10/api`
- **Flood API**: `https://api01.nve.no/hydrology/forecast/flood/v1.0.10/api`
- **Update interval**: 30 minutes (warnings updated 1-2x daily)
- **No SSL issues**: Uses standard aiohttp (unlike met_alerts which needed certifi)

### Configuration
- **County-based**: Users select from 11 Norwegian counties
- **Warning types**: Landslide, Flood, or Both
- **Bilingual**: English and Norwegian support
- **UI Config Flow**: No YAML required

## File Structure

```
no.varsom/
├── custom_components/
│   └── varsom/
│       ├── __init__.py           # Integration setup
│       ├── config_flow.py        # UI configuration
│       ├── const.py              # Constants (counties, API URLs)
│       ├── manifest.json         # Integration metadata
│       ├── sensor.py             # Main sensor logic (single sensor)
│       ├── strings.json          # UI strings
│       └── translations/
│           └── en.json           # English translations
├── .gitignore
├── CHANGELOG.md
├── hacs.json
├── INSTALLATION.md
├── README.md
└── test_varsom_api.py           # API test script
```

## Sensor Data Structure

### State
Integer 1-4 representing highest alert level:
- `1` = Green (no warnings)
- `2` = Yellow (moderate)
- `3` = Orange (considerable)
- `4` = Red (high/extreme)

### Attributes
```python
{
    "active_alerts": 2,                    # Count of active warnings
    "highest_level": "yellow",             # Text representation
    "highest_level_numeric": 2,            # Numeric level
    "county_name": "Vestland",
    "county_id": "46",
    "alerts": [                            # Array of all active alerts
        {
            "id": "584731",                # NVE forecast ID
            "level": 2,                     # 1-4
            "level_name": "yellow",
            "danger_type": "Jord- og flomskredfare",
            "warning_type": "landslide",    # or "flood"
            "municipalities": ["Tysnes", "Bergen"],
            "valid_from": "2025-12-14T07:00:00",
            "valid_to": "2025-12-15T06:59:00",
            "danger_increases": "2025-12-14T16:00:00",
            "danger_decreases": "2025-12-15T19:00:00",
            "main_text": "Moderate avalanche danger...",
            "warning_text": "Up to 150mm precipitation...",
            "advice_text": "Stay informed...",
            "consequence_text": "Landslides may occur...",
            "url": "https://www.varsom.no/en/flood-and-landslide-warning-service/forecastid/584731"
        },
        # ... more alerts
    ]
}
```

## Usage Examples

### Basic Automation
```yaml
automation:
  - alias: "Yellow Alert Notification"
    trigger:
      platform: numeric_state
      entity_id: sensor.varsom_landslide_vestland
      above: 1
    action:
      service: notify.mobile_app
      data:
        title: "Landslide Warning"
        message: "{{ state_attr('sensor.varsom_landslide_vestland', 'alerts')[0].main_text }}"
```

### Municipality Filter Template
```yaml
template:
  - sensor:
      name: "Bergen Alerts"
      state: >
        {% set alerts = state_attr('sensor.varsom_landslide_vestland', 'alerts') 
                        | selectattr('municipalities', 'search', 'Bergen') | list %}
        {{ alerts[0].level_name if alerts else 'green' }}
```

## Testing

### Test Script
Run `test_varsom_api.py` to verify API connection:
```bash
python test_varsom_api.py
```

Shows:
- Active warnings count
- Highest alert level
- Detailed alert information
- Preview of sensor state/attributes

### Manual Testing
1. Add integration in HA UI
2. Select county with active warnings (check varsom.no first)
3. Verify sensor appears with correct state
4. Check attributes contain alert data
5. Test automation triggers

## Comparison with met_alerts

| Feature | met_alerts | varsom |
|---------|-----------|--------|
| Data Source | Met.no weather | NVE landslide/flood |
| Sensor Pattern | 4 sensors (_2, _3, _4) | 1 sensor |
| Alert Storage | Split across sensors | All in attributes |
| Configuration | Lat/Lon coordinates | County selection |
| SSL Handling | Needs certifi | Standard |
| Alert Types | Weather events | Landslide/flood |

## Next Steps

### Before Production
- [ ] Test with live alerts (wait for active warnings)
- [ ] Test all 11 counties
- [ ] Test both English and Norwegian
- [ ] Test flood API endpoint
- [ ] Test "both" warning type option
- [ ] Verify options flow (reconfiguration)

### Future Enhancements
- Optional municipality filtering in config
- Add "last_update" timestamp attribute
- Diagnostic sensor for API status
- Support for alert history
- Custom update interval option
- Alert severity icons/badges
- Integration with HA alerts/notifications

### Documentation
- Add screenshots to README
- Create example Lovelace dashboard
- Add more automation examples
- Document template sensor patterns
- Add FAQ section

## API Notes

### County IDs (NVE)
```python
COUNTIES = {
    "03": "Oslo",
    "11": "Rogaland",
    "15": "Møre og Romsdal",
    "18": "Nordland",
    "30": "Viken",
    "34": "Innlandet",
    "38": "Vestfold og Telemark",
    "42": "Agder",
    "46": "Vestland",
    "50": "Trøndelag",
    "54": "Troms og Finnmark",
}
```

### Response Filtering
- Only alerts with `ActivityLevel != "1"` are included in attributes
- Alerts sorted by level (highest first)
- Green (level 1) responses still valid - just means no warnings

### Varsom.no URLs
Format: `https://www.varsom.no/[lang]/flood-and-landslide-warning-service/forecastid/{Id}`
- English: `/en/flood-and-landslide...`
- Norwegian: `/flood-and-landslide...` (no lang prefix)

## Technical Implementation

### Coordinator Pattern
Uses `DataUpdateCoordinator` for efficient polling:
- 30-minute update interval
- Automatic retry on failure
- Shared data across entities (if multiple in future)
- Proper error handling

### Config Flow
- Validates API connection during setup
- County dropdown with friendly names
- Warning type selection
- Language preference
- Options flow for reconfiguration

### Error Handling
- Connection errors: Logs and continues
- Invalid JSON: Logs and returns empty
- Missing data: Defaults to green/no alerts
- API down: Shows last known state

## Credits

Based on patterns from:
- `met_alerts` integration (structure)
- Home Assistant coordinator examples
- NVE API documentation at api.nve.no

## Related Files in met_alerts Branch

Files in `met_alerts` nve-test branch used for research:
- `DESIGN_NOTES.md` - API research and design decisions
- `test_nve_api.py` - Initial API exploration
- `check_nve_fields.py` - Response structure analysis

---

**Status**: ✅ Complete and ready for testing  
**Next**: Test with live alerts, commit to repo, test in Home Assistant
