from django.urls import path
import api.views


urlpatterns = [
    path('webhook', api.views.WebhookView.as_view())
]
