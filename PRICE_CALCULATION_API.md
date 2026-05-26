# Price Calculation API

**Endpoint**: `POST /api/orders/calculate-price/`

**Authentication**: Not required (public endpoint)

---

## Pricing Formula

### 1. Parcel Delivery
- **First 7.5 km**: 200 KSH (flat rate)
- **Additional km**: 23 KSH per km after 7.5 km
- **Emergency**: +50 KSH

**Example**:
- Distance: 10 km
- Base: 200 KSH
- Extra: (10 - 7.5) × 23 = 57.5 KSH
- **Total**: 257.5 KSH

### 2. Cargo Delivery
- **First 7 km**: 500 KSH (flat rate)
- **Additional km**: 28 KSH per km after 7 km
- **Emergency**: +50 KSH

**Example**:
- Distance: 12 km
- Base: 500 KSH
- Extra: (12 - 7) × 28 = 140 KSH
- **Total**: 640 KSH

### 3. Shopping Errand
- **Distance fee**: Same as parcel (200 for 7.5km, +23/km after)
- **Service fee**: 200 KSH for first 5000 KSH shopping, then +50 KSH per additional 5000 KSH
- **Payment split**:
  - **Upfront**: 30% of shopping amount
  - **On delivery**: 70% of shopping amount + distance fee + service fee
- **Emergency**: +50 KSH

**Example**:
- Distance: 8 km
- Shopping amount: 7000 KSH
- Distance fee: 200 + (8 - 7.5) × 23 = 211.5 KSH
- Service fee: 200 + 50 = 250 KSH (7000 is 2000 above 5000)
- Upfront: 7000 × 0.30 = 2100 KSH
- On delivery: 7000 × 0.70 + 211.5 + 250 = 5361.5 KSH
- **Total**: 7461.5 KSH

---

## Request

```json
POST /api/orders/calculate-price/
Content-Type: application/json

{
  "pickup_latitude": -1.286389,
  "pickup_longitude": 36.817223,
  "dropoff_latitude": -1.292066,
  "dropoff_longitude": 36.821945,
  "errand_type": "parcel",
  "is_emergency": false,
  "shopping_amount": 0
}
```

### Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `pickup_latitude` | number | Yes | Pickup location latitude |
| `pickup_longitude` | number | Yes | Pickup location longitude |
| `dropoff_latitude` | number | Yes | Dropoff location latitude |
| `dropoff_longitude` | number | Yes | Dropoff location longitude |
| `errand_type` | string | Yes | One of: `parcel`, `cargo`, `shopping` |
| `is_emergency` | boolean | No | Add 50 KSH emergency fee (default: false) |
| `shopping_amount` | number | Conditional | Required if `errand_type` is `shopping` |

---

## Response Examples

### Parcel (10 km)

```json
{
  "distance_km": 10.0,
  "errand_type": "parcel",
  "base_price": 200.0,
  "distance_fee": 57.5,
  "service_fee": 0.0,
  "emergency_fee": 0.0,
  "shopping_amount": 0,
  "total_price": 257.5,
  "upfront_payment": 257.5,
  "on_delivery_payment": 0.0,
  "breakdown": {
    "base_price": "200 KSH (first 7.5 km)",
    "distance_fee": "57.5 KSH (2.50 extra km)",
    "service_fee": "0 KSH",
    "emergency_fee": "0 KSH"
  }
}
```

### Cargo (12 km, Emergency)

```json
{
  "distance_km": 12.0,
  "errand_type": "cargo",
  "base_price": 500.0,
  "distance_fee": 140.0,
  "service_fee": 0.0,
  "emergency_fee": 50.0,
  "shopping_amount": 0,
  "total_price": 690.0,
  "upfront_payment": 690.0,
  "on_delivery_payment": 0.0,
  "breakdown": {
    "base_price": "500 KSH (first 7 km)",
    "distance_fee": "140 KSH (5.00 extra km)",
    "service_fee": "0 KSH",
    "emergency_fee": "50 KSH"
  }
}
```

### Shopping (8 km, 7000 KSH)

```json
{
  "distance_km": 8.0,
  "errand_type": "shopping",
  "base_price": 200.0,
  "distance_fee": 11.5,
  "service_fee": 250.0,
  "emergency_fee": 0.0,
  "shopping_amount": 7000.0,
  "total_price": 7461.5,
  "upfront_payment": 2100.0,
  "on_delivery_payment": 5361.5,
  "breakdown": {
    "base_price": "200 KSH (first 7.5 km)",
    "distance_fee": "11.5 KSH (0.50 extra km)",
    "service_fee": "250 KSH (shopping service)",
    "emergency_fee": "0 KSH"
  }
}
```

---

## Error Responses

### Missing Fields
```json
{
  "error": "Missing required fields"
}
```

### Invalid Errand Type
```json
{
  "error": "Invalid errand_type. Must be: parcel, cargo, or shopping"
}
```

### Missing Shopping Amount
```json
{
  "error": "shopping_amount required for shopping errands"
}
```

---

## Integration Example (JavaScript)

```javascript
// After user selects pickup and dropoff from autocomplete
const calculatePrice = async (pickup, dropoff, errandType, shoppingAmount = 0) => {
  const response = await fetch('/api/orders/calculate-price/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      pickup_latitude: pickup.lat,
      pickup_longitude: pickup.lng,
      dropoff_latitude: dropoff.lat,
      dropoff_longitude: dropoff.lng,
      errand_type: errandType,
      shopping_amount: shoppingAmount,
      is_emergency: false
    })
  });
  
  const data = await response.json();
  
  // Display price to user
  console.log(`Distance: ${data.distance_km} km`);
  console.log(`Total Price: ${data.total_price} KSH`);
  
  if (errandType === 'shopping') {
    console.log(`Pay now: ${data.upfront_payment} KSH`);
    console.log(`Pay on delivery: ${data.on_delivery_payment} KSH`);
  }
  
  return data;
};

// Usage
const pickup = { lat: -1.286389, lng: 36.817223 };
const dropoff = { lat: -1.292066, lng: 36.821945 };

// Parcel
await calculatePrice(pickup, dropoff, 'parcel');

// Shopping
await calculatePrice(pickup, dropoff, 'shopping', 7000);
```

---

## App Flow

1. User selects **pickup location** from autocomplete → Get lat/lng
2. User selects **dropoff location** from autocomplete → Get lat/lng
3. User selects **errand type** (parcel/cargo/shopping)
4. If shopping, user enters **shopping amount**
5. **Call `/api/orders/calculate-price/`** with all data
6. **Display price** to user
7. User confirms and proceeds to payment

---

## Notes

- Distance calculated using Haversine formula (accurate for Earth's curvature)
- All prices in Kenyan Shillings (KSH)
- Emergency fee applies to all errand types
- Shopping errands require upfront payment (30%) before rider accepts
- Remaining 70% + fees paid on delivery for shopping errands

---

**Built with ❤️ for FagiErrands**
