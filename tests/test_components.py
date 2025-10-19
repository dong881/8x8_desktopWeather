#!/usr/bin/env python3
"""
Test script for 8x8 Weather Display components
Tests API clients, data processing, and display components without hardware
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.data_processor import DataProcessor
from src.display.icons import WeatherIcons


def test_data_processor():
    """Test data processor functions"""
    print("Testing DataProcessor...")
    
    processor = DataProcessor()
    
    # Test temperature conversion
    temps = [15, 20, 25, 30]
    levels = processor._temperature_to_levels(temps)
    print(f"  Temperature levels: {levels}")
    assert len(levels) == 4, "Temperature levels count mismatch"
    assert all(0 <= l <= 7 for l in levels), "Temperature levels out of range"
    
    # Test precipitation conversion
    probs = [30, 70, 50, 80]
    pop_levels = processor._precipitation_to_levels(probs, threshold=60)
    print(f"  Precipitation levels: {pop_levels}")
    assert len(pop_levels) == 8, "Precipitation levels count mismatch"
    
    # Test time index calculation
    for hour in range(24):
        idx = processor.calculate_time_index(hour)
        assert 0 <= idx <= 7, f"Invalid time index for hour {hour}"
    print(f"  Time index calculation: OK")
    
    # Test weather icon name mapping
    icon_name = processor.get_weather_icon_name("晴天")
    assert icon_name == "sunny", "Weather icon mapping failed"
    print(f"  Weather icon mapping: OK")
    
    print("✓ DataProcessor tests passed\n")


def test_weather_icons():
    """Test weather icons"""
    print("Testing WeatherIcons...")
    
    # Test icon retrieval
    sunny = WeatherIcons.get_icon('sunny')
    assert len(sunny) == 8, "Icon should have 8 rows"
    assert all(isinstance(row, int) for row in sunny), "Icon rows should be integers"
    print(f"  Sunny icon: OK")
    
    rainy = WeatherIcons.get_icon('rainy')
    assert len(rainy) == 8, "Icon should have 8 rows"
    print(f"  Rainy icon: OK")
    
    earthquake = WeatherIcons.get_icon('earthquake')
    assert len(earthquake) == 8, "Icon should have 8 rows"
    print(f"  Earthquake icon: OK")
    
    # Test digit retrieval
    for digit in '0123456789':
        digit_icon = WeatherIcons.DIGITS.get(digit)
        assert digit_icon is not None, f"Digit {digit} not found"
        assert len(digit_icon) == 8, f"Digit {digit} should have 8 rows"
    print(f"  Digit icons: OK")
    
    print("✓ WeatherIcons tests passed\n")


def test_cwa_client_mock():
    """Test CWA client without making actual API calls"""
    print("Testing CWAClient (mock)...")
    
    from src.api.cwa_client import CWAClient
    
    # Create client with dummy token
    client = CWAClient("dummy_token_for_testing")
    
    # Check cache directory creation
    assert os.path.exists(client.CACHE_DIR), "Cache directory should be created"
    print(f"  Cache directory: OK")
    
    print("✓ CWAClient mock tests passed\n")


def test_display_manager_mock():
    """Test display manager without hardware"""
    print("Testing DisplayManager (mock)...")
    
    from src.display.display_manager import DisplayPage
    
    # Test display page creation
    def dummy_callback(device):
        pass
    
    page = DisplayPage("test_page", dummy_callback, duration=10.0, priority=3)
    assert page.name == "test_page", "Page name mismatch"
    assert page.duration == 10.0, "Page duration mismatch"
    assert page.priority == 3, "Page priority mismatch"
    print(f"  DisplayPage creation: OK")
    
    print("✓ DisplayManager mock tests passed\n")


def main():
    """Run all tests"""
    print("=" * 50)
    print("8x8 Weather Display - Component Tests")
    print("=" * 50)
    print()
    
    try:
        test_data_processor()
        test_weather_icons()
        test_cwa_client_mock()
        test_display_manager_mock()
        
        print("=" * 50)
        print("✓ All tests passed!")
        print("=" * 50)
        return 0
    
    except AssertionError as e:
        print(f"\n✗ Test failed: {str(e)}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
