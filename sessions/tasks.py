"""
Celery tasks for session management
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from sessions.models import WhatsAppSession
from sessions.services import WhatsAppService
from sessions.session_pool import SessionPoolService
import logging

logger = logging.getLogger(__name__)


@shared_task
def cleanup_expired_qr_codes():
    """
    Clean up expired QR codes and update session status
    Runs every minute to check for expired QR codes
    """
    try:
        now = timezone.now()
        
        # Find sessions with expired QR codes
        expired_sessions = WhatsAppSession.objects.filter(
            status='qr_pending',
            qr_expires_at__lt=now
        ).select_related('user')
        
        count = 0
        user_ids_to_invalidate = set()
        
        for session in expired_sessions:
            logger.info(f'Cleaning up expired QR code for session {session.session_id}')
            
            # Try to disconnect from Node.js service
            try:
                whatsapp_service = WhatsAppService()
                whatsapp_service.disconnect_session(session.session_id)
            except Exception as e:
                logger.warning(f'Failed to disconnect expired session {session.session_id}: {e}')
            
            # Update status to disconnected
            session.status = 'disconnected'
            session.qr_code = None
            session.qr_expires_at = None
            session.save()
            user_ids_to_invalidate.add(session.user_id)
            count += 1
        
        # Invalidate cache for affected users
        for user_id in user_ids_to_invalidate:
            SessionPoolService.invalidate_user_sessions_cache(user_id)
        
        if count > 0:
            logger.info(f'Cleaned up {count} expired QR codes')
        
        return f'Cleaned up {count} expired QR codes'
        
    except Exception as e:
        logger.error(f'Error in cleanup_expired_qr_codes task: {e}')
        return f'Error: {str(e)}'


@shared_task
def sync_session_status():
    """
    Sync session status with Node.js service for all active sessions
    Runs every 5 minutes to ensure database is in sync
    """
    try:
        whatsapp_service = WhatsAppService()
        
        # Get all sessions that should be active
        active_sessions = WhatsAppSession.objects.filter(
            status__in=['qr_pending', 'connected', 'initializing']
        ).select_related('user')
        
        synced_count = 0
        updated_count = 0
        user_ids_to_invalidate = set()
        
        for session in active_sessions:
            try:
                # Get status from Node.js
                result = whatsapp_service.get_session_status(session.session_id)
                
                node_status = result.get('status')
                
                # Update if status has changed
                if node_status and node_status != session.status:
                    logger.info(f'Syncing session {session.session_id}: {session.status} -> {node_status}')
                    
                    old_status = session.status
                    session.status = node_status
                    session.last_active_at = timezone.now()
                    
                    # Update phone number if connected
                    if node_status == 'connected' and result.get('phoneNumber'):
                        session.phone_number = result['phoneNumber']
                        if not session.connected_at:
                            session.connected_at = timezone.now()
                    
                    session.save()
                    updated_count += 1
                    
                    # Mark for cache invalidation if connected status changed
                    if old_status == 'connected' or node_status == 'connected':
                        user_ids_to_invalidate.add(session.user_id)
                
                synced_count += 1
                
            except Exception as e:
                logger.warning(f'Failed to sync session {session.session_id}: {e}')
                # If session doesn't exist in Node.js, mark as disconnected
                if 'not_found' in str(e).lower() or 'unavailable' in str(e).lower():
                    if session.status == 'connected':
                        user_ids_to_invalidate.add(session.user_id)
                    session.status = 'disconnected'
                    session.save()
                    updated_count += 1
        
        # Invalidate cache for affected users
        for user_id in user_ids_to_invalidate:
            SessionPoolService.invalidate_user_sessions_cache(user_id)
        
        logger.info(f'Session sync complete: {synced_count} checked, {updated_count} updated')
        return f'Synced {synced_count} sessions, updated {updated_count}'
        
    except Exception as e:
        logger.error(f'Error in sync_session_status task: {e}')
        return f'Error: {str(e)}'


@shared_task
def cleanup_disconnected_sessions():
    """
    Clean up sessions that have been disconnected for more than 7 days
    Runs daily
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=7)
        
        old_sessions = WhatsAppSession.objects.filter(
            status='disconnected',
            updated_at__lt=cutoff_date
        )
        
        count = old_sessions.count()
        
        if count > 0:
            logger.info(f'Deleting {count} old disconnected sessions')
            old_sessions.delete()
        
        return f'Deleted {count} old disconnected sessions'
        
    except Exception as e:
        logger.error(f'Error in cleanup_disconnected_sessions task: {e}')
        return f'Error: {str(e)}'

