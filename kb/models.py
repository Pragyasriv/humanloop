from django.db import models

class KnowledgeBaseEntry(models.Model):
    question = models.TextField()  # changed from CharField(255)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    source_request = models.ForeignKey('request.Request', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.question[:100]
