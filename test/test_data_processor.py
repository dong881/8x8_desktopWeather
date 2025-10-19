#!/usr/bin/env python3
"""
Test script to verify data processor fixes
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.data_processor import DataProcessor

def test_observation_data_with_valid_data():
    """Test observation data processing with valid data"""
    print("Test 1: Valid observation data")
    
    valid_data = {
        'records': {
            'Station': [{
                'ObsTime': {'DateTime': '2025-10-20T00:00:00+08:00'},
                'Temperature': 25.5,
                'RelativeHumidity': 65,
                'Weather': 'Partly Cloudy'
            }]
        }
    }
    
    result = DataProcessor.process_observation_data(valid_data)
    
    assert result is not None, "Result should not be None"
    assert result['temperature'] == 25.5, f"Expected 25.5, got {result['temperature']}"
    assert result['humidity'] == 65, f"Expected 65, got {result['humidity']}"
    assert result['weather'] == 'Partly Cloudy', f"Expected 'Partly Cloudy', got {result['weather']}"
    print("✓ Valid data test passed")


def test_observation_data_with_zeros():
    """Test observation data with zero values (should still be valid)"""
    print("\nTest 2: Observation data with zero temperature")
    
    data_with_zeros = {
        'records': {
            'Station': [{
                'ObsTime': {'DateTime': '2025-10-20T00:00:00+08:00'},
                'Temperature': 0.0,
                'RelativeHumidity': 0,
                'Weather': 'N/A'
            }]
        }
    }
    
    result = DataProcessor.process_observation_data(data_with_zeros)
    
    # This should still return valid data, even if temperature is 0
    assert result is not None, "Result should not be None even with zero values"
    assert result['temperature'] == 0.0, f"Expected 0.0, got {result['temperature']}"
    print("✓ Zero values test passed")


def test_observation_data_with_missing_data():
    """Test observation data with missing fields"""
    print("\nTest 3: Observation data with missing fields")
    
    missing_data = {
        'records': {
            'Station': [{
                'ObsTime': {'DateTime': '2025-10-20T00:00:00+08:00'}
                # Missing Temperature, RelativeHumidity, Weather
            }]
        }
    }
    
    result = DataProcessor.process_observation_data(missing_data)
    
    # Should handle missing fields gracefully
    assert result is not None, "Result should not be None"
    assert result['temperature'] == 0.0, f"Expected default 0.0, got {result['temperature']}"
    assert result['humidity'] == 0, f"Expected default 0, got {result['humidity']}"
    assert result['weather'] == 'N/A', f"Expected 'N/A', got {result['weather']}"
    print("✓ Missing fields test passed")


def test_observation_data_invalid():
    """Test observation data with invalid structure"""
    print("\nTest 4: Invalid observation data structure")
    
    invalid_data = {'invalid': 'structure'}
    
    result = DataProcessor.process_observation_data(invalid_data)
    
    assert result is None, "Result should be None for invalid data"
    print("✓ Invalid data test passed")


def test_time_index_calculation():
    """Test time index calculation for different hours"""
    print("\nTest 5: Time index calculation")
    
    test_cases = [
        (0, 7), (1, 0), (2, 0), (3, 0),
        (4, 1), (5, 1), (6, 1),
        (7, 2), (8, 2), (9, 2),
        (10, 3), (11, 3), (12, 3),
        (13, 4), (14, 4), (15, 4),
        (16, 5), (17, 5), (18, 5),
        (19, 6), (20, 6), (21, 6),
        (22, 7), (23, 7)
    ]
    
    for hour, expected_index in test_cases:
        result = DataProcessor.calculate_time_index(hour)
        assert result == expected_index, f"Hour {hour}: expected {expected_index}, got {result}"
    
    print("✓ Time index calculation test passed")


def test_weather_icon_name():
    """Test weather icon name selection"""
    print("\nTest 6: Weather icon name selection")
    
    test_cases = [
        ('晴天', 'sunny'),
        ('Sunny', 'sunny'),
        ('多雲', 'cloudy'),
        ('Cloudy', 'cloudy'),
        ('雨', 'rainy'),
        ('Rain', 'rainy'),
        ('雷雨', 'thunderstorm'),
        ('Thunderstorm', 'thunderstorm'),
        ('雪', 'snowy'),
        ('Snow', 'snowy'),
        ('颱風', 'typhoon'),
        ('Typhoon', 'typhoon'),
        ('Unknown', 'sunny')  # Default
    ]
    
    for desc, expected_icon in test_cases:
        result = DataProcessor.get_weather_icon_name(desc)
        assert result == expected_icon, f"'{desc}': expected '{expected_icon}', got '{result}'"
    
    print("✓ Weather icon name test passed")


def main():
    """Run all tests"""
    print("=" * 50)
    print("Data Processor Tests")
    print("=" * 50)
    
    try:
        test_observation_data_with_valid_data()
        test_observation_data_with_zeros()
        test_observation_data_with_missing_data()
        test_observation_data_invalid()
        test_time_index_calculation()
        test_weather_icon_name()
        
        print("\n" + "=" * 50)
        print("✓ All tests passed!")
        print("=" * 50)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
