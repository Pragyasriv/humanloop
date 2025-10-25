# request/views.py
from rest_framework import viewsets
from .models import Customer, Supervisor, Request
from .serializers import CustomerSerializer, SupervisorSerializer, RequestSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class SupervisorViewSet(viewsets.ModelViewSet):
    queryset = Supervisor.objects.all()
    serializer_class = SupervisorSerializer

class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all().order_by('-created_at')
    serializer_class = RequestSerializer

    def list(self, request, *args, **kwargs):
        # Auto-update status for all pending requests (lightweight timeout)
        for req in Request.objects.filter(status='PENDING'):
            try:
                req.auto_update_status()
            except Exception:
                # fail-safe: don't block listing if one update errors
                pass

        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        req = self.get_object()
        try:
            req.auto_update_status()
        except Exception:
            pass
        return super().retrieve(request, *args, **kwargs)
