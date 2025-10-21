"""
Animation Engine for 8x8 LED Matrix
Provides various animation effects for weather display
"""

import time
from typing import Callable, List, Optional
from luma.core.render import canvas
from .icons import WeatherIcons, AnimationFrames


class AnimationEngine:
    """Handles animations for weather display"""
    
    def __init__(self, device):
        """
        Initialize animation engine
        
        Args:
            device: luma.led_matrix device instance
        """
        self.device = device
    
    def rain_animation(self, duration: float = 6.0, fps: int = 5):
        """
        Animate rain falling effect with cute bouncing drops
        
        Args:
            duration: Animation duration in seconds (doubled for slower animation)
            fps: Frames per second (reduced for slower animation)
        """
        frames = AnimationFrames.RAIN
        frame_delay = 1.0 / fps
        end_time = time.time() + duration
        
        while time.time() < end_time:
            for frame in frames:
                if time.time() >= end_time:
                    break
                with canvas(self.device) as draw:
                    WeatherIcons.draw_icon(draw, 0, 0, frame)
                time.sleep(frame_delay)
    
    def sun_animation(self, duration: float = 4.0, blink_rate: float = 1.0):
        """
        Animate sun shining effect (blinking rays) - slower and cuter
        
        Args:
            duration: Animation duration in seconds (doubled for slower animation)
            blink_rate: Time between blinks in seconds (doubled for slower animation)
        """
        frames = AnimationFrames.SUN
        end_time = time.time() + duration
        frame_idx = 0
        
        while time.time() < end_time:
            with canvas(self.device) as draw:
                WeatherIcons.draw_icon(draw, 0, 0, frames[frame_idx % 2])
            frame_idx += 1
            time.sleep(blink_rate)
    
    def earthquake_shake(self, duration: float = 5.0, shake_speed: float = 0.1):
        """
        Animate earthquake shaking effect
        
        Args:
            duration: Animation duration in seconds
            shake_speed: Time between shake frames
        """
        frames = AnimationFrames.SHAKE
        end_time = time.time() + duration
        frame_idx = 0
        
        while time.time() < end_time:
            with canvas(self.device) as draw:
                WeatherIcons.draw_icon(draw, 0, 0, frames[frame_idx % len(frames)])
            frame_idx += 1
            time.sleep(shake_speed)
    
    def fade_transition(self, callback: Callable, duration: float = 0.5):
        """
        Fade out, execute callback, then fade in
        
        Args:
            callback: Function to execute during transition
            duration: Fade duration in seconds
        """
        # Fade out
        for intensity in range(15, -1, -1):
            self.device.contrast(intensity * 16)
            time.sleep(duration / 16)
        
        # Execute callback during black screen
        callback()
        
        # Fade in
        for intensity in range(16):
            self.device.contrast(intensity * 16)
            time.sleep(duration / 16)
    
    def blink(self, icon: List[int], duration: float = 2.0, blink_rate: float = 0.5):
        """
        Blink an icon on/off
        
        Args:
            icon: Icon byte array to blink
            duration: Total blink duration
            blink_rate: Time between blinks
        """
        end_time = time.time() + duration
        visible = True
        
        while time.time() < end_time:
            if visible:
                with canvas(self.device) as draw:
                    WeatherIcons.draw_icon(draw, 0, 0, icon)
            else:
                with canvas(self.device) as draw:
                    draw.rectangle(self.device.bounding_box, outline="black", fill="black")
            
            visible = not visible
            time.sleep(blink_rate)
    
    def scroll_text_horizontal(self, text: str, speed: float = 0.05):
        """
        Scroll text horizontally across display
        
        Args:
            text: Text to scroll
            speed: Scroll speed (seconds per pixel)
        """
        from luma.core.legacy import show_message
        from luma.core.legacy.font import proportional, CP437_FONT
        
        show_message(self.device, text, fill="white", 
                    font=proportional(CP437_FONT), scroll_delay=speed)
    
    def slide_in(self, content_callback: Callable, direction: str = "left"):
        """
        Slide in new content from specified direction
        
        Args:
            content_callback: Function that draws content on canvas
            direction: Slide direction ('left', 'right', 'up', 'down')
        """
        from luma.core.virtual import viewport
        from PIL import Image
        
        # Create virtual canvas larger than display
        if direction in ['left', 'right']:
            virtual = viewport(self.device, width=16, height=8)
        else:
            virtual = viewport(self.device, width=8, height=16)
        
        # Draw content on virtual canvas
        with canvas(virtual) as draw:
            content_callback(draw)
        
        # Animate sliding
        if direction == "left":
            for x in range(8, -1, -1):
                virtual.set_position((x, 0))
                time.sleep(0.05)
        elif direction == "right":
            for x in range(-8, 1):
                virtual.set_position((x, 0))
                time.sleep(0.05)
        elif direction == "up":
            for y in range(8, -1, -1):
                virtual.set_position((0, y))
                time.sleep(0.05)
        elif direction == "down":
            for y in range(-8, 1):
                virtual.set_position((0, y))
                time.sleep(0.05)
    
    def cute_cloud_animation(self, duration: float = 4.0):
        """
        Animate cute cloud floating effect
        
        Args:
            duration: Animation duration in seconds
        """
        frames = AnimationFrames.CUTE_CLOUD
        frame_delay = 0.8  # Slower animation
        end_time = time.time() + duration
        
        while time.time() < end_time:
            for frame in frames:
                if time.time() >= end_time:
                    break
                with canvas(self.device) as draw:
                    WeatherIcons.draw_icon(draw, 0, 0, frame)
                time.sleep(frame_delay)
    
    def cute_sun_animation(self, duration: float = 4.0):
        """
        Animate cute sun with winking effect
        
        Args:
            duration: Animation duration in seconds
        """
        frames = AnimationFrames.CUTE_SUN
        frame_delay = 1.2  # Slower animation
        end_time = time.time() + duration
        
        while time.time() < end_time:
            for frame in frames:
                if time.time() >= end_time:
                    break
                with canvas(self.device) as draw:
                    WeatherIcons.draw_icon(draw, 0, 0, frame)
                time.sleep(frame_delay)
    
    def cute_rain_animation(self, duration: float = 6.0):
        """
        Animate cute rain with bouncing drops
        
        Args:
            duration: Animation duration in seconds
        """
        frames = AnimationFrames.CUTE_RAIN
        frame_delay = 0.6  # Slower animation
        end_time = time.time() + duration
        
        while time.time() < end_time:
            for frame in frames:
                if time.time() >= end_time:
                    break
                with canvas(self.device) as draw:
                    WeatherIcons.draw_icon_fullscreen(draw, frame)
                time.sleep(frame_delay)
    
    def cute_wind_animation(self, duration: float = 4.0):
        """
        Animate cute wind effect with moving lines
        
        Args:
            duration: Animation duration in seconds
        """
        frames = AnimationFrames.CUTE_WIND
        frame_delay = 0.8  # Slower animation
        end_time = time.time() + duration
        
        while time.time() < end_time:
            for frame in frames:
                if time.time() >= end_time:
                    break
                with canvas(self.device) as draw:
                    WeatherIcons.draw_icon_fullscreen(draw, frame)
                time.sleep(frame_delay)
