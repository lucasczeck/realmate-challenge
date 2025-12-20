from django.urls import path
import api.views


urlpatterns = [
    path('webhook/', api.views.WebhookView.as_view()),
    path('conversations/', api.views.ConversationView.as_view()),
    path('conversations/<uuid:conversation_id>/', api.views.ConversationDetailView.as_view())
]
