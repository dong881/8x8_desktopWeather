#!/usr/bin/env python3
"""
Test script to verify weather forecast API format handling
Tests both old and new CWA OpenData API formats
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.data_processor import DataProcessor


def test_old_forecast_format():
    """Test old forecast API format with capitalized field names"""
    print("Test 1: Old forecast API format (capitalized fields)")
    
    old_format = {
        'records': {
            'Locations': [{
                'Location': [{
                    'locationName': '大安區',
                    'WeatherElement': [
                        {
                            'ElementName': 'T',
                            'Time': [
                                {
                                    'startTime': '2025-10-20 12:00:00',
                                    'endTime': '2025-10-20 15:00:00',
                                    'ElementValue': [{'Temperature': '28'}]
                                },
                                {
                                    'startTime': '2025-10-20 15:00:00',
                                    'endTime': '2025-10-20 18:00:00',
                                    'ElementValue': [{'Temperature': '26'}]
                                },
                                {
                                    'startTime': '2025-10-20 18:00:00',
                                    'endTime': '2025-10-20 21:00:00',
                                    'ElementValue': [{'Temperature': '24'}]
                                },
                                {
                                    'startTime': '2025-10-20 21:00:00',
                                    'endTime': '2025-10-21 00:00:00',
                                    'ElementValue': [{'Temperature': '22'}]
                                }
                            ]
                        },
                        {
                            'ElementName': 'PoP6h',
                            'Time': [
                                {
                                    'startTime': '2025-10-20 12:00:00',
                                    'endTime': '2025-10-20 18:00:00',
                                    'ElementValue': [{'Probability': '30'}]
                                },
                                {
                                    'startTime': '2025-10-20 18:00:00',
                                    'endTime': '2025-10-21 00:00:00',
                                    'ElementValue': [{'Probability': '70'}]
                                }
                            ]
                        }
                    ]
                }]
            }]
        }
    }
    
    result = DataProcessor.process_weather_forecast(old_format)
    
    assert result is not None, "Result should not be None"
    temp_levels, rain_levels = result
    assert len(temp_levels) > 0, "Temperature levels should not be empty"
    assert len(rain_levels) > 0, "Rain levels should not be empty"
    print(f"✓ Old format test passed: temp_levels={temp_levels}, rain_levels={rain_levels}")


def test_new_forecast_format():
    """Test new forecast API format with lowercase field names"""
    print("\nTest 2: New forecast API format (lowercase fields)")
    
    new_format = {
        'success': 'true',
        'records': {
            'Locations': [{
                'Location': [{
                    'locationName': '大安區',
                    'weatherElement': [
                        {
                            'elementName': 'T',
                            'time': [
                                {
                                    'startTime': '2025-10-20 12:00:00',
                                    'endTime': '2025-10-20 15:00:00',
                                    'elementValue': [{'temperature': '28'}]
                                },
                                {
                                    'startTime': '2025-10-20 15:00:00',
                                    'endTime': '2025-10-20 18:00:00',
                                    'elementValue': [{'temperature': '26'}]
                                },
                                {
                                    'startTime': '2025-10-20 18:00:00',
                                    'endTime': '2025-10-20 21:00:00',
                                    'elementValue': [{'temperature': '24'}]
                                },
                                {
                                    'startTime': '2025-10-20 21:00:00',
                                    'endTime': '2025-10-21 00:00:00',
                                    'elementValue': [{'temperature': '22'}]
                                }
                            ]
                        },
                        {
                            'elementName': 'PoP6h',
                            'time': [
                                {
                                    'startTime': '2025-10-20 12:00:00',
                                    'endTime': '2025-10-20 18:00:00',
                                    'elementValue': [{'probability': '30'}]
                                },
                                {
                                    'startTime': '2025-10-20 18:00:00',
                                    'endTime': '2025-10-21 00:00:00',
                                    'elementValue': [{'probability': '70'}]
                                }
                            ]
                        }
                    ]
                }]
            }]
        }
    }
    
    result = DataProcessor.process_weather_forecast(new_format)
    
    assert result is not None, "Result should not be None"
    temp_levels, rain_levels = result
    assert len(temp_levels) > 0, "Temperature levels should not be empty"
    assert len(rain_levels) > 0, "Rain levels should not be empty"
    print(f"✓ New format test passed: temp_levels={temp_levels}, rain_levels={rain_levels}")


def test_mixed_forecast_format():
    """Test mixed format (some old, some new field names)"""
    print("\nTest 3: Mixed forecast API format")
    
    mixed_format = {
        'records': {
            'Locations': [{
                'Location': [{
                    'locationName': '大安區',
                    'weatherElement': [  # lowercase
                        {
                            'ElementName': 'T',  # uppercase (old)
                            'Time': [  # uppercase (old)
                                {
                                    'startTime': '2025-10-20 12:00:00',
                                    'endTime': '2025-10-20 15:00:00',
                                    'ElementValue': [{'Temperature': '28'}]
                                },
                                {
                                    'startTime': '2025-10-20 15:00:00',
                                    'endTime': '2025-10-20 18:00:00',
                                    'ElementValue': [{'Temperature': '26'}]
                                },
                                {
                                    'startTime': '2025-10-20 18:00:00',
                                    'endTime': '2025-10-20 21:00:00',
                                    'ElementValue': [{'Temperature': '24'}]
                                },
                                {
                                    'startTime': '2025-10-20 21:00:00',
                                    'endTime': '2025-10-21 00:00:00',
                                    'ElementValue': [{'Temperature': '22'}]
                                }
                            ]
                        },
                        {
                            'ElementName': 'PoP6h',
                            'Time': [
                                {
                                    'startTime': '2025-10-20 12:00:00',
                                    'endTime': '2025-10-20 18:00:00',
                                    'ElementValue': [{'Probability': '30'}]
                                },
                                {
                                    'startTime': '2025-10-20 18:00:00',
                                    'endTime': '2025-10-21 00:00:00',
                                    'ElementValue': [{'Probability': '70'}]
                                }
                            ]
                        }
                    ]
                }]
            }]
        }
    }
    
    result = DataProcessor.process_weather_forecast(mixed_format)
    
    assert result is not None, "Result should not be None"
    temp_levels, rain_levels = result
    assert len(temp_levels) > 0, "Temperature levels should not be empty"
    assert len(rain_levels) > 0, "Rain levels should not be empty"
    print(f"✓ Mixed format test passed: temp_levels={temp_levels}, rain_levels={rain_levels}")


def test_comprehensive_forecast_format():
    """Test comprehensive forecast with full data"""
    print("\nTest 4: Comprehensive forecast with 8+ time periods")
    
    comprehensive = {
        'success': 'true',
        'result': {
            'resource_id': 'F-D0047-061',
            'fields': []
        },
        'records': {
            'Locations': [{
                'locationsName': '臺北市',
                'Location': [{
                    'locationName': '大安區',
                    'geocode': '63000100',
                    'weatherElement': [
                        {
                            'elementName': 'T',
                            'description': '溫度',
                            'time': [
                                {'elementValue': [{'temperature': '28', 'measures': '攝氏度'}]},
                                {'elementValue': [{'temperature': '26', 'measures': '攝氏度'}]},
                                {'elementValue': [{'temperature': '24', 'measures': '攝氏度'}]},
                                {'elementValue': [{'temperature': '22', 'measures': '攝氏度'}]},
                                {'elementValue': [{'temperature': '20', 'measures': '攝氏度'}]},
                                {'elementValue': [{'temperature': '19', 'measures': '攝氏度'}]},
                                {'elementValue': [{'temperature': '18', 'measures': '攝氏度'}]},
                                {'elementValue': [{'temperature': '23', 'measures': '攝氏度'}]},
                            ]
                        },
                        {
                            'elementName': 'PoP6h',
                            'description': '6小時降雨機率',
                            'time': [
                                {'elementValue': [{'probability': '20', 'measures': '百分比'}]},
                                {'elementValue': [{'probability': '30', 'measures': '百分比'}]},
                                {'elementValue': [{'probability': '70', 'measures': '百分比'}]},
                                {'elementValue': [{'probability': '80', 'measures': '百分比'}]},
                            ]
                        }
                    ]
                }]
            }]
        }
    }
    
    result = DataProcessor.process_weather_forecast(comprehensive)
    
    assert result is not None, "Result should not be None"
    temp_levels, rain_levels = result
    assert len(temp_levels) == 8, f"Expected 8 temperature levels, got {len(temp_levels)}"
    print(f"✓ Comprehensive test passed: {len(temp_levels)} temp levels, {len(rain_levels)} rain levels")


def test_invalid_forecast_format():
    """Test invalid forecast data"""
    print("\nTest 5: Invalid forecast data handling")
    
    invalid_data = {
        'records': {
            'Locations': []  # Empty locations
        }
    }
    
    result = DataProcessor.process_weather_forecast(invalid_data)
    
    assert result is None, "Result should be None for invalid data"
    print("✓ Invalid data test passed")


def test_missing_elements_forecast():
    """Test forecast data with missing elements"""
    print("\nTest 6: Forecast data with missing elements")
    
    missing_pop = {
        'records': {
            'Locations': [{
                'Location': [{
                    'locationName': '大安區',
                    'weatherElement': [
                        {
                            'elementName': 'T',
                            'time': [
                                {'elementValue': [{'temperature': '28'}]},
                                {'elementValue': [{'temperature': '26'}]},
                            ]
                        }
                        # Missing PoP6h element
                    ]
                }]
            }]
        }
    }
    
    result = DataProcessor.process_weather_forecast(missing_pop)
    
    assert result is None, "Result should be None when PoP6h is missing"
    print("✓ Missing elements test passed")


def main():
    """Run all tests"""
    print("=" * 70)
    print("CWA Weather Forecast API Format Tests")
    print("Testing support for old and new API structures")
    print("=" * 70)
    
    try:
        test_old_forecast_format()
        test_new_forecast_format()
        test_mixed_forecast_format()
        test_comprehensive_forecast_format()
        test_invalid_forecast_format()
        test_missing_elements_forecast()
        
        print("\n" + "=" * 70)
        print("✓ All forecast API format tests passed!")
        print("=" * 70)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
