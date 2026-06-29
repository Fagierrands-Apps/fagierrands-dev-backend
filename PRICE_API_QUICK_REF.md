# Price Calculation API - Quick Reference

## Endpoint
```
POST /api/orders/calculate-delivery-price/
```

## Request Format
```json
{
  "pickup_latitude": -1.2921,
  "pickup_longitude": 36.8219,
  "delivery_latitude": -1.2500,
  "delivery_longitude": 36.8500,
  "errand_type": "parcel",
  "shopping_value": 0  // Only for shopping errands
}
```

## Response Format
```json
{
  "distance_km": 5.23,
  "errand_type": "parcel",
  "price": "200.00",
  "breakdown": { ... },
  "currency": "KSH"
}
```

## Pricing Summary

| Errand Type | Base Fee | Base Distance | Additional Rate |
|-------------|----------|---------------|-----------------|
| Parcel      | 200 KSH  | 7.5 km        | 23 KSH/km       |
| Cargo       | 500 KSH  | 7 km          | 28 KSH/km       |
| Shopping    | Service Fee + Errand Fee (same as Parcel) | - | - |

### Shopping Service Fee
- First 5,000 KSH worth: 200 KSH
- Each additional 5,000 KSH (or part): +50 KSH

## Quick Examples

### Parcel - 5 km
```
Price = 200 KSH (within base distance)
```

### Parcel - 15 km
```
Price = 200 + ((15 - 7.5) × 23) = 372.50 KSH
```

### Cargo - 10 km
```
Price = 500 + ((10 - 7) × 28) = 584 KSH
```

### Shopping - 8,000 KSH worth, 5 km
```
Service Fee = 200 + 50 = 250 KSH
Errand Fee = 200 KSH
Total = 450 KSH
```

## Integration Steps

1. **Get coordinates from Google Maps autocomplete**
2. **Store pickup and delivery coordinates**
3. **When user selects errand type, call API**
4. **Display calculated price**
5. **User proceeds to complete order**

## Error Handling
- Missing fields → 400 Bad Request
- Invalid coordinates → 400 Bad Request
- Invalid errand type → 400 Bad Request
- No authentication → 401 Unauthorized
