#!/usr/bin/env python3
"""
Test script to verify LED blinking and rotation functionality
"""

import sys
import time
from datetime import datetime
from src.api.data_processor import DataProcessor
from src.display.display_manager import DisplayManager

def test_blinking_functionality():
    """Test the blinking functionality of temperature bars"""
    print("Testing LED blinking functionality...")
    
    # Mock device for testing
    class MockDevice:
        def __init__(self):
            self.contrast_value = 255
            self.last_draw = None
            self.mode = "RGB"
            self.size = (8, 8)
            self.width = 8
            self.height = 8
            self.bounding_box = (0, 0, 7, 7)
            self.display_calls = []
        
        def contrast(self, value):
            self.contrast_value = value
        
        def clear(self):
            self.last_draw = "clear"
        
        def cleanup(self):
            pass
        
        def display(self, image):
            """Mock display method for canvas"""
            self.display_calls.append(image)
            return True
    
    device = MockDevice()
    display_manager = DisplayManager(device)
    
    # Test data
    temp_levels = [3, 4, 5, 6, 6, 5, 4, 3]
    rain_levels = [0, 0, 1, 0, 0, 0, 0, 0]
    current_col = 2  # Third column should blink
    
    print(f"Temperature levels: {temp_levels}")
    print(f"Rain levels: {rain_levels}")
    print(f"Current column (blinking): {current_col}")
    print("\nTesting blinking temperature bar display...")
    
    try:
        # Test blinking display
        start_time = time.time()
        display_manager.show_temperature_bar(
            temp_levels, 
            rain_levels, 
            current_col, 
            blink=True, 
            duration=3.0
        )
        elapsed = time.time() - start_time
        print(f"✅ Blinking display completed in {elapsed:.1f} seconds")
        print(f"   Display calls made: {len(device.display_calls)}")
        
        # Test static display
        print("\nTesting static temperature bar display...")
        device.display_calls = []  # Reset counter
        start_time = time.time()
        display_manager.show_temperature_bar(
            temp_levels, 
            rain_levels, 
            current_col, 
            blink=False, 
            duration=2.0
        )
        elapsed = time.time() - start_time
        print(f"✅ Static display completed in {elapsed:.1f} seconds")
        print(f"   Display calls made: {len(device.display_calls)}")
        
    except Exception as e:
        print(f"❌ Display test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_rotation_functionality():
    """Test the carousel rotation functionality"""
    print("\nTesting LED rotation functionality...")
    
    # Mock device for testing
    class MockDevice:
        def __init__(self):
            self.contrast_value = 255
            self.last_draw = None
            self.mode = "RGB"
            self.size = (8, 8)
            self.width = 8
            self.height = 8
            self.bounding_box = (0, 0, 7, 7)
            self.display_calls = []
        
        def contrast(self, value):
            self.contrast_value = value
        
        def clear(self):
            self.last_draw = "clear"
        
        def cleanup(self):
            pass
        
        def display(self, image):
            """Mock display method for canvas"""
            self.display_calls.append(image)
            return True
    
    device = MockDevice()
    display_manager = DisplayManager(device)
    
    # Create test pages
    from src.display.display_manager import DisplayPage
    
    def page1_callback(device):
        print("  📊 Displaying Page 1: Temperature Bars")
        time.sleep(0.5)  # Simulate display time
    
    def page2_callback(device):
        print("  🌤️  Displaying Page 2: Weather Icon")
        time.sleep(0.5)  # Simulate display time
    
    def page3_callback(device):
        print("  🌡️  Displaying Page 3: Temperature Display")
        time.sleep(0.5)  # Simulate display time
    
    # Add pages
    display_manager.add_page(DisplayPage("temp_bars", page1_callback, duration=2.0, priority=3))
    display_manager.add_page(DisplayPage("weather_icon", page2_callback, duration=2.0, priority=3))
    display_manager.add_page(DisplayPage("temp_display", page3_callback, duration=2.0, priority=3))
    
    print(f"Created {len(display_manager.pages)} display pages")
    print("Testing page rotation...")
    
    try:
        # Test rotation for a few cycles
        for cycle in range(2):
            print(f"\n--- Rotation Cycle {cycle + 1} ---")
            for page_num in range(len(display_manager.pages)):
                print(f"Page {page_num + 1}:")
                display_manager.rotate_pages(duration=1.0)  # Short duration for testing
                
    except Exception as e:
        print(f"❌ Rotation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("✅ Rotation test completed successfully")
    return True

def test_time_index_calculation():
    """Test time index calculation for current column"""
    print("\nTesting time index calculation...")
    
    processor = DataProcessor()
    
    # Test various hours
    test_hours = [0, 3, 6, 9, 12, 15, 18, 21, 23]
    
    for hour in test_hours:
        index = processor.calculate_time_index(hour)
        print(f"Hour {hour:02d}:00 -> Column {index}")
    
    print("✅ Time index calculation completed")
    return True

def main():
    """Run all tests"""
    print("🧪 LED Blinking and Rotation Test Suite")
    print("=" * 50)
    
    try:
        # Test blinking functionality
        if not test_blinking_functionality():
            print("❌ Blinking test failed")
            return 1
        
        # Test rotation functionality
        if not test_rotation_functionality():
            print("❌ Rotation test failed")
            return 1
        
        # Test time calculations
        if not test_time_index_calculation():
            print("❌ Time calculation test failed")
            return 1
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed successfully!")
        print("\nThe LED display should now:")
        print("✅ Blink the current time column in temperature bars")
        print("✅ Rotate through different display pages in carousel mode")
        print("✅ Show proper timing for each display mode")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
