import BO.log.log
import os


class LogMiddleware:

    def __init__(self, get_response):

        self.get_response = get_response

    def __call__(self, request):

        try:
            body = str(str(dict(request.POST))) if not request.POST.get('password') else ''
            if body == '{}':
                body = str(request.body)
        except:
            body = None

        response = self.get_response(request)
        BO.log.log.Log(request=request).salvar_log(request=request, response=response, body=body)

        return response
