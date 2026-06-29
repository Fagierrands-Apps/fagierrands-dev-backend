# Price Calculation API Documentation

## Overview
This endpoint calculates delivery prices based on distance and errand type. It accepts coordinates from Google Maps autocomplete and returns the calculated price with a detailed breakdown.

## Endpoint
```
POST /api/orders/calculate-delivery-price/
```

## Authentication
Requires authentication token in the header:
```
Authorization: Bearer <your_token>
```

## Request Body

### Required Fields
- `pickup_latitude` (float): Latitude of pickup location from Google Maps
- `pickup_longitude` (float): Longitude of pickup location from Google Maps
- `delivery_latitude` (float): Latitude of delivery location from Google Maps
- `delivery_longitude` (float): Longitude of delivery location from Google Maps
- `errand_type` (string): Type of errand - must be one of: `"parcel"`, `"cargo"`, or `"shopping"`

### Optional Fields
- `shopping_value` (float): Required only for shopping errands - the estimated value of items to be purchased (in KSH)

### Example Request
```json
{
  "pickup_latitude": -1.2921,
  "pickup_longitude": 36.8219,
  "delivery_latitude": -1.2500,
  "delivery_longitude": 36.8500,
  "errand_type": "parcel"
}
```

### Example Request for Shopping
```json
{
  "pickup_latitude": -1.2921,
  "pickup_longitude": 36.8219,
  "delivery_latitude": -1.2500,
  "delivery_longitude": 36.8500,
  "errand_type": "shopping",
  "shopping_value": 8000
}
```

## Response

### Success Response (200 OK)
```json
{
  "distance_km": 5.23,
  "errand_type": "parcel",
  "price": "200.00",
  "breakdown": {
    "base_fee": "200",
    "distance_covered": "5.23 km (within base 7.5 km)"
  },
  "currency": "KSH"
}
```

### Error Response (400 Bad Request)
```json
{
  "error": "Missing required fields: pickup_latitude, pickup_longitude, delivery_latitude, delivery_longitude, errand_type"
}
```

## Pricing Logic

### 1. Parcel Delivery
- **Base Fee**: 200 KSH for the first 7.5 km
- **Additional Distance**: 23 KSH per km for any distance beyond 7.5 km
- **Formula**: 
  - If distance ≤ 7.5 km: Price = 200 KSH
  - If distance > 7.5 km: Price = 200 + ((distance - 7.5) × 23) KSH

**Example Calculations:**
- 5 km: 200 KSH
- 10 km: 200 + ((10 - 7.5) × 23) = 200 + 57.5 = 257.50 KSH
- 15 km: 200 + ((15 - 7.5) × 23) = 200 + 172.5 = 372.50 KSH

### 2. Cargo Delivery
- **Base Fee**: 500 KSH for the first 7 km
- **Additional Distance**: 28 KSH per km for any distance beyond 7 km
- **Formula**: 
  - If distance ≤ 7 km: Price = 500 KSH
  - If distance > 7 km: Price = 500 + ((distance - 7) × 28) KSH

**Example Calculations:**
- 5 km: 500 KSH
- 10 km: 500 + ((10 - 7) × 28) = 500 + 84 = 584 KSH
- 15 km: 500 + ((15 - 7) × 28) = 500 + 224 = 724 KSH

### 3. Shopping Service
Shopping errands have two components:
1. **Service Fee** (based on shopping value)
2. **Errand Fee** (based on distance, same as parcel)

#### Service Fee Calculation:
- **First 5,000 KSH**: 200 KSH service fee
- **Additional 5,000 KSH blocks**: 50 KSH per block (or part thereof)
- **Formula**: 
  - If value ≤ 5,000: Service Fee = 200 KSH
  - If value > 5,000: Service Fee = 200 + (ceil((value - 5,000) / 5,000) × 50) KSH

#### Errand Fee Calculation:
- Same as Parcel: 200 KSH for first 7.5 km, then 23 KSH per additional km

#### Total Price = Service Fee + Errand Fee

**Example Calculations:**
- 3,000 KSH worth, 5 km: 200 (service) + 200 (errand) = 400 KSH
- 8,000 KSH worth, 5 km: 250 (service) + 200 (errand) = 450 KSH
- 12,000 KSH worth, 10 km: 350 (service) + 257.50 (errand) = 607.50 KSH

## Integration Guide for App Developer

### Step 1: Get Coordinates from Google Maps
When the user selects a location from Google Maps autocomplete:
```javascript
// Example using Google Places Autocomplete
const place = autocomplete.getPlace();
const latitude = place.geometry.location.lat();
const longitude = place.geometry.location.lng();
```

