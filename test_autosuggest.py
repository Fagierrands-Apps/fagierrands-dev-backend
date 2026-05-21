#!/usr/bin/env python
import os
import django
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrandsbackup.settings')
os.environ['ALLOWED_HOSTS'] = 'localhost,127.0.0.1,testserver'

django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from accounts.models import User
from locations.views import LocationAutocompleteView

def test_autosuggest():
    factory = APIRequestFactory()
    view = LocationAutocompleteView.as_view()
    
    # Get or create a test user
    user = User.objects.filter(is_active=True).first()
    if not user:
        print("Creating test user...")
        user = User.objects.create_user(
            phone_number="+254700000000",
            email="test@example.com",
            password="testpass123"
        )
    
    print(f"Using user: {user.phone_number}")
    
    # Test 1: Basic autocomplete
    print("\n=== Test 1: Basic Autocomplete ===")
    request = factory.get("/api/locations/autocomplete/", {"q": "Nairobi"})
    force_authenticate(request, user=user)
    response = view(request)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.data}")
    
    # Test 2: With coordinates
    print("\n=== Test 2: With Coordinates ===")
    request = factory.get("/api/locations/autocomplete/", {"q": "Westlands", "include_coords": "true"})
    force_authenticate(request, user=user)
    response = view(request)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.data}")
    
    # Test 3: Short query
    print("\n=== Test 3: Short Query ===")
    request = factory.get("/api/locations/autocomplete/", {"q": "N"})
    force_authenticate(request, user=user)
    response = view(request)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.data}")
    
    # Test 4: Missing query
    print("\n=== Test 4: Missing Query ===")
    request = factory.get("/api/locations/autocomplete/")
    force_authenticate(request, user=user)
    response = view(request)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.data}")
    
    # Test 5: Without coordinates
    print("\n=== Test 5: Without Coordinates ===")
    request = factory.get("/api/locations/autocomplete/", {"q": "Karen", "include_coords": "false"})
    force_authenticate(request, user=user)
    response = view(request)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.data}")

if __name__ == "__main__":
    test_autosuggest()
