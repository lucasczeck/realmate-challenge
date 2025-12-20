import uuid
import json
from datetime import datetime
from django.test import TestCase, Client
from django.utils import timezone
from rest_framework.test import APIClient

from api.views import WebhookView
import api.models


class WebhookViewTestCase(TestCase):
    """Testes para a view WebhookView em api/views.py"""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.client = APIClient()
        self.timestamp = timezone.now().isoformat()

    def test_webhook_post_new_conversation_success(self):
        """Testa POST para criar nova conversa"""
        conversation_id = str(uuid.uuid4())
        data = {
            'type': 'NEW_CONVERSATION',
            'timestamp': self.timestamp,
            'data': {
                'id': conversation_id
            }
        }
        
        response = self.client.post('/webhook', data, format='json')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['status'])
        self.assertEqual(response_data['status_code'], 200)
        self.assertEqual(response_data['response']['type'], 'NEW_CONVERSATION')
        self.assertEqual(response_data['response']['id'], conversation_id)
        
        # Verifica se foi criada no banco
        conversation = api.models.Conversation.objects.get(id=conversation_id)
        self.assertIsNotNone(conversation)

    def test_webhook_post_new_message_success(self):
        """Testa POST para criar nova mensagem"""
        # Primeiro cria uma conversa
        conversation_id = str(uuid.uuid4())
        conversation_data = {
            'type': 'NEW_CONVERSATION',
            'timestamp': self.timestamp,
            'data': {'id': conversation_id}
        }
        self.client.post('/webhook', conversation_data, format='json')
        
        # Cria a mensagem
        message_id = str(uuid.uuid4())
        message_data = {
            'type': 'NEW_MESSAGE',
            'timestamp': self.timestamp,
            'data': {
                'id': message_id,
                'direction': 'SENT',
                'content': 'Hello, world!',
                'conversation_id': conversation_id
            }
        }
        
        response = self.client.post('/webhook', message_data, format='json')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['status'])
        self.assertEqual(response_data['response']['type'], 'NEW_MESSAGE')
        self.assertEqual(response_data['response']['id'], message_id)
        
        # Verifica se foi criada no banco
        message = api.models.Message.objects.get(id=message_id)
        self.assertIsNotNone(message)

    def test_webhook_post_close_conversation_success(self):
        """Testa POST para fechar conversa"""
        # Primeiro cria uma conversa
        conversation_id = str(uuid.uuid4())
        conversation_data = {
            'type': 'NEW_CONVERSATION',
            'timestamp': self.timestamp,
            'data': {'id': conversation_id}
        }
        self.client.post('/webhook', conversation_data, format='json')
        
        # Fecha a conversa
        close_data = {
            'type': 'CLOSE_CONVERSATION',
            'timestamp': self.timestamp,
            'data': {'id': conversation_id}
        }
        
        response = self.client.post('/webhook', close_data, format='json')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['status'])
        self.assertEqual(response_data['response']['type'], 'CLOSE_CONVERSATION')
        
        # Verifica se foi fechada no banco
        conversation = api.models.Conversation.objects.get(id=conversation_id)
        self.assertEqual(conversation.status, 'CLOSED')

    def test_webhook_post_missing_type(self):
        """Testa POST sem o campo type"""
        data = {
            'timestamp': self.timestamp,
            'data': {'id': str(uuid.uuid4())}
        }
        
        response = self.client.post('/webhook', data, format='json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['status'])
        self.assertEqual(response_data['status_code'], 400)
        self.assertEqual(response_data['description'], 'Type not specified')

    def test_webhook_post_missing_timestamp(self):
        """Testa POST sem o campo timestamp"""
        data = {
            'type': 'NEW_CONVERSATION',
            'data': {'id': str(uuid.uuid4())}
        }
        
        response = self.client.post('/webhook', data, format='json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['status'])
        self.assertEqual(response_data['status_code'], 400)
        self.assertEqual(response_data['description'], 'Timestamp not specified')

    def test_webhook_post_missing_data(self):
        """Testa POST sem o campo data"""
        data = {
            'type': 'NEW_CONVERSATION',
            'timestamp': self.timestamp
        }
        
        response = self.client.post('/webhook', data, format='json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['status'])
        self.assertEqual(response_data['status_code'], 400)
        self.assertEqual(response_data['description'], 'Data not specified')

    def test_webhook_post_invalid_type(self):
        """Testa POST com tipo inválido"""
        data = {
            'type': 'INVALID_TYPE',
            'timestamp': self.timestamp,
            'data': {'id': str(uuid.uuid4())}
        }
        
        response = self.client.post('/webhook', data, format='json')
        
        self.assertEqual(response.status_code, 422)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['status'])
        self.assertEqual(response_data['status_code'], 422)

    def test_webhook_post_invalid_conversation_id(self):
        """Testa POST com conversation_id inválido"""
        data = {
            'type': 'NEW_MESSAGE',
            'timestamp': self.timestamp,
            'data': {
                'id': str(uuid.uuid4()),
                'direction': 'SENT',
                'content': 'Test',
                'conversation_id': 'invalid-uuid'
            }
        }
        
        response = self.client.post('/webhook', data, format='json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['status'])
        self.assertIn('UUID v4 format', response_data['description'])

    def test_webhook_post_nonexistent_conversation(self):
        """Testa POST de mensagem para conversa inexistente"""
        data = {
            'type': 'NEW_MESSAGE',
            'timestamp': self.timestamp,
            'data': {
                'id': str(uuid.uuid4()),
                'direction': 'SENT',
                'content': 'Test',
                'conversation_id': str(uuid.uuid4())
            }
        }
        
        response = self.client.post('/webhook', data, format='json')
        
        self.assertEqual(response.status_code, 422)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['status'])
        self.assertIn('does not exist', response_data['description'])

    def test_webhook_post_message_to_closed_conversation(self):
        """Testa POST de mensagem para conversa fechada"""
        # Cria e fecha uma conversa
        conversation_id = str(uuid.uuid4())
        conversation_data = {
            'type': 'NEW_CONVERSATION',
            'timestamp': self.timestamp,
            'data': {'id': conversation_id}
        }
        self.client.post('/webhook', conversation_data, format='json')
        
        close_data = {
            'type': 'CLOSE_CONVERSATION',
            'timestamp': self.timestamp,
            'data': {'id': conversation_id}
        }
        self.client.post('/webhook', close_data, format='json')
        
        # Tenta criar mensagem na conversa fechada
        message_data = {
            'type': 'NEW_MESSAGE',
            'timestamp': self.timestamp,
            'data': {
                'id': str(uuid.uuid4()),
                'direction': 'SENT',
                'content': 'Test',
                'conversation_id': conversation_id
            }
        }
        
        response = self.client.post('/webhook', message_data, format='json')
        
        self.assertEqual(response.status_code, 422)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['status'])
        self.assertIn('already been closed', response_data['description'])

