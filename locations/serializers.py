from rest_framework import serializers
from .models import Location, UserLocation, Waypoint

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocation
        fields = '__all__'
        read_only_fields = ['user', 'updated_at']

class WaypointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waypoint
        fields = '__all__'
