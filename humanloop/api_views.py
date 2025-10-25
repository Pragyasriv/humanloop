# humanloop/api_views.py

import difflib
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models.functions import Cast
from django.db.models import TextField
from kb.models import KnowledgeBaseEntry
from request.models import Request, Supervisor
from agent.models import AIResponse
from supervisor.models import SupervisorResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging

TRIGRAM_THRESHOLD = 0.45   # similarity threshold for trigram match
DIFFLIB_CUTOFF = 0.75       # fallback similarity threshold for difflib


class ChatAPIView(APIView):
    """
    POST /api/chat/
    Body: { "customer_id": 1, "question": "..." }
    """

    def post(self, request):

        customer_id = request.data.get("customer_id")
        question = (request.data.get("question") or "").strip()

        if not question or not customer_id:
            return Response(
                {"detail": "customer_id and question are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        print(f"🔍 Incoming question from customer {customer_id}: {question}")
        kb_match = None

        # --- 1️⃣ Try TrigramSimilarity (Postgres full-text) ---
        try:
            kb_qs = KnowledgeBaseEntry.objects.annotate(
                qtext=Cast('question', TextField()),
                similarity=TrigramSimilarity('question', question)
            ).order_by('-similarity')

            kb_match = kb_qs.filter(similarity__gt=TRIGRAM_THRESHOLD).first()

            if kb_match:
                print(f"✅ Trigram KB match found: '{kb_match.question[:80]}'")
        except Exception as e:
            print("⚠️ Trigram query error:", repr(e))

        # --- 2️⃣ If trigram matched ---
        if kb_match:
            req = Request.objects.create(customer_id=customer_id, question=question, status='RESOLVED')
            AIResponse.objects.create(request=req, answer_text=kb_match.answer)
            return Response(
                {
                    "answer": kb_match.answer,
                    "source": "ai",
                    "similarity": round(getattr(kb_match, "similarity", 0) or 0, 3),
                    "request_id": req.id
                },
                status=status.HTTP_200_OK
            )

        # --- 3️⃣ Fallback: difflib match ---
        try:
            all_qs = list(KnowledgeBaseEntry.objects.values_list('question', flat=True))
            if all_qs:
                best = difflib.get_close_matches(question, all_qs, n=1, cutoff=DIFFLIB_CUTOFF)
                if best:
                    kb_match = KnowledgeBaseEntry.objects.filter(question=best[0]).first()
                    print(f"✅ difflib KB match: '{kb_match.question[:80]}'")
        except Exception as e:
            print("⚠️ difflib fallback error:", repr(e))

        if kb_match:
            req = Request.objects.create(customer_id=customer_id, question=question, status='RESOLVED')
            #AIResponse.objects.create(request=req, answer_text=kb_match.answer)
            return Response(
                {
                    "answer": kb_match.answer,
                    "source": "ai",
                    "method": "difflib",
                    "request_id": req.id
                },
                status=status.HTTP_200_OK
            )

        # --- 4️⃣ No match: escalate to supervisor ---
        try:
            print("⚠️ No KB match found → Escalating to supervisor.")
            req = Request.objects.create(customer_id=customer_id, question=question, status='PENDING')

            supervisor = Supervisor.objects.first()
            if not supervisor:
                print("⚠️ No supervisor exists in DB!")
                return Response(
                    {"answer": "No supervisor available to handle this request."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            SupervisorResponse.objects.create(
                request=req,
                supervisor=supervisor,
                answer=""  # empty for now
            )

            return Response(
                {
                    "answer": "Please wait, let me connect with supervisor…",
                    "source": "pending",
                    "request_id": req.id
                },
                status=status.HTTP_202_ACCEPTED
            )


        except Exception as e:
            print("❌ Error while escalating to supervisor:", repr(e))
            return Response(
                {"error": "Failed to escalate question", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================
# 🆕 ChatFollowUpAPIView → check if supervisor answered yet
# ============================================================

class ChatFollowUpAPIView(APIView):
    """
    GET /api/chat/followup/<request_id>/
    Returns the supervisor answer if available.
    """

    def get(self, request, request_id, *args, **kwargs):
        from agent.models import AIResponse
        from request.models import Request

        try:
            req = Request.objects.get(id=request_id)
        except Request.DoesNotExist:
            return Response({"detail": "Invalid request ID"}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Force response as JSON only
        request.accepted_renderer = None
        request.accepted_media_type = 'application/json'

        # ✅ Supervisor has answered
        if req.status == "RESOLVED":
            ai_response = AIResponse.objects.filter(request=req).first()
            if ai_response:
                return Response(
                    {"answer": ai_response.answer_text, "source": "supervisor"},
                    status=status.HTTP_200_OK,
                    content_type="application/json"
                )

        # Still pending
        return Response(
            {"answer": "Still waiting for supervisor…", "source": "pending"},
            status=status.HTTP_202_ACCEPTED,
            content_type="application/json"
        )


# --- LiveKit Token Generation ---
from rest_framework.decorators import api_view
from rest_framework.response import Response
import os, uuid
from livekit import api


@api_view(["GET"])
def generate_livekit_token(request):
  LIVEKIT_URL = os.getenv("LIVEKIT_URL", "wss://frontdesk-g6uqpour.livekit.cloud")
  identity = f"caller-{uuid.uuid4().hex[:6]}"
  room_name = request.GET.get("room", "salon-room")

  token = api.AccessToken(os.getenv('LIVEKIT_API_KEY'), os.getenv('LIVEKIT_API_SECRET')) \
    .with_identity(identity) \
    .with_name("my name") \
    .with_grants(api.VideoGrants(
        room_join=True,
        room=room_name,
    ))

  return Response({
        "token": token.to_jwt(),
        "wsUrl": LIVEKIT_URL,
        "room": room_name,
        "identity": identity
    })

# @api_view(["GET"])
# def generate_livekit_token(request):
#     """
#     Generates a LiveKit token for joining a voice room with full permissions.
#     """

#     LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
#     LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
#     LIVEKIT_URL = os.getenv("LIVEKIT_URL", "wss://frontdesk-g6uqpour.livekit.cloud")

#     if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
#         return Response({"error": "Missing LiveKit API credentials."}, status=500)

#     try:
#         # Import with multiple fallbacks
#         try:
#             from livekit.api import AccessToken, VideoGrants
#         except ImportError:
#             from livekit import api
#             AccessToken = api.AccessToken
#             VideoGrants = api.VideoGrants

#         identity = f"caller-{uuid.uuid4().hex[:6]}"
#         room_name = request.GET.get("room", "salon-room")

#         print(f"👤 Creating token for identity: {identity}, room: {room_name}")
#         print(f"🔑 API Key: {LIVEKIT_API_KEY[:15]}...")

#         # Method 1: Try with VideoGrants as a separate object
#         try:
#             token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
#             token.identity = identity
#             token.name = identity
            
#             # Create grants
#             grants = VideoGrants(
#                 room_join=True,
#                 room=room_name,
#                 can_publish=True,
#                 can_subscribe=True,
#                 can_publish_data=True,
#             )
            
#             # Try different attribute names
#             if hasattr(token, 'video_grant'):
#                 token.video_grant = grants
#             elif hasattr(token, 'video'):
#                 token.video = grants
#             elif hasattr(token, 'grants'):
#                 token.grants = grants
#             else:
#                 # Manual attribute setting
#                 token.video = grants
            
#             jwt = token.to_jwt()
            
#             # Verify the token has grants by checking length
#             # A token without grants is shorter
#             if len(jwt) < 150:
#                 raise ValueError("Token seems to be missing grants (too short)")
            
#             print(f"✅ Token generated with method 1")
#             print(f"📝 Token length: {len(jwt)} chars")
            
#         except Exception as e1:
#             print(f"⚠️ Method 1 failed: {e1}")
            
#             # Method 2: Use with_grants or add_grants if available
#             try:
#                 token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
#                 token.identity = identity
#                 token.name = identity
                
#                 grants = VideoGrants(
#                     room_join=True,
#                     room=room_name,
#                     can_publish=True,
#                     can_subscribe=True,
#                     can_publish_data=True,
#                 )
                
#                 if hasattr(token, 'with_grants'):
#                     token = token.with_grants(video=grants)
#                 elif hasattr(token, 'add_grant'):
#                     token.add_grant(grants)
#                 else:
#                     raise ValueError("No method to add grants found")
                
#                 jwt = token.to_jwt()
#                 print(f"✅ Token generated with method 2")
                
#             except Exception as e2:
#                 print(f"⚠️ Method 2 also failed: {e2}")
                
#                 # Method 3: Direct instantiation with grants
#                 grants = VideoGrants(
#                     room_join=True,
#                     room=room_name,
#                     can_publish=True,
#                     can_subscribe=True,
#                     can_publish_data=True,
#                 )
                
#                 token = AccessToken(
#                     api_key=LIVEKIT_API_KEY,
#                     api_secret=LIVEKIT_API_SECRET,
#                     identity=identity,
#                     name=identity,
#                     grants=grants
#                 )
                
#                 jwt = token.to_jwt()
#                 print(f"✅ Token generated with method 3")

#         return Response({
#             "token": jwt,
#             "wsUrl": LIVEKIT_URL,
#             "room": room_name,
#             "identity": identity
#         })

#     except Exception as e:
#         print(f"❌ All methods failed: {e}")
#         import traceback
#         traceback.print_exc()
#         return Response({"error": str(e)}, status=500)