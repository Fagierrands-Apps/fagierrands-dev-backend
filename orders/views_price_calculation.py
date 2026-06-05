from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from decimal import Decimal
import math
from .models import OrderType


class CalculatePriceView(APIView):
    """
    Calculate delivery price based on distance and errand type.
    Accepts pickup and delivery coordinates from Google Maps autocomplete.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Get coordinates from request
        pickup_lat = request.data.get('pickup_latitude')
        pickup_lng = request.data.get('pickup_longitude')
        delivery_lat = request.data.get('delivery_latitude')
        delivery_lng = request.data.get('delivery_longitude')
        errand_type = request.data.get('errand_type')  # 'parcel', 'cargo', or 'shopping'
        shopping_value = request.data.get('shopping_value', 0)  # For shopping errands
        
        # Validate input
        if None in [pickup_lat, pickup_lng, delivery_lat, delivery_lng, errand_type]:
            return Response(
                {"error": "Missing required fields: pickup_latitude, pickup_longitude, delivery_latitude, delivery_longitude, errand_type"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Convert to float
            pickup_lat = float(pickup_lat)
            pickup_lng = float(pickup_lng)
            delivery_lat = float(delivery_lat)
            delivery_lng = float(delivery_lng)
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid coordinates. Please provide valid numeric values."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate distance using Haversine formula
        distance_km = self._calculate_distance(pickup_lat, pickup_lng, delivery_lat, delivery_lng)
        
        # Calculate price based on errand type
        try:
            price_data = self._calculate_price_by_type(errand_type, distance_km, shopping_value)
            
            return Response({
                "distance_km": round(distance_km, 2),
                "errand_type": errand_type,
                "price": str(price_data['price']),
                "breakdown": price_data['breakdown'],
                "currency": "KSH"
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    def _calculate_price_by_type(self, errand_type, distance_km, shopping_value=0):
        """Calculate price based on errand type and distance"""
        errand_type = errand_type.lower()
        
        if errand_type == 'parcel':
            # Parcel: 200 KSH for first 7.5 km, 23 KSH per additional km
            base_distance = Decimal('7.5')
            base_fee = Decimal('200')
            per_km_fee = Decimal('23')
            
            if distance_km <= base_distance:
                price = base_fee
                breakdown = {
                    "base_fee": str(base_fee),
                    "distance_covered": f"{distance_km:.2f} km (within base {base_distance} km)"
                }
            else:
                additional_km = Decimal(str(distance_km)) - base_distance
                additional_fee = additional_km * per_km_fee
                price = base_fee + additional_fee
                breakdown = {
                    "base_fee": str(base_fee),
                    "base_distance": f"{base_distance} km",
                    "additional_distance": f"{additional_km:.2f} km",
                    "additional_fee": str(additional_fee),
                    "per_km_rate": str(per_km_fee)
                }
            
            return {"price": price, "breakdown": breakdown}
        
        elif errand_type == 'cargo':
            # Cargo: 500 KSH for first 7 km, 28 KSH per additional km
            base_distance = Decimal('7')
            base_fee = Decimal('500')
            per_km_fee = Decimal('28')
            
            if distance_km <= base_distance:
                price = base_fee
                breakdown = {
                    "base_fee": str(base_fee),
                    "distance_covered": f"{distance_km:.2f} km (within base {base_distance} km)"
                }
            else:
                additional_km = Decimal(str(distance_km)) - base_distance
                additional_fee = additional_km * per_km_fee
                price = base_fee + additional_fee
                breakdown = {
                    "base_fee": str(base_fee),
                    "base_distance": f"{base_distance} km",
                    "additional_distance": f"{additional_km:.2f} km",
                    "additional_fee": str(additional_fee),
                    "per_km_rate": str(per_km_fee)
                }
            
            return {"price": price, "breakdown": breakdown}
        
        elif errand_type == 'shopping':
            # Shopping: Service fee + errand fee
            # Service fee: 200 KSH for first 5000 KSH worth, 50 KSH per additional 5000 KSH
            shopping_value = Decimal(str(shopping_value))
            
            # Calculate service fee
            if shopping_value <= 5000:
                service_fee = Decimal('200')
            else:
                additional_value = shopping_value - Decimal('5000')
                additional_blocks = math.ceil(float(additional_value / Decimal('5000')))
                service_fee = Decimal('200') + (Decimal('50') * additional_blocks)
            
            # Calculate errand fee (same as parcel)
            base_distance = Decimal('7.5')
            base_errand_fee = Decimal('200')
            per_km_fee = Decimal('23')
            
            if distance_km <= base_distance:
                errand_fee = base_errand_fee
            else:
                additional_km = Decimal(str(distance_km)) - base_distance
                errand_fee = base_errand_fee + (additional_km * per_km_fee)
            
            price = service_fee + errand_fee
            
            breakdown = {
                "service_fee": str(service_fee),
                "shopping_value": str(shopping_value),
                "errand_fee": str(errand_fee),
                "distance": f"{distance_km:.2f} km",
                "total": str(price)
            }
            
            return {"price": price, "breakdown": breakdown}
        
        else:
            raise ValueError(f"Invalid errand type: {errand_type}. Must be 'parcel', 'cargo', or 'shopping'")
