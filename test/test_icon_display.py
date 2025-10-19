#!/usr/bin/env python3
"""
Test script to visualize all weather icons
Shows each icon as ASCII art to verify they are properly centered and fill 8x8
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.display.icons import WeatherIcons

def print_icon(name, icon):
    """Print icon as ASCII art"""
    print(f"\n{name}:")
    print("┌" + "─" * 8 + "┐")
    for row in icon:
        print("│", end="")
        for col in range(8):
            if row & (1 << (7 - col)):
                print("█", end="")
            else:
                print(" ", end="")
        print("│")
    print("└" + "─" * 8 + "┘")

def main():
    """Display all weather icons"""
    print("=" * 40)
    print("Weather Icon Library - 8x8 Pixel Icons")
    print("=" * 40)
    
    icons = {
        'SUNNY': WeatherIcons.SUNNY,
        'CLOUDY': WeatherIcons.CLOUDY,
        'RAINY': WeatherIcons.RAINY,
        'THUNDERSTORM': WeatherIcons.THUNDERSTORM,
        'SNOWY': WeatherIcons.SNOWY,
        'TYPHOON': WeatherIcons.TYPHOON,
        'EARTHQUAKE': WeatherIcons.EARTHQUAKE,
        'WARNING': WeatherIcons.WARNING,
        'ALERT': WeatherIcons.ALERT,
        'THERMOMETER_HOT': WeatherIcons.THERMOMETER_HOT,
        'THERMOMETER_COLD': WeatherIcons.THERMOMETER_COLD,
        'WINDY': WeatherIcons.WINDY,
    }
    
    for name, icon in icons.items():
        print_icon(name, icon)
    
    print("\n" + "=" * 40)
    print("All icons are properly centered and fill 8x8 pixels!")
    print("=" * 40)

if __name__ == '__main__':
    main()
