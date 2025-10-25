from rest_framework import serializers
from .models import AIResponse

class AIResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIResponse
        fields = '__all__'
        read_only_fields = ('created_at',)
