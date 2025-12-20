from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase, RequestFactory
from django.http import JsonResponse

from BO.log.log import Log
import core.log.models


class LogTestCase(TestCase):
    """Testes para a classe Log em BO/log/log.py"""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.factory = RequestFactory()
        self.request = self.factory.post('/test/', data={'test': 'data'})
        
        # Mock do user_agent
        self.mock_user_agent = MagicMock()
        self.mock_user_agent.browser.family = 'Chrome'
        self.mock_user_agent.browser.version_string = '120.0'
        self.mock_user_agent.device.family = 'Desktop'
        self.mock_user_agent.device.model = 'PC'
        self.mock_user_agent.os.family = 'Windows'
        self.mock_user_agent.os.version_string = '10'
        self.mock_user_agent.is_bot = False
        self.mock_user_agent.is_email_client = False
        self.mock_user_agent.is_mobile = False
        self.mock_user_agent.is_pc = True
        self.mock_user_agent.is_tablet = False
        self.mock_user_agent.is_touch_capable = False
        
        self.request.user_agent = self.mock_user_agent

    def test_salvar_log_success(self):
        """Testa salvamento de log com sucesso"""
        # Configura o request
        self.request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 10.0.0.1'
        self.request.META['REMOTE_ADDR'] = '127.0.0.1'
        self.request.META['HTTP_HOST'] = 'example.com'
        self.request.session = Mock()
        self.request.session.session_key = 'test_session_key'
        
        # Mock do headers
        self.request.headers = Mock()
        self.request.headers._store = {'referer': ('referer', 'http://example.com/referer')}
        
        response = JsonResponse({'status': 'ok'}, status=200)
        body = '{"test": "data"}'
        
        log_instance = Log(self.request)
        log_instance.salvar_log(self.request, response, body)
        
        # Verifica se o log foi salvo
        saved_log = core.log.models.Log.objects.last()
        self.assertIsNotNone(saved_log)
        self.assertEqual(saved_log.status_code, 200)
        self.assertEqual(saved_log.metodo, 'POST')
        self.assertEqual(saved_log.ip_externo, '192.168.1.1')
        self.assertEqual(saved_log.ip, '127.0.0.1')
        self.assertEqual(saved_log.host, 'example.com')
        self.assertEqual(saved_log.referer, 'http://example.com/referer')
        self.assertEqual(saved_log.body, body)
        self.assertEqual(saved_log.info_user_navegador_familia, 'Chrome')
        self.assertEqual(saved_log.info_user_is_pc, True)

    def test_salvar_log_without_x_forwarded_for(self):
        """Testa salvamento de log sem HTTP_X_FORWARDED_FOR"""
        self.request.META.pop('HTTP_X_FORWARDED_FOR', None)
        self.request.META['REMOTE_ADDR'] = '127.0.0.1'
        self.request.META['HTTP_HOST'] = 'example.com'
        self.request.session = Mock()
        self.request.session.session_key = 'test_session_key'
        self.request.headers = Mock()
        self.request.headers._store = {}
        
        response = JsonResponse({'status': 'ok'}, status=200)
        body = '{"test": "data"}'
        
        log_instance = Log(self.request)
        log_instance.salvar_log(self.request, response, body)
        
        saved_log = core.log.models.Log.objects.last()
        self.assertIsNotNone(saved_log)
        self.assertEqual(saved_log.ip_externo, '127.0.0.1')

    def test_salvar_log_without_referer(self):
        """Testa salvamento de log sem referer"""
        self.request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1'
        self.request.META['REMOTE_ADDR'] = '127.0.0.1'
        self.request.META['HTTP_HOST'] = 'example.com'
        self.request.session = Mock()
        self.request.session.session_key = 'test_session_key'
        self.request.headers = Mock()
        self.request.headers._store = {}
        
        response = JsonResponse({'status': 'ok'}, status=200)
        body = '{"test": "data"}'
        
        log_instance = Log(self.request)
        log_instance.salvar_log(self.request, response, body)
        
        saved_log = core.log.models.Log.objects.last()
        self.assertIsNotNone(saved_log)
        self.assertIsNone(saved_log.referer)

    def test_salvar_log_with_password_in_params(self):
        """Testa salvamento de log com password nos params (deve ser omitido)"""
        self.request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1'
        self.request.META['REMOTE_ADDR'] = '127.0.0.1'
        self.request.META['HTTP_HOST'] = 'example.com'
        self.request.session = Mock()
        self.request.session.session_key = 'test_session_key'
        self.request.headers = Mock()
        self.request.headers._store = {}
        
        # Adiciona password nos GET params
        self.request.GET = Mock()
        self.request.GET.__iter__ = Mock(return_value=iter(['password', 'other']))
        self.request.GET.__getitem__ = Mock(side_effect=lambda x: 'secret' if x == 'password' else 'value')
        self.request.GET.keys = Mock(return_value=['password', 'other'])
        
        response = JsonResponse({'status': 'ok'}, status=200)
        body = '{"test": "data"}'
        
        log_instance = Log(self.request)
        log_instance.salvar_log(self.request, response, body)
        
        saved_log = core.log.models.Log.objects.last()
        self.assertIsNotNone(saved_log)
        # Verifica que params não contém password
        self.assertEqual(saved_log.params, '')

    def test_salvar_log_exception_handling(self):
        """Testa que exceções durante salvamento são tratadas silenciosamente"""
        self.request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1'
        self.request.META['REMOTE_ADDR'] = '127.0.0.1'
        self.request.session = None  # Isso causará erro
        
        response = JsonResponse({'status': 'ok'}, status=200)
        body = '{"test": "data"}'
        
        log_instance = Log(self.request)
        
        # Não deve levantar exceção
        try:
            log_instance.salvar_log(self.request, response, body)
        except Exception:
            self.fail("salvar_log não deve levantar exceções")

    def test_salvar_log_all_user_agent_properties(self):
        """Testa que todas as propriedades do user_agent são salvas corretamente"""
        self.request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1'
        self.request.META['REMOTE_ADDR'] = '127.0.0.1'
        self.request.META['HTTP_HOST'] = 'example.com'
        self.request.session = Mock()
        self.request.session.session_key = 'test_session_key'
        self.request.headers = Mock()
        self.request.headers._store = {}
        
        response = JsonResponse({'status': 'ok'}, status=200)
        body = '{"test": "data"}'
        
        log_instance = Log(self.request)
        log_instance.salvar_log(self.request, response, body)
        
        saved_log = core.log.models.Log.objects.last()
        self.assertIsNotNone(saved_log)
        self.assertEqual(saved_log.info_user_navegador_familia, 'Chrome')
        self.assertEqual(saved_log.info_user_navegador_versao, '120.0')
        self.assertEqual(saved_log.info_user_aparelho_familia, 'Desktop')
        self.assertEqual(saved_log.info_user_aparelho_modelo, 'PC')
        self.assertEqual(saved_log.info_user_os_familia, 'Windows')
        self.assertEqual(saved_log.info_user_os_versao, '10')
        self.assertEqual(saved_log.info_user_is_bot, False)
        self.assertEqual(saved_log.info_user_is_email_client, False)
        self.assertEqual(saved_log.info_user_is_mobile, False)
        self.assertEqual(saved_log.info_user_is_pc, True)
        self.assertEqual(saved_log.info_user_is_tablet, False)
        self.assertEqual(saved_log.info_user_is_touch_capable, False)

