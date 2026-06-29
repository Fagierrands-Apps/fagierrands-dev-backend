from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from .models import (
    DailyMetrics, UserRetention, ServicePerformance,
    CustomerSatisfaction, AdvertisementMetrics
)
from rest_framework import serializers


# Serializers
class DailyMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyMetrics
        fields = '__all__'


class UserRetentionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRetention
        fields = '__all__'


class ServicePerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePerformance
        fields = '__all__'


class CustomerSatisfactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerSatisfaction
        fields = '__all__'


class AdvertisementMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvertisementMetrics
        fields = '__all__'


# ViewSets
class DailyMetricsViewSet(viewsets.ModelViewSet):
    """Daily metrics and statistics"""
    queryset = DailyMetrics.objects.all()
    serializer_class = DailyMetricsSerializer
    permission_classes = [IsAdminUser]
    
    def get_view_name(self):
        return "Daily Metrics"
    
    @action(detail=False, methods=['get'])
    def time_series(self, request):
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        metrics = self.queryset.filter(date__gte=start_date).order_by('date')
        serializer = self.get_serializer(metrics, many=True)
        return Response(serializer.data)


class UserRetentionViewSet(viewsets.ModelViewSet):
    """User retention analysis"""
    queryset = UserRetention.objects.all()
    serializer_class = UserRetentionSerializer
    permission_classes = [IsAdminUser]
    
    def get_view_name(self):
        return "User Retention"
    
    @action(detail=False, methods=['get'])
    def cohort_analysis(self, request):
        data = self.queryset.values('cohort_month').annotate(
            avg_retention=Avg('retention_rate'),
            total_users=Sum('users_count')
        ).order_by('cohort_month')
        return Response(data)


class ServicePerformanceViewSet(viewsets.ModelViewSet):
    """Service performance metrics"""
    queryset = ServicePerformance.objects.all()
    serializer_class = ServicePerformanceSerializer
    permission_classes = [IsAdminUser]
    
    def get_view_name(self):
        return "Service Performance"
    
    @action(detail=False, methods=['get'])
    def service_comparison(self, request):
        data = self.queryset.values('service_type').annotate(
            total_orders=Sum('total_orders'),
            avg_rating=Avg('avg_rating'),
            total_revenue=Sum('revenue')
        ).order_by('-total_revenue')
        return Response(data)


class CustomerSatisfactionViewSet(viewsets.ModelViewSet):
    """Customer satisfaction metrics"""
    queryset = CustomerSatisfaction.objects.all()
    serializer_class = CustomerSatisfactionSerializer
    permission_classes = [IsAdminUser]
    
    def get_view_name(self):
        return "Customer Satisfaction"
    
    @action(detail=False, methods=['get'])
    def rating_distribution(self, request):
        latest = self.queryset.latest('date')
        return Response({
            'positive': latest.positive_reviews,
            'negative': latest.negative_reviews,
            'total': latest.total_reviews,
            'avg_rating': float(latest.avg_rating)
        })
    
    @action(detail=False, methods=['get'])
    def nps_trend(self, request):
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        data = self.queryset.filter(date__gte=start_date).order_by('date')
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)


class AdvertisementMetricsViewSet(viewsets.ModelViewSet):
    """Advertisement performance metrics"""
    queryset = AdvertisementMetrics.objects.all()
    serializer_class = AdvertisementMetricsSerializer
    permission_classes = [IsAdminUser]
    
    def get_view_name(self):
        return "Advertisement Metrics"
    
    @action(detail=False, methods=['get'])
    def ad_performance(self, request):
        data = self.queryset.values('platform').annotate(
            total_impressions=Sum('impressions'),
            total_clicks=Sum('clicks'),
            total_conversions=Sum('conversions'),
            total_cost=Sum('cost'),
            total_revenue=Sum('revenue')
        ).order_by('-total_revenue')
        return Response(data)
