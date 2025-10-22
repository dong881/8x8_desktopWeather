#!/usr/bin/env python3

import requests
import urllib3
from datetime import datetime, timedelta

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Read the authorization token from config.py
import sys
sys.path.append('/workspace')
from config import WeatherAPI

Authorization = WeatherAPI['Authorization'].strip()

def debug_weather_api():
    # Get current time
    TODAY_Date = datetime.now()
    today = TODAY_Date.strftime('%Y-%m-%d')
    tomorrow = (TODAY_Date + timedelta(days=1)).strftime('%Y-%m-%d')
    NowTime = ("0" if(TODAY_Date.hour<10) else "" )+ str(TODAY_Date.hour)
    
    print(f"Debugging weather API for {today} to {tomorrow} at {NowTime}:00")
    print("=" * 60)
    
    # Test temperature API
    url_temp = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-061?Authorization={Authorization}&limit=8&LocationName=%E5%A4%A7%E5%AE%89%E5%8D%80&elementName=T&timeFrom={today}T{NowTime}%3A00%3A00&timeTo={tomorrow}T{NowTime}%3A00%3A00'
    print("Temperature URL:", url_temp)
    
    try:
        response_temp = requests.get(url_temp, verify=False, timeout=10)
        data_temp = response_temp.json()
        print("\nTemperature API Response:")
        print("Status:", response_temp.status_code)
        print("Full response:", data_temp)
        
        if "records" in data_temp and "Locations" in data_temp["records"]:
            T_data = data_temp["records"]["Locations"][0]["Location"][0]["WeatherElement"][0]["Time"]
            print("\nTemperature data structure:")
            for i, item in enumerate(T_data):
                print(f"  Item {i}: {item}")
                if 'ElementValue' in item:
                    print(f"    ElementValue: {item['ElementValue']}")
            
            TDataList = [list(d['ElementValue'][0].values())[0] for d in T_data]
            print(f"\nExtracted temperature values: {TDataList}")
        else:
            print("No temperature data found in response")
            
    except Exception as e:
        print(f"Temperature API error: {e}")
    
    print("\n" + "=" * 60)
    
    # Test precipitation API
    url_pop = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-091?Authorization={Authorization}&limit=8&LocationName=%E5%A4%A7%E5%AE%89%E5%8D%80&elementName=PoP6h&timeFrom={today}T{NowTime}%3A00%3A00&timeTo={tomorrow}T{NowTime}%3A00%3A00'
    print("Precipitation URL:", url_pop)
    
    try:
        response_pop = requests.get(url_pop, verify=False, timeout=10)
        data_pop = response_pop.json()
        print("\nPrecipitation API Response:")
        print("Status:", response_pop.status_code)
        print("Full response:", data_pop)
        
        if "records" in data_pop and "Locations" in data_pop["records"]:
            PoPdata = data_pop["records"]["Locations"][0]["Location"][0]["WeatherElement"][0]["Time"]
            print("\nPrecipitation data structure:")
            for i, item in enumerate(PoPdata):
                print(f"  Item {i}: {item}")
                if 'ElementValue' in item:
                    print(f"    ElementValue: {item['ElementValue']}")
            
            PopDataList = [list(d['ElementValue'][0].values())[0] for d in PoPdata]
            print(f"\nExtracted precipitation values: {PopDataList}")
        else:
            print("No precipitation data found in response")
            
    except Exception as e:
        print(f"Precipitation API error: {e}")

if __name__ == "__main__":
    debug_weather_api()