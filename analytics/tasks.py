"""
Celery tasks for analytics and usage tracking
"""
from celery import shared_task
from django.utils import timezone
from django.core.cache import cache
from datetime import datetime, timedelta
from .models import UsageStats, APILog
from users.models import User
import logging

logger = logging.getLogger(__name__)


@shared_task
def aggregate_daily_usage_stats():
    """Aggregate daily usage statistics for all users"""
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    logger.info(f"Starting daily usage aggregation for {yesterday}")
    
    # Get all users
    users = User.objects.filter(is_active=True)
    aggregated_count = 0
    
    for user in users:
        try:
            # Get usage data from Redis
            user_id = user.id
            date_key = yesterday.strftime('%Y-%m-%d')
            
            # Get API requests count
            api_requests = cache.get(f"usage:daily_api:{user_id}:{yesterday}", 0)
            
            # Get messages sent count
            messages_sent = cache.get(f"rate_limit:daily:{user_id}:{yesterday}", 0)
            
            # Get media messages count
            media_sent = cache.get(f"usage:daily_media:{user_id}:{yesterday}", 0)
            
            # Create or update UsageStats record
            usage_stats, created = UsageStats.objects.get_or_create(
                user=user,
                date=yesterday,
                defaults={
                    'messages_sent': messages_sent,
                    'api_requests': api_requests,
                    'media_sent': media_sent,
                }
            )
            
            if not created:
                # Update existing record
                usage_stats.messages_sent = messages_sent
                usage_stats.api_requests = api_requests
                usage_stats.media_sent = media_sent
                usage_stats.save()
            
            aggregated_count += 1
            
        except Exception as e:
            logger.error(f"Error aggregating stats for user {user.id}: {e}")
            continue
    
    logger.info(f"Daily usage aggregation completed. Processed {aggregated_count} users")
    return f"Aggregated stats for {aggregated_count} users"


@shared_task
def cleanup_old_usage_data():
    """Clean up old usage data from Redis"""
    cutoff_date = timezone.now().date() - timedelta(days=30)
    
    logger.info(f"Cleaning up usage data older than {cutoff_date}")
    
    # Get all users
    users = User.objects.filter(is_active=True)
    cleaned_keys = 0
    
    for user in users:
        user_id = user.id
        
        # Clean up old daily API request keys
        for i in range(31):  # Check last 31 days
            check_date = cutoff_date - timedelta(days=i)
            api_key = f"usage:daily_api:{user_id}:{check_date}"
            rate_key = f"rate_limit:daily:{user_id}:{check_date}"
            media_key = f"usage:daily_media:{user_id}:{check_date}"
            
            # Delete old keys
            for key in [api_key, rate_key, media_key]:
                if cache.get(key) is not None:
                    cache.delete(key)
                    cleaned_keys += 1
    
    logger.info(f"Cleanup completed. Removed {cleaned_keys} old keys")
    return f"Cleaned up {cleaned_keys} old usage keys"


@shared_task
def cleanup_inactive_sessions():
    """Clean up inactive WhatsApp sessions"""
    from sessions.models import WhatsAppSession
    from django.utils import timezone
    
    # Find sessions that haven't been active for more than 24 hours
    cutoff_time = timezone.now() - timedelta(hours=24)
    inactive_sessions = WhatsAppSession.objects.filter(
        last_active_at__lt=cutoff_time,
        status='connected'
    )
    
    logger.info(f"Found {inactive_sessions.count()} inactive sessions")
    
    cleaned_count = 0
    for session in inactive_sessions:
        try:
            # Update session status to disconnected
            session.status = 'disconnected'
            session.save()
            cleaned_count += 1
            logger.info(f"Marked session {session.id} as disconnected")
        except Exception as e:
            logger.error(f"Error cleaning session {session.id}: {e}")
    
    logger.info(f"Session cleanup completed. Processed {cleaned_count} sessions")
    return f"Cleaned up {cleaned_count} inactive sessions"


@shared_task
def cleanup_old_messages():
    """Clean up old message records and files"""
    from messages.models import Message
    from django.utils import timezone
    import os
    
    # Find messages older than 90 days
    cutoff_date = timezone.now() - timedelta(days=90)
    old_messages = Message.objects.filter(sent_at__lt=cutoff_date)
    
    logger.info(f"Found {old_messages.count()} old messages to clean up")
    
    cleaned_count = 0
    for message in old_messages:
        try:
            # Delete associated media files if they exist
            if message.content and message.message_type in ['image', 'document', 'video']:
                file_path = message.content
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted media file: {file_path}")
            
            # Delete the message record
            message.delete()
            cleaned_count += 1
            
        except Exception as e:
            logger.error(f"Error cleaning message {message.id}: {e}")
    
    logger.info(f"Message cleanup completed. Removed {cleaned_count} old messages")
    return f"Cleaned up {cleaned_count} old messages"


@shared_task
def health_check():
    """Perform system health check"""
    from django.db import connection
    from django.core.cache import cache
    from sessions.models import WhatsAppSession
    
    health_status = {
        'timestamp': timezone.now().isoformat(),
        'database': False,
        'cache': False,
        'active_sessions': 0,
        'total_users': 0,
    }
    
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['database'] = True
        
        # Check cache connection
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health_status['cache'] = True
        
        # Get active sessions count
        health_status['active_sessions'] = WhatsAppSession.objects.filter(
            status='connected'
        ).count()
        
        # Get total users count
        health_status['total_users'] = User.objects.filter(is_active=True).count()
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        health_status['error'] = str(e)
    
    logger.info(f"Health check completed: {health_status}")
    return health_status
