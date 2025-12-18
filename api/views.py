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
