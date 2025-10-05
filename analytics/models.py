from django.db import models
from django.conf import settings


class UsageStats(models.Model):
    """Daily usage statistics per user"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='usage_stats'
    )
    date = models.DateField()
    messages_sent = models.IntegerField(default=0)
    api_requests = models.IntegerField(default=0)
    media_sent = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'usage_stats'
        verbose_name = 'Usage Statistics'
        verbose_name_plural = 'Usage Statistics'
        unique_together = ['user', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', '-date']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.date}'


class APILog(models.Model):
    """API request logs"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='api_logs',
        null=True,
        blank=True
    )
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'api_logs'
        verbose_name = 'API Log'
        verbose_name_plural = 'API Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        user = self.user.username if self.user else 'Anonymous'
        return f'{user} - {self.method} {self.endpoint}'

