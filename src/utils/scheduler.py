"""
Content Scheduler
Manages data updates and display content rotation
"""

import time
import threading
from typing import Callable, Optional
from datetime import datetime


class ContentScheduler:
    """Schedules data updates and content rotation"""
    
    def __init__(self, cwa_client, display_manager):
        """
        Initialize scheduler
        
        Args:
            cwa_client: CWA API client instance
            display_manager: Display manager instance
        """
        self.cwa_client = cwa_client
        self.display_manager = display_manager
        self.running = False
        self.update_threads = []
        
        # Update intervals (seconds)
        self.weather_update_interval = 1800  # 30 minutes
        self.earthquake_check_interval = 300  # 5 minutes
        self.observation_update_interval = 600  # 10 minutes
        
        # Last update timestamps
        self.last_weather_update = 0
        self.last_earthquake_check = 0
        self.last_observation_update = 0
        
        # Callbacks for data updates
        self.on_weather_update: Optional[Callable] = None
        self.on_earthquake_detected: Optional[Callable] = None
        self.on_observation_update: Optional[Callable] = None
    
    def start(self):
        """Start the scheduler"""
        self.running = True
        
        # Start background threads for different update tasks
        self.update_threads = [
            threading.Thread(target=self._weather_update_loop, daemon=True),
            threading.Thread(target=self._earthquake_check_loop, daemon=True),
            threading.Thread(target=self._observation_update_loop, daemon=True),
        ]
        
        for thread in self.update_threads:
            thread.start()
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        
        # Wait for threads to finish
        for thread in self.update_threads:
            if thread.is_alive():
                thread.join(timeout=2)
    
    def _weather_update_loop(self):
        """Background loop for weather forecast updates"""
        while self.running:
            current_time = time.time()
            
            if current_time - self.last_weather_update >= self.weather_update_interval:
                try:
                    data = self.cwa_client.get_weather_forecast()
                    if data and self.on_weather_update:
                        self.on_weather_update(data)
                    self.last_weather_update = current_time
                except Exception as e:
                    print(f"Weather update error: {str(e)}")
            
            time.sleep(60)  # Check every minute
    
    def _earthquake_check_loop(self):
        """Background loop for earthquake monitoring"""
        while self.running:
            current_time = time.time()
            
            if current_time - self.last_earthquake_check >= self.earthquake_check_interval:
                try:
                    # Check for recent earthquakes (within 10 minutes)
                    eq_data = self.cwa_client.check_recent_earthquake(time_threshold=600)
                    
                    if eq_data and self.on_earthquake_detected:
                        # Trigger earthquake alert
                        self.on_earthquake_detected(eq_data)
                    
                    self.last_earthquake_check = current_time
                except Exception as e:
                    print(f"Earthquake check error: {str(e)}")
            
            time.sleep(60)  # Check every minute
    
    def _observation_update_loop(self):
        """Background loop for observation data updates"""
        while self.running:
            current_time = time.time()
            
            if current_time - self.last_observation_update >= self.observation_update_interval:
                try:
                    data = self.cwa_client.get_observation_data()
                    if data and self.on_observation_update:
                        self.on_observation_update(data)
                    self.last_observation_update = current_time
                except Exception as e:
                    print(f"Observation update error: {str(e)}")
            
            time.sleep(60)  # Check every minute
    
    def force_weather_update(self):
        """Force immediate weather update"""
        try:
            data = self.cwa_client.get_weather_forecast()
            if data and self.on_weather_update:
                self.on_weather_update(data)
            self.last_weather_update = time.time()
            return True
        except Exception as e:
            print(f"Force weather update error: {str(e)}")
            return False
    
    def force_earthquake_check(self):
        """Force immediate earthquake check"""
        try:
            eq_data = self.cwa_client.check_recent_earthquake(time_threshold=600)
            if eq_data and self.on_earthquake_detected:
                self.on_earthquake_detected(eq_data)
            self.last_earthquake_check = time.time()
            return True
        except Exception as e:
            print(f"Force earthquake check error: {str(e)}")
            return False
