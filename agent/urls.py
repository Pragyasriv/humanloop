# agent/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import AIResponseViewSet

router = DefaultRouter()
router.register(r'airesponses', AIResponseViewSet, basename='airesponse')

urlpatterns = [
    path('', include(router.urls)),
]
