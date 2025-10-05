"""
Message API views
"""
from rest_framework import views, generics, permissions, status
from messages.models import Message
from messages.services import MessageService
from .serializers import MessageSerializer, SendTextMessageSerializer, SendMediaMessageSerializer
from core.responses import APIResponse
from core.permissions import IsActiveUser
from core.exceptions import SessionNotConnected, APIException
import logging

logger = logging.getLogger(__name__)


class SendTextMessageView(views.APIView):
    """Send text message"""
    
    permission_classes = [IsActiveUser]
    
    def post(self, request):
        # Validate request
        serializer = SendTextMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        recipient = serializer.validated_data['recipient']
        message_text = serializer.validated_data['message']
        user = request.user
        
        try:
            # Send message via service
            message_service = MessageService()
            result = message_service.send_text_message(user, recipient, message_text)
            
            if result.get('success'):
                return APIResponse.success({
                    'messageId': result.get('messageId'),
                    'timestamp': result.get('timestamp'),
                    'dbId': result.get('dbId'),
                    'message': 'Message sent successfully'
                })
            else:
                return APIResponse.error(
                    result.get('error', 'Failed to send message'),
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        except SessionNotConnected as e:
            return APIResponse.error(
                str(e),
                error_code='SESSION_NOT_CONNECTED',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except APIException as e:
            logger.error(f'API error sending text message: {e}')
            return APIResponse.error(
                str(e),
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f'Unexpected error sending text message: {e}')
            return APIResponse.error(
                f'Failed to send message: {str(e)}',
                error_code='MESSAGE_SEND_ERROR',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SendMediaMessageView(views.APIView):
    """Send media message"""
    
    permission_classes = [IsActiveUser]
    
    def post(self, request):
        # Validate request
        serializer = SendMediaMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        recipient = serializer.validated_data['recipient']
        media_type = serializer.validated_data['media_type']
        file = serializer.validated_data['file']
        caption = serializer.validated_data.get('caption', '')
        user = request.user
        
        try:
            # Send media via service
            message_service = MessageService()
            result = message_service.send_media_message(
                user, recipient, file, caption, media_type
            )
            
            if result.get('success'):
                return APIResponse.success({
                    'messageId': result.get('messageId'),
                    'timestamp': result.get('timestamp'),
                    'dbId': result.get('dbId'),
                    'filePath': result.get('filePath'),
                    'message': 'Media sent successfully'
                })
            else:
                return APIResponse.error(
                    result.get('error', 'Failed to send media'),
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        except SessionNotConnected as e:
            return APIResponse.error(
                str(e),
                error_code='SESSION_NOT_CONNECTED',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except APIException as e:
            logger.error(f'API error sending media message: {e}')
            return APIResponse.error(
                str(e),
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f'Unexpected error sending media message: {e}')
            return APIResponse.error(
                f'Failed to send media: {str(e)}',
                error_code='MEDIA_SEND_ERROR',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MessageListView(generics.ListAPIView):
    """List user's messages"""
    
    permission_classes = [IsActiveUser]
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        return Message.objects.filter(user=self.request.user)

