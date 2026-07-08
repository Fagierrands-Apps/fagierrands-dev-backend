# API Response Examples

## Example 1: Parcel - Short Distance (5 km)

### Request
```json
POST /api/orders/calculate-delivery-price/
{
  "pickup_latitude": -1.2921,
  "pickup_longitude": 36.8219,
  "delivery_latitude": -1.2500,
  "delivery_longitude": 36.8500,
  "errand_type": "parcel"
}
```

### Response (200 OK)
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

---

## Example 2: Parcel - Long Distance (15 km)

### Request
```json
POST /api/orders/calculate-delivery-price/
{
  "pickup_latitude": -1.2921,
  "pickup_longitude": 36.8219,
  "delivery_latitude": -1.1500,
  "delivery_longitude": 36.9500,
  "errand_type": "parcel"
}
```

### Response (200 OK)
```json
{
  "distance_km": 15.42,
  "errand_type": "parcel",
  "price": "382.16",
  "breakdown": {
    "base_fee": "200",
    "base_distance": "7.5 km",
    "additional_distance": "7.92 km",
    "additional_fee": "182.16",
    "per_km_rate": "23"
  },
  "currency": "KSH"
}
```

---

## Example 3: Cargo - Short Distance (5 km)

### Request
```json
POST /api/orders/calculate-delivery-price/
{
  "pickup_latitude": -1.2921,
  "pickup_longitude": 36.8219,
  "delivery_latitude": -1.2500,
  "delivery_longitude": 36.8500,
  "errand_type": "cargo"
}
```

### Response (200 OK)
```json
{
  "distance_km": 5.23,
  "errand_type": "cargo",
  "price": "500.00",
  "breakdown": {
    "base_fee": "500",
    "distance_covered": "5.23 km (within base 7 km)"
  },
  "currency": "KSH"
}
```

---

## Example 4: Cargo - Long Distance (15 km)

### Request
```json
POST /api/orders/calculate-delivery-price/
{
  "pickup_latitude": -1.2921,
  "pickup_longitude": 36.8219,
  "delivery_latitude": -1.1500,
  "delivery_longitude": 36.9500,
  "errand_type": "cargo"
}
```

### Response (200 OK)
```json
{
  "distance_km": 15.42,
  "errand_type": "cargo",
  "price": "735.76",
  "breakdown": {
    "base_fee": "500",
    "base_distance": "7 km",
    "additional_distance": "8.42 km",
    "additional_fee": "235.76",
    "per_km_rate": "28"
  },
  "currency": "KSH"
}
```

---

## Example 5: Shopping - Low Value (3,000 KSH), Short Distance

### Request
```json
POST /api/orders/calculate-delivery-price/
{
  "pickup_latitude": -1.2921,
  "pickup_longitude": 36.8219,
  "delivery_latitude": -1.2500,
  "delivery_longitude": 36.8500,
  "errand_type": "shopping",
  "shopping_value": 3000
}
```

### Response (200 OK)
```json
{
  "distance_km": 5.23,
  "errand_type": "shopping",
  "price": "400.00",
  "breakdown": {
    "service_fee": "200",
    "shopping_value": "3000",
    "errand_fee": "200",
    "distance": "5.23 km",
    "total": "400.00"
  },
  "currency": "KSH"
}
```

---

## Example 6: Shopping - Medium Value (8,000 KSH), Short Distance

### Request
```json
POST /api/orders/calculate-delivery-price/
{
  "pickup_latitude": -1.2921,
  "pickup_longitude": 36.8219,
  "delivery_latitude": -1.2500,
  "delivery_longitude": 36.8500,
  "errand_type": "shopping",
  "shopping_value": 8000
}
```

### Response (200 OK)
```json
{
  "distance_km": 5.23,
  "errand_type": "shopping",
  "price": "450.00",
  "breakdown": {
    "service_fee": "250",
    "shopping_value": "8000",
    "errand_fee": "200",
    "distance": "5.23 km",
    "total": "450.00"
  },
  "currency": "KSH"
}
```

**Calculation Breakdown:**
- Shopping value: 8,000 KSH
- Service fee: 200 + 50 = 250 KSH (first 5,000 + one additional 5,000 block)
- Errand fee: 200 KSH (distance within 7.5 km)
- Total: 250 + 200 = 450 KSH

---

## Example 7: Shopping - High Value (12,000 KSH), Long Distance

### Request
```json
POST /api/orders/calculate-delivery-price/
{
  "pickup_latitude": -1.2921,
  "pickup_longitude": 36.8219,
  "delivery_latitude": -1.2000,
  "delivery_longitude": 36.9000,
  "errand_type": "shopping",
  "shopping_value": 12000
}
```

