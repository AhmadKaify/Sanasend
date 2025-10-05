"""
Custom decorators for the application
"""
from functools import wraps
from django.core.cache import cache
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


def rate_limit(limit=None, period='minute', key_func=None):
    """
    Rate limiting decorator
    
    Args:
        limit: Number of requests allowed (defaults to settings)
        period: 'minute' or 'daily'
        key_func: Function to generate cache key (defaults to user-based)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Get user from request
            user = getattr(request, 'user', None)
            if not user or not user.is_authenticated:
                return view_func(request, *args, **kwargs)
            
            # Determine limit
            if limit is None:
                if period == 'daily':
                    request_limit = getattr(user, 'max_messages_per_day', settings.MAX_MESSAGES_PER_DAY)
                else:
                    request_limit = settings.MAX_MESSAGES_PER_MINUTE
            else:
                request_limit = limit
            
            # Generate cache key
            if key_func:
                cache_key = key_func(request, period)
            else:
                now = timezone.now()
                user_id = user.id
                
                if period == 'daily':
                    cache_key = f"decorator_rate_limit:daily:{user_id}:{now.date()}"
                else:
                    cache_key = f"decorator_rate_limit:minute:{user_id}:{now.strftime('%Y-%m-%d-%H-%M')}"
            
            # Check current count
            current_count = cache.get(cache_key, 0)
            
            if current_count >= request_limit:
                # Rate limit exceeded
                reset_time = None
                if period == 'daily':
                    reset_time = (timezone.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                else:
                    reset_time = timezone.now().replace(second=0, microsecond=0) + timedelta(minutes=1)
                
                return JsonResponse({
                    'success': False,
                    'message': f'{period.title()} rate limit exceeded',
                    'error_code': 'RATE_LIMIT_EXCEEDED',
                    'rate_limit': {
                        'limit': request_limit,
                        'current': current_count,
                        'period': period,
                        'reset_time': reset_time.isoformat()
                    }
                }, status=429)
            
            # Increment counter
            cache.incr(cache_key)
            
            # Set expiration
            if period == 'daily':
                cache.expire(cache_key, 86400)  # 24 hours
            else:
                cache.expire(cache_key, 60)  # 1 minute
            
            # Call the original view
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def track_usage(view_func):
    """
    Decorator to track API usage
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Call the original view first
        response = view_func(request, *args, **kwargs)
        
        # Track usage if successful
        if response.status_code == 200:
            user = getattr(request, 'user', None)
            if user and user.is_authenticated:
                now = timezone.now()
                user_id = user.id
                
                # Track API request
                daily_key = f"usage:daily_api:{user_id}:{now.date()}"
                cache.incr(daily_key)
                cache.expire(daily_key, 86400)
                
                # Track specific endpoint usage
                endpoint_key = f"usage:endpoint:{user_id}:{request.path}:{now.date()}"
                cache.incr(endpoint_key)
                cache.expire(endpoint_key, 86400)
        
        return response
    
    return wrapper


def require_api_key(view_func):
    """
    Decorator to ensure API key authentication
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return JsonResponse({
                'success': False,
                'message': 'API key required',
                'error_code': 'API_KEY_REQUIRED'
            }, status=401)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
