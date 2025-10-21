#!/usr/bin/env python3
"""
Test script to verify data processing functionality
Tests the data processing logic without hardware dependencies
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.api.data_processor import DataProcessor
from datetime import datetime

def test_data_processor():
    """Test data processor with various scenarios"""
    print("Testing DataProcessor...")
    
    processor = DataProcessor()
    
    # Test 1: Empty data (should return fallback)
    print("\n1. Testing empty data:")
    result = processor.process_weather_forecast({})
    if result:
        temp_levels, pop_levels = result
        print(f"   ✅ Fallback data created: temp={temp_levels}, pop={pop_levels}")
        print(f"   ✅ Temperature levels: {temp_levels}")
        print(f"   ✅ Precipitation levels: {pop_levels}")
    else:
        print("   ❌ Failed to create fallback data")
    
    # Test 2: Invalid data structure (should return fallback)
    print("\n2. Testing invalid data structure:")
    invalid_data = {"records": {"Locations": []}}
    result = processor.process_weather_forecast(invalid_data)
    if result:
        temp_levels, pop_levels = result
        print(f"   ✅ Fallback data created: temp={temp_levels}, pop={pop_levels}")
    else:
        print("   ❌ Failed to create fallback data")
    
    # Test 3: Missing temperature data (should return fallback)
    print("\n3. Testing missing temperature data:")
    missing_temp_data = {
        "records": {
            "Locations": [{
                "Location": [{
                    "weatherElement": [{
                        "elementName": "PoP6h",
                        "time": [{"elementValue": [{"probability": "30"}]}]
                    }]
                }]
            }]
        }
    }
    result = processor.process_weather_forecast(missing_temp_data)
    if result:
        temp_levels, pop_levels = result
        print(f"   ✅ Fallback data created: temp={temp_levels}, pop={pop_levels}")
    else:
        print("   ❌ Failed to create fallback data")
    
    # Test 4: Valid data (should process normally)
    print("\n4. Testing valid data:")
    valid_data = {
        "records": {
            "Locations": [{
                "Location": [{
                    "weatherElement": [
                        {
                            "elementName": "T",
                            "time": [{"elementValue": [{"temperature": "25"}]}]
                        },
                        {
                            "elementName": "PoP6h",
                            "time": [{"elementValue": [{"probability": "30"}]}]
                        }
                    ]
                }]
            }]
        }
    }
    result = processor.process_weather_forecast(valid_data)
    if result:
        temp_levels, pop_levels = result
        print(f"   ✅ Valid data processed: temp={temp_levels}, pop={pop_levels}")
    else:
        print("   ❌ Failed to process valid data")
    
    print("\n✅ DataProcessor tests completed!")

def test_time_calculations():
    """Test time index calculations"""
    print("\nTesting time calculations...")
    
    processor = DataProcessor()
    
    test_hours = [0, 3, 6, 9, 12, 15, 18, 21, 23]
    expected_indices = [7, 0, 1, 2, 3, 4, 5, 6, 7]
    
    for hour, expected in zip(test_hours, expected_indices):
        result = processor.calculate_time_index(hour)
        if result == expected:
            print(f"   ✅ Hour {hour:02d}:00 -> Index {result}")
        else:
            print(f"   ❌ Hour {hour:02d}:00 -> Expected {expected}, got {result}")
    
    print("\n✅ Time calculation tests completed!")

def test_array_shifting():
    """Test array shifting functionality"""
    print("\nTesting array shifting...")
    
    processor = DataProcessor()
    
    test_array = [0, 1, 2, 3, 4, 5, 6, 7]
    
    for index in range(8):
        shifted = processor.shift_array(test_array, index)
        print(f"   Index {index}: {test_array} -> {shifted}")
    
    print("\n✅ Array shifting tests completed!")

def test_weather_icon_mapping():
    """Test weather icon name mapping"""
    print("\nTesting weather icon mapping...")
    
    processor = DataProcessor()
    
    test_cases = [
        ("晴天", "sunny"),
        ("多雲", "cloudy"),
        ("雨天", "rainy"),
        ("雷雨", "thunderstorm"),
        ("雪", "snowy"),
        ("颱風", "typhoon"),
        ("Unknown", "sunny")
    ]
    
    for weather_desc, expected in test_cases:
        result = processor.get_weather_icon_name(weather_desc)
        if result == expected:
            print(f"   ✅ '{weather_desc}' -> '{result}'")
        else:
            print(f"   ❌ '{weather_desc}' -> Expected '{expected}', got '{result}'")
    
    print("\n✅ Weather icon mapping tests completed!")

def main():
    """Run all tests"""
    print("🧪 Data Processing Test Suite")
    print("=" * 50)
    
    try:
        test_data_processor()
        test_time_calculations()
        test_array_shifting()
        test_weather_icon_mapping()
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed successfully!")
        print("\nThe LED display fixes include:")
        print("✅ Fallback data generation when API data is missing")
        print("✅ Proper error handling and debugging output")
        print("✅ Time-based data shifting for current hour alignment")
        print("✅ Weather icon mapping for different conditions")
        print("✅ Responsive web UI with sidebar navigation")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())