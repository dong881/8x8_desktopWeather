#!/usr/bin/env python3
"""
Test script to verify new CWA OpenData API format handling
Based on actual API response structure from 2025
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.data_processor import DataProcessor


def test_new_api_format_with_weather_element():
    """Test observation data processing with new API format (WeatherElement nested structure)"""
    print("Test 1: New API format with WeatherElement")
    
    new_format_data = {
        'success': 'true',
        'records': {
            'Station': [{
                'StationName': '臺北',
                'StationId': '466920',
                'ObsTime': {
                    'DateTime': '2025-10-20T23:00:00+08:00'
                },
                'GeoInfo': {
                    'Coordinates': [
                        {'CoordinateName': '緯度', 'StationLatitude': 25.037},
                        {'CoordinateName': '經度', 'StationLongitude': 121.565}
                    ]
                },
                'WeatherElement': {
                    'Weather': '陰',
                    'AirTemperature': 23.5,
                    'RelativeHumidity': 85,
                    'AirPressure': 1013.2,
                    'WindSpeed': 2.5
                }
            }]
        }
    }
    
    result = DataProcessor.process_observation_data(new_format_data)
    
    assert result is not None, "Result should not be None"
    assert result['temperature'] == 23.5, f"Expected 23.5, got {result['temperature']}"
    assert result['humidity'] == 85, f"Expected 85, got {result['humidity']}"
    assert result['weather'] == '陰', f"Expected '陰', got {result['weather']}"
    assert result['time'] == '2025-10-20T23:00:00+08:00', f"Unexpected time: {result['time']}"
    print(f"✓ New API format test passed: {result}")


def test_old_api_format_backward_compatibility():
    """Test that old API format still works (backward compatibility)"""
    print("\nTest 2: Old API format (backward compatibility)")
    
    old_format_data = {
        'records': {
            'Station': [{
                'ObsTime': {'DateTime': '2025-10-20T22:00:00+08:00'},
                'Temperature': 25.5,
                'RelativeHumidity': 65,
                'Weather': 'Partly Cloudy'
            }]
        }
    }
    
    result = DataProcessor.process_observation_data(old_format_data)
    
    assert result is not None, "Result should not be None"
    assert result['temperature'] == 25.5, f"Expected 25.5, got {result['temperature']}"
    assert result['humidity'] == 65, f"Expected 65, got {result['humidity']}"
    assert result['weather'] == 'Partly Cloudy', f"Expected 'Partly Cloudy', got {result['weather']}"
    print(f"✓ Old API format test passed: {result}")


def test_new_api_format_with_missing_fields():
    """Test new API format with some missing weather element fields"""
    print("\nTest 3: New API format with missing fields")
    
    partial_data = {
        'records': {
            'Station': [{
                'StationName': '臺北',
                'StationId': '466920',
                'ObsTime': {
                    'DateTime': '2025-10-20T23:00:00+08:00'
                },
                'WeatherElement': {
                    'Weather': '晴'
                    # Missing AirTemperature and RelativeHumidity
                }
            }]
        }
    }
    
    result = DataProcessor.process_observation_data(partial_data)
    
    assert result is not None, "Result should not be None"
    assert result['temperature'] == 0.0, f"Expected 0.0 for missing temp, got {result['temperature']}"
    assert result['humidity'] == 0, f"Expected 0 for missing humidity, got {result['humidity']}"
    assert result['weather'] == '晴', f"Expected '晴', got {result['weather']}"
    print(f"✓ Missing fields test passed: {result}")


def test_new_api_format_with_dash_values():
    """Test new API format with '-' values (no data)"""
    print("\nTest 4: New API format with '-' values")
    
    dash_data = {
        'records': {
            'Station': [{
                'StationName': '臺北',
                'ObsTime': {
                    'DateTime': '2025-10-20T23:00:00+08:00'
                },
                'WeatherElement': {
                    'Weather': '-',
                    'AirTemperature': '-',
                    'RelativeHumidity': '-'
                }
            }]
        }
    }
    
    result = DataProcessor.process_observation_data(dash_data)
    
    assert result is not None, "Result should not be None"
    assert result['temperature'] == 0.0, f"Expected 0.0 for '-', got {result['temperature']}"
    assert result['humidity'] == 0, f"Expected 0 for '-', got {result['humidity']}"
    assert result['weather'] == 'N/A', f"Expected 'N/A' for '-', got {result['weather']}"
    print(f"✓ Dash values test passed: {result}")


def test_new_api_format_with_string_numbers():
    """Test new API format with string number values"""
    print("\nTest 5: New API format with string numbers")
    
    string_data = {
        'records': {
            'Station': [{
                'ObsTime': {
                    'DateTime': '2025-10-20T23:00:00+08:00'
                },
                'WeatherElement': {
                    'Weather': '多雲',
                    'AirTemperature': '28.3',  # String instead of number
                    'RelativeHumidity': '72'   # String instead of number
                }
            }]
        }
    }
    
    result = DataProcessor.process_observation_data(string_data)
    
    assert result is not None, "Result should not be None"
    assert result['temperature'] == 28.3, f"Expected 28.3, got {result['temperature']}"
    assert result['humidity'] == 72, f"Expected 72, got {result['humidity']}"
    assert result['weather'] == '多雲', f"Expected '多雲', got {result['weather']}"
    print(f"✓ String numbers test passed: {result}")


def test_new_api_format_comprehensive():
    """Test new API format with all fields populated"""
    print("\nTest 6: New API format comprehensive test")
    
    comprehensive_data = {
        'success': 'true',
        'result': {
            'resource_id': 'O-A0001-001',
            'fields': []
        },
        'records': {
            'Station': [{
                'StationName': '臺北',
                'StationId': '466920',
                'ObsTime': {
                    'DateTime': '2025-10-20T23:00:00+08:00'
                },
                'GeoInfo': {
                    'Coordinates': [
                        {
                            'CoordinateName': '緯度',
                            'CoordinateFormat': 'decimal degrees',
                            'StationLatitude': 25.037
                        },
                        {
                            'CoordinateName': '經度',
                            'CoordinateFormat': 'decimal degrees',
                            'StationLongitude': 121.565
                        },
                        {
                            'CoordinateName': '高度',
                            'CoordinateFormat': 'meter',
                            'StationAltitude': 6.3
                        }
                    ]
                },
                'WeatherElement': {
                    'Weather': '陰短暫雨',
                    'Now': {
                        'Precipitation': 0.5
                    },
                    'WindDirection': 45.0,
                    'WindSpeed': 2.5,
                    'AirTemperature': 20.8,
                    'RelativeHumidity': 92,
                    'AirPressure': 1013.2,
                    'GustInfo': {
                        'PeakGustSpeed': 5.2,
                        'Occurred_at': {
                            'WindDirection': 90.0,
                            'DateTime': '2025-10-20T22:45:00+08:00'
                        }
                    },
                    'DailyExtreme': {
                        'DailyHigh': {
                            'TemperatureInfo': {
                                'AirTemperature': 24.5,
                                'Occurred_at': {
                                    'DateTime': '2025-10-20T14:30:00+08:00'
                                }
                            }
                        },
                        'DailyLow': {
                            'TemperatureInfo': {
                                'AirTemperature': 18.2,
                                'Occurred_at': {
                                    'DateTime': '2025-10-20T06:15:00+08:00'
                                }
                            }
                        }
                    }
                }
            }]
        }
    }
    
    result = DataProcessor.process_observation_data(comprehensive_data)
    
    assert result is not None, "Result should not be None"
    assert result['temperature'] == 20.8, f"Expected 20.8, got {result['temperature']}"
    assert result['humidity'] == 92, f"Expected 92, got {result['humidity']}"
    assert result['weather'] == '陰短暫雨', f"Expected '陰短暫雨', got {result['weather']}"
    assert result['time'] == '2025-10-20T23:00:00+08:00', f"Unexpected time: {result['time']}"
    print(f"✓ Comprehensive test passed: {result}")


def main():
    """Run all tests"""
    print("=" * 70)
    print("CWA OpenData API New Format Tests")
    print("Testing support for 2025 API structure changes")
    print("=" * 70)
    
    try:
        test_new_api_format_with_weather_element()
        test_old_api_format_backward_compatibility()
        test_new_api_format_with_missing_fields()
        test_new_api_format_with_dash_values()
        test_new_api_format_with_string_numbers()
        test_new_api_format_comprehensive()
        
        print("\n" + "=" * 70)
        print("✓ All new API format tests passed!")
        print("=" * 70)
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
