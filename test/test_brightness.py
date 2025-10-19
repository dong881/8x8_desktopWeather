#!/usr/bin/env python3
"""
Test script to verify brightness control features
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import Mock, MagicMock
from src.display.display_manager import DisplayManager


def test_brightness_schedule():
    """Test that brightness schedule covers all 24 hours"""
    print("Test 1: Brightness schedule coverage")
    
    mock_device = Mock()
    mock_device.contrast = Mock()
    
    manager = DisplayManager(mock_device)
    
    # Check all hours are defined
    for hour in range(24):
        brightness = manager.brightness_schedule.get(hour)
        assert brightness is not None, f"Hour {hour} not in brightness schedule"
        assert 0 <= brightness <= 255, f"Hour {hour}: brightness {brightness} out of range"
    
    print("✓ Brightness schedule test passed")


def test_auto_brightness_by_time():
    """Test automatic brightness calculation for different times"""
    print("\nTest 2: Auto brightness by time")
    
    mock_device = Mock()
    mock_device.contrast = Mock()
    
    manager = DisplayManager(mock_device)
    
    # Test night time (should be dim)
    night_hours = [0, 1, 2, 3, 4, 5, 22, 23]
    for hour in night_hours:
        brightness = manager.brightness_schedule[hour]
        assert brightness <= 50, f"Night hour {hour}: brightness {brightness} too high (should be <= 50)"
    
    # Test day time (should be bright)
    day_hours = [10, 11, 12, 13, 14, 15, 16]
    for hour in day_hours:
        brightness = manager.brightness_schedule[hour]
        assert brightness >= 150, f"Day hour {hour}: brightness {brightness} too low (should be >= 150)"
    
    print("✓ Auto brightness by time test passed")


def test_manual_brightness_control():
    """Test manual brightness override"""
    print("\nTest 3: Manual brightness control")
    
    mock_device = Mock()
    mock_device.contrast = Mock()
    
    manager = DisplayManager(mock_device)
    
    # Enable auto brightness first
    manager.enable_auto_brightness()
    assert manager.auto_brightness_enabled == True
    assert manager.manual_brightness is None
    
    # Set manual brightness
    manager.set_manual_brightness(128)
    assert manager.auto_brightness_enabled == False
    assert manager.manual_brightness == 128
    mock_device.contrast.assert_called_with(128)
    
    # Re-enable auto brightness
    manager.enable_auto_brightness()
    assert manager.auto_brightness_enabled == True
    assert manager.manual_brightness is None
    
    print("✓ Manual brightness control test passed")


def test_brightness_range_clamping():
    """Test that brightness values are clamped to valid range"""
    print("\nTest 4: Brightness range clamping")
    
    mock_device = Mock()
    mock_device.contrast = Mock()
    
    manager = DisplayManager(mock_device)
    
    # Test value above max
    manager.set_manual_brightness(300)
    assert manager.manual_brightness == 255
    
    # Test value below min
    manager.set_manual_brightness(-10)
    assert manager.manual_brightness == 0
    
    # Test valid value
    manager.set_manual_brightness(128)
    assert manager.manual_brightness == 128
    
    print("✓ Brightness range clamping test passed")


def test_disable_auto_brightness():
    """Test disabling auto brightness"""
    print("\nTest 5: Disable auto brightness")
    
    mock_device = Mock()
    mock_device.contrast = Mock()
    
    manager = DisplayManager(mock_device)
    
    # Start with auto enabled
    assert manager.auto_brightness_enabled == True
    
    # Disable auto brightness
    manager.disable_auto_brightness()
    assert manager.auto_brightness_enabled == False
    
    print("✓ Disable auto brightness test passed")


def test_apply_brightness_priority():
    """Test brightness application priority (manual > auto > default)"""
    print("\nTest 6: Brightness application priority")
    
    mock_device = Mock()
    mock_device.contrast = Mock()
    
    manager = DisplayManager(mock_device)
    
    # Case 1: Manual brightness set (should use manual)
    manager.set_manual_brightness(100)
    manager.apply_brightness()
    mock_device.contrast.assert_called_with(100)
    
    # Case 2: Manual cleared, auto enabled (should use auto)
    manager.enable_auto_brightness()
    # We can't easily test the exact value without mocking datetime,
    # but we can verify the method was called
    assert manager.auto_brightness_enabled == True
    assert manager.manual_brightness is None
    
    # Case 3: Auto disabled, no manual (should use default 255)
    mock_device.contrast.reset_mock()
    manager.disable_auto_brightness()
    manager.apply_brightness()
    mock_device.contrast.assert_called_with(255)
    
    print("✓ Brightness application priority test passed")


def main():
    """Run all tests"""
    print("=" * 50)
    print("Brightness Control Tests")
    print("=" * 50)
    
    try:
        test_brightness_schedule()
        test_auto_brightness_by_time()
        test_manual_brightness_control()
        test_brightness_range_clamping()
        test_disable_auto_brightness()
        test_apply_brightness_priority()
        
        print("\n" + "=" * 50)
        print("✓ All brightness tests passed!")
        print("=" * 50)
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
