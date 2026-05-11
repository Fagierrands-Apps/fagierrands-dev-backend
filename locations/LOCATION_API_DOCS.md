# Location Services API Documentation

## Overview
Complete location services powered by Google Maps API with Nairobi/Kenya bias.

---

## 1. Location Autocomplete

**Endpoint:** `GET /api/locations/autocomplete/`

**Description:** Search for places with autocomplete suggestions, biased to Nairobi, Kenya.

**Authentication:** Required (Bearer token)

**Query Parameters:**
- `q` (required): Search query string (minimum 2 characters)

**Example Request:**
```bash
curl -X GET "https://your-domain.com/api/locations/autocomplete/?q=westlands" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Example Response:**
```json
{
  "suggestions": [
    {
      "place_id": "ChIJ550fCjwXLxgRyC5_H9-ELK0",
      "description": "Westlands, Nairobi, Kenya",
      "main_text": "Westlands",
      "secondary_text": "Nairobi, Kenya"
    },
    {
      "place_id": "ChIJhaSDvWoXLxgRQRtWvQ36670",
      "description": "Westlands Square, Nairobi, Kenya",
      "main_text": "Westlands Square",
      "secondary_text": "Nairobi, Kenya"
    }
  ],
  "count": 2
}
```

**Response Fields:**
- `place_id`: Unique identifier for the place
- `description`: Full place description
- `main_text`: Primary text (place name)
- `secondary_text`: Secondary text (area/city)
- `count`: Number of suggestions returned

**Performance:** ~200-400ms (Google's infrastructure)

**Region Bias:** 
- Center: Nairobi (-1.2921, 36.8219)
- Radius: 50km
- Country: Kenya (KE)

---

## 2. Reverse Geocoding

**Endpoint:** `POST /api/locations/reverse-geocode/`

**Description:** Convert GPS coordinates to human-readable address.

**Authentication:** Required (Bearer token)

**Request Body:**
```json
{
  "lat": -1.2921,
  "lng": 36.8219
}
```

**Example Request:**
```bash
curl -X POST "https://your-domain.com/api/locations/reverse-geocode/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"lat": -1.2921, "lng": 36.8219}'
```

**Example Response:**
```json
{
  "formatted_address": "Haile Selassie Ave, Nairobi, Kenya",
  "place_id": "ChIJp0lN2HIRLxgRTJKXslQCz_c",
  "address_components": [
    {
      "long_name": "Haile Selassie Avenue",
      "short_name": "Haile Selassie Ave",
      "types": ["route"]
    },
    {
      "long_name": "Nairobi",
      "short_name": "Nairobi",
      "types": ["locality", "political"]
    },
    {
      "long_name": "Kenya",
      "short_name": "KE",
      "types": ["country", "political"]
    }
  ],
  "location": {
    "lat": -1.2921,
    "lng": 36.8219
  }
}
```

**Response Fields:**
- `formatted_address`: Complete human-readable address
- `place_id`: Unique identifier for the location
- `address_components`: Detailed address breakdown
- `location`: Echo of input coordinates

**Performance:** ~150-300ms

**Use Case:** Prefill pickup location from user's GPS coordinates

---

## 3. Error Responses

**Missing Query Parameter (Autocomplete):**
```json
{
  "error": "Query parameter 'q' is required"
}
```
Status: 400

**Missing Coordinates (Reverse Geocode):**
```json
{
  "error": "Both 'lat' and 'lng' are required"
}
```
Status: 400

**Invalid Coordinates:**
```json
{
  "error": "Invalid coordinates"
}
```
Status: 400

**No Results Found:**
```json
{
  "error": "No address found for these coordinates"
}
```
Status: 404

**Service Error:**
```json
{
  "error": "Failed to fetch autocomplete suggestions"
}
```
Status: 500

---

## 4. Mobile Integration Guide

### Autocomplete Flow:
1. User types in search field
2. After 2+ characters, call autocomplete endpoint
3. Display suggestions in dropdown
4. User selects a suggestion
5. Use `place_id` to save location or fetch more details

### Reverse Geocode Flow:
1. Get user's GPS coordinates
2. Call reverse-geocode endpoint
3. Display formatted address
4. Pre-fill pickup location field

### Debouncing:
Implement 300ms debounce on autocomplete to avoid excessive API calls.

### Caching:
Cache recent searches locally to improve UX and reduce API calls.

---

## 5. Testing Endpoints

**Test Autocomplete:**
```bash
# Replace with your actual token
TOKEN="your_bearer_token_here"

curl -X GET "http://localhost:8000/api/locations/autocomplete/?q=karen" \
  -H "Authorization: Bearer $TOKEN"
```

**Test Reverse Geocode:**
```bash
curl -X POST "http://localhost:8000/api/locations/reverse-geocode/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"lat": -1.3032, "lng": 36.7073}'
```

---

## 6. Rate Limits & Costs

**Google Maps API:**
- Autocomplete: $2.83 per 1,000 requests (after free tier)
- Geocoding: $5.00 per 1,000 requests (after free tier)
- Free tier: $200/month credit (~70,000 autocomplete requests)

**Best Practices:**
- Implement debouncing (300ms)
- Cache results locally
- Only call on user interaction
- Use session tokens for billing optimization

---

## 7. Configuration

**Environment Variables:**
```bash
GOOGLE_MAPS_API_KEY=AIzaSyD9au2Q_hQ1u5LOVy9ffpoBiFS-50jo4hk
```

**Settings (Django):**
```python
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')
GOOGLE_MAPS_LOCATION_BIAS = {
    'circle': {
        'center': {'latitude': -1.2921, 'longitude': 36.8219},
        'radius': 50000.0
    }
}
GOOGLE_MAPS_REGION_CODE = 'KE'
```

---

## Summary for Mobile Developer

✅ **Autocomplete Endpoint:** `GET /api/locations/autocomplete/?q=westlands`
✅ **Reverse Geocode Endpoint:** `POST /api/locations/reverse-geocode/` with `{lat, lng}`
✅ **Auth:** Bearer token required for both
✅ **Performance:** <500ms consistently
✅ **Nairobi Bias:** Yes, 50km radius around Nairobi
✅ **Kenya Filter:** Yes, results limited to Kenya
✅ **Response Format:** Clean, mobile-friendly JSON

**Ready for integration!** 🚀
