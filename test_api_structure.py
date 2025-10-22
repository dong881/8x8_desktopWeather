#!/usr/bin/env python3

import requests
import urllib3
from datetime import datetime, timedelta
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_api_structure():
    """Test API structure and show how to get correct precipitation data"""
    
    print("=" * 80)
    print("🌤️  CWA Weather API Structure Test")
    print("=" * 80)
    
    # Get current time
    TODAY_Date = datetime.now()
    today = TODAY_Date.strftime('%Y-%m-%d')
    tomorrow = (TODAY_Date + timedelta(days=1)).strftime('%Y-%m-%d')
    NowTime = ("0" if(TODAY_Date.hour<10) else "" )+ str(TODAY_Date.hour)
    
    print(f"Testing API for {today} to {tomorrow} at {NowTime}:00")
    print("=" * 80)
    
    # Test different API endpoints for precipitation data
    api_endpoints = [
        {
            'name': 'F-D0047-061 (Temperature API)',
            'url': f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-061?Authorization=YOUR_TOKEN&limit=8&LocationName=%E5%A4%A7%E5%AE%89%E5%8D%80&elementName=T&timeFrom={today}T{NowTime}%3A00%3A00&timeTo={tomorrow}T{NowTime}%3A00%3A00',
            'description': 'Used for temperature data'
        },
        {
            'name': 'F-D0047-091 (Township Forecast)',
            'url': f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-091?Authorization=YOUR_TOKEN&limit=8&LocationName=%E5%A4%A7%E5%AE%89%E5%8D%80&elementName=PoP6h&timeFrom={today}T{NowTime}%3A00%3A00&timeTo={tomorrow}T{NowTime}%3A00%3A00',
            'description': 'Should contain precipitation data (PoP6h)'
        },
        {
            'name': 'F-D0047-091 (Alternative PoP)',
            'url': f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-091?Authorization=YOUR_TOKEN&limit=8&LocationName=%E5%A4%A7%E5%AE%89%E5%8D%80&elementName=PoP&timeFrom={today}T{NowTime}%3A00%3A00&timeTo={tomorrow}T{NowTime}%3A00%3A00',
            'description': 'Alternative precipitation data (PoP)'
        }
    ]
    
    print("📋 Available API Endpoints:")
    for i, endpoint in enumerate(api_endpoints, 1):
        print(f"{i}. {endpoint['name']}")
        print(f"   Description: {endpoint['description']}")
        print(f"   URL: {endpoint['url']}")
        print()
    
    print("=" * 80)
    print("🔧 How to Fix the Precipitation Data Issue:")
    print("=" * 80)
    print("1. Get your API token from: https://opendata.cwa.gov.tw/user/authkey")
    print("2. Replace 'YOUR_TOKEN' in the URLs above with your actual token")
    print("3. Test the URLs in a browser or with curl to see the response structure")
    print("4. Update config.py with your token")
    print("5. The code will automatically use the correct API endpoint")
    print()
    print("📊 Expected Data Structure:")
    print("Temperature data should have: {'Temperature': '24'}")
    print("Precipitation data should have: {'PoP6h': '30'} or {'PoP': '30'}")
    print()
    print("⚠️  Current Issue:")
    print("The API is returning temperature data when requesting precipitation data.")
    print("This suggests the API endpoint or element name may be incorrect.")
    print("The fix uses F-D0047-091 API which should contain proper precipitation data.")
    print("=" * 80)

if __name__ == "__main__":
    test_api_structure()