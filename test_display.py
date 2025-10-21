#!/usr/bin/env python3
"""
Test script for 8x8 LED Matrix Display
Tests the display functionality without requiring actual hardware
"""

import sys
import time
from datetime import datetime
from src.api.data_processor import DataProcessor
from src.display.icons import WeatherIcons

def test_icons():
    """Test icon rendering"""
    print("Testing weather icons...")
    
    # Test basic icons
    icons_to_test = ['sunny', 'cloudy', 'rainy', 'thunderstorm', 'snowy']
    
    for icon_name in icons_to_test:
        icon = WeatherIcons.get_icon(icon_name)
        print(f"\n{icon_name.upper()} icon:")
        for row in icon:
            print(f"  {row:08b}".replace('0', ' ').replace('1', '█'))
    
    # Test digits
    print("\nTesting digits:")
    for digit in '0123456789':
        icon = WeatherIcons.DIGITS[digit]
        print(f"\nDigit {digit}:")
        for row in icon:
            print(f"  {row:08b}".replace('0', ' ').replace('1', '█'))

def test_data_processing():
    """Test data processing functions"""
    print("\nTesting data processing...")
    
    processor = DataProcessor()
    
    # Test temperature conversion
    test_temps = [15, 20, 25, 30, 35]
    temp_levels = processor._temperature_to_levels(test_temps)
    print(f"Temperature levels: {temp_levels}")
    
    # Test precipitation conversion
    test_probs = [30, 60, 80, 40, 70]
    pop_levels = processor._precipitation_to_levels(test_probs)
    print(f"Precipitation levels: {pop_levels}")
    
    # Test weather icon mapping
    test_weathers = ['晴天', '多雲', '陰天', '雷雨', '下雨', '下雪']
    for weather in test_weathers:
        icon_name = processor.get_weather_icon_name(weather)
        print(f"Weather '{weather}' -> Icon '{icon_name}'")

def test_time_index():
    """Test time index calculation"""
    print("\nTesting time index calculation...")
    
    processor = DataProcessor()
    
    for hour in range(24):
        index = processor.calculate_time_index(hour)
        print(f"Hour {hour:02d}:00 -> Index {index}")

def simulate_display():
    """Simulate display content"""
    print("\nSimulating display content...")
    
    # Simulate temperature data
    temp_levels = [2, 3, 4, 5, 6, 4, 3, 2]
    rain_levels = [0, 1, 0, 1, 0, 0, 1, 0]
    
    print("Temperature bars (8x8 display):")
    for row in range(8):
        line = ""
        for col in range(8):
            if row < temp_levels[col]:
                line += "█"
            elif row == 7 and rain_levels[col]:
                line += "·"
            else:
                line += " "
        print(f"  {line}")
    
    # Simulate temperature display
    temp = 25
    temp_str = f"{temp:02d}"
    print(f"\nTemperature display ({temp}°C):")
    
    # Draw first digit
    digit1 = WeatherIcons.DIGITS[temp_str[0]]
    digit2 = WeatherIcons.DIGITS[temp_str[1]]
    
    for row in range(8):
        line = ""
        # First digit (left half)
        for col in range(4):
            if digit1[row] & (1 << (7 - col)):
                line += "█"
            else:
                line += " "
        # Second digit (right half)
        for col in range(4):
            if digit2[row] & (1 << (7 - col)):
                line += "█"
            else:
                line += " "
        print(f"  {line}")

def main():
    """Run all tests"""
    print("8x8 LED Matrix Display Test")
    print("=" * 40)
    
    try:
        test_icons()
        test_data_processing()
        test_time_index()
        simulate_display()
        
        print("\n" + "=" * 40)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()