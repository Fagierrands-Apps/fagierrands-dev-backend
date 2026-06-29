"""
Locations Models
"""

from django.db import models
from django.conf import settings


class Location(models.Model):
    """Saved location"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=100)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"


class UserLocation(models.Model):
    """Current user location tracking"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='current_location')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    updated_at = models.DateTimeField(auto_now=True)


class Waypoint(models.Model):
    """Order route waypoints"""
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='waypoints')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    sequence = models.IntegerField()
    reached_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['sequence']


class RouteCalculation(models.Model):
    """Cached route calculations"""
    origin_lat = models.DecimalField(max_digits=9, decimal_places=6)
    origin_lng = models.DecimalField(max_digits=9, decimal_places=6)
    dest_lat = models.DecimalField(max_digits=9, decimal_places=6)
    dest_lng = models.DecimalField(max_digits=9, decimal_places=6)
    distance_km = models.DecimalField(max_digits=6, decimal_places=2)
    duration_minutes = models.IntegerField()
    calculated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['origin_lat', 'origin_lng', 'dest_lat', 'dest_lng']),
        ]
