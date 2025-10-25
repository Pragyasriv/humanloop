from rest_framework.routers import DefaultRouter
from .views import KnowledgeBaseEntryViewSet

router = DefaultRouter()
router.register(r'knowledge-base', KnowledgeBaseEntryViewSet, basename='knowledgebase')

urlpatterns = router.urls
