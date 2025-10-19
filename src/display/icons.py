"""
8x8 Pixel Icon Library for Weather Display
Each icon is represented as an 8x8 byte array
"""

from typing import List


class WeatherIcons:
    """8x8 pixel weather icons as byte arrays"""
    
    # Weather condition icons
    SUNNY = [
        0b00010000,
        0b01010100,
        0b00111000,
        0b01111100,
        0b01111100,
        0b00111000,
        0b01010100,
        0b00010000,
    ]
    
    CLOUDY = [
        0b00011000,
        0b00111100,
        0b01111110,
        0b11111111,
        0b11111111,
        0b11111111,
        0b01111110,
        0b00000000,
    ]
    
    RAINY = [
        0b00111100,
        0b01111110,
        0b11111111,
        0b11111111,
        0b01010101,
        0b00000000,
        0b10101010,
        0b00000000,
    ]
    
    THUNDERSTORM = [
        0b00111100,
        0b01111110,
        0b11111111,
        0b00011000,
        0b00110000,
        0b01100000,
        0b11000000,
        0b10000000,
    ]
    
    SNOWY = [
        0b00111100,
        0b01111110,
        0b11111111,
        0b00000000,
        0b10101010,
        0b01010101,
        0b10101010,
        0b00000000,
    ]
    
    TYPHOON = [
        0b00011000,
        0b00111100,
        0b01111110,
        0b11111111,
        0b11111111,
        0b01111110,
        0b00111100,
        0b00011000,
    ]
    
    # Alert icons
    EARTHQUAKE = [
        0b00011000,
        0b00111100,
        0b01111110,
        0b11111111,
        0b11111111,
        0b01111110,
        0b00111100,
        0b00011000,
    ]
    
    WARNING = [
        0b00011000,
        0b00111100,
        0b01111110,
        0b11011011,
        0b11011011,
        0b11111111,
        0b11111111,
        0b01111110,
    ]
    
    ALERT = [
        0b00011000,
        0b00011000,
        0b00111100,
        0b00111100,
        0b01111110,
        0b01111110,
        0b11111111,
        0b11111111,
    ]
    
    # Temperature icons
    THERMOMETER_HOT = [
        0b00011000,
        0b00100100,
        0b00100100,
        0b00100100,
        0b00111100,
        0b01111110,
        0b01111110,
        0b00111100,
    ]
    
    THERMOMETER_COLD = [
        0b00011000,
        0b00100100,
        0b00100100,
        0b00100100,
        0b00100100,
        0b00111100,
        0b00111100,
        0b00011000,
    ]
    
    # Wind icon
    WINDY = [
        0b00000000,
        0b11111100,
        0b00000110,
        0b00000000,
        0b01111111,
        0b11000000,
        0b00000000,
        0b00000000,
    ]
    
    # Number digits (5x7 pixels, centered)
    DIGITS = {
        '0': [
            0b00000000,
            0b01110000,
            0b10001000,
            0b10011000,
            0b10101000,
            0b11001000,
            0b10001000,
            0b01110000,
        ],
        '1': [
            0b00000000,
            0b00100000,
            0b01100000,
            0b00100000,
            0b00100000,
            0b00100000,
            0b00100000,
            0b01110000,
        ],
        '2': [
            0b00000000,
            0b01110000,
            0b10001000,
            0b00001000,
            0b00110000,
            0b01000000,
            0b10000000,
            0b11111000,
        ],
        '3': [
            0b00000000,
            0b11111000,
            0b00001000,
            0b00010000,
            0b00110000,
            0b00001000,
            0b10001000,
            0b01110000,
        ],
        '4': [
            0b00000000,
            0b00010000,
            0b00110000,
            0b01010000,
            0b10010000,
            0b11111000,
            0b00010000,
            0b00010000,
        ],
        '5': [
            0b00000000,
            0b11111000,
            0b10000000,
            0b11110000,
            0b00001000,
            0b00001000,
            0b10001000,
            0b01110000,
        ],
        '6': [
            0b00000000,
            0b00110000,
            0b01000000,
            0b10000000,
            0b11110000,
            0b10001000,
            0b10001000,
            0b01110000,
        ],
        '7': [
            0b00000000,
            0b11111000,
            0b00001000,
            0b00010000,
            0b00100000,
            0b01000000,
            0b01000000,
            0b01000000,
        ],
        '8': [
            0b00000000,
            0b01110000,
            0b10001000,
            0b10001000,
            0b01110000,
            0b10001000,
            0b10001000,
            0b01110000,
        ],
        '9': [
            0b00000000,
            0b01110000,
            0b10001000,
            0b10001000,
            0b01111000,
            0b00001000,
            0b00010000,
            0b01100000,
        ],
    }
    
    @staticmethod
    def get_icon(name: str) -> List[int]:
        """
        Get icon by name
        
        Args:
            name: Icon name (e.g., 'sunny', 'rainy', 'earthquake')
            
        Returns:
            8x8 byte array representing the icon
        """
        name = name.upper()
        return getattr(WeatherIcons, name, WeatherIcons.SUNNY)
    
    @staticmethod
    def draw_icon(draw, x: int, y: int, icon: List[int], fill: str = "white"):
        """
        Draw icon on canvas
        
        Args:
            draw: PIL Draw object
            x: X coordinate (left)
            y: Y coordinate (top)
            icon: Icon byte array
            fill: Pixel color
        """
        for row in range(8):
            for col in range(8):
                if icon[row] & (1 << (7 - col)):
                    draw.point((x + col, y + row), fill=fill)
    
    @staticmethod
    def draw_digit(draw, x: int, y: int, digit: str, fill: str = "white"):
        """
        Draw a digit on canvas
        
        Args:
            draw: PIL Draw object
            x: X coordinate (left)
            y: Y coordinate (top)
            digit: Digit character ('0'-'9')
            fill: Pixel color
        """
        if digit not in WeatherIcons.DIGITS:
            return
        
        icon = WeatherIcons.DIGITS[digit]
        for row in range(8):
            for col in range(8):
                if icon[row] & (1 << (7 - col)):
                    draw.point((x + col, y + row), fill=fill)