### Response (200 OK)
```json
{
  "distance_km": 10.15,
  "errand_type": "shopping",
  "price": "660.95",
  "breakdown": {
    "service_fee": "300",
    "shopping_value": "12000",
    "errand_fee": "360.95",
    "distance": "10.15 km",
    "total": "660.95"
  },
  "currency": "KSH"
}
```

**Calculation Breakdown:**
- Shopping value: 12,000 KSH
- Service fee: 200 + (2 × 50) = 300 KSH (first 5,000 + two additional 5,000 blocks)
- Distance: 10.15 km
- Errand fee: 200 + ((10.15 - 7.5) × 23) = 200 + 60.95 = 260.95 KSH
- Total: 300 + 260.95 = 560.95 KSH

---

## Error Examples

### Error 1: Missing Required Fields

#### Request
```json
POST /api/orders/calculate-delivery-price/
{
  "pickup_latitude": -1.2921,
  "pickup_longitude": 36.8219,
  "errand_type": "parcel"
}
```

#### Response (400 Bad Request)
```json
{
  "error": "Missing required fields: pickup_latitude, pickup_longitude, delivery_latitude, delivery_longitude, errand_type"
}
```

---

### Error 2: Invalid Coordinates

#### Request
```json
POST /api/orders/calculate-delivery-price/
{
  "pickup_latitude": "invalid",
  "pickup_longitude": 36.8219,
  "delivery_latitude": -1.2500,
  "delivery_longitude": 36.8500,
  "errand_type": "parcel"
}
```

#### Response (400 Bad Request)
```json
{
  "error": "Invalid coordinates. Please provide valid numeric values."
}
```

---

### Error 3: Invalid Errand Type

#### Request
```json
POST /api/orders/calculate-delivery-price/
{
  "pickup_latitude": -1.2921,
  "pickup_longitude": 36.8219,
  "delivery_latitude": -1.2500,
  "delivery_longitude": 36.8500,
  "errand_type": "invalid_type"
}
```

#### Response (400 Bad Request)
```json
{
  "error": "Invalid errand type: invalid_type. Must be 'parcel', 'cargo', or 'shopping'"
}
```

---

### Error 4: Missing Authentication

#### Request
```json
POST /api/orders/calculate-delivery-price/
(No Authorization header)
{
  "pickup_latitude": -1.2921,
  "pickup_longitude": 36.8219,
  "delivery_latitude": -1.2500,
  "delivery_longitude": 36.8500,
  "errand_type": "parcel"
}
```

#### Response (401 Unauthorized)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## Testing with cURL

### Test Parcel
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

### Test Cargo
```bash
curl -X POST http://localhost:8000/api/orders/calculate-delivery-price/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "pickup_latitude": -1.2921,
    "pickup_longitude": 36.8219,
    "delivery_latitude": -1.1500,
    "delivery_longitude": 36.9500,
    "errand_type": "cargo"
  }'
```

### Test Shopping
```bash
curl -X POST http://localhost:8000/api/orders/calculate-delivery-price/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "pickup_latitude": -1.2921,
    "pickup_longitude": 36.8219,
    "delivery_latitude": -1.2500,
    "delivery_longitude": 36.8500,
    "errand_type": "shopping",
    "shopping_value": 8000
  }'
```

---

## Testing with Postman

1. **Create a new POST request**
2. **Set URL**: `http://localhost:8000/api/orders/calculate-delivery-price/`
3. **Add Headers**:
   - `Content-Type: application/json`
   - `Authorization: Bearer YOUR_TOKEN`
4. **Add Body** (raw JSON):
   ```json
   {
     "pickup_latitude": -1.2921,
     "pickup_longitude": 36.8219,
     "delivery_latitude": -1.2500,
     "delivery_longitude": 36.8500,
     "errand_type": "parcel"
   }
   ```
5. **Click Send**

---

## Quick Price Reference Table

| Distance | Parcel | Cargo | Shopping (5K) | Shopping (10K) |
|----------|--------|-------|---------------|----------------|
| 5 km     | 200    | 500   | 400           | 450            |
| 7 km     | 200    | 500   | 400           | 450            |
| 10 km    | 257.50 | 584   | 457.50        | 507.50         |
| 15 km    | 372.50 | 724   | 572.50        | 622.50         |
| 20 km    | 487.50 | 864   | 687.50        | 737.50         |

*Shopping prices assume 5,000 KSH and 10,000 KSH shopping values respectively*
