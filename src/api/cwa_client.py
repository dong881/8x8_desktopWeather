"""
Central Weather Administration (CWA) API Client
Handles all interactions with CWA OpenData API endpoints
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CWAClient:
    """Client for CWA OpenData API with multiple endpoint support"""
    
    BASE_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"
    CACHE_DIR = "data/cache"
    
    def __init__(self, authorization: str):
        """
        Initialize CWA API client
        
        Args:
            authorization: CWA API authorization token
        """
        self.authorization = authorization
        self.session = requests.Session()
        self._ensure_cache_dir()
        
    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        if not os.path.exists(self.CACHE_DIR):
            os.makedirs(self.CACHE_DIR, exist_ok=True)
    
    def _make_request(self, endpoint: str, params: Dict[str, Any], 
                      cache_file: Optional[str] = None,
                      cache_duration: int = 600) -> Optional[Dict]:
        """
        Make API request with caching support
        
        Args:
            endpoint: API endpoint (e.g., 'F-D0047-061')
            params: Query parameters
            cache_file: Cache file name
            cache_duration: Cache duration in seconds
            
        Returns:
            API response data or None on error
        """
        # Add authorization to params
        params['Authorization'] = self.authorization
        
        # Check cache first
        if cache_file:
            cache_path = os.path.join(self.CACHE_DIR, cache_file)
            if os.path.exists(cache_path):
                cache_age = datetime.now().timestamp() - os.path.getmtime(cache_path)
                if cache_age < cache_duration:
                    try:
                        with open(cache_path, 'r', encoding='utf-8') as f:
                            return json.load(f)
                    except Exception:
                        pass
        
        # Make API request
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = self.session.get(url, params=params, verify=False, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Cache response
            if cache_file:
                cache_path = os.path.join(self.CACHE_DIR, cache_file)
                try:
                    with open(cache_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                except Exception:
                    pass
            
            return data
        except Exception as e:
            print(f"API request error for {endpoint}: {str(e)}")
            
            # Try to load from cache as fallback
            if cache_file:
                cache_path = os.path.join(self.CACHE_DIR, cache_file)
                if os.path.exists(cache_path):
                    try:
                        with open(cache_path, 'r', encoding='utf-8') as f:
                            print(f"Using cached data from {cache_file}")
                            return json.load(f)
                    except Exception:
                        pass
            
            return None
    
    def get_weather_forecast(self, location: str = "大安區", 
                           element_name: str = "T,PoP6h") -> Optional[Dict]:
        """
        Get weather forecast for specified location
        
        Args:
            location: Location name (default: 大安區)
            element_name: Weather elements to fetch (T=Temperature, PoP6h=Precipitation)
            
        Returns:
            Weather forecast data or None
        """
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        tomorrow = (now + timedelta(days=1)).strftime('%Y-%m-%d')
        hour = f"{now.hour:02d}"
        
        params = {
            'limit': 8,
            'LocationName': location,
            'elementName': element_name,
            'timeFrom': f'{today}T{hour}:00:00',
            'timeTo': f'{tomorrow}T{hour}:00:00'
        }
        
        return self._make_request(
            'F-D0047-061',
            params,
            cache_file='weather_forecast.json',
            cache_duration=1800  # 30 minutes
        )
    
    def get_observation_data(self, station_id: str = "466920") -> Optional[Dict]:
        """
        Get real-time observation data from automatic weather station
        
        Args:
            station_id: Weather station ID (default: Taipei 466920)
            
        Returns:
            Observation data or None
        """
        print(f"Requesting observation data for station: {station_id}")
        params = {'stationId': station_id}
        
        data = self._make_request(
            'O-A0001-001',
            params,
            cache_file='observation.json',
            cache_duration=600  # 10 minutes
        )
        
        if data:
            print(f"Observation data received successfully")
            # Log basic structure to help debug
            if 'records' in data:
                print(f"  - Has 'records' key")
                if 'Station' in data['records']:
                    stations = data['records']['Station']
                    print(f"  - Found {len(stations)} station(s)")
                    if stations:
                        station = stations[0]
                        print(f"  - Station keys: {list(station.keys())[:10]}")
                else:
                    print(f"  - No 'Station' key in records")
            else:
                print(f"  - No 'records' key in response")
        else:
            print(f"Failed to get observation data for station {station_id}")
        
        return data
    
    def get_earthquake_report(self) -> Optional[Dict]:
        """
        Get recent significant earthquake reports
        
        Returns:
            Earthquake report data or None
        """
        return self._make_request(
            'E-A0015-001',
            {},
            cache_file='earthquake.json',
            cache_duration=300  # 5 minutes
        )
    
    def get_weather_alerts(self) -> Optional[Dict]:
        """
        Get active weather alerts (typhoon, heavy rain, etc.)
        
        Returns:
            Weather alerts data or None
        """
        return self._make_request(
            'W-C0033-001',
            {},
            cache_file='alerts.json',
            cache_duration=600  # 10 minutes
        )
    
    def get_uv_index(self) -> Optional[Dict]:
        """
        Get UV index observation data
        
        Returns:
            UV index data or None
        """
        return self._make_request(
            'O-A0005-001',
            {},
            cache_file='uv_index.json',
            cache_duration=3600  # 1 hour
        )
    
    def check_recent_earthquake(self, time_threshold: int = 600) -> Optional[Dict]:
        """
        Check if there's a recent earthquake (within time_threshold seconds)
        
        Args:
            time_threshold: Time threshold in seconds (default: 10 minutes)
            
        Returns:
            Recent earthquake data or None
        """
        data = self.get_earthquake_report()
        if not data or 'records' not in data:
            return None
        
        try:
            earthquakes = data['records']['Earthquake']
            if not earthquakes:
                return None
            
            # Get most recent earthquake
            latest = earthquakes[0]
            
            # Try to get time from OriginTime first, then fall back to EarthquakeNo
            eq_time = None
            origin_time = latest.get('EarthquakeInfo', {}).get('OriginTime')
            
            if origin_time:
                # Parse OriginTime (format: "2025/10/20 00:32:45" or "2025-10-20T00:32:45")
                cleaned = str(origin_time).replace('/', '-')
                for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S'):
                    try:
                        eq_time = datetime.strptime(cleaned, fmt)
                        break
                    except ValueError:
                        continue
            
            if eq_time is None:
                # Fall back to EarthquakeNo (format: YYYYMMDDHHMMSS)
                eq_no = latest.get('EarthquakeNo')
                if eq_no is not None:
                    try:
                        eq_time = datetime.strptime(str(eq_no), '%Y%m%d%H%M%S')
                    except ValueError:
                        pass
            
            if eq_time is None:
                print("Warning: Could not parse earthquake time")
                return None
            
            # Check if within threshold
            time_diff = (datetime.now() - eq_time).total_seconds()
            if time_diff <= time_threshold:
                return latest
        except Exception as e:
            print(f"Error checking earthquake data: {str(e)}")
        
        return None


class EPAClient:
    """Client for Environmental Protection Administration Air Quality API"""
    
    BASE_URL = "https://data.moenv.gov.tw/api/v2"
    
    def __init__(self):
        """Initialize EPA API client"""
        self.session = requests.Session()
        self.cache_dir = "data/cache"
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_air_quality(self, location: str = "大安") -> Optional[Dict]:
        """
        Get air quality data for specified location
        
        Args:
            location: Location name (default: 大安)
            
        Returns:
            Air quality data or None
        """
        cache_file = os.path.join(self.cache_dir, 'air_quality.json')
        
        # Check cache
        if os.path.exists(cache_file):
            cache_age = datetime.now().timestamp() - os.path.getmtime(cache_file)
            if cache_age < 1800:  # 30 minutes
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Filter by location if data exists
                        if 'records' in data:
                            for record in data['records']:
                                if location in record.get('sitename', ''):
                                    return record
                        return data
                except Exception:
                    pass
        
        # Note: EPA API requires API key, using cache-only mode
        # Users should configure EPA API separately if needed
        return None
