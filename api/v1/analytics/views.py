"""
Analytics API views
"""
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
from analytics.models import UsageStats, APILog
from analytics.serializers import UsageStatsSerializer, APILogSerializer
from core.responses import APIResponse
from core.permissions import HasValidAPIKey
import logging

logger = logging.getLogger(__name__)


class RateLimitInfoView(generics.GenericAPIView):
    """Get current rate limit information for the authenticated user"""
    permission_classes = [IsAuthenticated, HasValidAPIKey]
    
    def get(self, request):
        """Get rate limit information"""
        user = request.user
        now = timezone.now()
        user_id = user.id
        
        # Get current usage from Redis
        daily_key = f"rate_limit:daily:{user_id}:{now.date()}"
        minute_key = f"rate_limit:minute:{user_id}:{now.strftime('%Y-%m-%d-%H-%M')}"
        
        daily_count = cache.get(daily_key, 0)
        minute_count = cache.get(minute_key, 0)
        
        # Get limits
        daily_limit = getattr(user, 'max_messages_per_day', 1000)
        minute_limit = 10  # From settings
        
        # Calculate reset times
        daily_reset = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        minute_reset = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
        
        rate_limit_info = {
            'daily': {
                'limit': daily_limit,
                'used': daily_count,
                'remaining': max(0, daily_limit - daily_count),
                'reset_time': daily_reset.isoformat(),
            },
            'minute': {
                'limit': minute_limit,
                'used': minute_count,
                'remaining': max(0, minute_limit - minute_count),
                'reset_time': minute_reset.isoformat(),
            }
        }
        
        return APIResponse.success(
            data=rate_limit_info,
            message="Rate limit information retrieved successfully"
        )


class UsageStatsListView(generics.ListAPIView):
    """Get usage statistics for the authenticated user"""
    serializer_class = UsageStatsSerializer
    permission_classes = [IsAuthenticated, HasValidAPIKey]
    
    def get_queryset(self):
        """Filter usage stats by user and date range"""
        queryset = UsageStats.objects.filter(user=self.request.user)
        
        # Optional date filtering
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                pass
        
        return queryset.order_by('-date')


class APILogListView(generics.ListAPIView):
    """Get API logs for the authenticated user"""
    serializer_class = APILogSerializer
    permission_classes = [IsAuthenticated, HasValidAPIKey]
    
    def get_queryset(self):
        """Filter API logs by user and date range"""
        queryset = APILog.objects.filter(user=self.request.user)
        
        # Optional filtering
        endpoint = self.request.query_params.get('endpoint')
        status_code = self.request.query_params.get('status_code')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if endpoint:
            queryset = queryset.filter(endpoint__icontains=endpoint)
        
        if status_code:
            try:
                status_code = int(status_code)
                queryset = queryset.filter(status_code=status_code)
            except ValueError:
                pass
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(timestamp__date__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(timestamp__date__lte=end_date)
            except ValueError:
                pass
        
        return queryset.order_by('-timestamp')


class CurrentUsageView(generics.GenericAPIView):
    """Get current usage statistics from Redis"""
    permission_classes = [IsAuthenticated, HasValidAPIKey]
    
    def get(self, request):
        """Get current usage from Redis cache"""
        user = request.user
        now = timezone.now()
        user_id = user.id
        
        # Get current usage from Redis
        today = now.date()
        current_hour = now.strftime('%Y-%m-%d-%H')
        current_minute = now.strftime('%Y-%m-%d-%H-%M')
        
        # Daily stats
        daily_api_requests = cache.get(f"usage:daily_api:{user_id}:{today}", 0)
        daily_messages = cache.get(f"rate_limit:daily:{user_id}:{today}", 0)
        daily_media = cache.get(f"usage:daily_media:{user_id}:{today}", 0)
        
        # Hourly stats
        hourly_api_requests = cache.get(f"usage:hourly_api:{user_id}:{current_hour}", 0)
        
        # Per-minute stats
        minute_api_requests = cache.get(f"usage:minute_api:{user_id}:{current_minute}", 0)
        minute_messages = cache.get(f"rate_limit:minute:{user_id}:{current_minute}", 0)
        
        usage_data = {
            'today': {
                'api_requests': daily_api_requests,
                'messages_sent': daily_messages,
                'media_sent': daily_media,
                'text_messages': daily_messages - daily_media,
            },
            'this_hour': {
                'api_requests': hourly_api_requests,
            },
            'this_minute': {
                'api_requests': minute_api_requests,
                'messages_sent': minute_messages,
            },
            'timestamp': now.isoformat(),
        }
        
        return APIResponse.success(
            data=usage_data,
            message="Current usage statistics retrieved successfully"
        )


class UsageSummaryView(generics.GenericAPIView):
    """Get usage summary for the authenticated user"""
    permission_classes = [IsAuthenticated, HasValidAPIKey]
    
    def get(self, request):
        """Get usage summary"""
        user = request.user
        
        # Get date range (default to last 30 days)
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get usage stats from database
        usage_stats = UsageStats.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        # Calculate totals
        total_messages = sum(stats.messages_sent for stats in usage_stats)
        total_api_requests = sum(stats.api_requests for stats in usage_stats)
        total_media = sum(stats.media_sent for stats in usage_stats)
        
        # Get daily breakdown
        daily_breakdown = []
        for stats in usage_stats:
            daily_breakdown.append({
                'date': stats.date.isoformat(),
                'messages_sent': stats.messages_sent,
                'api_requests': stats.api_requests,
                'media_sent': stats.media_sent,
            })
        
        summary = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days,
            },
            'totals': {
                'messages_sent': total_messages,
                'api_requests': total_api_requests,
                'media_sent': total_media,
                'text_messages': total_messages - total_media,
            },
            'daily_breakdown': daily_breakdown,
        }
        
        return APIResponse.success(
            data=summary,
            message="Usage summary retrieved successfully"
        )