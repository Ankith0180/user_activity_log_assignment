from django.urls import path
from .views import UserActivityLogCreateView, UserActivityLogListView, UserActivityStatusUpdateView

urlpatterns = [
    path('logs/', UserActivityLogCreateView.as_view(), name='create-log'),
    path('logs/<int:user_id>/', UserActivityLogListView.as_view(), name='user-logs'),
    path('logs/<int:pk>/status/', UserActivityStatusUpdateView.as_view(), name='log-status-update'),
]
