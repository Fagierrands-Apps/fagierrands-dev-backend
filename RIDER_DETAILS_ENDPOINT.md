# Rider Details Endpoint

## Overview
Endpoint to retrieve assigned rider details after a handler assigns a rider to an errand.

## Endpoint Details

**URL:** `/api/orders/<order_id>/rider-details/`  
**Method:** `GET`  
**Authentication:** Required (Bearer Token)  
**Permission:** Order client only

## Implementation

### File Location
- **View:** `orders/views_rider_details.py`
- **URL:** Added to `orders/urls.py`

### Request

```http
GET /api/orders/{order_id}/rider-details/
Authorization: Bearer <token>
```

### Response Format

#### Success - Rider Assigned (200 OK)
```json
{
  "assigned": true,
  "rider": {
    "id": 123,
    "name": "John Doe",
    "phone_number": "+254712345678",
    "profile_image": "https://example.com/image.jpg",
    "plate_number": "KAA 123B"
  },
  "order_status": "assigned",
  "assigned_at": "2026-05-21T14:30:00Z"
}
```

#### Success - No Rider Yet (200 OK)
```json
{
  "error": "No rider assigned yet",
  "assigned": false
}
```

#### Error - Unauthorized (403 Forbidden)
```json
{
  "error": "You don't have permission to view this order"
}
```

#### Error - Not Found (404 Not Found)
```json
{
  "error": "Order not found"
}
```

## Features

1. **Security**
   - Only the order client can view rider details
   - Requires authentication
   - Returns 403 for unauthorized access

2. **Data Returned**
   - Rider ID
   - Full name (first_name + last_name or username)
   - Phone number
   - Profile image URL
   - Vehicle plate number
   - Order status
   - Assignment timestamp

3. **Handles Edge Cases**
   - No rider assigned yet
   - Missing profile data
   - Order not found
   - Unauthorized access

## Usage Flow

1. **Client places errand** → Status: `pending`
2. **Handler assigns rider** → Status: `assigned`
3. **Client polls this endpoint** to get rider details
4. **Display rider info** in mobile app

## Mobile Integration

### Polling Strategy
```javascript
// Poll every 5 seconds until rider is assigned
const pollRiderDetails = async (orderId) => {
  const interval = setInterval(async () => {
    const response = await fetch(
      `/api/orders/${orderId}/rider-details/`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );
    
    const data = await response.json();
    
    if (data.assigned) {
      clearInterval(interval);
      displayRiderInfo(data.rider);
    }
  }, 5000);
};
```

### Display Example
```
🚴 Your Rider
━━━━━━━━━━━━━━━━
Name: John Doe
Phone: +254712345678
Plate: KAA 123B
[Profile Image]
[Call Button] [Track Button]
```

## Testing

### Manual Test with cURL
```bash
# Get rider details
curl -X GET \
  http://localhost:8000/api/orders/1/rider-details/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Expected Behavior
- ✅ Returns rider details when assigned
- ✅ Returns "not assigned" message when no rider
- ✅ Blocks unauthorized users
- ✅ Handles missing profile gracefully

## Database Fields Used

### Order Model
- `id` - Order identifier
- `client` - Order owner
- `assistant` - Assigned rider
- `status` - Order status
- `assigned_at` - Assignment timestamp

### User Model
- `id` - User identifier
- `first_name` - First name
- `last_name` - Last name
- `username` - Username (fallback)
- `phone_number` - Contact number

### Profile Model
- `profile_picture_url` - Rider photo
- `plate_number` - Vehicle plate

## Next Steps

1. **Add WebSocket Support** - Real-time updates instead of polling
2. **Add Rider Rating** - Show rider's average rating
3. **Add Estimated Arrival** - Show ETA to pickup location
4. **Add Live Tracking** - Link to real-time location tracking

## Related Endpoints

- `/api/orders/<order_id>/rider-status/` - Check if rider is being searched
- `/api/orders/<order_id>/tracking/` - Track rider location
- `/api/orders/<order_id>/` - Get full order details

## Status Codes

| Code | Meaning |
|------|---------|
| 200  | Success - Rider details or not assigned message |
| 403  | Forbidden - Not the order client |
| 404  | Not Found - Order doesn't exist |
| 401  | Unauthorized - No authentication token |
