from django.db import models


class SupervisorResponse(models.Model):
    # Each SupervisorResponse belongs to one Request (Request has many SupervisorResponses)
    request = models.ForeignKey('request.Request', on_delete=models.CASCADE, related_name='supervisor_responses')

    # Each SupervisorResponse belongs to one Supervisor (Supervisor has many SupervisorResponses)
    supervisor = models.ForeignKey('request.Supervisor', on_delete=models.CASCADE, related_name='supervisor_responses')

    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SupervisorResponse by {self.supervisor.name} for Request {self.request.id}"
