import core.log.models


class Log:

    def __init__(self, request):
        self.request = request

    def salvar_log(self, request, response, body):
        try:
            try:
                ip_externo = request.META.get('HTTP_X_FORWARDED_FOR', None).split(',')[0]
            except:
                ip_externo = request.META.get('REMOTE_ADDR')

            try:
                referer = request.headers._store['referer'][1]
            except:
                referer = None

            try:
                log = core.log.models.Log(
                    status_code=response.status_code,
                    reason_phrase=response.reason_phrase,
                    metodo=request.method,
                    referer=referer,
                    ip=request.META.get('REMOTE_ADDR'),
                    ip_externo=ip_externo,
                    path=request.path,
                    session_key=request.session.session_key if request.session else None,
                    host=request.META.get('HTTP_HOST'),
                    http_x_encaminhado=request.META.get('HTTP_X_FORWARDED_FOR', None),
                    remote_addr=request.META.get('REMOTE_ADDR'),
                    body=body,
                    params=str(dict(request.GET)) if 'password' not in dict(request.GET) else '',
                    info_user=str(request.user_agent),
                    info_user_navegador_familia=request.user_agent.browser.family,
                    info_user_navegador_versao=request.user_agent.browser.version_string,
                    info_user_aparelho_familia=request.user_agent.device.family,
                    info_user_aparelho_modelo=request.user_agent.device.model,
                    info_user_os_familia=request.user_agent.os.family,
                    info_user_os_versao=request.user_agent.os.version_string,
                    info_user_is_bot=request.user_agent.is_bot,
                    info_user_is_email_client=request.user_agent.is_email_client,
                    info_user_is_mobile=request.user_agent.is_mobile,
                    info_user_is_pc=request.user_agent.is_pc,
                    info_user_is_tablet=request.user_agent.is_tablet,
                    info_user_is_touch_capable=request.user_agent.is_touch_capable,
                )
                log.save()
            except Exception as e:
                print(e)

        except:
            pass
