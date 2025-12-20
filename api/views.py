from django.http import JsonResponse
from rest_framework.views import APIView

import BO.api.api


class WebhookView(APIView):
    def post(self, *args, **kwargs):
        type_webhook = self.request.data.get('type')
        timestamp = self.request.data.get('timestamp')
        data = self.request.data.get('data')

        response = BO.api.api.Webhook().process_webhook(type_webhook, timestamp, data)

        return JsonResponse(response, safe=False, status=response['status_code'])


class ConversationView(APIView):
    def get(self, *args, **kwargs):
        status = self.request.GET.get('status')
        date = self.request.GET.get('date')

        response = BO.api.api.Conversations().get_conversations(status=status, date=date)

        return JsonResponse(response, safe=False, status=response['status_code'])


class ConversationDetailView(APIView):
    def get(self, *args, **kwargs):
        conversation_id = kwargs['conversation_id']

        response = BO.api.api.Conversations().get_conversation_detail(conversation_id=conversation_id)

        return JsonResponse(response, safe=False, status=response['status_code'])
