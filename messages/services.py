"""
Message service layer with multi-instance support
"""
from django.conf import settings
from sessions.services import WhatsAppService
from sessions.models import WhatsAppSession
from sessions.session_pool import SessionPoolService
from messages.models import Message
from core.exceptions import SessionNotConnected
import logging

logger = logging.getLogger(__name__)


class MessageService:
    """Service for sending messages with session pool support"""
    
    def __init__(self):
        self.whatsapp_service = WhatsAppService()
        self.session_pool = SessionPoolService()
    
    def send_text_message(self, user, recipient, message_text):
        """
        Send text message using session pool with fallback
        """
        # Check if user has any connected sessions
        available_sessions = self.session_pool.get_available_sessions(user)
        if not available_sessions:
            raise SessionNotConnected('No active WhatsApp sessions. Please connect at least one session.')
        
        # Create message record
        message = Message.objects.create(
            user=user,
            recipient=recipient,
            message_type='text',
            content=message_text,
            status='pending'
        )
        
        try:
            # Send using session pool with fallback
            result = self.session_pool.send_with_fallback(
                user=user,
                recipient=recipient,
                message_data={'content': message_text},
                message_type='text'
            )
            
            if result.get('success'):
                message.status = 'sent'
                message.save()
                
                # Log which session was used
                session_used = result.get('session_used', {})
                logger.info(f'Message sent via session {session_used.get("instance_name", "unknown")} (ID: {session_used.get("id")})')
                
                return {
                    'success': True,
                    'messageId': result.get('message_id'),
                    'timestamp': result.get('timestamp'),
                    'dbId': message.id,
                    'sessionUsed': session_used,
                    'attempts': result.get('attempts', [])
                }
            else:
                message.status = 'failed'
                message.error_message = result.get('error', 'Failed to send message')
                message.save()
                
                logger.error(f'Failed to send message after {result.get("sessions_tried", 0)} attempts: {result.get("error")}')
                
                return {
                    'success': False,
                    'error': result.get('error', 'Failed to send message'),
                    'dbId': message.id,
                    'attempts': result.get('attempts', [])
                }
        
        except Exception as e:
            logger.error(f'Error sending text message for user {user.id}: {e}')
            message.status = 'failed'
            message.error_message = str(e)
            message.save()
            raise
    
    def send_media_message(self, user, recipient, file, caption='', media_type='image'):
        """
        Send media message using session pool with fallback
        """
        # Check if user has any connected sessions
        available_sessions = self.session_pool.get_available_sessions(user)
        if not available_sessions:
            raise SessionNotConnected('No active WhatsApp sessions. Please connect at least one session.')
        
        # Save file and get URL
        from django.core.files.storage import default_storage
        file_path = default_storage.save(f'whatsapp_media/{user.id}/{file.name}', file)
        media_url = f'{settings.MEDIA_URL}{file_path}'
        
        # Make it absolute URL
        if not media_url.startswith('http'):
            # Get Django base URL from environment or use default
            base_url = settings.DJANGO_BASE_URL if hasattr(settings, 'DJANGO_BASE_URL') else 'http://localhost:8000'
            media_url = f'{base_url}{media_url}'
        
        # Create message record
        message = Message.objects.create(
            user=user,
            recipient=recipient,
            message_type=media_type,
            content=file_path,
            status='pending'
        )
        
        try:
            # Send using session pool with fallback
            result = self.session_pool.send_with_fallback(
                user=user,
                recipient=recipient,
                message_data={
                    'media_url': media_url,
                    'caption': caption
                },
                message_type=media_type
            )
            
            if result.get('success'):
                message.status = 'sent'
                message.save()
                
                # Log which session was used
                session_used = result.get('session_used', {})
                logger.info(f'Media message sent via session {session_used.get("instance_name", "unknown")} (ID: {session_used.get("id")})')
                
                return {
                    'success': True,
                    'messageId': result.get('message_id'),
                    'timestamp': result.get('timestamp'),
                    'dbId': message.id,
                    'filePath': file_path,
                    'sessionUsed': session_used,
                    'attempts': result.get('attempts', [])
                }
            else:
                message.status = 'failed'
                message.error_message = result.get('error', 'Failed to send media')
                message.save()
                
                logger.error(f'Failed to send media after {result.get("sessions_tried", 0)} attempts: {result.get("error")}')
                
                return {
                    'success': False,
                    'error': result.get('error', 'Failed to send media'),
                    'dbId': message.id,
                    'attempts': result.get('attempts', [])
                }
        
        except Exception as e:
            logger.error(f'Error sending media message for user {user.id}: {e}')
            message.status = 'failed'
            message.error_message = str(e)
            message.save()
            raise

