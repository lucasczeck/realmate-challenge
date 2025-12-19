from django.db import models
import core.models


class Log(models.Model):
    status_code = models.IntegerField(null=True)
    reason_phrase = models.CharField(max_length=500, null=True)
    metodo = models.CharField(max_length=30, null=True)
    ip = models.GenericIPAddressField(null=True)
    ip_externo = models.TextField(null=True)
    path = models.CharField(max_length=500, null=True)
    session_key = models.CharField(max_length=200, null=True)
    host = models.TextField(null=True)
    remote_addr = models.TextField(null=True)
    http_x_encaminhado = models.TextField(null=True)
    body = models.TextField(null=True)
    params = models.TextField(null=True)
    info_user = models.TextField(null=True)
    referer = models.TextField(null=True)
    info_user_navegador_familia = models.CharField(max_length=200, null=True)
    info_user_navegador_versao = models.CharField(max_length=50, null=True)
    info_user_aparelho_familia = models.CharField(max_length=200, null=True)
    info_user_aparelho_modelo = models.CharField(max_length=200, null=True)
    info_user_os_familia = models.CharField(max_length=200, null=True)
    info_user_os_versao = models.CharField(max_length=50, null=True)
    info_user_is_bot = models.BooleanField(null=True)
    info_user_is_email_client = models.BooleanField(null=True)
    info_user_is_mobile = models.BooleanField(null=True)
    info_user_is_pc = models.BooleanField(null=True)
    info_user_is_tablet = models.BooleanField(null=True)
    info_user_is_touch_capable = models.BooleanField(null=True)

    class Meta:
        db_table = 'log'
