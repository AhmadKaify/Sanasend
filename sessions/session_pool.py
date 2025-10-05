"""
Session Pool Service for Multi-Instance WhatsApp Management
"""
import random
import logging
from typing import List, Optional, Dict, Any
from django.db import transaction
from django.core.cache import cache
from sessions.models import WhatsAppSession
from sessions.services import WhatsAppService
from core.exceptions import SessionNotConnected

logger = logging.getLogger(__name__)


class SessionPoolService:
    """Service for managing multiple WhatsApp sessions with load balancing and fallback"""
    
    # Cache timeout in seconds
    SESSION_CACHE_TIMEOUT = 60
    
    def __init__(self):
        self.whatsapp_service = WhatsAppService()
    
    @staticmethod
    def _get_user_sessions_cache_key(user_id):
        """Get cache key for user's connected sessions"""
        return f"sessions:user:{user_id}:connected"
    
    @staticmethod
    def invalidate_user_sessions_cache(user_id):
        """Invalidate cached sessions for a user"""
        cache_key = SessionPoolService._get_user_sessions_cache_key(user_id)
        cache.delete(cache_key)
        logger.debug(f'Invalidated session cache for user {user_id}')
    
    def get_available_sessions(self, user) -> List[WhatsAppSession]:
        """Get all connected sessions for a user (with caching)"""
        cache_key = self._get_user_sessions_cache_key(user.id)
        sessions = cache.get(cache_key)
        
        if sessions is None:
            # Cache miss - query database
            sessions = list(WhatsAppSession.objects.filter(
                user=user,
                status='connected'
            ).select_related('user').order_by('last_active_at'))
            
            # Cache for 60 seconds
            cache.set(cache_key, sessions, self.SESSION_CACHE_TIMEOUT)
            logger.debug(f'Cached {len(sessions)} sessions for user {user.id}')
        else:
            logger.debug(f'Retrieved {len(sessions)} sessions from cache for user {user.id}')
        
        return sessions
    
    def get_random_session(self, user) -> Optional[WhatsAppSession]:
        """Get a random connected session for load balancing"""
        sessions = self.get_available_sessions(user)
        
        if not sessions:
            return None
        
        # Weighted random selection (prefer less recently used sessions)
        weights = []
        for session in sessions:
            # Give higher weight to sessions that haven't been used recently
            # This helps distribute load more evenly
            weight = 1.0
            if session.last_active_at:
                # Older last_active_at = higher weight
                from django.utils import timezone
                time_diff = timezone.now() - session.last_active_at
                weight += time_diff.total_seconds() / 3600  # Add hours since last use
            weights.append(weight)
        
        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        else:
            weights = [1.0 / len(sessions)] * len(sessions)
        
        return random.choices(sessions, weights=weights, k=1)[0]
    
    def get_primary_session(self, user) -> Optional[WhatsAppSession]:
        """Get the primary session for a user"""
        return WhatsAppSession.objects.filter(
            user=user,
            is_primary=True,
            status='connected'
        ).first()
    
    def send_with_fallback(self, user, recipient: str, message_data: Dict[str, Any], 
                          message_type: str = 'text') -> Dict[str, Any]:
        """
        Send message with automatic fallback to other sessions if first attempt fails
        
        Args:
            user: User object
            recipient: Phone number to send to
            message_data: Message data (content, media_url, etc.
            message_type: Type of message ('text', 'image', 'document', 'video')
        
        Returns:
            Dict with success status, message_id, session_used, and attempts
        """
        sessions = self.get_available_sessions(user)
        
        if not sessions:
            raise SessionNotConnected('No connected WhatsApp sessions available')
        
        # Try primary session first, then random selection
        primary_session = self.get_primary_session(user)
        if primary_session:
            sessions = [primary_session] + [s for s in sessions if s.id != primary_session.id]
        else:
            # Randomize order for load balancing
            random.shuffle(sessions)
        
        last_error = None
        attempts = []
        
        for i, session in enumerate(sessions):
            try:
                logger.info(f'Attempting to send message via session {session.instance_name} (attempt {i+1})')
                
                # Update last active time atomically
                from django.utils import timezone
                WhatsAppSession.objects.filter(id=session.id).update(
                    last_active_at=timezone.now()
                )
                # Update local object for consistency
                session.last_active_at = timezone.now()
                
                # Send message based on type
                if message_type == 'text':
                    result = self.whatsapp_service.send_text_message(
                        session.session_id,
                        recipient,
                        message_data['content']
                    )
                elif message_type in ['image', 'document', 'video']:
                    result = self.whatsapp_service.send_media_message(
                        session.session_id,
                        recipient,
                        message_data['media_url'],
                        message_data.get('caption', ''),
                        message_type
                    )
                else:
                    raise ValueError(f'Unsupported message type: {message_type}')
                
                if result.get('success'):
                    logger.info(f'Message sent successfully via session {session.instance_name}')
                    return {
                        'success': True,
                        'message_id': result.get('messageId'),
                        'session_used': {
                            'id': session.id,
                            'instance_name': session.instance_name,
                            'session_id': session.session_id
                        },
                        'attempts': attempts + [{
                            'session_id': session.id,
                            'instance_name': session.instance_name,
                            'success': True,
                            'message_id': result.get('messageId')
                        }],
                        'timestamp': result.get('timestamp')
                    }
                else:
                    error_msg = result.get('message', 'Unknown error')
                    logger.warning(f'Failed to send via session {session.instance_name}: {error_msg}')
                    
                    # Check if error indicates session is not actually connected
                    if any(keyword in error_msg.lower() for keyword in ['not found', 'reconnect', 'closed', 'not connected', 'not ready']):
                        logger.warning(f'Session {session.instance_name} appears disconnected, updating status')
                        session.status = 'disconnected'
                        session.save(update_fields=['status'])
                    
                    attempts.append({
                        'session_id': session.id,
                        'instance_name': session.instance_name,
                        'success': False,
                        'error': error_msg
                    })
                    last_error = error_msg
                    
            except Exception as e:
                error_msg = str(e)
                logger.error(f'Exception sending via session {session.instance_name}: {error_msg}')
                
                # Check if exception indicates disconnection
                if 'WhatsApp service error' in error_msg or 'timeout' in error_msg.lower():
                    logger.warning(f'Session {session.instance_name} might be disconnected, updating status')
                    session.status = 'disconnected'
                    session.save(update_fields=['status'])
                
                attempts.append({
                    'session_id': session.id,
                    'instance_name': session.instance_name,
                    'success': False,
                    'error': error_msg
                })
                last_error = error_msg
        
        # All sessions failed
        logger.error(f'All {len(sessions)} sessions failed to send message to {recipient}')
        return {
            'success': False,
            'error': f'Failed to send message after trying {len(sessions)} sessions. Last error: {last_error}',
            'attempts': attempts,
            'sessions_tried': len(sessions)
        }
    
    def get_session_stats(self, user) -> Dict[str, Any]:
        """Get statistics about user's sessions"""
        all_sessions = WhatsAppSession.objects.filter(user=user)
        connected_sessions = all_sessions.filter(status='connected')
        
        return {
            'total_sessions': all_sessions.count(),
            'connected_sessions': connected_sessions.count(),
            'disconnected_sessions': all_sessions.filter(status='disconnected').count(),
            'qr_pending_sessions': all_sessions.filter(status='qr_pending').count(),
            'primary_session': {
                'id': connected_sessions.filter(is_primary=True).first().id,
                'instance_name': connected_sessions.filter(is_primary=True).first().instance_name
            } if connected_sessions.filter(is_primary=True).exists() else None,
            'available_for_sending': connected_sessions.count() > 0
        }
    
    def rotate_primary_session(self, user) -> Optional[WhatsAppSession]:
        """Rotate primary session to a different connected session (with locking)"""
        connected_sessions = self.get_available_sessions(user)
        
        if len(connected_sessions) < 2:
            return None
        
        # Use atomic transaction with row-level locking
        with transaction.atomic():
            # Lock and get current primary
            current_primary = WhatsAppSession.objects.select_for_update().filter(
                user=user,
                is_primary=True,
                status='connected'
            ).first()
            
            # Find next session (excluding current primary)
            other_sessions_ids = [s.id for s in connected_sessions if current_primary and s.id != current_primary.id]
            if not other_sessions_ids:
                return None
            
            # Lock and get next primary session
            next_primary = WhatsAppSession.objects.select_for_update().filter(
                id=other_sessions_ids[0]
            ).first()
            
            if not next_primary:
                return None
            
            # Remove primary flag from all sessions
            WhatsAppSession.objects.select_for_update().filter(
                user=user, 
                is_primary=True
            ).update(is_primary=False)
            
            # Set new primary
            next_primary.is_primary = True
            next_primary.save()
        
        # Invalidate cache (outside transaction)
        self.invalidate_user_sessions_cache(user.id)
        
        logger.info(f'Rotated primary session from {current_primary.instance_name if current_primary else "None"} to {next_primary.instance_name}')
        return next_primary
