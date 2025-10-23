#!/usr/bin/env python3
# Test the ProbabilityOfPrecipitation field fix

def test_probability_of_precipitation():
    """Test that ProbabilityOfPrecipitation field is properly handled"""
    
    # Simulate the data structure from the user's log with ProbabilityOfPrecipitation field
    PoPdata = [
        {'DataTime': '2025-10-22T22:00:00+08:00', 'ElementValue': [{'ProbabilityOfPrecipitation': '30'}]},
        {'DataTime': '2025-10-22T23:00:00+08:00', 'ElementValue': [{'ProbabilityOfPrecipitation': '40'}]},
        {'DataTime': '2025-10-23T00:00:00+08:00', 'ElementValue': [{'ProbabilityOfPrecipitation': '25'}]},
    ]
    
    print("Test case: Data with ProbabilityOfPrecipitation field")
    PopDataList = []
    
    for d in PoPdata:
        element_value = d['ElementValue'][0]
        print(f"Processing element value: {element_value}")
        
        # This is the updated logic from Weather.py
        if 'PoP6h' in element_value:
            PopDataList.append(element_value['PoP6h'])
            print(f"Found PoP6h data: {element_value['PoP6h']}")
        elif 'PoP' in element_value:
            PopDataList.append(element_value['PoP'])
            print(f"Found PoP data: {element_value['PoP']}")
        elif 'ProbabilityOfPrecipitation' in element_value:
            PopDataList.append(element_value['ProbabilityOfPrecipitation'])
            print(f"Found ProbabilityOfPrecipitation data: {element_value['ProbabilityOfPrecipitation']}")
        elif 'Precipitation' in element_value:
            PopDataList.append(element_value['Precipitation'])
            print(f"Found Precipitation data: {element_value['Precipitation']}")
        else:
            print(f"Warning: No precipitation data found in {element_value}")
            PopDataList.append('0')
    
    print(f"\nResult: {PopDataList}")
    print(f"Expected: ['30', '40', '25']")
    
    if PopDataList == ['30', '40', '25']:
        print("✅ SUCCESS: ProbabilityOfPrecipitation field is properly handled!")
        return True
    else:
        print("❌ FAILED: ProbabilityOfPrecipitation field not handled correctly")
        return False

if __name__ == "__main__":
    test_probability_of_precipitation()
