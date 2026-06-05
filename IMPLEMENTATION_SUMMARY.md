# Price Calculation Endpoint Implementation Summary

## What Was Implemented

A new API endpoint that calculates delivery prices based on:
- Distance between pickup and delivery locations (from Google Maps coordinates)
- Errand type (Parcel, Cargo, or Shopping)
- Shopping value (for shopping errands)

## Files Created/Modified

### New Files
1. **`orders/views_price_calculation.py`**
   - Contains the `CalculatePriceView` class
   - Implements distance calculation using Haversine formula
   - Implements pricing logic for all three errand types

2. **`PRICE_CALCULATION_API.md`**
   - Comprehensive API documentation
   - Integration guide for app developer
   - Example code snippets
   - Test cases

3. **`PRICE_API_QUICK_REF.md`**
   - Quick reference guide
   - Pricing summary table
   - Quick examples

4. **`test_price_calculation.py`**
   - Test script with multiple test cases
   - Can be used to verify endpoint functionality

### Modified Files
1. **`orders/urls.py`**
   - Added import for `CalculatePriceView`
   - Added URL route: `/api/orders/calculate-delivery-price/`

## Pricing Logic Implemented

### 1. Parcel Delivery
- Base: 200 KSH for first 7.5 km
- Additional: 23 KSH per km beyond 7.5 km

### 2. Cargo Delivery
- Base: 500 KSH for first 7 km
- Additional: 28 KSH per km beyond 7 km

### 3. Shopping Service
- Service Fee:
  - 200 KSH for first 5,000 KSH worth of shopping
  - 50 KSH for each additional 5,000 KSH (or part thereof)
- Errand Fee: Same as Parcel (200 KSH base + 23 KSH/km)
- Total = Service Fee + Errand Fee

## How It Works

1. **Client selects pickup location** from Google Maps autocomplete → App gets coordinates
2. **Client selects delivery location** from Google Maps autocomplete → App gets coordinates
3. **Client clicks "Next"** → Navigates to errand type selection
4. **Client selects errand type** → App calls price calculation API
5. **API calculates distance** using Haversine formula
6. **API calculates price** based on errand type and distance
7. **API returns price with breakdown** → App displays to user

## API Endpoint

**URL**: `POST /api/orders/calculate-delivery-price/`

**Authentication**: Required (Bearer token)

**Request Body**:
```json
{
  "pickup_latitude": -1.2921,
  "pickup_longitude": 36.8219,
  "delivery_latitude": -1.2500,
  "delivery_longitude": 36.8500,
  "errand_type": "parcel",
  "shopping_value": 0
}
```

**Response**:
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

## Key Features

✅ **Accurate Distance Calculation**: Uses Haversine formula for precise distance
✅ **Three Errand Types**: Supports Parcel, Cargo, and Shopping
✅ **Detailed Breakdown**: Returns price breakdown for transparency
✅ **Error Handling**: Validates all inputs and returns clear error messages
✅ **Google Maps Integration**: Works seamlessly with Google Maps coordinates
✅ **No Breaking Changes**: Existing functionality remains intact

## Testing

Run the test script:
```bash
python test_price_calculation.py
```

Or test manually using curl:
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

## Next Steps for App Developer

1. **Review Documentation**: Read `PRICE_CALCULATION_API.md` for detailed integration guide
2. **Test Endpoint**: Use the test script or manual testing to verify functionality
3. **Integrate in App**: Follow the integration steps in the documentation
4. **Handle Errors**: Implement proper error handling as shown in examples
5. **Test User Flow**: Test the complete flow from location selection to price display

## Notes

- The endpoint does NOT create an order, it only calculates the price
- Distance is calculated as straight-line distance (Haversine formula)
- All prices are in Kenyan Shillings (KSH)
- Authentication is required for all requests
- Coordinates must come from Google Maps autocomplete for accuracy
