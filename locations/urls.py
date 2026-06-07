from django.urls import path
from . import views

urlpatterns = [
    # Saved locations
    path('saved/', views.saved_locations, name='saved-locations'),
    path('saved/<int:location_id>/', views.location_detail, name='location-detail'),
    
    # Current location tracking
    path('update-current/', views.update_current_location, name='update-current-location'),
    path('rider/<int:rider_id>/', views.get_rider_location, name='rider-location'),
    
    # Google Maps integration
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('reverse-geocode/', views.reverse_geocode, name='reverse-geocode'),
    path('calculate-distance/', views.calculate_distance, name='calculate-distance'),
    path('map-config/', views.map_config, name='map-config'),
]
