"""
Unified response structures for API consistency
"""
from rest_framework.response import Response
from rest_framework import status


class APIResponse:
    """Unified API response structure"""
    
    @staticmethod
    def success(data=None, message="Success", status_code=status.HTTP_200_OK):
        """Return success response"""
        return Response({
            'success': True,
            'message': message,
            'data': data
        }, status=status_code)
    
    @staticmethod
    def error(message="Error", errors=None, error_code=None, status_code=status.HTTP_400_BAD_REQUEST):
        """Return error response"""
        return Response({
            'success': False,
            'message': message,
            'errors': errors,
            'error_code': error_code
        }, status=status_code)
    
    @staticmethod
    def created(data=None, message="Created successfully"):
        """Return created response"""
        return APIResponse.success(data, message, status.HTTP_201_CREATED)
    
    @staticmethod
    def no_content(message="Deleted successfully"):
        """Return no content response"""
        return Response({
            'success': True,
            'message': message
        }, status=status.HTTP_204_NO_CONTENT)

