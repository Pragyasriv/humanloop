# request/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, SupervisorViewSet, RequestViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'supervisors', SupervisorViewSet)
router.register(r'requests', RequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
