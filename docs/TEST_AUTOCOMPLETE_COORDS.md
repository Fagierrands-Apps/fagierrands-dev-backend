# 🧪 Test Autocomplete - Lat/Lng Return

## 🎯 Test Commands

### 1. Get Auth Token First
```bash
# Login to get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"YOUR_USERNAME","password":"YOUR_PASSWORD"}' \
  | jq -r '.access')

echo "Token: $TOKEN"
```

### 2. Test Autocomplete WITH Coordinates (Default)
```bash
curl -X GET "http://localhost:8000/api/locations/autocomplete/?q=Nairobi" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.'
```

**Expected Response:**
```json
{
  "suggestions": [
    {
      "place_id": "ChIJp0lN2HIRLxgRTJKXslQCz4E",
      "description": "Nairobi, Kenya",
      "main_text": "Nairobi",
      "secondary_text": "Kenya",
      "lat": -1.286389,
      "lng": 36.817223,
      "order": 0
    }
  ]
}
```

### 3. Test Autocomplete WITHOUT Coordinates
```bash
curl -X GET "http://localhost:8000/api/locations/autocomplete/?q=Nairobi&include_coords=false" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.'
```

**Expected Response:**
```json
{
  "suggestions": [
    {
      "place_id": "ChIJp0lN2HIRLxgRTJKXslQCz4E",
      "description": "Nairobi, Kenya",
      "main_text": "Nairobi",
      "secondary_text": "Kenya",
      "order": 0
    }
  ]
}
```

---

## 🔍 What to Check

### ✅ GOOD Response (Has Coordinates):
```json
{
  "lat": -1.286389,    ← Present
  "lng": 36.817223     ← Present
}
```

### ❌ BAD Response (Missing Coordinates):
```json
{
  "lat": null,         ← Missing or null
  "lng": null          ← Missing or null
}
```

---

## 🧪 Full Test Scenario

### Test Pickup Location:
```bash
curl -X GET "http://localhost:8000/api/locations/autocomplete/?q=Westlands" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.suggestions[0] | {description, lat, lng}'
```

### Test Delivery Location:
```bash
curl -X GET "http://localhost:8000/api/locations/autocomplete/?q=Karen" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.suggestions[0] | {description, lat, lng}'
```

---

## 🚨 If Coordinates Are NULL

### Possible Causes:

1. **Google Maps API Key Missing**
   ```bash
   echo $GOOGLE_MAPS_API_KEY
   ```
   Should show your API key, not empty.

2. **API Key Not Enabled**
   - Check Google Cloud Console
   - Enable "Places API (New)"
   - Enable "Geocoding API"

3. **Place Details API Failing**
   Check server logs for errors:
   ```
   Failed to fetch coords for ChIJ...
   ```

---

## 🔧 Quick Fix Test

### Check if Google Maps is configured:
```bash
cd /home/fagitone/Documents/GitHub/fagierrands-dev-backend
python manage.py shell
```

```python
from django.conf import settings
print(f"Google Maps API Key: {settings.GOOGLE_MAPS_API_KEY[:10]}..." if settings.GOOGLE_MAPS_API_KEY else "NOT SET")

from locations.google_maps_service import GoogleMapsService
service = GoogleMapsService()
result = service.get_autocomplete("Nairobi")
print(f"Autocomplete working: {len(result.get('suggestions', []))} results")

# Test place details (this fetches lat/lng)
if result.get('suggestions'):
    place_id = result['suggestions'][0]['placePrediction']['placeId']
    details = service.get_place_details(place_id)
    print(f"Coordinates: {details.get('location')}")
```

---

## 📋 Expected Behavior

**For Price Calculation to Work:**
1. ✅ Pickup autocomplete returns `lat` and `lng`
2. ✅ Delivery autocomplete returns `lat` and `lng`
3. ✅ Both coordinates are used in price calculation API

**Endpoint:** `POST /api/orders/calculate-price/`
```json
{
  "pickup_latitude": -1.286389,
  "pickup_longitude": 36.817223,
  "delivery_latitude": -1.292066,
  "delivery_longitude": 36.821945,
  "order_type": 1
}
```

---

## 🎯 One-Line Test

```bash
# Quick test - should show lat/lng
curl -s -X GET "http://localhost:8000/api/locations/autocomplete/?q=Nairobi" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.suggestions[0] | {has_lat: (.lat != null), has_lng: (.lng != null), lat, lng}'
```

**Expected:**
```json
{
  "has_lat": true,
  "has_lng": true,
  "lat": -1.286389,
  "lng": 36.817223
}
```

---

**Run these tests and share the output to diagnose the issue!** 🔍
