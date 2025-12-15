# Setup Checklist - Varsom Alerts Integration

## Pre-Installation

- [ ] Home Assistant 2024.1.0 or newer installed
- [ ] Located in Norway or monitoring Norwegian regions
- [ ] Internet connection available

## Installation

### Option A: Manual Install
- [ ] Copy `custom_components/varsom/` to HA config directory
- [ ] Verify file permissions
- [ ] Restart Home Assistant
- [ ] Check HA logs for loading errors

### Option B: HACS Install
- [ ] HACS installed and configured
- [ ] Add custom repository
- [ ] Install Varsom Alerts from HACS
- [ ] Restart Home Assistant

## Configuration

- [ ] Go to Settings → Devices & Services
- [ ] Click "+ Add Integration"
- [ ] Search for "Varsom Alerts"
- [ ] Select county (e.g., Vestland = 46)
- [ ] Choose warning type (Landslide/Flood/Both)
- [ ] Select language (English/Norwegian)
- [ ] Complete setup

## Verification

- [ ] Integration appears in Devices & Services
- [ ] Sensor entity created: `sensor.varsom_[type]_[county]`
- [ ] Sensor has valid state (1-4)
- [ ] Attributes contain expected fields:
  - [ ] `active_alerts`
  - [ ] `highest_level`
  - [ ] `county_name`
  - [ ] `alerts` array
- [ ] Check Developer Tools → States for sensor
- [ ] Verify icon displays correctly
- [ ] Wait 30 minutes for first update (or trigger manual update)

## Testing with Live Data

To test with actual warnings:

- [ ] Visit https://www.varsom.no/ to find counties with active warnings
- [ ] Configure integration for county with active alert
- [ ] Verify sensor state > 1 (yellow/orange/red)
- [ ] Check alerts array contains warning data
- [ ] Verify municipality names are present
- [ ] Check Varsom.no URL in each alert works

## Optional: Multiple Counties

You can monitor multiple counties:

- [ ] Add integration again (repeat process)
- [ ] Select different county
- [ ] Each creates separate sensor
- [ ] All update independently

Example:
- `sensor.varsom_landslide_vestland`
- `sensor.varsom_landslide_rogaland`
- `sensor.varsom_flood_oslo`

## Automation Setup

Create test automation:

```yaml
automation:
  - alias: "Test Varsom Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.varsom_landslide_vestland
      above: 1
    action:
      service: persistent_notification.create
      data:
        title: "Landslide Warning"
        message: "Alert level: {{ states('sensor.varsom_landslide_vestland') }}"
```

- [ ] Create automation
- [ ] Test triggers when alert level changes
- [ ] Verify notification received

## Troubleshooting

If issues occur:

### Integration Not Found
- [ ] Check files in `/config/custom_components/varsom/`
- [ ] Verify manifest.json exists
- [ ] Check HA logs: Settings → System → Logs
- [ ] Search for "varsom" in logs

### Connection Errors
- [ ] Test internet: ping api01.nve.no
- [ ] Check HA can access external APIs
- [ ] Verify no firewall blocking
- [ ] Try different county

### No Data Showing
- [ ] Confirm county has active warnings (check varsom.no)
- [ ] State = 1 (green) is normal when no warnings
- [ ] Check `last_updated` attribute
- [ ] Manually trigger update in Developer Tools

### Sensor Not Updating
- [ ] Default interval is 30 minutes (expected)
- [ ] Check HA logs for coordinator errors
- [ ] Verify API accessible: https://api01.nve.no/
- [ ] Try manual update via Developer Tools

## Advanced Usage

### Template Sensors
- [ ] Create municipality-filtered sensor
- [ ] Test template renders correctly
- [ ] Add to Lovelace dashboard

### Lovelace Cards
- [ ] Add entities card with sensor
- [ ] Show active_alerts attribute
- [ ] Display alert details
- [ ] Link to Varsom.no URLs

### Notifications
- [ ] Configure mobile app notifications
- [ ] Add actionable notifications
- [ ] Include alert URLs in notifications
- [ ] Test on iOS/Android

## Maintenance

Regular checks:

- [ ] Monthly: Verify sensor still updating
- [ ] Quarterly: Check for integration updates
- [ ] Yearly: Review automation still relevant
- [ ] As needed: Update county selection

## Documentation Reference

Files to review:
- `README.md` - Main documentation
- `INSTALLATION.md` - Detailed install guide
- `DEV_SUMMARY.md` - Technical details
- `CHANGELOG.md` - Version history

## Support

If problems persist:
- [ ] Review all documentation
- [ ] Check GitHub issues
- [ ] Create new issue with:
  - HA version
  - Integration version
  - Error logs
  - Steps to reproduce

---

**Setup Date**: _____________  
**HA Version**: _____________  
**Integration Version**: 1.0.0  
**Counties Configured**: _____________  
**Notes**: _____________
