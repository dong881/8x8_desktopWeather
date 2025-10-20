# CWA OpenData API Updates (2025)

## Overview

The Central Weather Administration (CWA) OpenData API has undergone structure changes in 2025. This document explains the changes and how this project handles them.

## Changes Summary

### 1. Observation Data API (`O-A0001-001`)

#### Old Structure (Before 2025)
```json
{
  "records": {
    "Station": [{
      "ObsTime": {"DateTime": "2025-10-20T23:00:00+08:00"},
      "Temperature": 25.5,
      "RelativeHumidity": 65,
      "Weather": "Partly Cloudy"
    }]
  }
}
```

#### New Structure (2025+)
```json
{
  "records": {
    "Station": [{
      "StationName": "臺北",
      "StationId": "466920",
      "ObsTime": {"DateTime": "2025-10-20T23:00:00+08:00"},
      "GeoInfo": { ... },
      "WeatherElement": {
        "Weather": "陰",
        "AirTemperature": 23.5,
        "RelativeHumidity": 85,
        "AirPressure": 1013.2,
        "WindSpeed": 2.5
      }
    }]
  }
}
```

**Key Changes:**
- Weather data is now nested inside `WeatherElement` object
- `Temperature` renamed to `AirTemperature`
- Added additional fields like `GeoInfo`, station metadata

### 2. Forecast Data API (`F-D0047-061`)

#### Field Name Case Changes

Some API responses may use different field name cases:

**Old Format (Capitalized):**
- `WeatherElement`
- `ElementName`
- `ElementValue`
- `Temperature`
- `Probability`

**New Format (Lowercase):**
- `weatherElement`
- `elementName`
- `elementValue`
- `temperature`
- `probability`

## How This Project Handles Changes

### Backward Compatibility

The data processor now supports both old and new API formats automatically:

```python
# Handles both formats seamlessly
result = DataProcessor.process_observation_data(api_response)
# Works with both old and new structures

result = DataProcessor.process_weather_forecast(api_response)
# Works with both capitalized and lowercase field names
```

### Implementation Details

1. **Observation Data**: Checks for `WeatherElement` nested structure first, falls back to flat structure
2. **Forecast Data**: Supports both field name cases (uppercase and lowercase)
3. **Graceful Degradation**: Returns default/zero values for missing fields rather than crashing

## Testing

Comprehensive test suites verify both old and new formats:

```bash
# Test observation API format handling
python3 test/test_new_api_format.py

# Test forecast API format handling
python3 test/test_forecast_api_format.py

# Test original functionality
python3 test/test_data_processor.py
```

## API Request Format

### Authorization

The API requires an authorization token passed as a query parameter:

```
GET https://opendata.cwa.gov.tw/api/v1/rest/datastore/{dataset_id}?Authorization={your_token}
```

### Getting Your API Token

1. Visit: https://opendata.cwa.gov.tw
2. Register/login to your account
3. Navigate to: https://opendata.cwa.gov.tw/user/authkey
4. Copy your authorization token
5. Add it to `config.py`:

```python
WeatherAPI = {
    'Authorization': 'YOUR_TOKEN_HERE'
}
```

## Common API Endpoints

| Dataset ID | Description | Update Frequency |
|------------|-------------|------------------|
| `F-D0047-061` | Weather Forecast (District) | 3 hours |
| `O-A0001-001` | Automatic Weather Station Data | 10 minutes |
| `E-A0015-001` | Significant Earthquake Report | Real-time |
| `W-C0033-001` | Weather Alerts | Real-time |
| `O-A0005-001` | UV Index | 1 hour |

## Response Format

All API responses follow this general structure:

```json
{
  "success": "true",
  "result": {
    "resource_id": "...",
    "fields": [...]
  },
  "records": {
    // Data structure varies by endpoint
  }
}
```

## Error Handling

The application handles API errors gracefully:

1. **Cache Fallback**: Uses cached data if API request fails
2. **Default Values**: Returns zero/N/A for missing data
3. **Logging**: Logs errors for debugging
4. **Retry Logic**: Built into the scheduler for automatic retries

## Troubleshooting

### Issue: Getting Zero Values for Temperature/Humidity

**Cause**: API structure has changed, old code can't find fields

**Solution**: This update fixes the issue. Ensure you're using the latest version.

### Issue: API Returns 401 Unauthorized

**Cause**: Invalid or missing authorization token

**Solution**: 
1. Verify token in `config.py`
2. Check token is still valid at https://opendata.cwa.gov.tw/user/authkey
3. Regenerate token if necessary

### Issue: API Returns 404 Not Found

**Cause**: Invalid dataset ID or endpoint

**Solution**: Verify dataset IDs at https://opendata.cwa.gov.tw/dist/opendata-swagger.html

## References

- **Official API Documentation**: https://opendata.cwa.gov.tw/dist/opendata-swagger.html
- **API Usage Guide**: https://opendata.cwa.gov.tw/devManual/insrtuction
- **Dataset List**: https://opendata.cwa.gov.tw/devManual/datalist
- **FAQ**: https://opendata.cwa.gov.tw/faq

## Version History

- **2025-10**: Updated to support new API structure with WeatherElement
- **2023**: Initial implementation with original API format

## Related Documentation

- [API_GUIDE.md](API_GUIDE.md) - Complete API integration guide
- [FEATURES.md](FEATURES.md) - Project features overview
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
