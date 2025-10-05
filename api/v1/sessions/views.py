"""
Session API views - Multi-instance support
"""
from rest_framework import views, permissions, status
from django.utils import timezone
from datetime import timedelta
from core.responses import APIResponse
from core.permissions import IsActiveUser
from core.exceptions import APIException
from sessions.models import WhatsAppSession
from sessions.services import WhatsAppService
from sessions.session_pool import SessionPoolService
from api_keys.authentication import NodeServiceAuthentication
import logging
import random

logger = logging.getLogger(__name__)


class SessionListView(views.APIView):
    """List all sessions for user"""
    
    permission_classes = [IsActiveUser]
    
    def get(self, request):
        user = request.user
        
        try:
            sessions = WhatsAppSession.objects.filter(user=user).select_related('user').order_by('-created_at')
            
            session_data = []
            for session in sessions:
                session_data.append({
                    'id': session.id,
                    'instance_name': session.instance_name,
                    'session_id': session.session_id,
                    'status': session.status,
                    'phone_number': session.phone_number,
                    'is_primary': session.is_primary,
                    'connected_at': session.connected_at,
                    'last_active_at': session.last_active_at,
                    'created_at': session.created_at
                })
            
            return APIResponse.success({
                'sessions': session_data,
                'total_count': len(session_data),
                'connected_count': len([s for s in session_data if s['status'] == 'connected'])
            })
            
        except Exception as e:
            logger.error(f'Error listing sessions for user {user.id}: {e}')
            return APIResponse.error(
                'Failed to list sessions',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SessionStatusView(views.APIView):
    """Get specific session status"""
    
    permission_classes = [IsActiveUser]
    
    def get(self, request, session_id=None):
        user = request.user
        
        try:
            # Get specific session or first connected session
            if session_id:
                session = WhatsAppSession.objects.filter(user=user, id=session_id).first()
            else:
                # Get primary session or first connected session
                session = WhatsAppSession.objects.filter(
                    user=user, 
                    is_primary=True
                ).first()
                
                if not session:
                    session = WhatsAppSession.objects.filter(
                        user=user, 
                        status='connected'
                    ).first()
            
            if not session:
                return APIResponse.success({
                    'exists': False,
                    'status': 'not_found',
                    'message': 'No session found. Please initialize a session first.'
                })
            
            # Get status from Node.js service
            whatsapp_service = WhatsAppService()
            result = whatsapp_service.get_session_status(session.session_id)
            
            # Update database if needed
            if result.get('status') and result['status'] != session.status:
                old_status = session.status
                session.status = result['status']
                session.last_active_at = timezone.now()
                
                if result['status'] == 'connected' and result.get('phoneNumber'):
                    session.phone_number = result['phoneNumber']
                    if not session.connected_at:
                        session.connected_at = timezone.now()
                
                session.save()
                
                # Invalidate cache if status changed to/from connected
                if old_status == 'connected' or result['status'] == 'connected':
                    SessionPoolService.invalidate_user_sessions_cache(user.id)
            
            return APIResponse.success({
                'id': session.id,
                'instance_name': session.instance_name,
                'sessionId': session.session_id,
                'status': result.get('status'),
                'phoneNumber': result.get('phoneNumber'),
                'isReady': result.get('isReady'),
                'qrCode': session.qr_code if session.status == 'qr_pending' else None,
                'qrExpiresAt': session.qr_expires_at.isoformat() if session.qr_expires_at else None,
                'connectedAt': session.connected_at,
                'lastActiveAt': session.last_active_at,
                'is_primary': session.is_primary
            })
            
        except APIException as e:
            logger.error(f'Error getting session status for user {user.id}: {e}')
            return APIResponse.error(
                str(e),
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f'Unexpected error getting session status: {e}')
            return APIResponse.error(
                'Failed to get session status',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InitSessionView(views.APIView):
    """Initialize new WhatsApp session instance"""
    
    permission_classes = [IsActiveUser]
    
    def post(self, request):
        user = request.user
        
        try:
            # Get instance name from request
            instance_name = request.data.get('instance_name', 'Instance')
            
            # Check if instance name already exists
            existing_session = WhatsAppSession.objects.filter(
                user=user, 
                instance_name=instance_name
            ).first()
            
            if existing_session:
                return APIResponse.error(
                    f'Instance "{instance_name}" already exists',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Check max instances limit (10)
            existing_count = WhatsAppSession.objects.filter(user=user).count()
            if existing_count >= 10:
                return APIResponse.error(
                    'Maximum 10 WhatsApp instances allowed per user',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate unique session ID
            session_id = f"user_{user.id}_instance_{instance_name.lower().replace(' ', '_')}"
            
            # Call Node.js service to initialize
            whatsapp_service = WhatsAppService()
            result = whatsapp_service.init_session(user.id, session_id)
            
            if not result.get('success'):
                return APIResponse.error(
                    result.get('error', 'Failed to initialize session'),
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Create new session in database
            # QR code expires in 60 seconds
            qr_expires_at = timezone.now() + timedelta(seconds=60)
            
            # Set as primary if it's the first session
            is_primary = existing_count == 0
            
            session = WhatsAppSession.objects.create(
                user=user,
                instance_name=instance_name,
                session_id=session_id,
                status=result.get('status', 'qr_pending'),
                qr_code=result.get('qrCode'),
                qr_expires_at=qr_expires_at,
                is_primary=is_primary
            )
            
            # Invalidate session cache
            SessionPoolService.invalidate_user_sessions_cache(user.id)
            
            return APIResponse.success({
                'id': session.id,
                'instance_name': session.instance_name,
                'sessionId': session_id,
                'status': result.get('status'),
                'qrCode': result.get('qrCode'),
                'qrExpiresAt': qr_expires_at.isoformat(),
                'is_primary': is_primary,
                'message': 'Session initialized. Please scan the QR code with WhatsApp within 60 seconds.'
            })
            
        except APIException as e:
            logger.error(f'Error initializing session for user {user.id}: {e}')
            return APIResponse.error(
                str(e),
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f'Unexpected error initializing session: {e}')
            return APIResponse.error(
                'Failed to initialize session',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RefreshQRView(views.APIView):
    """Refresh QR code for pending session"""
    
    permission_classes = [IsActiveUser]
    
    def post(self, request, session_id=None):
        user = request.user
        
        try:
            # Get specific session or first non-connected session
            if session_id:
                session = WhatsAppSession.objects.filter(user=user, id=session_id).first()
            else:
                session = WhatsAppSession.objects.filter(user=user).exclude(status='connected').first()
            
            if not session:
                return APIResponse.error(
                    'No session found',
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            if session.status == 'connected':
                return APIResponse.error(
                    'Session is already connected',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Disconnect old session first to avoid "Client already exists" error
            whatsapp_service = WhatsAppService()
            try:
                whatsapp_service.disconnect_session(session.session_id)
                logger.info(f'Disconnected old session for user {user.id} before refresh')
            except Exception as e:
                # Continue even if disconnect fails (session might not exist in Node.js)
                logger.warning(f'Failed to disconnect old session during refresh: {e}')
            
            # Generate new session ID with timestamp to ensure uniqueness
            import time
            timestamp = int(time.time())
            new_session_id = f"user_{user.id}_instance_{session.instance_name.lower().replace(' ', '_')}_{timestamp}"
            
            # Call Node.js service to initialize with new QR
            result = whatsapp_service.init_session(user.id, new_session_id)
            
            if not result.get('success'):
                return APIResponse.error(
                    result.get('error', 'Failed to refresh QR code'),
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Update session with new QR code
            qr_expires_at = timezone.now() + timedelta(seconds=60)
            session.session_id = new_session_id
            session.status = result.get('status', 'qr_pending')
            session.qr_code = result.get('qrCode')
            session.qr_expires_at = qr_expires_at
            session.save()
            
            return APIResponse.success({
                'sessionId': new_session_id,
                'status': result.get('status'),
                'qrCode': result.get('qrCode'),
                'qrExpiresAt': qr_expires_at.isoformat(),
                'message': 'QR code refreshed. Please scan within 60 seconds.'
            })
            
        except APIException as e:
            logger.error(f'Error refreshing QR for user {user.id}: {e}')
            return APIResponse.error(
                str(e),
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f'Unexpected error refreshing QR: {e}')
            return APIResponse.error(
                'Failed to refresh QR code',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DisconnectSessionView(views.APIView):
    """Disconnect specific WhatsApp session"""
    
    permission_classes = [IsActiveUser]
    
    def post(self, request, session_id=None):
        user = request.user
        
        try:
            # Get specific session or first connected session
            if session_id:
                session = WhatsAppSession.objects.filter(user=user, id=session_id).first()
            else:
                session = WhatsAppSession.objects.filter(user=user, status='connected').first()
            
            if not session:
                return APIResponse.error(
                    'No session found',
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            # Call Node.js service to disconnect
            whatsapp_service = WhatsAppService()
            result = whatsapp_service.disconnect_session(session.session_id)
            
            if not result.get('success'):
                return APIResponse.error(
                    result.get('message', 'Failed to disconnect session'),
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Update database
            session.status = 'disconnected'
            session.qr_code = None
            session.qr_expires_at = None
            session.save()
            
            # Invalidate session cache
            SessionPoolService.invalidate_user_sessions_cache(user.id)
            
            return APIResponse.success({
                'message': f'Session "{session.instance_name}" disconnected successfully'
            })
            
        except APIException as e:
            logger.error(f'Error disconnecting session for user {user.id}: {e}')
            return APIResponse.error(
                str(e),
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f'Unexpected error disconnecting session: {e}')
            return APIResponse.error(
                'Failed to disconnect session',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeleteSessionView(views.APIView):
    """Delete WhatsApp session instance"""
    
    permission_classes = [IsActiveUser]
    
    def delete(self, request, session_id):
        user = request.user
        
        try:
            # Get session from database
            session = WhatsAppSession.objects.filter(user=user, id=session_id).first()
            
            if not session:
                return APIResponse.error(
                    'Session not found',
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            # Disconnect session first if connected
            if session.status == 'connected':
                whatsapp_service = WhatsAppService()
                try:
                    whatsapp_service.disconnect_session(session.session_id)
                except Exception as e:
                    logger.warning(f'Failed to disconnect session before deletion: {e}')
            
            # Delete session from database
            instance_name = session.instance_name
            user_id = session.user_id
            session.delete()
            
            # Invalidate session cache
            SessionPoolService.invalidate_user_sessions_cache(user_id)
            
            return APIResponse.success({
                'message': f'Session "{instance_name}" deleted successfully'
            })
            
        except Exception as e:
            logger.error(f'Error deleting session for user {user.id}: {e}')
            return APIResponse.error(
                'Failed to delete session',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SetPrimarySessionView(views.APIView):
    """Set primary session"""
    
    permission_classes = [IsActiveUser]
    
    def post(self, request, session_id):
        user = request.user
        
        try:
            # Use atomic transaction with row-level locking for race condition safety
            with transaction.atomic():
                # Lock all user sessions to prevent concurrent updates
                target_session = WhatsAppSession.objects.select_for_update().filter(
                    user=user, 
                    id=session_id
                ).first()
                
                if not target_session:
                    return APIResponse.error(
                        'Session not found',
                        status_code=status.HTTP_404_NOT_FOUND
                    )
                
                # Remove primary flag from all other sessions (with lock)
                WhatsAppSession.objects.select_for_update().filter(
                    user=user, 
                    is_primary=True
                ).exclude(id=session_id).update(is_primary=False)
                
                # Set target session as primary
                target_session.is_primary = True
                target_session.save()
            
            # Invalidate session cache (outside transaction)
            SessionPoolService.invalidate_user_sessions_cache(user.id)
            
            return APIResponse.success({
                'message': f'Session "{target_session.instance_name}" set as primary'
            })
            
        except Exception as e:
            logger.error(f'Error setting primary session for user {user.id}: {e}')
            return APIResponse.error(
                'Failed to set primary session',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ActiveSessionsForRestorationView(views.APIView):
    """
    Get all connected sessions for restoration after Node.js restart
    This endpoint is called by the Node.js service on startup
    """
    
    authentication_classes = [NodeServiceAuthentication]
    permission_classes = []  # Authenticated via NodeServiceAuthentication
    
    def get(self, request):
        try:
            # Get all sessions that should be connected (already has select_related)
            sessions = WhatsAppSession.objects.filter(
                status='connected'
            ).select_related('user').values(
                'id',
                'session_id',
                'user_id',
                'instance_name',
                'phone_number'
            )
            
            session_list = list(sessions)
            
            logger.info(f'Restoration query: found {len(session_list)} connected sessions')
            
            return APIResponse.success({
                'sessions': session_list,
                'count': len(session_list)
            })
            
        except Exception as e:
            logger.error(f'Error getting active sessions for restoration: {e}')
            return APIResponse.error(
                'Failed to get active sessions',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

