"""
API Keys URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import APIKeyViewSet

router = DefaultRouter()
router.register('', APIKeyViewSet, basename='apikey')

urlpatterns = [
    path('', include(router.urls)),
]

