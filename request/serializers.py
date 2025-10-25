# request/serializers.py
from rest_framework import serializers
from .models import Customer, Supervisor, Request
from agent.serializers import AIResponseSerializer
from supervisor.serializers import SupervisorResponseSerializer

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class SupervisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervisor
        fields = '__all__'

class RequestSerializer(serializers.ModelSerializer):
    ai_responses = AIResponseSerializer(many=True, read_only=True)
    supervisor_responses = SupervisorResponseSerializer(many=True, read_only=True)

    class Meta:
        model = Request
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
