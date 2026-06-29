# Location Services Test UI

Simple web interface to test location API endpoints.

## Quick Start

1. **Start the server:**
   ```bash
   cd test_location_ui
   python3 -m http.server 8080
   ```

2. **Open in browser:**
   ```
   http://localhost:8080
   ```

3. **Test the endpoints:**
   - Login with credentials
   - Search locations (autocomplete with coordinates)
   - Reverse geocode coordinates to address
   - Calculate distance between two points

## Features

- ✅ Real-time autocomplete with lat/lng coordinates
- ✅ Shows API response time
- ✅ Interactive location selection
- ✅ All 4 location endpoints tested
- ✅ Works with both local and production API

## API Endpoints Tested

1. `POST /api/accounts/login/` - Authentication
2. `GET /api/locations/autocomplete/?q=query&include_coords=true` - Search with coords
3. `POST /api/locations/reverse-geocode/` - Coords to address
4. `POST /api/locations/calculate-distance/` - Distance calculation

## Default Credentials

- Phone: +254704291657
- Password: NewPass123!

## Notes

- Currently uses production URL: `https://fagierrands-dev-backend.onrender.com/api`
- Change `BASE_URL` in index.html to test local backend
- Autocomplete fetches coordinates in parallel (~1.5s for 5 results)
