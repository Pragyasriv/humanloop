from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from supervisor.models import SupervisorResponse
from kb.models import KnowledgeBaseEntry
from request.models import Request
from django.utils import timezone
from agent.models import AIResponse  # ✅ for automatic follow-up creation


class SupervisorResponseAPIView(APIView):
    """
    GET: List all unanswered supervisor responses (empty answers)
    POST: Submit answer for a question
    """

    def get(self, request):
        # Get all pending supervisor responses (unanswered ones)
        pending = SupervisorResponse.objects.filter(answer__exact="").select_related('request')
        data = [
            {
                "id": s.id,
                "request_id": s.request.id,
                "question": s.request.question,
                "customer_id": s.request.customer_id,
                "created_at": s.created_at
            }
            for s in pending
        ]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        sr_id = request.data.get("id")
        answer = (request.data.get("answer") or "").strip()

        if not sr_id or not answer:
            return Response(
                {"detail": "Both 'id' and 'answer' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            sr = SupervisorResponse.objects.get(id=sr_id)
        except SupervisorResponse.DoesNotExist:
            return Response(
                {"detail": "SupervisorResponse not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # ✅ Save supervisor's provided answer
        sr.answer = answer
        sr.save()

        # ✅ Update the linked request status
        req = sr.request
        req.status = "RESOLVED"
        req.resolved_at = timezone.now()
        req.save()

        # ✅ Create AIResponse for follow-up
        AIResponse.objects.create(
            request=req,
            answer_text=answer
        )

        # ✅ Add the new Q&A to the Knowledge Base
        KnowledgeBaseEntry.objects.create(
            question=req.question,
            answer=answer,
            source_request=req
        )

        return Response(
            {"detail": "Answer saved, AIResponse created, and added to Knowledge Base."},
            status=status.HTTP_201_CREATED
        )
