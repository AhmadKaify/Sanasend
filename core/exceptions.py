"""
Custom exception handlers
"""
from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns consistent error responses
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response = {
            'success': False,
            'message': 'An error occurred',
            'errors': None,
            'error_code': None
        }
        
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                custom_response['message'] = response.data['detail']
            else:
                custom_response['message'] = str(response.data)
                custom_response['errors'] = response.data
        else:
            custom_response['message'] = str(response.data)
        
        response.data = custom_response
    
    return response


class APIException(Exception):
    """Base API exception"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = 'An error occurred'
    error_code = 'API_ERROR'
    
    def __init__(self, message=None, errors=None):
        self.message = message or self.default_message
        self.errors = errors
        super().__init__(self.message)


class SessionNotConnected(APIException):
    """WhatsApp session not connected"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = 'WhatsApp session is not connected'
    error_code = 'SESSION_NOT_CONNECTED'


class RateLimitExceeded(APIException):
    """Rate limit exceeded"""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_message = 'Rate limit exceeded'
    error_code = 'RATE_LIMIT_EXCEEDED'


class InvalidAPIKey(APIException):
    """Invalid API key"""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_message = 'Invalid API key'
    error_code = 'INVALID_API_KEY'

