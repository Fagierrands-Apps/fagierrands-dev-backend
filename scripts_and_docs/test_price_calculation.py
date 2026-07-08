#!/usr/bin/env python
"""
Test script for the price calculation endpoint
"""
import requests
import json

# Base URL - adjust if needed
BASE_URL = "http://localhost:8000"

# Test data
test_cases = [
    {
        "name": "Parcel - Short distance (5 km)",
        "data": {
            "pickup_latitude": -1.2921,
            "pickup_longitude": 36.8219,
            "delivery_latitude": -1.2500,
            "delivery_longitude": 36.8500,
            "errand_type": "parcel"
        }
    },
    {
        "name": "Parcel - Long distance (15 km)",
        "data": {
            "pickup_latitude": -1.2921,
            "pickup_longitude": 36.8219,
            "delivery_latitude": -1.1500,
            "delivery_longitude": 36.9500,
            "errand_type": "parcel"
        }
    },
    {
        "name": "Cargo - Short distance (5 km)",
        "data": {
            "pickup_latitude": -1.2921,
            "pickup_longitude": 36.8219,
            "delivery_latitude": -1.2500,
            "delivery_longitude": 36.8500,
            "errand_type": "cargo"
        }
    },
    {
        "name": "Cargo - Long distance (15 km)",
        "data": {
            "pickup_latitude": -1.2921,
            "pickup_longitude": 36.8219,
            "delivery_latitude": -1.1500,
            "delivery_longitude": 36.9500,
            "errand_type": "cargo"
        }
    },
    {
        "name": "Shopping - 3000 KSH worth, 5 km",
        "data": {
            "pickup_latitude": -1.2921,
            "pickup_longitude": 36.8219,
            "delivery_latitude": -1.2500,
            "delivery_longitude": 36.8500,
            "errand_type": "shopping",
            "shopping_value": 3000
        }
    },
    {
        "name": "Shopping - 12000 KSH worth, 10 km",
        "data": {
            "pickup_latitude": -1.2921,
            "pickup_longitude": 36.8219,
            "delivery_latitude": -1.2000,
            "delivery_longitude": 36.9000,
            "errand_type": "shopping",
            "shopping_value": 12000
        }
    }
]

def test_endpoint():
    """Test the price calculation endpoint"""
    print("=" * 80)
    print("Testing Price Calculation Endpoint")
    print("=" * 80)
    print()
    
    # Note: This test assumes you have authentication set up
    # You may need to add authentication headers
    headers = {
        "Content-Type": "application/json"
    }
    
    for test_case in test_cases:
        print(f"\nTest: {test_case['name']}")
        print("-" * 80)
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/orders/calculate-delivery-price/",
                json=test_case['data'],
                headers=headers
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Distance: {result['distance_km']} km")
                print(f"Errand Type: {result['errand_type']}")
                print(f"Price: {result['price']} {result['currency']}")
                print(f"Breakdown: {json.dumps(result['breakdown'], indent=2)}")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Exception: {str(e)}")
        
        print()

if __name__ == "__main__":
    print("\nNOTE: This test requires:")
    print("1. Django server running on localhost:8000")
    print("2. Authentication may be required - update headers if needed")
    print()
    
    try:
        test_endpoint()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nTest failed with error: {str(e)}")
