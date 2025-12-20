from django.test import TestCase
from django.test.utils import override_settings

from BO.base.decorator import Response
from BO.base.exception import ValidationError


class ResponseDecoratorTestCase(TestCase):
    """Testes para o decorator Response em BO/base/decorator.py"""

    def test_decorator_success_without_return_list(self):
        """Testa decorator com sucesso sem return_list"""
        @Response(desc_error='Error occurred', desc_success='Success')
        def test_function():
            return {'key': 'value'}
        
        result = test_function()
        
        self.assertTrue(result['status'])
        self.assertEqual(result['status_code'], 200)
        self.assertEqual(result['description'], 'Success')
        self.assertEqual(result['response'], {'key': 'value'})

    def test_decorator_success_with_return_list_dict(self):
        """Testa decorator com sucesso retornando dict e return_list"""
        @Response(desc_error='Error occurred', return_list=['data'])
        def test_function():
            return {'key': 'value'}
        
        result = test_function()
        
        self.assertTrue(result['status'])
        self.assertEqual(result['status_code'], 200)
        self.assertEqual(result['data'], {'key': 'value'})
        self.assertNotIn('response', result)

    def test_decorator_success_with_return_list_tuple(self):
        """Testa decorator com sucesso retornando tuple e return_list"""
        @Response(desc_error='Error occurred', return_list=['first', 'second'])
        def test_function():
            return ('value1', 'value2')
        
        result = test_function()
        
        self.assertTrue(result['status'])
        self.assertEqual(result['status_code'], 200)
        self.assertEqual(result['first'], 'value1')
        self.assertEqual(result['second'], 'value2')

    def test_decorator_success_with_return_list_single_value(self):
        """Testa decorator com sucesso retornando valor único e return_list"""
        @Response(desc_error='Error occurred', return_list=['data'])
        def test_function():
            return 'simple_value'
        
        result = test_function()
        
        self.assertTrue(result['status'])
        self.assertEqual(result['status_code'], 200)
        self.assertEqual(result['data'], 'simple_value')

    def test_decorator_validation_error(self):
        """Testa decorator capturando ValidationError"""
        @Response(desc_error='Error occurred')
        def test_function():
            raise ValidationError('Custom error message', status_code=400)
        
        result = test_function()
        
        self.assertFalse(result['status'])
        self.assertEqual(result['status_code'], 400)
        self.assertEqual(result['description'], 'Custom error message')

    def test_decorator_validation_error_with_response(self):
        """Testa decorator capturando ValidationError com response"""
        @Response(desc_error='Error occurred')
        def test_function():
            raise ValidationError('Error message', status_code=422, response={'error': 'details'})
        
        result = test_function()
        
        self.assertFalse(result['status'])
        self.assertEqual(result['status_code'], 422)
        self.assertEqual(result['description'], 'Error message')
        self.assertEqual(result['response'], {'error': 'details'})

    @override_settings(DEBUG=True)
    def test_decorator_generic_exception_debug_on(self):
        """Testa decorator capturando exceção genérica com DEBUG=True"""
        @Response(desc_error='Error occurred')
        def test_function():
            raise ValueError('Unexpected error')
        
        result = test_function()
        
        self.assertFalse(result['status'])
        self.assertEqual(result['status_code'], 500)
        self.assertEqual(result['description'], 'Error occurred')
        self.assertIn('error', result)
        self.assertIn('traceback', result['error'].lower())

    @override_settings(DEBUG=False)
    def test_decorator_generic_exception_debug_off(self):
        """Testa decorator capturando exceção genérica com DEBUG=False"""
        @Response(desc_error='Error occurred')
        def test_function():
            raise ValueError('Unexpected error')
        
        result = test_function()
        
        self.assertFalse(result['status'])
        self.assertEqual(result['status_code'], 500)
        self.assertEqual(result['description'], 'Error occurred')
        self.assertNotIn('error', result)

    def test_decorator_no_return_value(self):
        """Testa decorator com função que não retorna valor"""
        @Response(desc_error='Error occurred', return_list=['data'])
        def test_function():
            pass
        
        result = test_function()
        
        self.assertTrue(result['status'])
        self.assertEqual(result['status_code'], 200)
        self.assertIsNone(result['data'])

    def test_decorator_no_return_value_without_return_list(self):
        """Testa decorator sem return_value e sem return_list"""
        @Response(desc_error='Error occurred')
        def test_function():
            pass
        
        result = test_function()
        
        self.assertTrue(result['status'])
        self.assertEqual(result['status_code'], 200)
        self.assertNotIn('response', result)

    def test_decorator_multiple_return_list_values(self):
        """Testa decorator com múltiplos valores em return_list"""
        @Response(desc_error='Error occurred', return_list=['first', 'second', 'third'])
        def test_function():
            return ('value1', 'value2', 'value3')
        
        result = test_function()
        
        self.assertTrue(result['status'])
        self.assertEqual(result['first'], 'value1')
        self.assertEqual(result['second'], 'value2')
        self.assertEqual(result['third'], 'value3')

    def test_decorator_empty_desc_success(self):
        """Testa decorator com desc_success vazio"""
        @Response(desc_error='Error occurred', desc_success='')
        def test_function():
            return {'key': 'value'}
        
        result = test_function()
        
        self.assertTrue(result['status'])
        self.assertEqual(result['status_code'], 200)
        self.assertEqual(result['description'], '')

