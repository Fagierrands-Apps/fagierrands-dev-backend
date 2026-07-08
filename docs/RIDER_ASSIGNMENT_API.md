# Rider Assignment Status Polling API

## Overview
This endpoint allows the mobile app to poll for rider assignment status. Once a rider is assigned to an order, the endpoint returns the rider's details.

## Endpoint
```
GET /api/orders/{order_id}/rider-assignment/
```

## Authentication
Required - Bearer token

## Use Case
**Goal:** Inter-service communication - The app gets visibility on rider assignment in the backend.

**Flow:**
1. Client creates an order
2. App starts polling this endpoint every few seconds
3. When handler assigns a rider, endpoint returns rider details
4. App displays rider information to client

## Request

### URL Parameters
- `order_id` (integer, required) - The ID of the order

### Headers
```
Authorization: Bearer <token>
Content-Type: application/json
```

### Example Request
```bash
GET /api/orders/123/rider-assignment/
```

## Response

### When Rider NOT Assigned Yet (200 OK)
```json
{
  "order_id": 123,
  "status": "pending",
  "rider_assigned": false,
  "message": "Searching for available rider..."
}
```

### When Rider IS Assigned (200 OK)
```json
{
  "order_id": 123,
  "status": "assigned",
  "rider_assigned": true,
  "assigned_at": "2026-05-27T08:30:00Z",
  "rider": {
    "id": 45,
    "name": "John Doe",
    "phone_number": "+254712345678",
    "profile_picture": "https://example.com/profile.jpg",
    "rating": 4.8,
    "is_online": true
  }
}
```

## Polling Strategy

### Recommended Approach
```javascript
// Start polling after order creation
function startPollingForRider(orderId) {
  const pollInterval = setInterval(async () => {
    try {
      const response = await fetch(
        `https://api.example.com/api/orders/${orderId}/rider-assignment/`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      const data = await response.json();
      
      if (data.rider_assigned) {
        // Rider found! Display rider details
        displayRiderInfo(data.rider);
        clearInterval(pollInterval); // Stop polling
      } else {
        // Still searching...
        showSearchingMessage(data.message);
      }
    } catch (error) {
      console.error('Polling error:', error);
    }
  }, 3000); // Poll every 3 seconds
  
  // Stop polling after 5 minutes
  setTimeout(() => {
    clearInterval(pollInterval);
    showNoRiderFoundMessage();
  }, 300000);
}
```

### Polling Intervals
- **Recommended:** 3-5 seconds
- **Maximum duration:** 5 minutes
- **Stop polling when:** 
  - Rider is assigned
  - Order is cancelled
  - Timeout reached

## Integration Example

### React Native
```javascript
import { useState, useEffect } from 'react';

function OrderTracking({ orderId, authToken }) {
  const [riderInfo, setRiderInfo] = useState(null);
  const [searching, setSearching] = useState(true);
  
  useEffect(() => {
    let pollInterval;
    let timeout;
    
    const checkRiderAssignment = async () => {
      try {
        const response = await fetch(
          `https://api.example.com/api/orders/${orderId}/rider-assignment/`,
          {
            headers: {
              'Authorization': `Bearer ${authToken}`,
              'Content-Type': 'application/json'
            }
          }
        );
        
        const data = await response.json();
        
        if (data.rider_assigned) {
          setRiderInfo(data.rider);
          setSearching(false);
          clearInterval(pollInterval);
          clearTimeout(timeout);
        }
      } catch (error) {
        console.error('Error checking rider assignment:', error);
      }
    };
    
    // Start polling
    pollInterval = setInterval(checkRiderAssignment, 3000);
    
    // Stop after 5 minutes
    timeout = setTimeout(() => {
      clearInterval(pollInterval);
      setSearching(false);
    }, 300000);
    
    // Cleanup
    return () => {
      clearInterval(pollInterval);
      clearTimeout(timeout);
    };
  }, [orderId, authToken]);
  
  if (searching && !riderInfo) {
    return <SearchingForRider />;
  }
  
  if (riderInfo) {
    return (
      <RiderDetails
        name={riderInfo.name}
        phone={riderInfo.phone_number}
        rating={riderInfo.rating}
        profilePicture={riderInfo.profile_picture}
      />
    );
  }
  
  return <NoRiderFound />;
}
```

## Response Fields

### When Rider Assigned
| Field | Type | Description |
|-------|------|-------------|
| `order_id` | integer | The order ID |
| `status` | string | Current order status (assigned, in_progress, etc.) |
| `rider_assigned` | boolean | Always `true` when rider is assigned |
| `assigned_at` | datetime | When the rider was assigned |
| `rider.id` | integer | Rider's user ID |
| `rider.name` | string | Rider's full name |
| `rider.phone_number` | string | Rider's phone number |
| `rider.profile_picture` | string/null | URL to rider's profile picture |
| `rider.rating` | float/null | Rider's average rating (0-5) |
| `rider.is_online` | boolean | Whether rider is currently online |

### When Rider NOT Assigned
| Field | Type | Description |
|-------|------|-------------|
| `order_id` | integer | The order ID |
| `status` | string | Current order status (usually "pending") |
| `rider_assigned` | boolean | Always `false` when no rider assigned |
| `message` | string | Status message for the user |

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```
*Order doesn't exist or doesn't belong to the authenticated user*

