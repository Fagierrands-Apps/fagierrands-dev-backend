from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class DailyMetrics(models.Model):
    date = models.DateField(unique=True)
    total_orders = models.IntegerField(default=0)
    completed_orders = models.IntegerField(default=0)
    cancelled_orders = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    new_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Daily Metrics"
        ordering = ['-date']

    def __str__(self):
        return f"Metrics - {self.date}"


class UserRetention(models.Model):
    date = models.DateField()
    cohort_month = models.DateField()
    users_count = models.IntegerField(default=0)
    retention_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('date', 'cohort_month')
        ordering = ['-date']

    def __str__(self):
        return f"Retention - {self.date}"


class ServicePerformance(models.Model):
    date = models.DateField()
    service_type = models.CharField(max_length=100)
    total_orders = models.IntegerField(default=0)
    avg_completion_time = models.DurationField(null=True, blank=True)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('date', 'service_type')
        ordering = ['-date']

    def __str__(self):
        return f"{self.service_type} - {self.date}"


class CustomerSatisfaction(models.Model):
    date = models.DateField()
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.IntegerField(default=0)
    positive_reviews = models.IntegerField(default=0)
    negative_reviews = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Satisfaction - {self.date}"


class AdvertisementMetrics(models.Model):
    date = models.DateField()
    platform = models.CharField(max_length=100)
    impressions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Advertisement Metrics"
        unique_together = ('date', 'platform')
        ordering = ['-date']

    def __str__(self):
        return f"{self.platform} - {self.date}"