### Step 2: Store Coordinates
Store both pickup and delivery coordinates when user selects locations:
```javascript
const pickupLocation = {
  latitude: pickupPlace.geometry.location.lat(),
  longitude: pickupPlace.geometry.location.lng(),
  address: pickupPlace.formatted_address
};

const deliveryLocation = {
  latitude: deliveryPlace.geometry.location.lat(),
  longitude: deliveryPlace.geometry.location.lng(),
  address: deliveryPlace.formatted_address
};
```

### Step 3: Call Price Calculation API
When user clicks on an errand type (parcel, cargo, or shopping):
```javascript
async function calculatePrice(pickupLocation, deliveryLocation, errandType, shoppingValue = 0) {
  const requestBody = {
    pickup_latitude: pickupLocation.latitude,
    pickup_longitude: pickupLocation.longitude,
    delivery_latitude: deliveryLocation.latitude,
    delivery_longitude: deliveryLocation.longitude,
    errand_type: errandType.toLowerCase() // "parcel", "cargo", or "shopping"
  };
  
  // Add shopping value if it's a shopping errand
  if (errandType.toLowerCase() === 'shopping' && shoppingValue > 0) {
    requestBody.shopping_value = shoppingValue;
  }
  
  try {
    const response = await fetch('https://your-api-domain.com/api/orders/calculate-delivery-price/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify(requestBody)
    });
    
    if (response.ok) {
      const data = await response.json();
      return {
        success: true,
        distance: data.distance_km,
        price: data.price,
        currency: data.currency,
        breakdown: data.breakdown
      };
    } else {
      const error = await response.json();
      return {
        success: false,
        error: error.error
      };
    }
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}
```

### Step 4: Display Price to User
```javascript
// Example usage
const result = await calculatePrice(pickupLocation, deliveryLocation, 'parcel');

if (result.success) {
  // Display price to user
  console.log(`Distance: ${result.distance} km`);
  console.log(`Price: ${result.currency} ${result.price}`);
  
  // Show breakdown if needed
  console.log('Breakdown:', result.breakdown);
} else {
  // Handle error
  console.error('Error calculating price:', result.error);
}
```

## User Flow in App

1. **User enters pickup location** → Clicks Google autocomplete suggestion → App stores coordinates
2. **User enters delivery location** → Clicks Google autocomplete suggestion → App stores coordinates
3. **User clicks "Next"** → App navigates to errand type selection page
4. **User selects errand type** (Parcel/Cargo/Shopping):
   - For Parcel/Cargo: Immediately call API and display price
   - For Shopping: Show input for shopping value, then call API
5. **Display calculated price** with breakdown
6. **User proceeds** to complete order

## Error Handling

### Common Errors
1. **Missing coordinates**: Ensure user has selected from Google autocomplete
2. **Invalid errand type**: Must be exactly "parcel", "cargo", or "shopping" (case-insensitive)
3. **Missing shopping value**: Required when errand_type is "shopping"
4. **Authentication error**: Ensure valid token is provided

### Example Error Handling
```javascript
if (!result.success) {
  switch(result.error) {
    case 'Missing required fields':
      alert('Please select both pickup and delivery locations');
      break;
    case 'Invalid errand type':
      alert('Please select a valid errand type');
      break;
    default:
      alert('Error calculating price. Please try again.');
  }
}
```

## Testing

### Test Coordinates (Nairobi, Kenya)
- **Nairobi CBD**: -1.2921, 36.8219
- **Westlands**: -1.2676, 36.8108
- **Karen**: -1.3197, 36.7078
- **Eastleigh**: -1.2833, 36.8500

### Sample Test Cases
```javascript
// Test 1: Short distance parcel
calculatePrice(
  { latitude: -1.2921, longitude: 36.8219 },
  { latitude: -1.2676, longitude: 36.8108 },
  'parcel'
);
// Expected: ~200 KSH (within 7.5 km)

// Test 2: Long distance cargo
calculatePrice(
  { latitude: -1.2921, longitude: 36.8219 },
  { latitude: -1.3197, longitude: 36.7078 },
  'cargo'
);
// Expected: ~500+ KSH (beyond 7 km)

// Test 3: Shopping with value
calculatePrice(
  { latitude: -1.2921, longitude: 36.8219 },
  { latitude: -1.2833, longitude: 36.8500 },
  'shopping',
  8000
);
// Expected: Service fee + Errand fee
```

## Notes
- Distance is calculated using the Haversine formula (straight-line distance)
- All prices are in Kenyan Shillings (KSH)
- Prices are rounded to 2 decimal places
- The endpoint requires authentication
- Coordinates must be from Google Maps autocomplete for accuracy
