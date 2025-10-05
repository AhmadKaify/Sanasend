"""
Authentication API views
"""
from rest_framework import views, permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from core.responses import APIResponse
from .serializers import LoginSerializer, UserProfileSerializer


class LoginView(views.APIView):
    """Admin login endpoint"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return APIResponse.success({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserProfileSerializer(user).data
        }, 'Login successful')


class LogoutView(views.APIView):
    """Logout endpoint (blacklist refresh token)"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return APIResponse.error(
                    'Refresh token is required',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return APIResponse.success(message='Logout successful')
        except Exception as e:
            return APIResponse.error(
                str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )


class MeView(views.APIView):
    """Get current user profile"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return APIResponse.success(serializer.data)

