"""
Sessions API URLs - Multi-instance support
"""
from django.urls import path
from .views import (
    SessionListView, SessionStatusView, InitSessionView, RefreshQRView, 
    DisconnectSessionView, DeleteSessionView, SetPrimarySessionView,
    ActiveSessionsForRestorationView
)
from .webhooks import SessionWebhookView

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
    path('refresh-qr/<int:session_id>/', RefreshQRView.as_view(), name='session-refresh-qr-specific'),
    
    # Disconnect session
    path('disconnect/', DisconnectSessionView.as_view(), name='session-disconnect'),
    path('disconnect/<int:session_id>/', DisconnectSessionView.as_view(), name='session-disconnect-specific'),
    
    # Delete session
    path('delete/<int:session_id>/', DeleteSessionView.as_view(), name='session-delete'),
    
    # Set primary session
    path('set-primary/<int:session_id>/', SetPrimarySessionView.as_view(), name='session-set-primary'),
    
    # Webhook for Node.js status updates
    path('webhook/', SessionWebhookView.as_view(), name='session-webhook'),
    
    # Internal endpoint for session restoration (called by Node.js on startup)
    path('active-sessions/', ActiveSessionsForRestorationView.as_view(), name='active-sessions-restoration'),
]

