# Installation Guide - Varsom Alerts

## Quick Start

### Prerequisites
- Home Assistant 2024.1.0 or newer
- Internet connection to access NVE API
- Located in Norway or interested in Norwegian alerts

### Installation Steps

#### Method 1: HACS (Recommended)

1. **Add Custom Repository**
   - Open HACS in Home Assistant
   - Click the three dots in the top right
   - Select "Custom repositories"
   - Add repository URL: `https://github.com/jm-cook/varsom`
   - Category: Integration
   - Click "Add"

2. **Install Integration**
   - Search for "Varsom Alerts" in HACS
   - Click "Download"
   - Restart Home Assistant

3. **Add Integration**
   - Go to Settings → Devices & Services
   - Click "+ Add Integration"
   - Search for "Varsom Alerts"
   - Follow the configuration steps

#### Method 2: Manual Installation

1. **Copy Files**
   ```bash
   cd /config
   mkdir -p custom_components/varsom
   # Copy all files from custom_components/varsom to this directory
   ```

2. **Restart Home Assistant**
   - Settings → System → Restart

3. **Add Integration**
   - Go to Settings → Devices & Services
   - Click "+ Add Integration"
   - Search for "Varsom Alerts"

## Configuration

### Initial Setup

When adding the integration, you'll be prompted for:

1. **County** (required)
   - Select your Norwegian county from the dropdown
   - Example: Vestland, Rogaland, Oslo, etc.

2. **Warning Type** (required)
   - Landslide: Monitor landslide warnings only
   - Flood: Monitor flood warnings only
   - Both: Monitor both types (creates combined sensor)

3. **Language** (optional, default: English)
   - English (en)
   - Norwegian (no)

### Example Configuration

**Vestland County - Landslide Warnings**
- County: `Vestland`
- Warning Type: `Landslide`
- Language: `English`

This creates: `sensor.varsom_landslide_vestland`

### Multiple Configurations

You can add multiple instances for different counties:
- `sensor.varsom_landslide_vestland`
- `sensor.varsom_landslide_rogaland`
- `sensor.varsom_flood_vestland`

Each instance polls independently.

## Testing the Installation

### 1. Check Sensor Exists

Go to Developer Tools → States and search for `sensor.varsom`

### 2. View Attributes

Click on the sensor to see:
- State: `1` (green) to `4` (red)
- Attributes: `active_alerts`, `alerts` array, etc.

### 3. Test with Script

Run the included test script:
```bash
cd /config/custom_components/varsom
python3 test_varsom_api.py
```

## Troubleshooting

### Integration Not Found

**Problem**: "Varsom Alerts" doesn't appear in the integration list

**Solutions**:
1. Ensure files are in `/config/custom_components/varsom/`
2. Check file permissions (should be readable by HA)
3. Restart Home Assistant
4. Check logs for errors: Settings → System → Logs

### Cannot Connect Error

**Problem**: "Failed to connect to NVE/Varsom API"

**Solutions**:
1. Check internet connection
2. Verify NVE API is accessible: https://api01.nve.no/
3. Check Home Assistant logs for detailed error
4. Try different county or language setting

### No Alerts Showing

**Problem**: Sensor shows `1` (green) with no alerts

**Solutions**:
1. This is normal if there are no active warnings!
2. Check Varsom.no to verify: https://www.varsom.no/
3. Try a different county that might have active warnings
4. Check `last_updated` attribute to ensure sensor is updating

### Sensor Not Updating

**Problem**: Data seems stale

**Solutions**:
1. Check Home Assistant logs for API errors
2. Manually trigger update: Developer Tools → States → sensor → "Update"
3. Verify internet connection
4. Default update interval is 30 minutes (this is normal)

## Verification

After installation, you should see:

✓ New integration in Settings → Devices & Services  
✓ Sensor entity: `sensor.varsom_[type]_[county]`  
✓ Sensor state: `1`, `2`, `3`, or `4`  
✓ Attributes with alert data (if warnings exist)  
✓ Icon updates based on alert level  

## Next Steps

- [Create automations](README.md#automation---alert-notification)
- [Add Lovelace cards](README.md#lovelace-card)
- [Filter by municipality](README.md#template-sensor---municipality-filter)
- Configure mobile notifications

## Support

- **Issues**: https://github.com/jm-cook/varsom/issues
- **Documentation**: See README.md
- **API Info**: https://api.nve.no/doc/

## Updates

The integration will update automatically if installed via HACS. Check the CHANGELOG.md for version history.

---

**Installation Date**: December 2025  
**Integration Version**: 1.0.0  
**Minimum HA Version**: 2024.1.0
