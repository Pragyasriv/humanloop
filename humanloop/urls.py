from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from humanloop.views import api_index
from humanloop.api_views import ChatAPIView,ChatFollowUpAPIView, generate_livekit_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_index),

    # API routes
    path('api/', include('request.urls')),
    path('api/', include('agent.urls')),
    path('api/', include('supervisor.urls')),
    path('api/', include('kb.urls')),
    path('api/chat/', ChatAPIView.as_view(), name='chat'),
    path("api/chat/followup/<int:request_id>/", ChatFollowUpAPIView.as_view(), name="chat-followup"),
    path("api/generate-livekit-token/", generate_livekit_token),
]

# ✅ Serve static build files properly during development
urlpatterns += static(
    '/assets/',
    document_root=settings.BASE_DIR / 'humanloop' / 'frontend_build' / 'assets'
)

# ✅ React SPA fallback — AFTER static file serving
urlpatterns += [
    re_path(r'^$', TemplateView.as_view(template_name='index.html')),
    re_path(r'^(?!assets/).*$', TemplateView.as_view(template_name='index.html')),
]


