#!/usr/bin/env python3

# Test the improved precipitation data extraction fix
def test_improved_precipitation_extraction():
    # Simulate the data structure from the user's log (broken case)
    PoPdata = [
        {'DataTime': '2025-10-22T22:00:00+08:00', 'ElementValue': [{'Temperature': '23'}]},
        {'DataTime': '2025-10-22T23:00:00+08:00', 'ElementValue': [{'Temperature': '23'}]},
    ]
    
    print("Test case 1: Data with only Temperature field (broken API response)")
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
            # This handles the case where API returns temperature data for precipitation
            print(f"Warning: No precipitation data found in {element_value}, using default value 0")
            PopDataList.append('0')
    
    print(f"Result: {PopDataList}")
    print(f"Expected: ['0', '0'] (default values instead of temperature)")
    
    # Test case 2: Data with correct PoP6h field
    PoPdata_correct = [
        {'DataTime': '2025-10-22T22:00:00+08:00', 'ElementValue': [{'PoP6h': '50'}]},
        {'DataTime': '2025-10-22T23:00:00+08:00', 'ElementValue': [{'PoP6h': '60'}]},
    ]
    
    print("\nTest case 2: Data with correct PoP6h field")
    PopDataList_correct = []
    for d in PoPdata_correct:
        element_value = d['ElementValue'][0]
        if 'PoP6h' in element_value:
            PopDataList_correct.append(element_value['PoP6h'])
        elif 'PoP' in element_value:
            PopDataList_correct.append(element_value['PoP'])
        elif 'Precipitation' in element_value:
            PopDataList_correct.append(element_value['Precipitation'])
        else:
            print(f"Warning: No precipitation data found in {element_value}, using default value 0")
            PopDataList_correct.append('0')
    
    print(f"Result: {PopDataList_correct}")
    print(f"Expected: ['50', '60']")

if __name__ == "__main__":
    test_improved_precipitation_extraction()