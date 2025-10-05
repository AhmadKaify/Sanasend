"""
Analytics API URLs
"""
from django.urls import path
from . import views

urlpatterns = [
    path('rate-limits/', views.RateLimitInfoView.as_view(), name='rate-limit-info'),
    path('usage-stats/', views.UsageStatsListView.as_view(), name='usage-stats-list'),
    path('api-logs/', views.APILogListView.as_view(), name='api-logs-list'),
    path('current-usage/', views.CurrentUsageView.as_view(), name='current-usage'),
    path('usage-summary/', views.UsageSummaryView.as_view(), name='usage-summary'),
]

