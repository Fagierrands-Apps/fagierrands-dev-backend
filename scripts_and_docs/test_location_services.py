#!/usr/bin/env python
"""
Quick test script for Google Maps location services
Run: python scripts_and_docs/test_location_services.py
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrandsbackup.settings')
django.setup()

from locations.google_maps_service import GoogleMapsService
import json


def test_autocomplete():
    print("\n" + "="*60)
    print("Testing Location Autocomplete")
    print("="*60)
    
    service = GoogleMapsService()
    
    test_queries = ['westlands', 'karen', 'kilimani', 'cbd']
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        try:
            result = service.get_autocomplete(query)
            suggestions = result.get('suggestions', [])
            print(f"✅ Found {len(suggestions)} suggestions:")
            
            for i, item in enumerate(suggestions[:3], 1):
                pred = item.get('placePrediction', {})
                main = pred.get('structuredFormat', {}).get('mainText', {}).get('text', '')
                secondary = pred.get('structuredFormat', {}).get('secondaryText', {}).get('text', '')
                print(f"   {i}. {main} - {secondary}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def test_reverse_geocode():
    print("\n" + "="*60)
    print("Testing Reverse Geocoding")
    print("="*60)
    
    service = GoogleMapsService()
    
    test_locations = [
        (-1.2921, 36.8219, "Nairobi CBD"),
        (-1.3032, 36.7073, "Karen"),
        (-1.2630, 36.8063, "Westlands"),
    ]
    
    for lat, lng, name in test_locations:
        print(f"\n📍 Location: {name} ({lat}, {lng})")
        try:
            result = service.reverse_geocode(lat, lng)
            
            if result.get('status') == 'OK':
                address = result['results'][0]['formatted_address']
                print(f"✅ Address: {address}")
            else:
                print(f"❌ Status: {result.get('status')}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def test_api_key():
    print("\n" + "="*60)
    print("Checking API Key Configuration")
    print("="*60)
    
    from django.conf import settings
    
    if settings.GOOGLE_MAPS_API_KEY:
        print(f"✅ API Key configured: {settings.GOOGLE_MAPS_API_KEY[:20]}...")
        print(f"✅ Location bias: Nairobi ({settings.GOOGLE_MAPS_LOCATION_BIAS['circle']['center']})")
        print(f"✅ Region code: {settings.GOOGLE_MAPS_REGION_CODE}")
    else:
        print("❌ API Key not configured!")


if __name__ == '__main__':
    print("\n🚀 Google Maps Location Services Test")
    print("="*60)
    
    test_api_key()
    test_autocomplete()
    test_reverse_geocode()
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60 + "\n")
