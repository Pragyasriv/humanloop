from django.urls import path
from .views import SupervisorResponseAPIView

urlpatterns = [
    path('supervisorresponses/', SupervisorResponseAPIView.as_view(), name='supervisorresponses'),
]
