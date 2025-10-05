"""
Session webhook handler for receiving status updates from Node.js service
"""
from rest_framework import views, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from core.responses import APIResponse
from sessions.models import WhatsAppSession
from sessions.session_pool import SessionPoolService
from api_keys.authentication import NodeServiceAuthentication
import logging

logger = logging.getLogger(__name__)


class SessionWebhookView(views.APIView):
    """
    Webhook endpoint to receive session status updates from Node.js service
    
    Expected payload:
    {
        "sessionId": "user_123_instance_primary",
        "userId": 123,
        "status": "connected",
        "phoneNumber": "1234567890",  // optional
        "timestamp": "2024-01-01T00:00:00Z"
    }
    """
    
    authentication_classes = [NodeServiceAuthentication]
    permission_classes = [AllowAny]  # Authentication handled by NodeServiceAuthentication
    
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            session_id = request.data.get('sessionId')
            user_id = request.data.get('userId')
            new_status = request.data.get('status')
            phone_number = request.data.get('phoneNumber')
            error_msg = request.data.get('error')
            reason = request.data.get('reason')
            
            if not session_id or not new_status:
                return APIResponse.error(
                    'sessionId and status are required',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Find session in database
            session = WhatsAppSession.objects.filter(session_id=session_id).first()
            
            if not session:
                logger.warning(f'Webhook received for unknown session: {session_id}')
                return APIResponse.error(
                    'Session not found',
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            # Update session status
            session.status = new_status
            session.last_active_at = timezone.now()
            
            # Handle different status updates
            if new_status == 'connected':
                if phone_number:
                    session.phone_number = phone_number
                if not session.connected_at:
                    session.connected_at = timezone.now()
                # Clear QR code data on connection
                session.qr_code = None
                session.qr_expires_at = None
                
            elif new_status == 'disconnected':
                # Clear QR code data on disconnect
                session.qr_code = None
                session.qr_expires_at = None
                
            elif new_status == 'auth_failed':
                # Clear QR code data on auth failure
                session.qr_code = None
                session.qr_expires_at = None
            
            session.save()
            
            # Invalidate session cache for the user
            SessionPoolService.invalidate_user_sessions_cache(session.user_id)
            
            logger.info(f'Session {session_id} status updated to {new_status} via webhook')
            
            return APIResponse.success({
                'message': 'Session status updated successfully',
                'session_id': session_id,
                'new_status': new_status
            })
            
        except Exception as e:
            logger.error(f'Error processing webhook: {e}')
            return APIResponse.error(
                'Failed to process webhook',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

