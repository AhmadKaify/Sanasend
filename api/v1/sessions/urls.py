"""
Sessions API URLs - Multi-instance support
"""
from django.urls import path
from .views import (
    SessionListView, SessionStatusView, InitSessionView, RefreshQRView, 
    DisconnectSessionView, DeleteSessionView, SetPrimarySessionView
)

urlpatterns = [
    # List all sessions
    path('list/', SessionListView.as_view(), name='session-list'),
    
    # Session status (specific session or primary)
    path('status/', SessionStatusView.as_view(), name='session-status'),
    path('status/<int:session_id>/', SessionStatusView.as_view(), name='session-status-specific'),
    
    # Initialize new session
    path('init/', InitSessionView.as_view(), name='session-init'),
    
    # Refresh QR code
    path('refresh-qr/', RefreshQRView.as_view(), name='session-refresh-qr'),
    
    # Disconnect session
    path('disconnect/', DisconnectSessionView.as_view(), name='session-disconnect'),
    path('disconnect/<int:session_id>/', DisconnectSessionView.as_view(), name='session-disconnect-specific'),
    
    # Delete session
    path('delete/<int:session_id>/', DeleteSessionView.as_view(), name='session-delete'),
    
    # Set primary session
    path('set-primary/<int:session_id>/', SetPrimarySessionView.as_view(), name='session-set-primary'),
]

