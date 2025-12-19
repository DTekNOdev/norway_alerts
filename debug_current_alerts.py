#!/usr/bin/env python3
"""
Test current avalanche API to see what activity levels we're getting
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'custom_components', 'varsom'))

# Set up the package path
import custom_components.varsom.api as api_module
from custom_components.varsom.api import WarningAPIFactory

async def test_current_alerts():
    """Test what activity levels are in current alerts"""
    # Use Vestland (46) which often has avalanche warnings
    api = WarningAPIFactory.get_api("avalanche", "46", "en")
    
    try:
        alerts = await api.fetch_warnings(municipality_filter="")
        
        print(f"=== Current Avalanche Alerts Debug ===")
        print(f"County: 46 (Vestland)")
        print(f"Found {len(alerts)} alerts")
        print()
        
        for i, alert in enumerate(alerts):
            activity_level = alert.get("ActivityLevel", "unknown")
            region_name = alert.get("RegionName", "Unknown")
            valid_from = alert.get("ValidFrom", "")
            valid_to = alert.get("ValidTo", "")
            
            print(f"Alert {i+1}: {region_name}")
            print(f"  Activity Level: {activity_level}")
            print(f"  Valid: {valid_from} - {valid_to}")
            
            # Test icon selection for this level
            from custom_components.varsom.const import ACTIVITY_LEVEL_NAMES, ICON_DATA_URLS
            level_color = ACTIVITY_LEVEL_NAMES.get(str(activity_level), "green")
            if level_color != "green":
                icon_key = f"avalanche-{level_color}"
                icon_available = icon_key in ICON_DATA_URLS
                print(f"  Maps to color: {level_color}")
                print(f"  Icon key: {icon_key}")
                print(f"  Icon available: {'Yes' if icon_available else 'No'}")
                
                # Check if this matches user's base64 data
                if icon_available:
                    icon_data = ICON_DATA_URLS[icon_key]
                    if 'FFE600' in icon_data:  # User's yellow color
                        print(f"  *** This is the YELLOW icon the user is seeing! ***")
            else:
                print(f"  Green level - no icon")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_current_alerts())