from rest_framework import viewsets
from .models import KnowledgeBaseEntry
from .serializers import KnowledgeBaseEntrySerializer

class KnowledgeBaseEntryViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeBaseEntry.objects.all().order_by('-created_at')
    serializer_class = KnowledgeBaseEntrySerializer
