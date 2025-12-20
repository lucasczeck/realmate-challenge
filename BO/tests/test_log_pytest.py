"""
Testes para a classe Log em BO/log/log.py usando pytest.
"""
from unittest.mock import Mock, patch
import pytest
from django.test import RequestFactory
from django.http import JsonResponse

from BO.log.log import Log
import core.log.models


@pytest.fixture
def factory():
    """Fixture para RequestFactory."""
    return RequestFactory()


@pytest.fixture
def request_with_user_agent(factory, mock_user_agent):
    """Fixture que cria um request com user_agent mockado."""
    request = factory.post('/test/', data={'test': 'data'})
    request.user_agent = mock_user_agent
    return request


@pytest.mark.django_db
def test_salvar_log_success(request_with_user_agent, mock_user_agent):
    """Testa salvamento de log com sucesso."""
    # Configura o request
    request_with_user_agent.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 10.0.0.1'
    request_with_user_agent.META['REMOTE_ADDR'] = '127.0.0.1'
    request_with_user_agent.META['HTTP_HOST'] = 'example.com'
    request_with_user_agent.session = Mock()
    request_with_user_agent.session.session_key = 'test_session_key'
    
    # Mock do headers
    request_with_user_agent.headers = Mock()
    request_with_user_agent.headers._store = {'referer': ('referer', 'http://example.com/referer')}
    
    response = JsonResponse({'status': 'ok'}, status=200)
    body = '{"test": "data"}'
    
    log_instance = Log(request_with_user_agent)
    log_instance.salvar_log(request_with_user_agent, response, body)
    
    # Verifica se o log foi salvo
    saved_log = core.log.models.Log.objects.last()
    assert saved_log is not None
    assert saved_log.status_code == 200
    assert saved_log.metodo == 'POST'
    assert saved_log.ip_externo == '192.168.1.1'
    assert saved_log.ip == '127.0.0.1'
    assert saved_log.host == 'example.com'
    assert saved_log.referer == 'http://example.com/referer'
    assert saved_log.body == body
    assert saved_log.info_user_navegador_familia == 'Chrome'
    assert saved_log.info_user_is_pc is True


@pytest.mark.django_db
def test_salvar_log_without_x_forwarded_for(request_with_user_agent):
    """Testa salvamento de log sem HTTP_X_FORWARDED_FOR."""
    request_with_user_agent.META.pop('HTTP_X_FORWARDED_FOR', None)
    request_with_user_agent.META['REMOTE_ADDR'] = '127.0.0.1'
    request_with_user_agent.META['HTTP_HOST'] = 'example.com'
    request_with_user_agent.session = Mock()
    request_with_user_agent.session.session_key = 'test_session_key'
    request_with_user_agent.headers = Mock()
    request_with_user_agent.headers._store = {}
    
    response = JsonResponse({'status': 'ok'}, status=200)
    body = '{"test": "data"}'
    
    log_instance = Log(request_with_user_agent)
    log_instance.salvar_log(request_with_user_agent, response, body)
    
    saved_log = core.log.models.Log.objects.last()
    assert saved_log is not None
    assert saved_log.ip_externo == '127.0.0.1'


@pytest.mark.django_db
def test_salvar_log_without_referer(request_with_user_agent):
    """Testa salvamento de log sem referer."""
    request_with_user_agent.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1'
    request_with_user_agent.META['REMOTE_ADDR'] = '127.0.0.1'
    request_with_user_agent.META['HTTP_HOST'] = 'example.com'
    request_with_user_agent.session = Mock()
    request_with_user_agent.session.session_key = 'test_session_key'
    request_with_user_agent.headers = Mock()
    request_with_user_agent.headers._store = {}
    
    response = JsonResponse({'status': 'ok'}, status=200)
    body = '{"test": "data"}'
    
    log_instance = Log(request_with_user_agent)
    log_instance.salvar_log(request_with_user_agent, response, body)
    
    saved_log = core.log.models.Log.objects.last()
    assert saved_log is not None
    assert saved_log.referer is None


@pytest.mark.django_db
def test_salvar_log_with_password_in_params(request_with_user_agent):
    """Testa salvamento de log com password nos params (deve ser omitido)."""
    request_with_user_agent.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1'
    request_with_user_agent.META['REMOTE_ADDR'] = '127.0.0.1'
    request_with_user_agent.META['HTTP_HOST'] = 'example.com'
    request_with_user_agent.session = Mock()
    request_with_user_agent.session.session_key = 'test_session_key'
    request_with_user_agent.headers = Mock()
    request_with_user_agent.headers._store = {}
    
    # Adiciona password nos GET params
    request_with_user_agent.GET = Mock()
    request_with_user_agent.GET.__iter__ = Mock(return_value=iter(['password', 'other']))
    request_with_user_agent.GET.__getitem__ = Mock(side_effect=lambda x: 'secret' if x == 'password' else 'value')
    request_with_user_agent.GET.keys = Mock(return_value=['password', 'other'])
    
    response = JsonResponse({'status': 'ok'}, status=200)
    body = '{"test": "data"}'
    
    log_instance = Log(request_with_user_agent)
    log_instance.salvar_log(request_with_user_agent, response, body)
    
    saved_log = core.log.models.Log.objects.last()
    assert saved_log is not None
    # Verifica que params não contém password
    assert saved_log.params == ''


def test_salvar_log_exception_handling(request_with_user_agent):
    """Testa que exceções durante salvamento são tratadas silenciosamente."""
    request_with_user_agent.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1'
    request_with_user_agent.META['REMOTE_ADDR'] = '127.0.0.1'
    request_with_user_agent.session = None  # Isso causará erro
    
    response = JsonResponse({'status': 'ok'}, status=200)
    body = '{"test": "data"}'
    
    log_instance = Log(request_with_user_agent)
    
    # Não deve levantar exceção
    log_instance.salvar_log(request_with_user_agent, response, body)
    # Se chegou aqui, não levantou exceção


@pytest.mark.django_db
def test_salvar_log_all_user_agent_properties(request_with_user_agent):
    """Testa que todas as propriedades do user_agent são salvas corretamente."""
    request_with_user_agent.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1'
    request_with_user_agent.META['REMOTE_ADDR'] = '127.0.0.1'
    request_with_user_agent.META['HTTP_HOST'] = 'example.com'
    request_with_user_agent.session = Mock()
    request_with_user_agent.session.session_key = 'test_session_key'
    request_with_user_agent.headers = Mock()
    request_with_user_agent.headers._store = {}
    
    response = JsonResponse({'status': 'ok'}, status=200)
    body = '{"test": "data"}'
    
    log_instance = Log(request_with_user_agent)
    log_instance.salvar_log(request_with_user_agent, response, body)
    
    saved_log = core.log.models.Log.objects.last()
    assert saved_log is not None
    assert saved_log.info_user_navegador_familia == 'Chrome'
    assert saved_log.info_user_navegador_versao == '120.0'
    assert saved_log.info_user_aparelho_familia == 'Desktop'
    assert saved_log.info_user_aparelho_modelo == 'PC'
    assert saved_log.info_user_os_familia == 'Windows'
    assert saved_log.info_user_os_versao == '10'
    assert saved_log.info_user_is_bot is False
    assert saved_log.info_user_is_email_client is False
    assert saved_log.info_user_is_mobile is False
    assert saved_log.info_user_is_pc is True
    assert saved_log.info_user_is_tablet is False
    assert saved_log.info_user_is_touch_capable is False
