from rest_framework import serializers
from .models import KnowledgeBaseEntry

class KnowledgeBaseEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBaseEntry
        fields = '__all__'
        read_only_fields = ('created_at',)
