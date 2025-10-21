"""
Display Manager for 8x8 LED Matrix
Manages different display modes and content presentation
"""

import time
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from luma.core.render import canvas
from .icons import WeatherIcons
from .animations import AnimationEngine
from ..utils.logger import setup_logger

logger = setup_logger("display_manager")


class DisplayPage:
    """Represents a single display page/screen"""
    
    def __init__(self, name: str, content_callback: Callable, 
                 duration: float = 15.0, priority: int = 3):
        """
        Initialize display page
        
        Args:
            name: Page identifier
            content_callback: Function that draws content on device
            duration: Display duration in seconds
            priority: Priority level (1=highest/urgent, 3=normal)
        """
        self.name = name
        self.content_callback = content_callback
        self.duration = duration
        self.priority = priority


class DisplayManager:
    """Manages display modes and content rotation"""
    
    MODE_CAROUSEL = "carousel"
    MODE_SCROLLING = "scrolling"
    MODE_ICON = "icon"
    MODE_MIXED = "mixed"
    MODE_ALERT = "alert"
    
    def __init__(self, device):
        """
        Initialize display manager
        
        Args:
            device: luma.led_matrix device instance
        """
        self.device = device
        self.animator = AnimationEngine(device)
        self.pages: List[DisplayPage] = []
        self.current_page_idx = 0
        self.alert_active = False
        self.alert_callback: Optional[Callable] = None
        self.auto_brightness_enabled = True
        self.manual_brightness = None  # Override auto brightness if set
        
        # Brightness schedule (hour: brightness_level)
        # 0-255 scale, only dim during midnight to 6am (00:00-06:00)
        # Full brightness all other times
        self.brightness_schedule = {
            0: 5,     # Midnight - very dim
            1: 5,     # 1am - very dim
            2: 5,     # 2am - very dim
            3: 5,     # 3am - very dim
            4: 5,     # 4am - very dim
            5: 10,    # 5am - slightly brighter
            6: 100,   # 6am - return to normal brightness
            7: 120,   # Morning - bright
            8: 140,   # Morning - bright
            9: 160,   # Day - bright
            10: 180,  # Day - bright
            11: 200,  # Midday - very bright
            12: 220,  # Midday - very bright
            13: 220,  # Afternoon - very bright
            14: 200,  # Afternoon - very bright
            15: 180,  # Afternoon - bright
            16: 160,  # Evening - bright
            17: 140,  # Evening - bright
            18: 120,  # Evening - normal
            19: 120,  # Evening - normal
            20: 120,  # Night - normal (NOT dimmed)
            21: 120,  # Night - normal (NOT dimmed)
            22: 120,  # Night - normal (NOT dimmed)
            23: 120,  # Night - normal (NOT dimmed)
        }
    
    def add_page(self, page: DisplayPage):
        """
        Add a page to the display rotation
        
        Args:
            page: DisplayPage to add
        """
        self.pages.append(page)
    
    def clear_pages(self):
        """Clear all pages"""
        self.pages.clear()
        self.current_page_idx = 0
    
    def get_auto_brightness(self) -> int:
        """
        Get automatic brightness based on time of day
        
        Returns:
            Brightness level (0-255)
        """
        current_hour = datetime.now().hour
        return self.brightness_schedule.get(current_hour, 255)
    
    def set_manual_brightness(self, brightness: int):
        """
        Set manual brightness override
        
        Args:
            brightness: Brightness level (0-255), None to disable manual override
        """
        if brightness is None:
            self.manual_brightness = None
            self.auto_brightness_enabled = True
        else:
            self.manual_brightness = max(0, min(255, brightness))
            self.auto_brightness_enabled = False
        self.apply_brightness()
    
    def enable_auto_brightness(self):
        """Enable automatic brightness adjustment based on time"""
        self.auto_brightness_enabled = True
        self.manual_brightness = None
        self.apply_brightness()
    
    def disable_auto_brightness(self):
        """Disable automatic brightness adjustment"""
        self.auto_brightness_enabled = False
    
    def apply_brightness(self):
        """Apply current brightness setting to device"""
        if self.manual_brightness is not None:
            brightness = self.manual_brightness
        elif self.auto_brightness_enabled:
            brightness = self.get_auto_brightness()
        else:
            brightness = 255  # Default to full brightness
        
        # Ensure brightness is within valid range
        brightness = max(0, min(255, brightness))
        self.device.contrast(brightness)
    
    def update_brightness(self):
        """Update brightness based on current time (call periodically)"""
        if self.auto_brightness_enabled:
            self.apply_brightness()
    
    def show_icon(self, icon_name: str, duration: float = 3.0, animate: bool = True):
        """
        Display a weather icon (full screen, centered)
        
        Args:
            icon_name: Name of icon to display
            duration: Display duration
            animate: Whether to animate the icon (default True for cute animations)
        """
        icon = WeatherIcons.get_icon(icon_name)
        
        if animate:
            # Always use cute animations by default
            icon_upper = icon_name.upper()
            if 'RAIN' in icon_upper or 'SHOWER' in icon_upper:
                self.animator.cute_rain_animation(duration)
            elif 'SUN' in icon_upper or 'CLEAR' in icon_upper:
                self.animator.cute_sun_animation(duration)
            elif 'CLOUD' in icon_upper or 'OVERCAST' in icon_upper:
                self.animator.cute_cloud_animation(duration)
            elif 'WIND' in icon_upper:
                # Windy animation - blink with faster rate
                self.animator.blink(icon, duration, blink_rate=0.4)
            elif 'THUNDER' in icon_upper or 'STORM' in icon_upper:
                # Thunderstorm animation - fast blinking
                self.animator.blink(icon, duration, blink_rate=0.3)
            elif 'SNOW' in icon_upper:
                # Snow animation - slow gentle blinking
                self.animator.blink(icon, duration, blink_rate=0.6)
            else:
                # Default cute animation for other icons
                self.animator.blink(icon, duration, blink_rate=0.5)
        else:
            # Static display - full screen, centered (0,0 for 8x8)
            with canvas(self.device) as draw:
                WeatherIcons.draw_icon(draw, 0, 0, icon)
            time.sleep(duration)
    
    def show_text_scroll(self, text: str, speed: float = 0.05):
        """
        Display scrolling text
        
        Args:
            text: Text to display
            speed: Scroll speed
        """
        # Simple scrolling text implementation
        text_width = len(text) * 4  # Approximate width per character
        scroll_positions = text_width + 8  # Scroll from right to left
        
        for pos in range(scroll_positions):
            with canvas(self.device) as draw:
                # Calculate which part of text to show
                start_char = max(0, (pos - 8) // 4)
                end_char = min(len(text), (pos + 8) // 4 + 1)
                
                if start_char < len(text):
                    visible_text = text[start_char:end_char]
                    text_x = 8 - pos + start_char * 4
                    
                    # Draw visible text
                    if text_x < 8:
                        self._draw_simple_text(draw, max(0, text_x), 1, visible_text)
            
            time.sleep(speed)
    
    def show_mixed(self, icon_name: str, text: str, duration: float = 10.0):
        """
        Display icon and text side by side (4x8 each)
        
        Args:
            icon_name: Icon to display on left
            text: Text to display on right (max 2-3 chars)
            duration: Display duration
        """
        icon = WeatherIcons.get_icon(icon_name)
        
        with canvas(self.device) as draw:
            # Draw icon on left half (4x8 pixels)
            for row in range(8):
                for col in range(4):
                    # Sample every other pixel from icon for 4-pixel width
                    if icon[row] & (1 << (7 - col * 2)):
                        draw.point((col, row), fill="white")
            
            # Draw text on right half using simple pixel font
            self._draw_simple_text(draw, 4, 1, text)
        
        time.sleep(duration)
    
    def _draw_simple_text(self, draw, x: int, y: int, text: str):
        """Draw simple text using pixel patterns"""
        char_width = 3
        char_height = 5
        
        for i, char in enumerate(text[:2]):  # Max 2 characters for 4-pixel width
            char_x = x + i * char_width
            if char_x + char_width > 8:
                break
            self._draw_simple_char(draw, char_x, y, char)
    
    def _draw_simple_char(self, draw, x: int, y: int, char: str):
        """Draw a simple character using pixel patterns"""
        char_height = 5
        char_width = 3
        
        # Simple 3x5 pixel font patterns
        patterns = {
            '0': [
                [1, 1, 1],
                [1, 0, 1],
                [1, 0, 1],
                [1, 0, 1],
                [1, 1, 1]
            ],
            '1': [
                [0, 1, 0],
                [1, 1, 0],
                [0, 1, 0],
                [0, 1, 0],
                [1, 1, 1]
            ],
            '2': [
                [1, 1, 1],
                [0, 0, 1],
                [1, 1, 1],
                [1, 0, 0],
                [1, 1, 1]
            ],
            '3': [
                [1, 1, 1],
                [0, 0, 1],
                [1, 1, 1],
                [0, 0, 1],
                [1, 1, 1]
            ],
            '4': [
                [1, 0, 1],
                [1, 0, 1],
                [1, 1, 1],
                [0, 0, 1],
                [0, 0, 1]
            ],
            '5': [
                [1, 1, 1],
                [1, 0, 0],
                [1, 1, 1],
                [0, 0, 1],
                [1, 1, 1]
            ],
            '6': [
                [1, 1, 1],
                [1, 0, 0],
                [1, 1, 1],
                [1, 0, 1],
                [1, 1, 1]
            ],
            '7': [
                [1, 1, 1],
                [0, 0, 1],
                [0, 0, 1],
                [0, 0, 1],
                [0, 0, 1]
            ],
            '8': [
                [1, 1, 1],
                [1, 0, 1],
                [1, 1, 1],
                [1, 0, 1],
                [1, 1, 1]
            ],
            '9': [
                [1, 1, 1],
                [1, 0, 1],
                [1, 1, 1],
                [0, 0, 1],
                [1, 1, 1]
            ],
            '°': [
                [0, 1, 0],
                [1, 0, 1],
                [0, 1, 0],
                [0, 0, 0],
                [0, 0, 0]
            ],
            'C': [
                [1, 1, 1],
                [1, 0, 0],
                [1, 0, 0],
                [1, 0, 0],
                [1, 1, 1]
            ],
            'F': [
                [1, 1, 1],
                [1, 0, 0],
                [1, 1, 0],
                [1, 0, 0],
                [1, 0, 0]
            ]
        }
        
        pattern = patterns.get(char, patterns['0'])
        for row in range(min(char_height, 8 - y)):
            for col in range(min(char_width, 8 - x)):
                if pattern[row][col]:
                    draw.point((x + col, y + row), fill="white")
    
    def show_temperature_bar(self, temperatures: List[int], rainfall: List[int], 
                           current_col: int, blink: bool = True, duration: float = 2.0):
        """
        Show temperature bars (original display mode) with blinking current column
        
        Args:
            temperatures: List of 8 temperature levels (0-7)
            rainfall: List of 8 rainfall indicators (0 or 1)
            current_col: Current time column to blink
            blink: Whether to blink current column
            duration: Display duration in seconds
        """
        if not blink:
            # Static display without blinking
            with canvas(self.device) as draw:
                for i in range(8):
                    height = temperatures[i]
                    for j in range(height):
                        draw.point((i, 7 - j - 1), fill="white")
                    if rainfall[i] == 1:
                        draw.point((i, 7), fill="white")
            time.sleep(duration)
        else:
            # Blinking display for current column
            end_time = time.time() + duration
            blink_state = True
            
            while time.time() < end_time:
                with canvas(self.device) as draw:
                    for i in range(8):
                        # Skip current column if blinking off
                        if i == current_col and not blink_state:
                            continue
                            
                        height = temperatures[i]
                        for j in range(height):
                            draw.point((i, 7 - j - 1), fill="white")
                        if rainfall[i] == 1:
                            draw.point((i, 7), fill="white")
                
                # Toggle blink state every 0.5 seconds
                time.sleep(0.5)
                blink_state = not blink_state
    
    def trigger_alert(self, alert_type: str, data: Dict[str, Any], duration: float = 60.0):
        """
        Trigger an alert display (interrupts normal rotation)
        
        Args:
            alert_type: Type of alert ('earthquake', 'typhoon', 'warning')
            data: Alert data
            duration: Alert display duration
        """
        self.alert_active = True
        end_time = time.time() + min(duration, 30.0)  # Max 30 seconds
        
        while time.time() < end_time and self.alert_active:
            if alert_type == 'earthquake':
                # Show earthquake animation
                self.animator.earthquake_shake(duration=2.0)
                
                # Show earthquake details as scrolling text
                magnitude = data.get('magnitude', 'N/A')
                location = data.get('location', 'Unknown')
                text = f"EQ M{magnitude} {location[:8]}"
                self.show_text_scroll(text, speed=0.08)
            
            elif alert_type == 'typhoon':
                # Show typhoon icon with blinking
                self.animator.blink(WeatherIcons.TYPHOON, duration=2.0)
                
                # Show typhoon details
                name = data.get('name', 'TYPHOON')
                text = f"TYPHOON {name[:6]}"
                self.show_text_scroll(text, speed=0.08)
            
            elif alert_type == 'warning':
                # Show warning icon with blinking
                self.animator.blink(WeatherIcons.WARNING, duration=2.0)
                
                # Show warning message
                message = data.get('message', 'WARNING')
                self.show_text_scroll(message[:12], speed=0.08)
            
            # Brief pause between alert cycles
            time.sleep(0.5)
        
        self.alert_active = False
    
    def rotate_pages(self, duration: float = None):
        """
        Display current page and advance to next (handles rotation automatically)
        
        Args:
            duration: Override default page duration (if None, uses page's duration)
        """
        if not self.pages:
            return
        
        # Check for alerts
        if self.alert_active:
            return
        
        # Sort pages by priority (1=highest)
        sorted_pages = sorted(self.pages, key=lambda p: p.priority)
        
        # Get current page
        page = sorted_pages[self.current_page_idx % len(sorted_pages)]
        
        # Execute page content callback to display the page
        page.content_callback(self.device)
        
        # Wait for page duration before moving to next
        page_duration = duration if duration is not None else page.duration
        time.sleep(page_duration)
        
        # Advance to next page for subsequent call
        self.current_page_idx = (self.current_page_idx + 1) % len(sorted_pages)
    
    def transition_to(self, content_callback: Callable, transition: str = "fade"):
        """
        Transition to new content with effect
        
        Args:
            content_callback: Function to draw new content
            transition: Transition type ('fade', 'slide_left', 'slide_right')
        """
        if transition == "fade":
            self.animator.fade_transition(lambda: content_callback(self.device))
        elif transition.startswith("slide_"):
            direction = transition.split("_")[1]
            self.animator.slide_in(lambda draw: content_callback(self.device), 
                                 direction=direction)
        else:
            content_callback(self.device)
    
    def show_startup_logo(self):
        """Show startup logo animation with smiley face"""
        # Smiley face icon (8x8)
        SMILEY = [
            0b00111100,
            0b01000010,
            0b10100101,
            0b10000001,
            0b10100101,
            0b10011001,
            0b01000010,
            0b00111100,
        ]
        
        # Draw smiley face
        with canvas(self.device) as draw:
            for row in range(8):
                for col in range(8):
                    if SMILEY[row] & (1 << (7 - col)):
                        draw.point((col, row), fill="white")
        
        time.sleep(0.5)
        
        # Fade out
        for intensity in range(15, -1, -1):
            self.device.contrast(intensity * 16)
            time.sleep(0.05)
        
        # Fade in
        for intensity in range(16):
            self.device.contrast(intensity * 16)
            time.sleep(0.05)
        
        # Blink effect (eyes)
        for _ in range(2):
            # Close eyes (remove dots at row 2)
            with canvas(self.device) as draw:
                for row in range(8):
                    for col in range(8):
                        if row == 2:
                            # Draw closed eyes (horizontal line)
                            if col in [2, 5]:
                                draw.point((col, row), fill="white")
                        elif SMILEY[row] & (1 << (7 - col)):
                            draw.point((col, row), fill="white")
            time.sleep(0.15)
            
            # Open eyes (back to normal)
            with canvas(self.device) as draw:
                for row in range(8):
                    for col in range(8):
                        if SMILEY[row] & (1 << (7 - col)):
                            draw.point((col, row), fill="white")
            time.sleep(0.3)
        
        time.sleep(0.3)
        self.device.clear()
    
    def set_display_mode(self, mode: str):
        """
        Set the current display mode
        
        Args:
            mode: Display mode ('carousel', 'icon', 'scrolling', 'mixed', 'alert')
        """
        self.current_mode = mode
        logger.info(f"Display mode set to: {mode}")
    
    def show_mode_content(self, weather_data: Dict[str, Any] = None, temperature_data: List[int] = None, 
                         rainfall_data: List[int] = None, current_col: int = 0):
        """
        Show content based on current display mode
        
        Args:
            weather_data: Current weather observation data
            temperature_data: Temperature levels for bar display
            rainfall_data: Rainfall levels for bar display
            current_col: Current time column for blinking
        """
        if self.current_mode == self.MODE_ICON:
            if weather_data and weather_data.get('weather') != 'N/A':
                weather_desc = weather_data.get('weather', '')
                icon_name = self._get_weather_icon_name(weather_desc)
                self.show_icon(icon_name, duration=10.0, animate=True)
            else:
                self.show_icon('sunny', duration=10.0, animate=True)
        
        elif self.current_mode == self.MODE_SCROLLING:
            if weather_data:
                temp = weather_data.get('temperature', 0)
                weather = weather_data.get('weather', 'N/A')
                text = f"{temp:.0f}C {weather[:8]}"
            else:
                text = "Loading..."
            self.show_text_scroll(text, speed=0.08)
        
        elif self.current_mode == self.MODE_MIXED:
            if weather_data and weather_data.get('weather') != 'N/A':
                weather_desc = weather_data.get('weather', '')
                icon_name = self._get_weather_icon_name(weather_desc)
                temp = weather_data.get('temperature', 0)
                self.show_icon(icon_name, duration=5.0, animate=True)
            else:
                self.show_icon('sunny', duration=5.0, animate=True)
        
        elif self.current_mode == self.MODE_ALERT:
            self.animator.blink(WeatherIcons.WARNING, duration=3.0, blink_rate=0.3)
            if weather_data:
                temp = weather_data.get('temperature', 0)
                text = f"ALERT {temp:.0f}C"
            else:
                text = "ALERT MODE"
            self.show_text_scroll(text, speed=0.1)
        
        else:  # MODE_CAROUSEL or default
            # Show temperature bars (original display)
            if temperature_data and rainfall_data:
                self.show_temperature_bar(temperature_data, rainfall_data, current_col, blink=True)
            else:
                self.show_icon('sunny', duration=5.0, animate=True)
    
    def _get_weather_icon_name(self, weather_desc: str) -> str:
        """Get appropriate icon name from weather description"""
        weather_desc = weather_desc.lower()
        
        if 'sun' in weather_desc or 'clear' in weather_desc:
            return 'sunny'
        elif 'rain' in weather_desc or 'shower' in weather_desc:
            return 'rainy'
        elif 'cloud' in weather_desc or 'overcast' in weather_desc:
            return 'cloudy'
        elif 'thunder' in weather_desc or 'storm' in weather_desc:
            return 'thunderstorm'
        elif 'snow' in weather_desc:
            return 'snowy'
        elif 'wind' in weather_desc:
            return 'windy'
        else:
            return 'sunny'  # Default
