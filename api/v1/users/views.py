"""
User API views with performance optimization
"""
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from django.core.cache import cache
from django.db.models import Prefetch, Count, Q
from users.models import User
from api_keys.models import APIKey
from sessions.models import WhatsAppSession
from analytics.models import UsageStats
from .serializers import UserSerializer, UserCreateSerializer
from core.responses import APIResponse
from core.permissions import IsAdminUser
from core.performance import (
    optimize_queries, monitor_performance, cache_performance,
    QueryOptimizer, PaginationOptimizer, CacheManager
)


class UserViewSet(viewsets.ModelViewSet):
    """User management viewset with performance optimization (Admin only)"""
    
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """Optimize queryset with select_related and prefetch_related"""
        return QueryOptimizer.optimize_user_list_queryset()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    @monitor_performance
    def list(self, request, *args, **kwargs):
        """Optimized user list with caching"""
        # Check cache first
        cache_key = f"user_list:{hash(str(request.GET))}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return APIResponse.success(cached_result, 'Users retrieved from cache')
        
        # Optimize queryset
        queryset = self.get_queryset()
        
        # Apply filters
        queryset = self.filter_queryset(queryset)
        
        # Use optimized pagination
        page_size = self.paginator.page_size
        page_number = request.GET.get('page', 1)
        
        paginated_result = PaginationOptimizer.optimize_pagination(
            queryset, page_size, page_number
        )
        
        # Serialize data
        serializer = self.get_serializer(paginated_result, many=True)
        result = {
            'users': serializer.data,
            'total_count': paginated_result.paginator.count,
            'page_count': paginated_result.paginator.num_pages,
            'current_page': paginated_result.number,
        }
        
        # Cache result for 5 minutes
        cache.set(cache_key, result, 300)
        
        return APIResponse.success(result)
    
    @monitor_performance
    def retrieve(self, request, *args, **kwargs):
        """Optimized user detail with related data"""
        user = self.get_object()
        
        # Check cache
        cache_key = f"user_detail:{user.id}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return APIResponse.success(cached_result, 'User details retrieved from cache')
        
        # Get related data efficiently
        user_data = UserSerializer(user).data
        
        # Add session information
        sessions = user.whatsapp_sessions.filter(status='connected')
        user_data['active_sessions'] = len(sessions)
        user_data['primary_session'] = sessions.filter(is_primary=True).first()
        
        # Add API key information
        api_keys = user.api_keys.filter(is_active=True)
        user_data['active_api_keys'] = len(api_keys)
        
        # Add usage statistics
        today_stats = UsageStats.objects.filter(user=user).order_by('-date').first()
        user_data['today_stats'] = {
            'messages_sent': today_stats.messages_sent if today_stats else 0,
            'api_requests': today_stats.api_requests if today_stats else 0,
        } if today_stats else {'messages_sent': 0, 'api_requests': 0}
        
        # Cache result for 2 minutes
        cache.set(cache_key, user_data, 120)
        
        return APIResponse.success(user_data)
    
    @monitor_performance
    def create(self, request, *args, **kwargs):
        """Create user with performance monitoring"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Invalidate user list cache
        cache.delete_pattern('user_list:*')
        
        return APIResponse.created(
            UserSerializer(user).data,
            'User created successfully'
        )
    
    @action(detail=True, methods=['post'])
    @monitor_performance
    def activate(self, request, pk=None):
        """Activate user with cache invalidation"""
        user = self.get_object()
        user.is_active = True
        user.save()
        
        # Invalidate caches
        cache.delete(f"user_detail:{user.id}")
        cache.delete_pattern('user_list:*')
        
        return APIResponse.success(message='User activated successfully')
    
    @action(detail=True, methods=['post'])
    @monitor_performance
    def deactivate(self, request, pk=None):
        """Deactivate user with cache invalidation"""
        user = self.get_object()
        user.is_active = False
        user.save()
        
        # Invalidate caches
        cache.delete(f"user_detail:{user.id}")
        cache.delete_pattern('user_list:*')
        
        return APIResponse.success(message='User deactivated successfully')
    
    @action(detail=False, methods=['get'])
    @monitor_performance
    def stats(self, request):
        """Get user statistics with caching"""
        cache_key = 'user_stats_summary'
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return APIResponse.success(cached_stats, 'User statistics from cache')
        
        # Calculate statistics efficiently
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        users_with_sessions = User.objects.filter(
            whatsapp_sessions__status='connected'
        ).distinct().count()
        users_with_api_keys = User.objects.filter(
            api_keys__is_active=True
        ).distinct().count()
        
        stats = {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'users_with_sessions': users_with_sessions,
            'users_with_api_keys': users_with_api_keys,
        }
        
        # Cache for 10 minutes
        cache.set(cache_key, stats, 600)
        
        return APIResponse.success(stats)

