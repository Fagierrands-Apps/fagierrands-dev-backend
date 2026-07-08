# Price Calculation Endpoint - Complete Documentation

## 📋 Overview

This implementation adds a new API endpoint that calculates delivery prices based on distance and errand type. The endpoint accepts coordinates from Google Maps autocomplete and returns the calculated price with a detailed breakdown.

## 🎯 What Problem Does This Solve?

Previously, clients had to create an order to see the price. Now they can:
1. Select pickup and delivery locations from Google Maps
2. Choose an errand type (Parcel, Cargo, or Shopping)
3. **Instantly see the price** before creating an order
4. Handlers receive precise locations because coordinates come from Google Maps

## 📁 Documentation Files

| File | Description |
|------|-------------|
| **IMPLEMENTATION_SUMMARY.md** | Overview of what was implemented |
| **PRICE_CALCULATION_API.md** | Complete API documentation with integration guide |
| **PRICE_API_QUICK_REF.md** | Quick reference for developers |
| **FLOW_DIAGRAM.md** | Visual flow diagrams |
| **API_RESPONSE_EXAMPLES.md** | Example requests and responses |
| **test_price_calculation.py** | Test script |

## 🚀 Quick Start

### For App Developer

1. **Read the documentation** (start with PRICE_CALCULATION_API.md)
2. **Test the endpoint** using the test script or Postman
3. **Integrate in your app** following the examples
4. **Test the complete flow** from location selection to price display

### For Backend Developer

1. **Files created**:
   - `orders/views_price_calculation.py` - Main implementation
   - Documentation files (see above)

2. **Files modified**:
   - `orders/urls.py` - Added new route

3. **No database changes** - Works with existing models

## 🔗 API Endpoint

```
POST /api/orders/calculate-delivery-price/
```

**Authentication**: Required (Bearer token)

## 📊 Pricing Rules

### Parcel Delivery
- **Base**: 200 KSH for first 7.5 km
- **Additional**: 23 KSH per km beyond 7.5 km

### Cargo Delivery
- **Base**: 500 KSH for first 7 km
- **Additional**: 28 KSH per km beyond 7 km

### Shopping Service
- **Service Fee**: 200 KSH for first 5,000 KSH worth + 50 KSH per additional 5,000 KSH
- **Errand Fee**: Same as Parcel (200 KSH + 23 KSH/km)
- **Total**: Service Fee + Errand Fee

## 💡 Example Usage

### JavaScript/React Native
```javascript
async function calculatePrice(pickupCoords, deliveryCoords, errandType) {
  const response = await fetch('https://api.example.com/api/orders/calculate-delivery-price/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      pickup_latitude: pickupCoords.lat,
      pickup_longitude: pickupCoords.lng,
      delivery_latitude: deliveryCoords.lat,
      delivery_longitude: deliveryCoords.lng,
      errand_type: errandType
    })
  });
  
  return await response.json();
}
```

### Python
```python
import requests

response = requests.post(
    'http://localhost:8000/api/orders/calculate-delivery-price/',
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    },
    json={
        'pickup_latitude': -1.2921,
        'pickup_longitude': 36.8219,
        'delivery_latitude': -1.2500,
        'delivery_longitude': 36.8500,
        'errand_type': 'parcel'
    }
)

result = response.json()
print(f"Price: {result['price']} {result['currency']}")
```

## 🧪 Testing

### Run Test Script
```bash
python test_price_calculation.py
```

### Manual Testing with cURL
```bash
curl -X POST http://localhost:8000/api/orders/calculate-delivery-price/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "pickup_latitude": -1.2921,
    "pickup_longitude": 36.8219,
    "delivery_latitude": -1.2500,
    "delivery_longitude": 36.8500,
    "errand_type": "parcel"
  }'
```

## ✅ Key Features

- ✅ Accurate distance calculation using Haversine formula
- ✅ Three errand types supported (Parcel, Cargo, Shopping)
- ✅ Detailed price breakdown for transparency
- ✅ Comprehensive error handling
- ✅ Works seamlessly with Google Maps coordinates
- ✅ No breaking changes to existing functionality
- ✅ Fully documented with examples

## 📱 User Flow in App

1. User selects **pickup location** from Google Maps autocomplete
2. User selects **delivery location** from Google Maps autocomplete
3. User clicks **"Next"**
4. User selects **errand type** (Parcel/Cargo/Shopping)
5. App calls API and **displays price**
6. User proceeds to complete order

## 🔍 What's Next?

### For App Developer:
1. Review **PRICE_CALCULATION_API.md** for detailed integration guide
2. Test the endpoint with your authentication
3. Integrate into your app following the examples
4. Test the complete user flow

### For Backend Developer:
1. Deploy the changes to staging/production
2. Monitor API performance
3. Consider adding caching if needed
4. Add analytics to track usage

## 📞 Support

If you encounter any issues:
1. Check **API_RESPONSE_EXAMPLES.md** for error examples
2. Verify authentication token is valid
3. Ensure coordinates are from Google Maps autocomplete
4. Check that errand_type is one of: "parcel", "cargo", "shopping"

## 🎉 Summary

This implementation provides a clean, efficient way to calculate delivery prices before order creation. It integrates seamlessly with Google Maps, provides transparent pricing, and maintains the existing system architecture without breaking changes.

**No database migrations required. No existing functionality affected. Ready to use!**
