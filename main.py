"""
Enhanced 8x8 Weather Display with Modular Architecture
Main application entry point with Web Configuration Interface
"""

import sys
import time
from datetime import datetime
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas

# Import configuration
from config import WeatherAPI

# Import modular components
from src.api.cwa_client import CWAClient
from src.api.data_processor import DataProcessor
from src.display.display_manager import DisplayManager, DisplayPage
from src.display.icons import WeatherIcons
from src.utils.scheduler import ContentScheduler
from src.utils.logger import setup_logger

# Import web configuration interface
from web_config import start_web_server

# Setup logger
logger = setup_logger("weather_display")


class EnhancedWeatherDisplay:
    """Enhanced weather display with multiple data sources and visualizations"""
    
    def __init__(self, authorization: str):
        """
        Initialize enhanced weather display
        
        Args:
            authorization: CWA API authorization token
        """
        # Initialize hardware
        logger.info("Initializing LED matrix device...")
        serial = spi(port=0, device=0, gpio=noop())
        self.device = max7219(serial, cascaded=1, block_orientation=0, rotate=0)
        
        # Initialize API clients
        logger.info("Initializing API clients...")
        self.cwa_client = CWAClient(authorization)
        self.processor = DataProcessor()
        
        # Initialize display manager
        logger.info("Initializing display manager...")
        self.display_manager = DisplayManager(self.device)
        self.display_manager.set_display_mode('carousel')  # Default mode
        
        # Initialize scheduler
        logger.info("Initializing scheduler...")
        self.scheduler = ContentScheduler(self.cwa_client, self.display_manager)
        
        # Data storage
        self.temperature_levels = []
        self.rainfall_levels = []
        self.current_hour_index = 0
        self.earthquake_data = None
        self.observation_data = None
        
        # Setup scheduler callbacks
        self.scheduler.on_weather_update = self.on_weather_update
        self.scheduler.on_earthquake_detected = self.on_earthquake_detected
        self.scheduler.on_observation_update = self.on_observation_update
    
    def on_weather_update(self, data):
        """Handle weather forecast update"""
        logger.info("Processing weather forecast update...")
        result = self.processor.process_weather_forecast(data)
        
        if result:
            temp_levels, rain_levels = result
            self.temperature_levels = temp_levels
            self.rainfall_levels = rain_levels
            
            # Update current time index
            now = datetime.now()
            self.current_hour_index = self.processor.calculate_time_index(now.hour)
            
            # Shift arrays to align with current time
            self.temperature_levels = self.processor.shift_array(
                self.temperature_levels, self.current_hour_index
            )
            self.rainfall_levels = self.processor.shift_array(
                self.rainfall_levels, 
                self.current_hour_index if now.hour in [7, 8, 9, 13, 14, 15, 19, 20, 21, 1, 2, 3] else 0
            )
            
            logger.info(f"Weather updated: Temp={self.temperature_levels}, Rain={self.rainfall_levels}")
    
    def on_earthquake_detected(self, eq_data):
        """Handle earthquake detection"""
        logger.warning(f"EARTHQUAKE DETECTED: {eq_data}")
        self.earthquake_data = eq_data
        
        # Process earthquake data
        processed = self.processor.process_earthquake_data({'records': {'Earthquake': [eq_data]}})
        
        if processed:
            # Trigger earthquake alert display
            self.display_manager.trigger_alert(
                'earthquake',
                {
                    'magnitude': processed['magnitude'],
                    'location': processed['location'],
                    'depth': processed['depth']
                },
                duration=60.0
            )
    
    def on_observation_update(self, data):
        """Handle observation data update"""
        logger.info("Processing observation data update...")
        self.observation_data = self.processor.process_observation_data(data)
        
        if self.observation_data:
            logger.info(f"Observation: {self.observation_data}")
        else:
            logger.warning("Observation data processing returned None or invalid data")
    
    def create_display_pages(self):
        """Create display pages for content rotation"""
        self.display_manager.clear_pages()
        
        # Page 1: Traditional temperature bar display
        def show_temp_bars(device):
            with canvas(device) as draw:
                # Clear the display first
                draw.rectangle(device.bounding_box, outline="black", fill="black")
                
                for i in range(8):
                    if i < len(self.temperature_levels):
                        height = max(0, min(7, self.temperature_levels[i]))  # Clamp to 0-7 range
                        for j in range(height):
                            draw.point((i, 7 - j - 1), fill="white")
                        if i < len(self.rainfall_levels) and self.rainfall_levels[i] == 1:
                            draw.point((i, 7), fill="white")
        
        self.display_manager.add_page(
            DisplayPage("temperature_bars", show_temp_bars, duration=20.0, priority=3)
        )
        
        # Page 2: Weather icon display
        if self.observation_data and self.observation_data.get('weather') != 'N/A':
            weather_desc = self.observation_data.get('weather', '')
            icon_name = self.processor.get_weather_icon_name(weather_desc)
            
            def show_weather_icon(device):
                icon = WeatherIcons.get_icon(icon_name)
                with canvas(device) as draw:
                    WeatherIcons.draw_icon_fullscreen(draw, icon)
            
            self.display_manager.add_page(
                DisplayPage("weather_icon", show_weather_icon, duration=16.0, priority=3)
            )
        
        # Page 3: Temperature display
        if self.observation_data and self.observation_data.get('temperature', 0) > 0:
            temp = int(self.observation_data.get('temperature', 0))
            
            def show_temperature(device):
                with canvas(device) as draw:
                    # Clear the display first
                    draw.rectangle(device.bounding_box, outline="black", fill="black")
                    
                    # Draw thermometer icon on left
                    icon = WeatherIcons.THERMOMETER_HOT if temp > 28 else WeatherIcons.THERMOMETER_COLD
                    for row in range(8):
                        for col in range(3):
                            if icon[row] & (1 << (7 - col)):
                                draw.point((col, row), fill="white")
                    
                    # Draw temperature digits on right
                    temp_str = f"{temp:02d}"
                    if len(temp_str) >= 1:
                        WeatherIcons.draw_digit(draw, 4, 0, temp_str[0] if len(temp_str) > 1 else '0')
                    if len(temp_str) >= 2:
                        WeatherIcons.draw_digit(draw, 6, 0, temp_str[1])
            
            self.display_manager.add_page(
                DisplayPage("temperature_display", show_temperature, duration=16.0, priority=3)
            )
    
    def run(self):
        """Main run loop"""
        try:
            # Show startup logo
            logger.info("Showing startup animation...")
            self.display_manager.show_startup_logo()
            
            # Initial data fetch
            logger.info("Fetching initial weather data...")
            self.scheduler.force_weather_update()
            
            # Wait a moment for data
            time.sleep(2)
            
            # Start background scheduler
            logger.info("Starting background scheduler...")
            self.scheduler.start()
            
            # Start web configuration interface
            logger.info("Starting web configuration interface on port 5000...")
            start_web_server(self.display_manager, self.scheduler, self)
            
            # Create display pages
            self.create_display_pages()
            
            # Main display loop
            logger.info("Entering main display loop...")
            update_counter = 0
            last_page_rotation = time.time()
            last_brightness_update = time.time()
            last_mode_check = time.time()
            
            while True:
                try:
                    current_time = time.time()
                    
                    # Update brightness every 60 seconds
                    if current_time - last_brightness_update >= 60:
                        self.display_manager.update_brightness()
                        last_brightness_update = current_time
                    
                    # Check if we need to update current hour index
                    now = datetime.now()
                    new_hour_index = self.processor.calculate_time_index(now.hour)
                    
                    if new_hour_index != self.current_hour_index:
                        self.current_hour_index = new_hour_index
                        logger.info(f"Hour changed to {now.hour}:00, display index updated to: {new_hour_index}")
                    
                    # Check for alerts first
                    if self.display_manager.alert_active:
                        # Alert mode - let alert handle display
                        time.sleep(1)
                        continue
                    
                    # Display content based on current mode
                    self.display_manager.show_mode_content(
                        weather_data=self.observation_data,
                        temperature_data=self.temperature_levels,
                        rainfall_data=self.rainfall_levels,
                        current_col=self.current_hour_index
                    )
                    
                    update_counter += 1
                    time.sleep(1)
                    
                    # Rotate through display pages (less frequent at night)
                    current_hour = now.hour
                    rotation_interval = 40 if 22 <= current_hour or current_hour <= 6 else 20  # Slower at night
                    
                    if (current_time - last_page_rotation >= rotation_interval and 
                        self.display_manager.current_mode == 'carousel'):
                        self.create_display_pages()
                        if len(self.display_manager.pages) > 1:
                            # Show 2 alternate pages with proper timing
                            self.display_manager.rotate_pages()
                            time.sleep(0.5)  # Brief pause between pages
                            self.display_manager.rotate_pages()
                        last_page_rotation = current_time
                
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    logger.error(f"Error in display loop: {str(e)}")
                    time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.scheduler.stop()
            self.device.cleanup()
        except Exception as e:
            logger.error(f"Fatal error: {str(e)}")
            self.scheduler.stop()
            self.device.cleanup()


def main():
    """Main entry point"""
    # Check authorization
    authorization = WeatherAPI.get('Authorization', '')
    
    if not authorization:
        logger.error("Authorization token not found in config.py")
        logger.error("Please set WeatherAPI['Authorization'] in config.py")
        logger.error("Get your token from: https://opendata.cwa.gov.tw/user/authkey")
        sys.exit(1)
    
    # Create and run display
    display = EnhancedWeatherDisplay(authorization)
    display.run()


if __name__ == "__main__":
    main()
