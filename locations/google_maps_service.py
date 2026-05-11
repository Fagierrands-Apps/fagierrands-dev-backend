import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class GoogleMapsService:
    """Service for Google Maps API interactions"""
    
    PLACES_AUTOCOMPLETE_URL = "https://places.googleapis.com/v1/places:autocomplete"
    GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"
    
    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        if not self.api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY not configured")
    
    def get_autocomplete(self, text_input, session_token=None):
        """
        Get place autocomplete suggestions
        
        Args:
            text_input: Search query string
            session_token: Optional session token for billing optimization
            
        Returns:
            dict: Autocomplete response with suggestions
        """
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': 'suggestions.placePrediction.placeId,suggestions.placePrediction.text,suggestions.placePrediction.structuredFormat'
        }
        
        payload = {
            'input': text_input,
            'locationBias': {
                'circle': {
                    'center': {
                        'latitude': -1.2921,
                        'longitude': 36.8219
                    },
                    'radius': 50000.0
                }
            },
            'includedRegionCodes': ['KE']
        }
        
        if session_token:
            payload['sessionToken'] = session_token
        
        try:
            response = requests.post(
                self.PLACES_AUTOCOMPLETE_URL,
                json=payload,
                headers=headers,
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Google Places Autocomplete error: {str(e)}")
            raise
    
    def reverse_geocode(self, lat, lng):
        """
        Convert coordinates to human-readable address
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            dict: Geocoding response with formatted address
        """
        params = {
            'latlng': f'{lat},{lng}',
            'key': self.api_key,
            'result_type': 'street_address|route|neighborhood|locality'
        }
        
        try:
            response = requests.get(
                self.GEOCODING_URL,
                params=params,
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Google Geocoding error: {str(e)}")
            raise
