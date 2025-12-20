"""
Testes para o decorator Response em BO/base/decorator.py usando pytest.
"""
import pytest
from django.test.utils import override_settings

from BO.base.decorator import Response
from BO.base.exception import ValidationError


def test_decorator_success_without_return_list():
    """Testa decorator com sucesso sem return_list."""
    @Response(desc_error='Error occurred', desc_success='Success')
    def test_function():
        return {'key': 'value'}
    
    result = test_function()
    
    assert result['status'] is True
    assert result['status_code'] == 200
    assert result['description'] == 'Success'
    assert result['response'] == {'key': 'value'}


def test_decorator_success_with_return_list_dict():
    """Testa decorator com sucesso retornando dict e return_list."""
    @Response(desc_error='Error occurred', return_list=['data'])
    def test_function():
        return {'key': 'value'}
    
    result = test_function()
    
    assert result['status'] is True
    assert result['status_code'] == 200
    assert result['data'] == {'key': 'value'}
    assert 'response' not in result


def test_decorator_success_with_return_list_tuple():
    """Testa decorator com sucesso retornando tuple e return_list."""
    @Response(desc_error='Error occurred', return_list=['first', 'second'])
    def test_function():
        return ('value1', 'value2')
    
    result = test_function()
    
    assert result['status'] is True
    assert result['status_code'] == 200
    assert result['first'] == 'value1'
    assert result['second'] == 'value2'


def test_decorator_success_with_return_list_single_value():
    """Testa decorator com sucesso retornando valor único e return_list."""
    @Response(desc_error='Error occurred', return_list=['data'])
    def test_function():
        return 'simple_value'
    
    result = test_function()
    
    assert result['status'] is True
    assert result['status_code'] == 200
    assert result['data'] == 'simple_value'


def test_decorator_validation_error():
    """Testa decorator capturando ValidationError."""
    @Response(desc_error='Error occurred')
    def test_function():
        raise ValidationError('Custom error message', status_code=400)
    
    result = test_function()
    
    assert result['status'] is False
    assert result['status_code'] == 400
    assert result['description'] == 'Custom error message'


def test_decorator_validation_error_with_response():
    """Testa decorator capturando ValidationError com response."""
    @Response(desc_error='Error occurred')
    def test_function():
        raise ValidationError('Error message', status_code=422, response={'error': 'details'})
    
    result = test_function()
    
    assert result['status'] is False
    assert result['status_code'] == 422
    assert result['description'] == 'Error message'
    assert result['response'] == {'error': 'details'}


@override_settings(DEBUG=True)
def test_decorator_generic_exception_debug_on():
    """Testa decorator capturando exceção genérica com DEBUG=True."""
    @Response(desc_error='Error occurred')
    def test_function():
        raise ValueError('Unexpected error')
    
    result = test_function()
    
    assert result['status'] is False
    assert result['status_code'] == 500
    assert result['description'] == 'Error occurred'
    assert 'error' in result
    assert 'traceback' in result['error'].lower()


@override_settings(DEBUG=False)
def test_decorator_generic_exception_debug_off():
    """Testa decorator capturando exceção genérica com DEBUG=False."""
    @Response(desc_error='Error occurred')
    def test_function():
        raise ValueError('Unexpected error')
    
    result = test_function()
    
    assert result['status'] is False
    assert result['status_code'] == 500
    assert result['description'] == 'Error occurred'
    assert 'error' not in result


def test_decorator_no_return_value():
    """Testa decorator com função que não retorna valor."""
    @Response(desc_error='Error occurred', return_list=['data'])
    def test_function():
        pass
    
    result = test_function()
    
    assert result['status'] is True
    assert result['status_code'] == 200
    assert result['data'] is None


def test_decorator_no_return_value_without_return_list():
    """Testa decorator sem return_value e sem return_list."""
    @Response(desc_error='Error occurred')
    def test_function():
        pass
    
    result = test_function()
    
    assert result['status'] is True
    assert result['status_code'] == 200
    assert 'response' not in result


def test_decorator_multiple_return_list_values():
    """Testa decorator com múltiplos valores em return_list."""
    @Response(desc_error='Error occurred', return_list=['first', 'second', 'third'])
    def test_function():
        return ('value1', 'value2', 'value3')
    
    result = test_function()
    
    assert result['status'] is True
    assert result['first'] == 'value1'
    assert result['second'] == 'value2'
    assert result['third'] == 'value3'


def test_decorator_empty_desc_success():
    """Testa decorator com desc_success vazio."""
    @Response(desc_error='Error occurred', desc_success='')
    def test_function():
        return {'key': 'value'}
    
    result = test_function()
    
    assert result['status'] is True
    assert result['status_code'] == 200
    assert result['description'] == ''
