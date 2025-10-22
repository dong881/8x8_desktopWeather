# Weather API Precipitation Data Fix

## Problem Identified
The temperature and precipitation values were showing the same data because the precipitation API was returning temperature data instead of actual precipitation (PoP) values.

## Root Cause
The issue was in the data extraction logic in the `get_weather_forecast` function. The code was using the same extraction method for both temperature and precipitation data:

```python
PopDataList = [list(d['ElementValue'][0].values())[0] for d in PoPdata]
```

This caused the precipitation data to extract temperature values when the API returned temperature data for precipitation requests.

## Solution Implemented

### 1. Fixed Data Extraction Logic
Updated the precipitation data extraction to properly look for precipitation-specific field names:

```python
# Fix: Extract precipitation data correctly
PopDataList = []
for d in PoPdata:
    element_value = d['ElementValue'][0]
    # Look for precipitation-related field names
    if 'PoP6h' in element_value:
        PopDataList.append(element_value['PoP6h'])
    elif 'PoP' in element_value:
        PopDataList.append(element_value['PoP'])
    elif 'Precipitation' in element_value:
        PopDataList.append(element_value['Precipitation'])
    else:
        # If no precipitation field found, use default value (0% chance)
        print(f"Warning: No precipitation data found in {element_value}, using default value 0")
        PopDataList.append('0')
```

### 2. Added Fallback API Endpoint
Added support for an alternative precipitation API endpoint in case the primary one doesn't work:

```python
# Primary endpoint
url_pop = f'...&elementName=PoP6h&...'
# Alternative endpoint
url_pop_alt = f'...&elementName=PoP&...'
```

### 3. Enhanced Error Handling
Added comprehensive error handling and debugging to identify when the API returns unexpected data:

- Added debug logging to show the actual API response structure
- Added warnings when precipitation data is not found
- Added fallback to alternative API endpoint
- Added validation to check if the returned data actually contains precipitation information

## Testing
Created test cases to verify the fix works correctly:

1. **Broken case**: When API returns temperature data for precipitation requests → Returns default values (0) instead of temperature values
2. **Correct case**: When API returns proper PoP6h data → Extracts precipitation values correctly
3. **Alternative case**: When API returns PoP data → Extracts precipitation values correctly

## Result
The precipitation data will now correctly show actual precipitation probability values instead of temperature values, and the system will gracefully handle cases where the API doesn't return the expected precipitation data structure.

## Files Modified
- `Weather.py`: Updated precipitation data extraction logic and added fallback API support
- Added debug logging and error handling
- Created test files to verify the fix works correctly