class AnimationFrames:
    """Animation frame sequences for weather effects"""
    
    # Rain animation frames (3 frames)
    RAIN = [
        # Frame 1
        [
            0b00111100,
            0b01111110,
            0b11111111,
            0b01000000,
            0b00100000,
            0b00010000,
            0b00000000,
            0b00000000,
        ],
        # Frame 2
        [
            0b00111100,
            0b01111110,
            0b11111111,
            0b00000000,
            0b01000000,
            0b00100000,
            0b00010000,
            0b00000000,
        ],
        # Frame 3
        [
            0b00111100,
            0b01111110,
            0b11111111,
            0b00000000,
            0b00000000,
            0b01000000,
            0b00100000,
            0b00010000,
        ],
    ]
    
    # Sun shine animation frames (2 frames)
    SUN = [
        # Frame 1 - with rays
        [
            0b10010001,
            0b01010100,
            0b00111000,
            0b01111100,
            0b01111100,
            0b00111000,
            0b01010100,
            0b10010001,
        ],
        # Frame 2 - without rays
        [
            0b00000000,
            0b00000000,
            0b00111000,
            0b01111100,
            0b01111100,
            0b00111000,
            0b00000000,
            0b00000000,
        ],
    ]
    
    # Earthquake shake animation frames (4 frames)
    SHAKE = [
        # Frame 1 - center
        [
            0b00011000,
            0b00111100,
            0b01111110,
            0b11111111,
            0b11111111,
            0b01111110,
            0b00111100,
            0b00011000,
        ],
        # Frame 2 - shift right
        [
            0b00110000,
            0b01111000,
            0b11111100,
            0b11111110,
            0b11111110,
            0b11111100,
            0b01111000,
            0b00110000,
        ],
        # Frame 3 - center
        [
            0b00011000,
            0b00111100,
            0b01111110,
            0b11111111,
            0b11111111,
            0b01111110,
            0b00111100,
            0b00011000,
        ],
        # Frame 4 - shift left
        [
            0b00001100,
            0b00011110,
            0b00111111,
            0b01111111,
            0b01111111,
            0b00111111,
            0b00011110,
            0b00001100,
        ],
    ]
