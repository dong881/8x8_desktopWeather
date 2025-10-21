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
    
    # Number digits (4x7 pixels each, designed to fit 2 digits on 8x8 display)
    DIGITS = {
        '0': [
            0b01100000,
            0b10010000,
            0b10010000,
            0b10010000,
            0b10010000,
            0b10010000,
            0b01100000,
            0b00000000,
        ],
        '1': [
            0b01000000,
            0b11000000,
            0b01000000,
            0b01000000,
            0b01000000,
            0b01000000,
            0b11100000,
            0b00000000,
        ],
        '2': [
            0b01100000,
            0b10010000,
            0b00010000,
            0b00100000,
            0b01000000,
            0b10000000,
            0b11110000,
            0b00000000,
        ],
        '3': [
            0b11100000,
            0b00010000,
            0b00010000,
            0b01100000,
            0b00010000,
            0b00010000,
            0b11100000,
            0b00000000,
        ],
        '4': [
            0b00100000,
            0b01100000,
            0b10100000,
            0b10100000,
            0b11110000,
            0b00100000,
            0b00100000,
            0b00000000,
        ],
        '5': [
            0b11110000,
            0b10000000,
            0b10000000,
            0b11100000,
            0b00010000,
            0b00010000,
            0b11100000,
            0b00000000,
        ],
        '6': [
            0b01100000,
            0b10000000,
            0b10000000,
            0b11100000,
            0b10010000,
            0b10010000,
            0b01100000,
            0b00000000,
        ],
        '7': [
            0b11110000,
            0b00010000,
            0b00100000,
            0b00100000,
            0b01000000,
            0b01000000,
            0b01000000,
            0b00000000,
        ],
        '8': [
            0b01100000,
            0b10010000,
            0b10010000,
            0b01100000,
            0b10010000,
            0b10010000,
            0b01100000,
            0b00000000,
        ],
        '9': [
            0b01100000,
            0b10010000,
            0b10010000,
            0b01110000,
            0b00010000,
            0b00010000,
            0b01100000,
            0b00000000,
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
    
    # Cute cloud animation frames (5 frames) - floating and expressive
    CUTE_CLOUD = [
        # Frame 1 - normal with happy face
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
        # Frame 2 - floating up with winking eye
        [
            0b00111100,
            0b01111110,
            0b11111111,
            0b11111111,
            0b01111110,
            0b00111100,
            0b00011000,
            0b00000000,
        ],
        # Frame 3 - floating down with surprised expression
        [
            0b00000000,
            0b00011000,
            0b00111100,
            0b01111110,
            0b11111111,
            0b11111111,
            0b01111110,
            0b00111100,
        ],
        # Frame 4 - back to center with smile
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
        # Frame 5 - gentle bounce
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
    ]
    
    # Cute sun animation frames (6 frames) - more expressive and cute
    CUTE_SUN = [
        # Frame 1 - normal with rays and happy expression
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
        # Frame 2 - winking left eye with smile
        [
            0b10000001,
            0b01010100,
            0b00111000,
            0b01111100,
            0b01111100,
            0b00111000,
            0b01010100,
            0b10010001,
        ],
        # Frame 3 - both eyes open, bigger smile
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
        # Frame 4 - winking right eye
        [
            0b10010001,
            0b01010100,
            0b00111000,
            0b01111100,
            0b01111100,
            0b00111000,
            0b01010100,
            0b10000001,
        ],
        # Frame 5 - surprised expression (bigger eyes)
        [
            0b11011011,
            0b01010100,
            0b00111000,
            0b01111100,
            0b01111100,
            0b00111000,
            0b01010100,
            0b11011011,
        ],
        # Frame 6 - back to normal happy
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
    ]
    
    # Cute rain animation frames (6 frames) - more dynamic and cute
    CUTE_RAIN = [
        # Frame 1 - normal rain with happy cloud
        [
            0b00111100,
            0b01111110,
            0b11111111,
            0b11111111,
            0b01010101,
            0b00000000,
            0b10101010,
            0b00000000,
        ],
        # Frame 2 - rain drops bouncing with cloud smile
        [
            0b00111100,
            0b01111110,
            0b11111111,
            0b11111111,
            0b00000000,
            0b01010101,
            0b00000000,
            0b10101010,
        ],
        # Frame 3 - heavy rain with cloud surprised
        [
            0b00111100,
            0b01111110,
            0b11111111,
            0b11111111,
            0b10101010,
            0b01010101,
            0b10101010,
            0b01010101,
        ],
        # Frame 4 - light rain with cloud winking
        [
            0b00111100,
            0b01111110,
            0b11111111,
            0b11111111,
            0b00000000,
            0b10101010,
            0b00000000,
            0b01010101,
        ],
        # Frame 5 - rain stopping with cloud happy
        [
            0b00111100,
            0b01111110,
            0b11111111,
            0b11111111,
            0b00000000,
            0b00000000,
            0b10101010,
            0b00000000,
        ],
        # Frame 6 - back to normal
        [
            0b00111100,
            0b01111110,
            0b11111111,
            0b11111111,
            0b01010101,
            0b00000000,
            0b10101010,
            0b00000000,
        ],
    ]
    
    # Cute snow animation frames (4 frames) - gentle and magical
    CUTE_SNOW = [
        # Frame 1 - gentle snow with happy cloud
        [
            0b00111100,
            0b01111110,
            0b11111111,
            0b11111111,
            0b00000000,
            0b10101010,
            0b00000000,
            0b01010101,
        ],
        # Frame 2 - snowflakes dancing
        [
            0b00111100,
            0b01111110,
            0b11111111,
            0b11111111,
            0b01010101,
            0b00000000,
            0b10101010,
            0b00000000,
        ],
        # Frame 3 - more snow with cloud excited
        [
            0b00111100,
            0b01111110,
            0b11111111,
            0b11111111,
            0b10101010,
            0b01010101,
            0b00000000,
            0b10101010,
        ],
        # Frame 4 - gentle snow ending
        [
            0b00111100,
            0b01111110,
            0b11111111,
            0b11111111,
            0b00000000,
            0b10101010,
            0b01010101,
            0b00000000,
        ],
    ]
    
    # Cute wind animation frames (4 frames) - playful and dynamic
    CUTE_WIND = [
        # Frame 1 - gentle breeze
        [
            0b00000000,
            0b11111100,
            0b00000110,
            0b00000000,
            0b01111111,
            0b11000000,
            0b00000000,
            0b00000000,
        ],
        # Frame 2 - stronger wind
        [
            0b00000000,
            0b00000000,
            0b11111100,
            0b00000110,
            0b00000000,
            0b01111111,
            0b11000000,
            0b00000000,
        ],
        # Frame 3 - very strong wind
        [
            0b00000000,
            0b00000000,
            0b00000000,
            0b11111100,
            0b00000110,
            0b00000000,
            0b01111111,
            0b11000000,
        ],
        # Frame 4 - wind calming down
        [
            0b00000000,
            0b11111100,
            0b00000110,
            0b00000000,
            0b01111111,
            0b11000000,
            0b00000000,
            0b00000000,
        ],
    ]
    
    # Cute thunderstorm animation frames (5 frames) - dramatic but cute
    CUTE_THUNDERSTORM = [
        # Frame 1 - dark cloud with lightning
        [
            0b00111100,
            0b01111110,
            0b11111111,
            0b11111111,
            0b00011000,
            0b00110000,
            0b01100000,
            0b11000000,
        ],
        # Frame 2 - lightning flash
        [
            0b00111100,
            0b01111110,
            0b11111111,
            0b11111111,
            0b00000000,
            0b00000000,
            0b00000000,
            0b00000000,
        ],
        # Frame 3 - rain with thunder
        [
            0b00111100,
            0b01111110,
            0b11111111,
            0b11111111,
            0b01010101,
            0b00000000,
            0b10101010,
            0b00000000,
        ],
        # Frame 4 - more lightning
        [
            0b00111100,
            0b01111110,
            0b11111111,
            0b11111111,
            0b00000000,
            0b00000000,
            0b00000000,
            0b00000000,
        ],
        # Frame 5 - storm calming
        [
            0b00111100,
            0b01111110,
            0b11111111,
            0b11111111,
            0b00011000,
            0b00110000,
            0b01100000,
            0b11000000,
        ],
    ]
