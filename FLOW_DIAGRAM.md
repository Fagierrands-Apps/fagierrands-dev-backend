# Price Calculation Flow Diagram

## User Flow in Mobile App

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER OPENS APP                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              STEP 1: SELECT PICKUP LOCATION                      │
│  • User types in search box                                      │
│  • Google Maps autocomplete shows suggestions                    │
│  • User clicks on a suggestion                                   │
│  • App stores: latitude, longitude, address                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│             STEP 2: SELECT DELIVERY LOCATION                     │
│  • User types in search box                                      │
│  • Google Maps autocomplete shows suggestions                    │
│  • User clicks on a suggestion                                   │
│  • App stores: latitude, longitude, address                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  STEP 3: CLICK "NEXT"                            │
│  • App navigates to errand type selection page                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              STEP 4: SELECT ERRAND TYPE                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                      │
│  │  PARCEL  │  │  CARGO   │  │ SHOPPING │                      │
│  └──────────┘  └──────────┘  └──────────┘                      │
│                                                                   │
│  When user clicks on any type:                                   │
│  • If SHOPPING: Show input for shopping value first              │
│  • Call API with coordinates + errand type                       │
│  • Display calculated price                                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  API CALL TO BACKEND                             │
│                                                                   │
│  POST /api/orders/calculate-delivery-price/                      │
│  {                                                                │
│    "pickup_latitude": -1.2921,                                   │
│    "pickup_longitude": 36.8219,                                  │
│    "delivery_latitude": -1.2500,                                 │
│    "delivery_longitude": 36.8500,                                │
│    "errand_type": "parcel",                                      │
│    "shopping_value": 0  // Only for shopping                     │
│  }                                                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  BACKEND PROCESSING                              │
│  1. Validate input (coordinates, errand type)                    │
│  2. Calculate distance using Haversine formula                   │
│  3. Calculate price based on errand type:                        │
│     • Parcel: 200 KSH base + 23 KSH/km after 7.5 km             │
│     • Cargo: 500 KSH base + 28 KSH/km after 7 km                │
│     • Shopping: Service fee + Errand fee                         │
│  4. Return price with breakdown                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  API RESPONSE                                    │
│  {                                                                │
│    "distance_km": 5.23,                                          │
│    "errand_type": "parcel",                                      │
│    "price": "200.00",                                            │
│    "breakdown": {                                                │
│      "base_fee": "200",                                          │
│      "distance_covered": "5.23 km (within base 7.5 km)"         │
│    },                                                             │
│    "currency": "KSH"                                             │
│  }                                                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              STEP 5: DISPLAY PRICE TO USER                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Delivery Fee: KSH 200.00                                │   │
│  │  Distance: 5.23 km                                       │   │
│  │                                                           │   │
│  │  [View Breakdown]  [Proceed to Order]                    │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              STEP 6: USER PROCEEDS TO COMPLETE ORDER             │
│  • User confirms and proceeds                                    │
│  • App creates the actual order with all details                 │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
┌──────────────┐
│  Mobile App  │
└──────┬───────┘
       │ 1. User selects locations from Google Maps
       │    (stores coordinates)
       │
       │ 2. User selects errand type
       │
       │ 3. App sends API request
       ↓
┌──────────────────────────────────────────────────────────┐
│  POST /api/orders/calculate-delivery-price/              │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Request Body:                                       │  │
│  │ • pickup_latitude                                   │  │
│  │ • pickup_longitude                                  │  │
│  │ • delivery_latitude                                 │  │
│  │ • delivery_longitude                                │  │
│  │ • errand_type                                       │  │
│  │ • shopping_value (optional)                         │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
       │
       │ 4. Backend calculates distance & price
       │
       ↓
┌──────────────────────────────────────────────────────────┐
│  Response                                                 │
│  ┌────────────────────────────────────────────────────┐  │
│  │ • distance_km                                       │  │
│  │ • errand_type                                       │  │
│  │ • price                                             │  │
│  │ • breakdown (detailed calculation)                  │  │
│  │ • currency                                          │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
       │
       │ 5. App displays price to user
       │
       ↓
┌──────────────┐
│  Mobile App  │
│  Shows Price │
└──────────────┘
```

## Important Notes for App Developer

### ✅ DO:
- Store coordinates when user clicks Google autocomplete suggestion
- Call API immediately when user selects errand type
- Display price clearly with currency
- Show breakdown if user wants details
- Handle errors gracefully

### ❌ DON'T:
- Don't manually enter coordinates
- Don't skip Google autocomplete
- Don't create order at this stage (only calculate price)
- Don't cache prices (always calculate fresh)

### 🔑 Key Points:
1. **Coordinates come from Google Maps** - This ensures accuracy
2. **API only calculates price** - It doesn't create an order
3. **Price is calculated in real-time** - Based on current distance
4. **Shopping requires value input** - Ask user for estimated shopping value
5. **Handler sees precise location** - Because coordinates are from Google
