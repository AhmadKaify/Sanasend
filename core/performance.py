"""
Performance optimization utilities
"""
import logging
import time
from functools import wraps
from django.core.cache import cache
from django.db import connection
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch, F, Count, Sum, Avg
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


def query_optimization_decorator(func):
    """Decorator to optimize database queries"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Start query count
        initial_queries = len(connection.queries)
        start_time = time.time()
        
        result = func(*args, **kwargs)
        
        # Log query performance
        final_queries = len(connection.queries)
        query_count = final_queries - initial_queries
        execution_time = time.time() - start_time
        
        if query_count > 10:  # Log if more than 10 queries
            logger.warning(f"High query count in {func.__name__}: {query_count} queries in {execution_time:.3f}s")
        
        if execution_time > 1.0:  # Log if execution takes more than 1 second
            logger.warning(f"Slow execution in {func.__name__}: {execution_time:.3f}s")
        
        return result
    return wrapper


class DatabaseOptimizer:
    """Database optimization utilities"""
    
    @staticmethod
    def optimize_user_queries():
        """Optimize user-related queries"""
        from users.models import User
        
        # Add database indexes for common queries
        User._meta.indexes = [
            'username',
            'email',
            'is_active',
            'created_at',
        ]
    
    @staticmethod
    def optimize_session_queries():
        """Optimize session-related queries"""
        from sessions.models import WhatsAppSession
        
        # Add composite indexes
        WhatsAppSession._meta.indexes = [
            ('user', 'status'),
            ('user', 'is_primary'),
            ('status', 'last_active_at'),
            ('created_at',),
        ]
    
    @staticmethod
    def optimize_message_queries():
        """Optimize message-related queries"""
        from messages.models import Message
        
        # Add indexes for message queries
        Message._meta.indexes = [
            ('user', 'sent_at'),
            ('status', 'sent_at'),
            ('recipient', 'sent_at'),
            ('message_type', 'sent_at'),
        ]
    
    @staticmethod
    def optimize_analytics_queries():
        """Optimize analytics queries"""
        from analytics.models import UsageStats, APILog
        
        # Add indexes for analytics
        UsageStats._meta.indexes = [
            ('user', 'date'),
            ('date',),
        ]
        
        APILog._meta.indexes = [
            ('user', 'timestamp'),
            ('timestamp',),
            ('status_code', 'timestamp'),
        ]


class CacheManager:
    """Redis cache management utilities"""
    
    @staticmethod
    def cache_user_stats(user_id, stats_data, timeout=300):
        """Cache user statistics"""
        cache_key = f"user_stats:{user_id}"
        cache.set(cache_key, stats_data, timeout)
        return stats_data
    
    @staticmethod
    def get_user_stats(user_id):
        """Get cached user statistics"""
        cache_key = f"user_stats:{user_id}"
        return cache.get(cache_key)
    
    @staticmethod
    def cache_session_status(session_id, status_data, timeout=60):
        """Cache session status"""
        cache_key = f"session_status:{session_id}"
        cache.set(cache_key, status_data, timeout)
        return status_data
    
    @staticmethod
    def get_session_status(session_id):
        """Get cached session status"""
        cache_key = f"session_status:{session_id}"
        return cache.get(cache_key)
    
    @staticmethod
    def cache_api_response(endpoint, params, response_data, timeout=300):
        """Cache API responses"""
        # Create cache key from endpoint and params
        cache_key = f"api_response:{endpoint}:{hash(str(params))}"
        cache.set(cache_key, response_data, timeout)
        return response_data
    
    @staticmethod
    def get_cached_api_response(endpoint, params):
        """Get cached API response"""
        cache_key = f"api_response:{endpoint}:{hash(str(params))}"
        return cache.get(cache_key)
    
    @staticmethod
    def invalidate_user_cache(user_id):
        """Invalidate all caches for a user"""
        cache.delete(f"user_stats:{user_id}")
        cache.delete_pattern(f"session_status:*")  # This might not work with all Redis backends
        cache.delete_pattern(f"api_response:*")  # This might not work with all Redis backends


class QueryOptimizer:
    """Query optimization utilities"""
    
    @staticmethod
    def optimize_user_list_queryset():
        """Optimize user list queries"""
        from users.models import User
        from api_keys.models import APIKey
        from sessions.models import WhatsAppSession
        
        return User.objects.select_related().prefetch_related(
            Prefetch('api_keys', queryset=APIKey.objects.filter(is_active=True)),
            Prefetch('whatsapp_sessions', queryset=WhatsAppSession.objects.filter(status='connected'))
        )
    
    @staticmethod
    def optimize_session_list_queryset():
        """Optimize session list queries"""
        from sessions.models import WhatsAppSession
        
        return WhatsAppSession.objects.select_related('user').prefetch_related(
            'user__api_keys'
        )
    
    @staticmethod
    def optimize_message_list_queryset():
        """Optimize message list queries"""
        from messages.models import Message
        
        return Message.objects.select_related('user').order_by('-sent_at')
    
    @staticmethod
    def optimize_analytics_queryset():
        """Optimize analytics queries"""
        from analytics.models import UsageStats, APILog
        
        return {
            'usage_stats': UsageStats.objects.select_related('user'),
            'api_logs': APILog.objects.select_related('user').order_by('-timestamp')
        }


class PaginationOptimizer:
    """Pagination optimization utilities"""
    
    @staticmethod
    def optimize_pagination(queryset, page_size=20, page_number=1):
        """Optimize pagination with efficient counting"""
        paginator = Paginator(queryset, page_size)
        
        # Use approximate count for large datasets
        if queryset.count() > 10000:
            # Use estimated count for better performance
            estimated_count = queryset.extra(select={'count': 'COUNT(*)'}).values('count')[0]['count']
            paginator.count = estimated_count
        
        return paginator.get_page(page_number)
    
    @staticmethod
    def cursor_based_pagination(queryset, cursor=None, page_size=20):
        """Implement cursor-based pagination for better performance"""
        if cursor:
            queryset = queryset.filter(id__gt=cursor)
        
        # Get one extra item to check if there's a next page
        items = list(queryset[:page_size + 1])
        has_next = len(items) > page_size
        
        if has_next:
            items = items[:-1]  # Remove the extra item
        
        next_cursor = items[-1].id if items and has_next else None
        
        return {
            'items': items,
            'next_cursor': next_cursor,
            'has_next': has_next
        }


class ConnectionPoolOptimizer:
    """Database connection pool optimization"""
    
    @staticmethod
    def optimize_connection_settings():
        """Optimize database connection settings"""
        return {
            'CONN_MAX_AGE': 600,  # 10 minutes
            'OPTIONS': {
                'MAX_CONNS': 20,
                'MIN_CONNS': 5,
                'sslmode': 'prefer',
            }
        }
    
    @staticmethod
    def get_connection_stats():
        """Get database connection statistics"""
        from django.db import connections
        
        stats = {}
        for alias in connections:
            conn = connections[alias]
            if hasattr(conn, 'connection'):
                stats[alias] = {
                    'is_usable': conn.is_usable(),
                    'queries': len(conn.queries) if hasattr(conn, 'queries') else 0,
                }
        
        return stats


class LazyLoadingOptimizer:
    """Lazy loading optimization utilities"""
    
    @staticmethod
    def lazy_load_user_sessions(user):
        """Lazy load user sessions"""
        if not hasattr(user, '_sessions_loaded'):
            user.sessions = user.whatsapp_sessions.filter(status='connected')
            user._sessions_loaded = True
        return user.sessions
    
    @staticmethod
    def lazy_load_user_stats(user):
        """Lazy load user statistics"""
        if not hasattr(user, '_stats_loaded'):
            from analytics.models import UsageStats
            today = timezone.now().date()
            user.stats = UsageStats.objects.filter(user=user, date=today).first()
            user._stats_loaded = True
        return user.stats


class PerformanceMonitor:
    """Performance monitoring utilities"""
    
    @staticmethod
    def monitor_view_performance(view_func):
        """Monitor view performance"""
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            initial_queries = len(connection.queries)
            
            result = view_func(*args, **kwargs)
            
            execution_time = time.time() - start_time
            query_count = len(connection.queries) - initial_queries
            
            # Log performance metrics
            logger.info(f"View {view_func.__name__}: {execution_time:.3f}s, {query_count} queries")
            
            # Store performance data in cache for monitoring
            performance_key = f"performance:{view_func.__name__}"
            performance_data = {
                'execution_time': execution_time,
                'query_count': query_count,
                'timestamp': timezone.now().isoformat()
            }
            cache.set(performance_key, performance_data, 3600)  # Cache for 1 hour
            
            return result
        return wrapper
    
    @staticmethod
    def get_performance_stats():
        """Get performance statistics"""
        stats = {}
        
        # Get database stats
        stats['database'] = ConnectionPoolOptimizer.get_connection_stats()
        
        # Get cache stats
        stats['cache'] = {
            'keys': cache.get('cache_stats', {}),
        }
        
        return stats


def optimize_queryset(queryset, select_related=None, prefetch_related=None):
    """Optimize a queryset with select_related and prefetch_related"""
    if select_related:
        queryset = queryset.select_related(*select_related)
    
    if prefetch_related:
        queryset = queryset.prefetch_related(*prefetch_related)
    
    return queryset


def cache_result(timeout=300):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator


class NodeJSOptimizer:
    """Node.js service optimization utilities"""
    
    @staticmethod
    def optimize_node_service():
        """Optimize Node.js service configuration"""
        return {
            'max_connections': 100,
            'keep_alive': True,
            'timeout': 30000,
            'retry_attempts': 3,
            'retry_delay': 1000,
        }
    
    @staticmethod
    def get_node_service_stats():
        """Get Node.js service statistics"""
        import requests
        from django.conf import settings
        
        try:
            response = requests.get(f"{settings.NODE_SERVICE_URL}/health", timeout=5)
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get Node.js service stats: {e}")
            return None


# Performance optimization decorators
def optimize_queries(func):
    """Decorator to optimize database queries"""
    return query_optimization_decorator(func)


def monitor_performance(func):
    """Decorator to monitor function performance"""
    return PerformanceMonitor.monitor_view_performance(func)


def cache_performance(timeout=300):
    """Decorator to cache function results with performance monitoring"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Try cache first
            cache_key = f"perf_cache:{func.__name__}:{hash(str(args) + str(kwargs))}"
            result = cache.get(cache_key)
            
            if result is not None:
                logger.info(f"Cache hit for {func.__name__}")
                return result
            
            # Execute function
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Cache result
            cache.set(cache_key, result, timeout)
            
            logger.info(f"Function {func.__name__} executed in {execution_time:.3f}s and cached")
            return result
        return wrapper
    return decorator
