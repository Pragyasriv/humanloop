# request/models.py
from django.db import models
from django.utils import timezone
from datetime import timedelta

TIMEOUT_MINUTES = 5  # change this if you want a different timeout

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Supervisor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name


class Request(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RESOLVED', 'Resolved'),
        ('UNRESOLVED', 'Unresolved'),
    ]

    # Each Request belongs to one Customer (Customer has many Requests)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="requests")

    # Each Request is optionally assigned to one Supervisor (Supervisor has many Requests)
    supervisor = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True, blank=True, related_name="requests")

    question = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request {self.id} - {self.question}"

    def auto_update_status(self):
        """
        Mark as UNRESOLVED if the request has been PENDING for longer than TIMEOUT_MINUTES.
        This is a lightweight Option-B approach that runs when a Request is fetched/listed.
        """
        if self.status == 'PENDING':
            cutoff = timezone.now() - timedelta(minutes=TIMEOUT_MINUTES)
            if self.created_at < cutoff:
                self.status = 'UNRESOLVED'
                self.save()
