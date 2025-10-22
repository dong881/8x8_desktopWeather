#!/usr/bin/env python3

# Test the precipitation data extraction fix
def test_precipitation_extraction():
    # Simulate the data structure from the user's log
    PoPdata = [
        {'DataTime': '2025-10-22T22:00:00+08:00', 'ElementValue': [{'Temperature': '23'}]},
        {'DataTime': '2025-10-22T23:00:00+08:00', 'ElementValue': [{'Temperature': '23'}]},
    ]
    
    # Test case 1: Data with Temperature field (current broken case)
    print("Test case 1: Data with Temperature field")
    PopDataList = []
    for d in PoPdata:
        element_value = d['ElementValue'][0]
        if 'PoP6h' in element_value:
            PopDataList.append(element_value['PoP6h'])
        elif 'PoP' in element_value:
            PopDataList.append(element_value['PoP'])
        elif 'Precipitation' in element_value:
            PopDataList.append(element_value['Precipitation'])
        else:
            # Fallback: use the first value that's not Temperature
            for key, value in element_value.items():
                if key != 'Temperature':
                    PopDataList.append(value)
                    break
            else:
                # If all else fails, use the first value
                PopDataList.append(list(element_value.values())[0])
    
    print(f"Result: {PopDataList}")
    print(f"Expected: Should not contain temperature values")
    
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
            # Fallback: use the first value that's not Temperature
            for key, value in element_value.items():
                if key != 'Temperature':
                    PopDataList_correct.append(value)
                    break
            else:
                # If all else fails, use the first value
                PopDataList_correct.append(list(element_value.values())[0])
    
    print(f"Result: {PopDataList_correct}")
    print(f"Expected: ['50', '60']")
    
    # Test case 3: Data with PoP field
    PoPdata_pop = [
        {'DataTime': '2025-10-22T22:00:00+08:00', 'ElementValue': [{'PoP': '30'}]},
        {'DataTime': '2025-10-22T23:00:00+08:00', 'ElementValue': [{'PoP': '40'}]},
    ]
    
    print("\nTest case 3: Data with PoP field")
    PopDataList_pop = []
    for d in PoPdata_pop:
        element_value = d['ElementValue'][0]
        if 'PoP6h' in element_value:
            PopDataList_pop.append(element_value['PoP6h'])
        elif 'PoP' in element_value:
            PopDataList_pop.append(element_value['PoP'])
        elif 'Precipitation' in element_value:
            PopDataList_pop.append(element_value['Precipitation'])
        else:
            # Fallback: use the first value that's not Temperature
            for key, value in element_value.items():
                if key != 'Temperature':
                    PopDataList_pop.append(value)
                    break
            else:
                # If all else fails, use the first value
                PopDataList_pop.append(list(element_value.values())[0])
    
    print(f"Result: {PopDataList_pop}")
    print(f"Expected: ['30', '40']")

if __name__ == "__main__":
    test_precipitation_extraction()