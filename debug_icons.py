#!/usr/bin/env python3
"""
Debug script to understand the icon selection logic for Varsom alerts
"""
import sys
sys.path.append('custom_components/varsom')

from const import ACTIVITY_LEVEL_NAMES, ICON_DATA_URLS

def test_icon_selection():
    """Test the icon selection logic"""
    warning_type = "avalanche"
    
    print("=== Icon Selection Debug ===")
    print(f"Warning type: {warning_type}")
    print()
    
    print("Activity level mapping (ACTIVITY_LEVEL_NAMES):")
    for level, color in ACTIVITY_LEVEL_NAMES.items():
        print(f"  Level {level}: {color}")
        
        # Test icon key generation
        if color != "green":
            icon_key = f"{warning_type}-{color}"
            icon_data = ICON_DATA_URLS.get(icon_key)
            icon_available = "✓" if icon_data else "✗"
            print(f"    Icon key: {icon_key} {icon_available}")
            if icon_data:
                # Extract color from SVG data if possible
                if 'fill="#' in icon_data:
                    start = icon_data.find('fill="#') + 6
                    end = icon_data.find('"', start)
                    svg_color = icon_data[start:end]
                    print(f"    SVG color: #{svg_color}")
        else:
            print(f"    No icon needed for green level")
        print()
    
    print("Available icon keys in ICON_DATA_URLS:")
    for key in sorted(ICON_DATA_URLS.keys()):
        if key.startswith('avalanche-'):
            print(f"  {key}")
    print()
    
    # Test specific cases
    test_cases = [
        ("1", "Should be green (no icon)"),
        ("2", "Should be yellow"),
        ("3", "Should be orange"), 
        ("4", "Should be red"),
        ("5", "Should be black (extreme)")
    ]
    
    print("Test cases:")
    for activity_level, expected in test_cases:
        level_color = ACTIVITY_LEVEL_NAMES.get(activity_level, "green")
        if level_color != "green":
            icon_key = f"{warning_type}-{level_color}"
            icon_available = icon_key in ICON_DATA_URLS
            print(f"  Level {activity_level}: {expected}")
            print(f"    Maps to: {level_color}")
            print(f"    Icon key: {icon_key}")
            print(f"    Available: {'Yes' if icon_available else 'No'}")
        else:
            print(f"  Level {activity_level}: {expected} (no icon)")
        print()

if __name__ == "__main__":
    test_icon_selection()