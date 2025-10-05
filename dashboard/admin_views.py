"""
Admin dashboard views for system-wide statistics
"""
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from django.db.models import Count, Sum
from users.models import User
from sessions.models import WhatsAppSession
from messages.models import Message
from api_keys.models import APIKey
from analytics.models import UsageStats, APILog
import logging

logger = logging.getLogger(__name__)


@staff_member_required
def admin_dashboard(request):
    """Admin dashboard with system-wide statistics"""
    today = timezone.now().date()
    now = timezone.now()
    
    # User statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    new_users_today = User.objects.filter(date_joined__date=today).count()
    
    # Session statistics
    total_sessions = WhatsAppSession.objects.count()
    connected_sessions = WhatsAppSession.objects.filter(status='connected').count()
    disconnected_sessions = WhatsAppSession.objects.filter(status='disconnected').count()
    qr_pending_sessions = WhatsAppSession.objects.filter(status='qr_pending').count()
    
    # Message statistics
    total_messages = Message.objects.count()
    messages_today = Message.objects.filter(sent_at__date=today).count()
    sent_messages = Message.objects.filter(status='sent').count()
    failed_messages = Message.objects.filter(status='failed').count()
    pending_messages = Message.objects.filter(status='pending').count()
    
    # API Key statistics
    total_api_keys = APIKey.objects.count()
    active_api_keys = APIKey.objects.filter(is_active=True).count()
    
    # Usage statistics from database
    today_usage = UsageStats.objects.filter(date=today).aggregate(
        total_messages=Sum('messages_sent'),
        total_api_requests=Sum('api_requests'),
        total_media=Sum('media_sent')
    )
    
    # Get usage from Redis for real-time data
    redis_usage = {
        'daily_api_requests': 0,
        'daily_messages': 0,
        'daily_media': 0,
    }
    
    # Aggregate Redis data for all users
    for user in User.objects.filter(is_active=True):
        user_id = user.id
        redis_usage['daily_api_requests'] += cache.get(f"usage:daily_api:{user_id}:{today}", 0)
        redis_usage['daily_messages'] += cache.get(f"rate_limit:daily:{user_id}:{today}", 0)
        redis_usage['daily_media'] += cache.get(f"usage:daily_media:{user_id}:{today}", 0)
    
    # Recent activity
    recent_messages = Message.objects.order_by('-sent_at')[:10]
    recent_api_logs = APILog.objects.order_by('-timestamp')[:10]
    
    # Usage trends (last 7 days)
    usage_trend = []
    for i in range(7):
        date = today - timedelta(days=i)
        day_usage = UsageStats.objects.filter(date=date).aggregate(
            messages=Sum('messages_sent'),
            api_requests=Sum('api_requests'),
            media=Sum('media_sent')
        )
        usage_trend.append({
            'date': date,
            'messages': day_usage['messages'] or 0,
            'api_requests': day_usage['api_requests'] or 0,
            'media': day_usage['media'] or 0,
        })
    
    # Top users by message count
    top_users = User.objects.annotate(
        message_count=Count('message')
    ).order_by('-message_count')[:5]
    
    # System health indicators
    system_health = {
        'database': True,  # Assume OK if we can query
        'cache': False,
        'node_service': False,  # Would need to check Node.js service
    }
    
    # Check cache health
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            system_health['cache'] = True
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
    
    context = {
        # User stats
        'total_users': total_users,
        'active_users': active_users,
        'new_users_today': new_users_today,
        
        # Session stats
        'total_sessions': total_sessions,
        'connected_sessions': connected_sessions,
        'disconnected_sessions': disconnected_sessions,
        'qr_pending_sessions': qr_pending_sessions,
        
        # Message stats
        'total_messages': total_messages,
        'messages_today': messages_today,
        'sent_messages': sent_messages,
        'failed_messages': failed_messages,
        'pending_messages': pending_messages,
        
        # API stats
        'total_api_keys': total_api_keys,
        'active_api_keys': active_api_keys,
        
        # Usage stats
        'today_usage': today_usage,
        'redis_usage': redis_usage,
        'usage_trend': usage_trend,
        
        # Recent activity
        'recent_messages': recent_messages,
        'recent_api_logs': recent_api_logs,
        'top_users': top_users,
        
        # System health
        'system_health': system_health,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)


@staff_member_required
def user_analytics(request, user_id):
    """Detailed analytics for a specific user"""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return render(request, 'dashboard/error.html', {'error': 'User not found'})
    
    today = timezone.now().date()
    
    # User's session
    session = WhatsAppSession.objects.filter(user=user).first()
    
    # User's messages
    user_messages = Message.objects.filter(user=user).order_by('-sent_at')
    total_messages = user_messages.count()
    messages_today = user_messages.filter(sent_at__date=today).count()
    
    # User's API keys
    api_keys = APIKey.objects.filter(user=user).order_by('-created_at')
    
    # User's usage stats
    usage_stats = UsageStats.objects.filter(user=user).order_by('-date')[:30]
    
    # User's API logs
    api_logs = APILog.objects.filter(user=user).order_by('-timestamp')[:50]
    
    # Current usage from Redis
    user_id = user.id
    daily_api_requests = cache.get(f"usage:daily_api:{user_id}:{today}", 0)
    daily_messages = cache.get(f"rate_limit:daily:{user_id}:{today}", 0)
    daily_media = cache.get(f"usage:daily_media:{user_id}:{today}", 0)
    
    # Usage trends for this user
    user_usage_trend = []
    for i in range(30):
        date = today - timedelta(days=i)
        day_usage = UsageStats.objects.filter(user=user, date=date).first()
        user_usage_trend.append({
            'date': date,
            'messages': day_usage.messages_sent if day_usage else 0,
            'api_requests': day_usage.api_requests if day_usage else 0,
            'media': day_usage.media_sent if day_usage else 0,
        })
    
    context = {
        'user': user,
        'session': session,
        'total_messages': total_messages,
        'messages_today': messages_today,
        'api_keys': api_keys,
        'usage_stats': usage_stats,
        'api_logs': api_logs,
        'daily_api_requests': daily_api_requests,
        'daily_messages': daily_messages,
        'daily_media': daily_media,
        'user_usage_trend': user_usage_trend,
    }
    
    return render(request, 'dashboard/user_analytics.html', context)
