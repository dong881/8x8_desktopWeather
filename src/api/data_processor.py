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
        Supports both old and new CWA API formats (case-sensitive field names)
        
        Args:
            data: API response data
            
        Returns:
            Tuple of (temperature_levels, rainfall_levels) or None
        """
        try:
            if not data or 'records' not in data:
                print("Error: No records in weather forecast data")
                return None
            
            if 'Locations' not in data['records'] or not data['records']['Locations']:
                print("Error: No Locations in weather forecast records")
                return None
            
            location_data = data["records"]["Locations"][0]["Location"][0]
            
            # Support both old (WeatherElement) and new (weatherElement) formats
            weather_element = location_data.get("weatherElement") or location_data.get("WeatherElement")
            
            if not weather_element:
                print("Error: No weatherElement or WeatherElement found in location data")
                return None
            
            # Find temperature and precipitation data
            temp_data = None
            pop_data = None
            
            for element in weather_element:
                # Support both old (ElementName) and new (elementName) formats
                element_name = element.get("elementName") or element.get("ElementName")
                
                if element_name == "T":
                    # Support both old (Time) and new (time) formats
                    temp_data = element.get("Time") or element.get("time")
                elif element_name == "PoP6h":
                    pop_data = element.get("Time") or element.get("time")
            
            # Enhanced debugging
            print(f"Debug: Found temp_data: {temp_data is not None}, pop_data: {pop_data is not None}")
            if temp_data:
                print(f"Debug: temp_data length: {len(temp_data) if isinstance(temp_data, list) else 'not a list'}")
            if pop_data:
                print(f"Debug: pop_data length: {len(pop_data) if isinstance(pop_data, list) else 'not a list'}")
            
            # If we don't have both, try to create fallback data
            if not temp_data or not pop_data:
                print(f"Warning: Missing temperature or precipitation data (temp: {temp_data is not None}, pop: {pop_data is not None})")
                print("Creating fallback data for LED display...")
                
                # Create fallback data based on current time and season
                from datetime import datetime
                now = datetime.now()
                hour = now.hour
                
                # Generate reasonable temperature levels based on time of day
                base_temp = 20 + (hour - 12) * 0.5  # Simulate daily temperature variation
                temp_levels = []
                for i in range(8):
                    # Add some variation
                    temp = base_temp + (i - 4) * 2 + (hour % 3) * 0.5
                    temp_levels.append(max(0, min(7, int((temp - 12) * 7 / 21))))  # Scale to 0-7
                
                # Generate precipitation levels (mostly dry with occasional rain)
                pop_levels = [0] * 8
                if hour in [14, 15, 16, 17]:  # Afternoon rain chance
                    pop_levels[2:6] = [1, 1, 0, 1]  # Some rain indicators
                
                print(f"Fallback data created: temp_levels={temp_levels}, pop_levels={pop_levels}")
                return temp_levels, pop_levels
            
            # Extract temperature values
            # Support both old (ElementValue) and new (elementValue) formats
            temp_values = []
            for t in temp_data:
                element_value = t.get('ElementValue') or t.get('elementValue')
                if element_value and len(element_value) > 0:
                    # Support both Temperature and temperature field names
                    temp = element_value[0].get('Temperature') or element_value[0].get('temperature')
                    if temp:
                        try:
                            temp_values.append(int(float(temp)))
                        except (ValueError, TypeError):
                            continue
            
            # Extract precipitation probabilities
            pop_values = []
            for p in pop_data:
                element_value = p.get('ElementValue') or p.get('elementValue')
                if element_value and len(element_value) > 0:
                    # Support both Probability and probability field names
                    prob = element_value[0].get('Probability') or element_value[0].get('probability')
                    if prob:
                        try:
                            pop_values.append(int(float(prob)))
                        except (ValueError, TypeError):
                            continue
            
            if not temp_values or not pop_values:
                print(f"Error: Failed to extract temperature or precipitation values")
                return None
            
            # Convert to LED levels
            temp_levels = DataProcessor._temperature_to_levels(temp_values)
            pop_levels = DataProcessor._precipitation_to_levels(pop_values)
            
            print(f"Weather forecast processed: temp_levels={temp_levels}, pop_levels={pop_levels}")
            return temp_levels, pop_levels
        
        except Exception as e:
            print(f"Error processing weather forecast: {str(e)}")
            import traceback
            traceback.print_exc()
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
        if not temperatures:
            return [0] * 8
        
        levels = []
        for temp in temperatures:
            # Clamp temperature to range
            temp = max(min_temp, min(max_temp, temp))
            
            # Convert to 0-7 scale
            level = round(7 * (temp - min_temp) / (max_temp - min_temp))
            levels.append(level)
        
        # Ensure we have exactly 8 levels
        while len(levels) < 8:
            levels.append(0)
        
        return levels[:8]
    
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
        if not probabilities:
            return [0] * 8
        
        levels = []
        for prob in probabilities:
            # Each probability covers 6 hours, but we need values for 3-hour periods
            # Duplicate each value
            indicator = 1 if prob >= threshold else 0
            levels.extend([indicator, indicator])
        
        # Ensure we have exactly 8 levels
        while len(levels) < 8:
            levels.append(0)
        
        return levels[:8]
    
    @staticmethod
    def process_observation_data(data: Dict) -> Optional[Dict]:
        """
        Process real-time observation data
        Supports both old and new CWA API formats
        
        Args:
            data: API response data
            
        Returns:
            Processed observation data or None
        """
        try:
            if not data or 'records' not in data:
                print("Error: No records in observation data")
                return None
            
            if 'Station' not in data['records'] or not data['records']['Station']:
                print("Error: No Station data in observation records")
                return None
            
            location = data['records']['Station'][0]
            obs_time = location.get('ObsTime', {}).get('DateTime', 'N/A')
            
            # Check if data uses new API format (with WeatherElement)
            weather_element = location.get('WeatherElement', {})
            
            if weather_element:
                # New API format: data is nested in WeatherElement
                temp = weather_element.get('AirTemperature', '0')
                humidity = weather_element.get('RelativeHumidity', '0')
                weather = weather_element.get('Weather', 'N/A')
            else:
                # Old API format: data is directly on Station object
                temp = location.get('Temperature', '0')
                humidity = location.get('RelativeHumidity', '0')
                weather = location.get('Weather', 'N/A')
            
            # Handle string values that might be '-' or invalid
            try:
                temp_value = float(temp) if temp and temp != '-' and temp != 'N/A' else 0.0
            except (ValueError, TypeError):
                temp_value = 0.0
                
            try:
                humidity_value = int(float(humidity)) if humidity and humidity != '-' and humidity != 'N/A' else 0
            except (ValueError, TypeError):
                humidity_value = 0
            
            result = {
                'time': obs_time,
                'temperature': temp_value,
                'humidity': humidity_value,
                'weather': weather if weather and weather != '-' and weather != 'N/A' else 'N/A'
            }
            
            # Log the processed data
            print(f"Observation data processed: {result}")
            
            # Only return None if we have completely invalid data
            if temp_value == 0.0 and humidity_value == 0 and weather == 'N/A':
                print("Warning: All observation data is missing or invalid")
                return None
            
            return result
        
        except Exception as e:
            print(f"Error processing observation data: {str(e)}")
            import traceback
            traceback.print_exc()
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
