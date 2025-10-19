"""
Data Processor for Weather Information
Processes and transforms API responses into display-ready format
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime


class DataProcessor:
    """Processes weather data from API responses"""
    
    @staticmethod
    def process_weather_forecast(data: Dict) -> Optional[Tuple[List[int], List[int]]]:
        """
        Process weather forecast data into temperature and rainfall arrays
        
        Args:
            data: API response data
            
        Returns:
            Tuple of (temperature_levels, rainfall_levels) or None
        """
        try:
            location_data = data["records"]["Locations"][0]["Location"][0]["WeatherElement"]
            
            # Find temperature and precipitation data
            temp_data = None
            pop_data = None
            
            for element in location_data:
                if element.get("ElementName") == "T":
                    temp_data = element["Time"]
                elif element.get("ElementName") == "PoP6h":
                    pop_data = element["Time"]
            
            if not temp_data or not pop_data:
                return None
            
            # Extract temperature values
            temp_values = [int(t['ElementValue'][0]['Temperature']) for t in temp_data]
            
            # Extract precipitation probabilities
            pop_values = [int(p['ElementValue'][0]['Probability']) for p in pop_data]
            
            # Convert to LED levels
            temp_levels = DataProcessor._temperature_to_levels(temp_values)
            pop_levels = DataProcessor._precipitation_to_levels(pop_values)
            
            return temp_levels, pop_levels
        
        except Exception as e:
            print(f"Error processing weather forecast: {str(e)}")
            return None
    
    @staticmethod
    def _temperature_to_levels(temperatures: List[int], 
                               min_temp: int = 12, 
                               max_temp: int = 33) -> List[int]:
        """
        Convert temperatures to 8 LED levels (0-7)
        
        Args:
            temperatures: List of temperature values
            min_temp: Minimum temperature for scaling
            max_temp: Maximum temperature for scaling
            
        Returns:
            List of LED levels (0-7)
        """
        levels = []
        for temp in temperatures:
            # Clamp temperature to range
            temp = max(min_temp, min(max_temp, temp))
            
            # Convert to 0-7 scale
            level = round(7 * (temp - min_temp) / (max_temp - min_temp))
            levels.append(level)
        
        return levels
    
    @staticmethod
    def _precipitation_to_levels(probabilities: List[int], 
                                threshold: int = 60) -> List[int]:
        """
        Convert precipitation probabilities to binary indicators
        
        Args:
            probabilities: List of precipitation probabilities (0-100)
            threshold: Threshold for rain indication
            
        Returns:
            List of binary indicators (0 or 1)
        """
        levels = []
        for prob in probabilities:
            # Each probability covers 6 hours, but we need values for 3-hour periods
            # Duplicate each value
            indicator = 1 if prob >= threshold else 0
            levels.extend([indicator, indicator])
        
        return levels
    
    @staticmethod
    def process_observation_data(data: Dict) -> Optional[Dict]:
        """
        Process real-time observation data
        
        Args:
            data: API response data
            
        Returns:
            Processed observation data or None
        """
        try:
            if not data or 'records' not in data:
                return None
            
            location = data['records']['Station'][0]
            obs_time = location['ObsTime']['DateTime']
            
            result = {
                'time': obs_time,
                'temperature': float(location.get('Temperature', 0)),
                'humidity': int(location.get('RelativeHumidity', 0)),
                'weather': location.get('Weather', 'N/A')
            }
            
            return result
        
        except Exception as e:
            print(f"Error processing observation data: {str(e)}")
            return None
    
    @staticmethod
    def process_earthquake_data(data: Dict) -> Optional[Dict]:
        """
        Process earthquake report data
        
        Args:
            data: API response data
            
        Returns:
            Processed earthquake data or None
        """
        try:
            if not data or 'records' not in data:
                return None
            
            earthquakes = data['records']['Earthquake']
            if not earthquakes:
                return None
            
            # Get most recent earthquake
            latest = earthquakes[0]
            
            result = {
                'time': latest['EarthquakeNo'],
                'magnitude': float(latest['EarthquakeMagnitude']['MagnitudeValue']),
                'location': latest['EarthquakeInfo']['Epicenter']['Location'],
                'depth': int(latest['EarthquakeInfo']['FocalDepth']),
                'intensity': latest.get('Intensity', {}).get('ShakingArea', [{}])[0].get('AreaIntensity', 'N/A')
            }
            
            return result
        
        except Exception as e:
            print(f"Error processing earthquake data: {str(e)}")
            return None
    
    @staticmethod
    def process_uv_index(data: Dict) -> Optional[int]:
        """
        Process UV index data
        
        Args:
            data: API response data
            
        Returns:
            UV index value or None
        """
        try:
            if not data or 'records' not in data:
                return None
            
            locations = data['records']['Station']
            if not locations:
                return None
            
            # Get first available UV index
            uv_value = int(locations[0].get('UVIndex', 0))
            return uv_value
        
        except Exception as e:
            print(f"Error processing UV index: {str(e)}")
            return None
    
    @staticmethod
    def get_weather_icon_name(weather_description: str) -> str:
        """
        Get appropriate icon name based on weather description
        
        Args:
            weather_description: Weather description text
            
        Returns:
            Icon name
        """
        desc = weather_description.lower()
        
        # Check for thunderstorm first (before rain)
        if '雷' in desc or 'thunder' in desc:
            return 'thunderstorm'
        elif '晴' in desc or 'clear' in desc or 'sunny' in desc:
            return 'sunny'
        elif '雨' in desc or 'rain' in desc:
            return 'rainy'
        elif '雪' in desc or 'snow' in desc:
            return 'snowy'
        elif '颱' in desc or 'typhoon' in desc:
            return 'typhoon'
        elif '雲' in desc or 'cloud' in desc or 'overcast' in desc:
            return 'cloudy'
        
        return 'sunny'
    
    @staticmethod
    def shift_array(data: List, index: int) -> List:
        """
        Shift array to align with current time index
        
        Args:
            data: Data array to shift
            index: Current time index
            
        Returns:
            Shifted array
        """
        start = 8 - index
        end = start + 8
        return data[start:end] + data[:start] + data[end:]
    
    @staticmethod
    def calculate_time_index(hour: int) -> int:
        """
        Calculate display column index based on hour
        
        Args:
            hour: Hour of day (0-23)
            
        Returns:
            Column index (0-7)
        """
        if hour in [1, 2, 3]:
            return 0
        elif hour in [4, 5, 6]:
            return 1
        elif hour in [7, 8, 9]:
            return 2
        elif hour in [10, 11, 12]:
            return 3
        elif hour in [13, 14, 15]:
            return 4
        elif hour in [16, 17, 18]:
            return 5
        elif hour in [19, 20, 21]:
            return 6
        elif hour in [22, 23, 0]:
            return 7
        else:
            return 0
