from rest_framework import serializers
from .models import SupervisorResponse

class SupervisorResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupervisorResponse
        fields = '__all__'
        read_only_fields = ('created_at',)