## Best Practices

### 1. Efficient Polling
```javascript
// Use exponential backoff
let pollInterval = 3000; // Start with 3 seconds
const maxInterval = 10000; // Max 10 seconds

function poll() {
  checkRiderAssignment().then(data => {
    if (!data.rider_assigned) {
      // Increase interval gradually
      pollInterval = Math.min(pollInterval * 1.2, maxInterval);
      setTimeout(poll, pollInterval);
    }
  });
}
```

### 2. Stop Polling Appropriately
```javascript
// Stop polling when:
// - Rider is assigned
// - Order is cancelled
// - User navigates away
// - Timeout reached
```

### 3. Handle Network Errors
```javascript
async function checkRiderAssignment() {
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Network error:', error);
    // Continue polling despite errors
    return { rider_assigned: false };
  }
}
```

## UI States

### 1. Searching State
```
┌─────────────────────────────┐
│  🔍 Finding Your Rider...   │
│                             │
│  [Loading Animation]        │
│                             │
│  Please wait while we       │
│  assign a rider to your     │
│  order.                     │
└─────────────────────────────┘
```

### 2. Rider Assigned State
```
┌─────────────────────────────┐
│  ✅ Rider Assigned!         │
│                             │
│  [Profile Picture]          │
│                             │
│  John Doe                   │
│  ⭐ 4.8 Rating              │
│  📞 +254712345678           │
│                             │
│  [Call Rider] [Track]       │
└─────────────────────────────┘
```

## Testing

### Manual Test with cURL
```bash
# Test when no rider assigned
curl -X GET "http://localhost:8000/api/orders/123/rider-assignment/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected: rider_assigned = false

# After handler assigns rider, test again
# Expected: rider_assigned = true with rider details
```

### Test Script
```python
import requests
import time

def test_rider_assignment_polling(order_id, token):
    url = f"http://localhost:8000/api/orders/{order_id}/rider-assignment/"
    headers = {"Authorization": f"Bearer {token}"}
    
    max_attempts = 20
    for attempt in range(max_attempts):
        response = requests.get(url, headers=headers)
        data = response.json()
        
        print(f"Attempt {attempt + 1}: Rider assigned = {data['rider_assigned']}")
        
        if data['rider_assigned']:
            print(f"Rider found: {data['rider']['name']}")
            print(f"Phone: {data['rider']['phone_number']}")
            break
        
        time.sleep(3)  # Wait 3 seconds before next poll
```

## Summary

**Endpoint:** `GET /api/orders/{order_id}/rider-assignment/`

**Purpose:** Poll to check if a rider has been assigned to an order

**Returns:**
- `rider_assigned: false` - Still searching
- `rider_assigned: true` - Rider found with details

**Polling:** Every 3-5 seconds, stop after 5 minutes or when rider assigned

**Use Case:** Real-time visibility of rider assignment in the mobile app
