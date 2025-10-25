# agent/models.py
from django.db import models


class AIResponse(models.Model):
    # Each AIResponse belongs to one Request (Request has many AIResponses)
    request = models.ForeignKey('request.Request', on_delete=models.CASCADE, related_name='ai_responses')
    
    # Each AIResponse belongs to one Supervisor (optional)
    supervisor = models.ForeignKey('request.Supervisor', on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_responses')
    
    # Text answer from AI or forwarded supervisor answer
    answer_text = models.TextField(blank=True, null=True)
    
    # Audio file containing the AI's answer (optional)
    answer_audio = models.FileField(upload_to='ai_responses/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AIResponse for Request {self.request.id}"
