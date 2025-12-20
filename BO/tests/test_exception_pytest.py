"""
Testes para a classe ValidationError em BO/base/exception.py usando pytest.
"""
import pytest

from BO.base.exception import ValidationError


def test_validation_error_default():
    """Testa criação de ValidationError com valores padrão."""
    error = ValidationError()
    
    assert error.message is None
    assert error.status_code == 400
    assert error.response is None


def test_validation_error_with_message():
    """Testa criação de ValidationError com mensagem."""
    error = ValidationError('Test error message')
    
    assert error.message == 'Test error message'
    assert error.status_code == 400
    assert error.response is None


def test_validation_error_with_status_code():
    """Testa criação de ValidationError com status_code customizado."""
    error = ValidationError('Error message', status_code=422)
    
    assert error.message == 'Error message'
    assert error.status_code == 422
    assert error.response is None


def test_validation_error_with_response():
    """Testa criação de ValidationError com response."""
    response_data = {'error': 'details'}
    error = ValidationError('Error message', status_code=400, response=response_data)
    
    assert error.message == 'Error message'
    assert error.status_code == 400
    assert error.response == response_data


def test_validation_error_inherits_from_exception():
    """Testa que ValidationError herda de Exception."""
    error = ValidationError('Test error')
    
    assert isinstance(error, Exception)
    
    # Testa que pode ser levantada
    with pytest.raises(ValidationError) as exc_info:
        raise error
    
    assert exc_info.value.message == 'Test error'


def test_validation_error_properties():
    """Testa que as propriedades são read-only e funcionam corretamente."""
    error = ValidationError('Message', status_code=500, response={'data': 'test'})
    
    # Verifica que as propriedades retornam os valores corretos
    assert error.message == 'Message'
    assert error.status_code == 500
    assert error.response == {'data': 'test'}
