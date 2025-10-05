"""
Messages API URLs
"""
from django.urls import path
from .views import SendTextMessageView, SendMediaMessageView, MessageListView

urlpatterns = [
    path('send-text/', SendTextMessageView.as_view(), name='send-text'),
    path('send-media/', SendMediaMessageView.as_view(), name='send-media'),
    path('list/', MessageListView.as_view(), name='message-list'),
]

