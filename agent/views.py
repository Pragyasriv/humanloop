from rest_framework import viewsets
from .models import AIResponse
from .serializers import AIResponseSerializer

class AIResponseViewSet(viewsets.ModelViewSet):
    queryset = AIResponse.objects.all().order_by('-created_at')
    serializer_class = AIResponseSerializer
