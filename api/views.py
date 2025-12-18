from django.http import JsonResponse
from rest_framework.views import APIView


class WebhookView(APIView):
    def post(self, *args, **kwargs):
        type = self.request.data.get('type')
        timestamp = self.request.data.get('timestamp')
        data = self.request.data.get('data')

        return JsonResponse(data, safe=False)
