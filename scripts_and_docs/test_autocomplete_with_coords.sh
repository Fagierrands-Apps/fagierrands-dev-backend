#!/bin/bash

# Test autocomplete with coordinates
echo "Testing autocomplete with coordinates..."
echo ""

# Login first
echo "1. Logging in..."
LOGIN_RESPONSE=$(curl -X POST "https://fagierrands-dev-backend.onrender.com/api/accounts/login/" \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"+254704291657","password":"NewPass123!"}' \
  -s)

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)
echo "Token obtained: ${TOKEN:0:20}..."
echo ""

# Test autocomplete WITH coordinates (default)
echo "2. Testing autocomplete WITH coordinates (include_coords=true)..."
curl -X GET "https://fagierrands-dev-backend.onrender.com/api/locations/autocomplete/?q=westlands&include_coords=true" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -s | python3 -m json.tool

echo ""
echo ""

# Test autocomplete WITHOUT coordinates (for comparison)
echo "3. Testing autocomplete WITHOUT coordinates (include_coords=false)..."
curl -X GET "https://fagierrands-dev-backend.onrender.com/api/locations/autocomplete/?q=westlands&include_coords=false" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -s | python3 -m json.tool
