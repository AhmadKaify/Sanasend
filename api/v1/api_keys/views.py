"""
API Key views
"""
from rest_framework import viewsets
from api_keys.models import APIKey
from .serializers import APIKeySerializer, APIKeyCreateSerializer
from core.responses import APIResponse
from core.permissions import IsAdminUser


class APIKeyViewSet(viewsets.ModelViewSet):
    """API Key management viewset (Admin only)"""
    
    queryset = APIKey.objects.all().select_related('user')
    permission_classes = [IsAdminUser]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return APIKeyCreateSerializer
        return APIKeySerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        api_key = serializer.save()
        
        # Return the raw key only once
        raw_key = getattr(api_key, '_raw_key', None)
        
        response_data = APIKeySerializer(api_key).data
        if raw_key:
            response_data['key'] = raw_key
            response_data['warning'] = 'Save this key. It will not be shown again.'
        
        return APIResponse.created(response_data, 'API Key created successfully')

