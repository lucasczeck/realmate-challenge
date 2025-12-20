from django.test import TestCase

from BO.base.exception import ValidationError


class ValidationErrorTestCase(TestCase):
    """Testes para a classe ValidationError em BO/base/exception.py"""

    def test_validation_error_default(self):
        """Testa criação de ValidationError com valores padrão"""
        error = ValidationError()
        
        self.assertIsNone(error.message)
        self.assertEqual(error.status_code, 400)
        self.assertIsNone(error.response)

    def test_validation_error_with_message(self):
        """Testa criação de ValidationError com mensagem"""
        error = ValidationError('Test error message')
        
        self.assertEqual(error.message, 'Test error message')
        self.assertEqual(error.status_code, 400)
        self.assertIsNone(error.response)

    def test_validation_error_with_status_code(self):
        """Testa criação de ValidationError com status_code customizado"""
        error = ValidationError('Error message', status_code=422)
        
        self.assertEqual(error.message, 'Error message')
        self.assertEqual(error.status_code, 422)
        self.assertIsNone(error.response)

    def test_validation_error_with_response(self):
        """Testa criação de ValidationError com response"""
        response_data = {'error': 'details'}
        error = ValidationError('Error message', status_code=400, response=response_data)
        
        self.assertEqual(error.message, 'Error message')
        self.assertEqual(error.status_code, 400)
        self.assertEqual(error.response, response_data)

    def test_validation_error_inherits_from_exception(self):
        """Testa que ValidationError herda de Exception"""
        error = ValidationError('Test error')
        
        self.assertIsInstance(error, Exception)
        
        # Testa que pode ser levantada
        with self.assertRaises(ValidationError) as context:
            raise error
        
        self.assertEqual(context.exception.message, 'Test error')

    def test_validation_error_properties(self):
        """Testa que as propriedades são read-only e funcionam corretamente"""
        error = ValidationError('Message', status_code=500, response={'data': 'test'})
        
        # Verifica que as propriedades retornam os valores corretos
        self.assertEqual(error.message, 'Message')
        self.assertEqual(error.status_code, 500)
        self.assertEqual(error.response, {'data': 'test'})

