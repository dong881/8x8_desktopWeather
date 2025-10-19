"""
Display Manager for 8x8 LED Matrix
Manages different display modes and content presentation
"""

import time
from typing import List, Dict, Any, Optional, Callable
from luma.core.render import canvas
from .icons import WeatherIcons
from .animations import AnimationEngine


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
    
    def show_icon(self, icon_name: str, duration: float = 3.0, animate: bool = False):
        """
        Display a weather icon
        
        Args:
            icon_name: Name of icon to display
            duration: Display duration
            animate: Whether to animate the icon
        """
        icon = WeatherIcons.get_icon(icon_name)
        
        if animate and icon_name.upper() == 'RAINY':
            self.animator.rain_animation(duration)
        elif animate and icon_name.upper() == 'SUNNY':
            self.animator.sun_animation(duration)
        else:
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
        self.animator.scroll_text_horizontal(text, speed)
    
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
            # Draw icon on left half (scaled down to 4 pixels wide)
            for row in range(8):
                for col in range(4):
                    # Sample every other pixel from icon
                    if icon[row] & (1 << (7 - col * 2)):
                        draw.point((col, row), fill="white")
            
            # Draw text on right half
            from luma.core.legacy.font import proportional, TINY_FONT
            from luma.core.legacy import text as draw_text
            draw_text(draw, (4, 0), text, fill="white", font=proportional(TINY_FONT))
        
        time.sleep(duration)
    
    def show_temperature_bar(self, temperatures: List[int], rainfall: List[int], 
                           current_col: int, blink: bool = True):
        """
        Show temperature bars (original display mode)
        
        Args:
            temperatures: List of 8 temperature levels (0-7)
            rainfall: List of 8 rainfall indicators (0 or 1)
            current_col: Current time column to blink
            blink: Whether to blink current column
        """
        with canvas(self.device) as draw:
            for i in range(8):
                if blink and i == current_col:
                    continue
                height = temperatures[i]
                for j in range(height):
                    draw.point((i, 7 - j - 1), fill="white")
                if rainfall[i] == 1:
                    draw.point((i, 7), fill="white")
    
    def trigger_alert(self, alert_type: str, data: Dict[str, Any], duration: float = 60.0):
        """
        Trigger an alert display (interrupts normal rotation)
        
        Args:
            alert_type: Type of alert ('earthquake', 'typhoon', 'warning')
            data: Alert data
            duration: Alert display duration
        """
        self.alert_active = True
        
        if alert_type == 'earthquake':
            # Show earthquake animation
            self.animator.earthquake_shake(duration=min(duration, 10.0))
            
            # Show earthquake details as scrolling text
            magnitude = data.get('magnitude', 'N/A')
            location = data.get('location', 'Unknown')
            text = f"EARTHQUAKE M{magnitude} {location}"
            self.show_text_scroll(text, speed=0.03)
        
        elif alert_type == 'typhoon':
            # Show typhoon icon with blinking
            self.animator.blink(WeatherIcons.TYPHOON, duration=min(duration, 10.0))
            
            # Show typhoon details
            name = data.get('name', 'TYPHOON')
            text = f"TYPHOON {name} ALERT"
            self.show_text_scroll(text, speed=0.03)
        
        elif alert_type == 'warning':
            # Show warning icon with blinking
            self.animator.blink(WeatherIcons.WARNING, duration=min(duration, 10.0))
            
            # Show warning message
            message = data.get('message', 'WARNING')
            self.show_text_scroll(message, speed=0.03)
        
        self.alert_active = False
    
    def rotate_pages(self, duration: float = None):
        """
        Display pages in rotation
        
        Args:
            duration: Override default page duration
        """
        if not self.pages:
            return
        
        # Check for alerts
        if self.alert_active:
            return
        
        # Sort pages by priority (1=highest)
        sorted_pages = sorted(self.pages, key=lambda p: p.priority)
        
        # Display current page
        page = sorted_pages[self.current_page_idx % len(sorted_pages)]
        
        # Execute page content callback
        page.content_callback(self.device)
        
        # Wait for page duration
        page_duration = duration if duration is not None else page.duration
        time.sleep(page_duration)
        
        # Move to next page
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
        """Display startup logo animation"""
        with canvas(self.device) as draw:
            draw.rectangle(self.device.bounding_box, outline="white", fill="black")
            draw.ellipse([(0, 0), (7, 7)], outline="white", fill="black")
            draw.ellipse([(2, 2), (5, 5)], outline="white", fill="black")
        
        time.sleep(0.5)
        
        # Fade out and in
        for intensity in list(range(15, 0, -1)):
            self.device.contrast(intensity * 16)
            time.sleep(0.05)
        
        for intensity in range(16):
            self.device.contrast(intensity * 16)
            time.sleep(0.05)
