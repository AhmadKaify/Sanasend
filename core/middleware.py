"""
Custom middleware
"""
import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class APILoggingMiddleware(MiddlewareMixin):
    """Log API requests and responses"""
    
    def process_request(self, request):
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            execution_time = time.time() - request.start_time
            
            # Log API calls
            if request.path.startswith('/api/'):
                user = getattr(request, 'user', None)
                user_id = user.id if user and user.is_authenticated else None
                
                logger.info(
                    f"API Request: {request.method} {request.path} | "
                    f"User: {user_id} | "
                    f"Status: {response.status_code} | "
                    f"Time: {execution_time:.3f}s"
                )
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """Rate limiting middleware using Redis"""
    
    def process_request(self, request):
        # Only apply rate limiting to API endpoints
        if not request.path.startswith('/api/'):
            return None
            
        # Skip rate limiting for admin endpoints
        if request.path.startswith('/api/admin/'):
            return None
            
        # Get user from request
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return None
            
        # Check if user has API key (for API key authentication)
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return None
            
        # Rate limiting logic
        return self._check_rate_limits(request, user)
    
    def _check_rate_limits(self, request, user):
        """Check rate limits for the user"""
        try:
            now = timezone.now()
            user_id = user.id
            
            # Check daily message limit
            daily_limit = getattr(user, 'max_messages_per_day', settings.MAX_MESSAGES_PER_DAY)
            daily_key = f"rate_limit:daily:{user_id}:{now.date()}"
            daily_count = cache.get(daily_key, 0)
            
            if daily_count >= daily_limit:
                return self._rate_limit_response(
                    "Daily message limit exceeded",
                    daily_limit,
                    daily_count,
                    "daily"
                )
            
            # Check per-minute limit
            minute_limit = settings.MAX_MESSAGES_PER_MINUTE
            minute_key = f"rate_limit:minute:{user_id}:{now.strftime('%Y-%m-%d-%H-%M')}"
            minute_count = cache.get(minute_key, 0)
            
            if minute_count >= minute_limit:
                return self._rate_limit_response(
                    "Per-minute message limit exceeded",
                    minute_limit,
                    minute_count,
                    "minute"
                )
            
            return None
        except Exception as e:
            # If cache is unavailable (e.g., Redis not running), log and allow request
            logger.warning(f"Rate limit check cache error: {e}. Allowing request.")
            return None
    
    def _rate_limit_response(self, message, limit, current, period):
        """Return rate limit exceeded response"""
        return JsonResponse({
            'success': False,
            'message': message,
            'error_code': 'RATE_LIMIT_EXCEEDED',
            'rate_limit': {
                'limit': limit,
                'current': current,
                'period': period,
                'reset_time': self._get_reset_time(period)
            }
        }, status=429)
    
    def _get_reset_time(self, period):
        """Get reset time for the rate limit period"""
        now = timezone.now()
        if period == 'daily':
            return (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'minute':
            return now.replace(second=0, microsecond=0) + timedelta(minutes=1)
        return now


class UsageTrackingMiddleware(MiddlewareMixin):
    """Track API usage and increment counters"""
    
    def process_response(self, request, response):
        # Only track API endpoints
        if not request.path.startswith('/api/'):
            return response
            
        # Skip tracking for admin endpoints
        if request.path.startswith('/api/admin/'):
            return response
            
        # Get user from request
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return response
            
        # Track API usage
        self._track_api_usage(request, user, response)
        
        return response
    
    def _track_api_usage(self, request, user, response):
        """Track API usage in Redis"""
        try:
            now = timezone.now()
            user_id = user.id
            
            # Increment daily API requests
            daily_key = f"usage:daily_api:{user_id}:{now.date()}"
            cache.incr(daily_key)
            cache.expire(daily_key, 86400)  # Expire after 24 hours
            
            # Increment per-minute API requests
            minute_key = f"usage:minute_api:{user_id}:{now.strftime('%Y-%m-%d-%H-%M')}"
            cache.incr(minute_key)
            cache.expire(minute_key, 60)  # Expire after 1 minute
            
            # Track message sending specifically
            if (request.path in ['/api/v1/messages/send-text/', '/api/v1/messages/send-media/'] 
                and request.method == 'POST' 
                and response.status_code == 200):
                
                # Increment daily message count
                daily_msg_key = f"rate_limit:daily:{user_id}:{now.date()}"
                cache.incr(daily_msg_key)
                cache.expire(daily_msg_key, 86400)
                
                # Increment per-minute message count
                minute_msg_key = f"rate_limit:minute:{user_id}:{now.strftime('%Y-%m-%d-%H-%M')}"
                cache.incr(minute_msg_key)
                cache.expire(minute_msg_key, 60)
                
                # Track media vs text messages
                if request.path == '/api/v1/messages/send-media/':
                    media_key = f"usage:daily_media:{user_id}:{now.date()}"
                    cache.incr(media_key)
                    cache.expire(media_key, 86400)
        except Exception as e:
            # If cache is unavailable (e.g., Redis not running), log and continue
            logger.warning(f"API usage tracking cache error: {e}. Continuing without tracking.")

