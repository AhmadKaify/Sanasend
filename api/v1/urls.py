"""
API v1 URL Configuration
"""
from django.urls import path, include

app_name = 'api_v1'

urlpatterns = [
    path('auth/', include('api.v1.auth.urls')),
    path('users/', include('api.v1.users.urls')),
    path('sessions/', include('api.v1.sessions.urls')),
    path('messages/', include('api.v1.messages.urls')),
    path('api-keys/', include('api.v1.api_keys.urls')),
    path('analytics/', include('api.v1.analytics.urls')),
]

