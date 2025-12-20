import uuid
from datetime import datetime
from django.test import TestCase
from django.utils import timezone

from BO.api.api import Webhook
from BO.base.exception import ValidationError
import api.models


class WebhookTestCase(TestCase):
    """Testes para a classe Webhook em BO/api/api.py"""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.webhook = Webhook()
        self.timestamp = timezone.now()

    def test_process_webhook_missing_type(self):
        """Testa process_webhook sem o campo type"""
        response = self.webhook.process_webhook(None, self.timestamp, {'id': str(uuid.uuid4())})
        
        self.assertFalse(response['status'])
        self.assertEqual(response['status_code'], 400)
        self.assertEqual(response['description'], 'Type not specified')

    def test_process_webhook_missing_timestamp(self):
        """Testa process_webhook sem o campo timestamp"""
        response = self.webhook.process_webhook('NEW_CONVERSATION', None, {'id': str(uuid.uuid4())})
        
        self.assertFalse(response['status'])
        self.assertEqual(response['status_code'], 400)
        self.assertEqual(response['description'], 'Timestamp not specified')

    def test_process_webhook_missing_data(self):
        """Testa process_webhook sem o campo data"""
        response = self.webhook.process_webhook('NEW_CONVERSATION', self.timestamp, None)
        
        self.assertFalse(response['status'])
        self.assertEqual(response['status_code'], 400)
        self.assertEqual(response['description'], 'Data not specified')

    def test_process_webhook_invalid_type(self):
        """Testa process_webhook com tipo inválido"""
        response = self.webhook.process_webhook('INVALID_TYPE', self.timestamp, {'id': str(uuid.uuid4())})
        
        self.assertFalse(response['status'])
        self.assertEqual(response['status_code'], 422)
        self.assertIn("The 'type' field only accepts", response['description'])

    def test_create_conversation_success(self):
        """Testa criação de conversa com sucesso"""
        conversation_id = str(uuid.uuid4())
        data = {'id': conversation_id}
        
        response = Webhook.create_conversation(self.timestamp, data)
        
        self.assertEqual(response['status'], 'CREATED')
        self.assertEqual(response['type'], 'NEW_CONVERSATION')
        self.assertEqual(str(response['id']), conversation_id)
        
        # Verifica se a conversa foi criada no banco
        conversation = api.models.Conversation.objects.get(id=conversation_id)
        self.assertEqual(conversation.status, 'OPEN')
        self.assertEqual(conversation.create_timestamp, self.timestamp)

    def test_create_conversation_missing_id(self):
        """Testa criação de conversa sem ID"""
        with self.assertRaises(ValidationError) as context:
            Webhook.create_conversation(self.timestamp, {})
        
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.message, 'Data.id not specified')

    def test_create_conversation_invalid_uuid(self):
        """Testa criação de conversa com UUID inválido"""
        data = {'id': 'invalid-uuid'}
        
        with self.assertRaises(ValidationError) as context:
            Webhook.create_conversation(self.timestamp, data)
        
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("UUID v4 format", context.exception.message)

    def test_create_conversation_duplicate_id(self):
        """Testa criação de conversa com ID duplicado"""
        conversation_id = str(uuid.uuid4())
        data = {'id': conversation_id}
        
        # Cria a primeira conversa
        Webhook.create_conversation(self.timestamp, data)
        
        # Tenta criar outra com o mesmo ID
        with self.assertRaises(ValidationError) as context:
            Webhook.create_conversation(self.timestamp, data)
        
        self.assertEqual(context.exception.status_code, 422)
        self.assertIn("already exists", context.exception.message)

    def test_create_message_success(self):
        """Testa criação de mensagem com sucesso"""
        # Primeiro cria uma conversa
        conversation_id = str(uuid.uuid4())
        conversation_data = {'id': conversation_id}
        Webhook.create_conversation(self.timestamp, conversation_data)
        
        # Cria a mensagem
        message_id = str(uuid.uuid4())
        message_data = {
            'id': message_id,
            'direction': 'SENT',
            'content': 'Test message',
            'conversation_id': conversation_id
        }
        
        response = Webhook.create_message(self.timestamp, message_data)
        
        self.assertEqual(response['status'], 'CREATED')
        self.assertEqual(response['type'], 'NEW_MESSAGE')
        self.assertEqual(str(response['id']), message_id)
        
        # Verifica se a mensagem foi criada no banco
        message = api.models.Message.objects.get(id=message_id)
        self.assertEqual(message.direction, 'SENT')
        self.assertEqual(message.content, 'Test message')
        self.assertEqual(str(message.conversation_id), conversation_id)

    def test_create_message_missing_id(self):
        """Testa criação de mensagem sem ID"""
        with self.assertRaises(ValidationError) as context:
            Webhook.create_message(self.timestamp, {'direction': 'SENT', 'content': 'Test'})
        
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.message, 'Data.id not specified')

    def test_create_message_missing_direction(self):
        """Testa criação de mensagem sem direction"""
        with self.assertRaises(ValidationError) as context:
            Webhook.create_message(self.timestamp, {'id': str(uuid.uuid4()), 'content': 'Test'})
        
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.message, 'Data.direction not specified')

    def test_create_message_invalid_direction(self):
        """Testa criação de mensagem com direction inválido"""
        data = {
            'id': str(uuid.uuid4()),
            'direction': 'INVALID',
            'content': 'Test',
            'conversation_id': str(uuid.uuid4())
        }
        
        with self.assertRaises(ValidationError) as context:
            Webhook.create_message(self.timestamp, data)
        
        self.assertEqual(context.exception.status_code, 422)
        self.assertIn("only accepts RECEIVED or SENT", context.exception.message)

    def test_create_message_missing_content(self):
        """Testa criação de mensagem sem content"""
        with self.assertRaises(ValidationError) as context:
            Webhook.create_message(self.timestamp, {
                'id': str(uuid.uuid4()),
                'direction': 'SENT'
            })
        
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.message, 'Data.content not specified')

    def test_create_message_missing_conversation_id(self):
        """Testa criação de mensagem sem conversation_id"""
        with self.assertRaises(ValidationError) as context:
            Webhook.create_message(self.timestamp, {
                'id': str(uuid.uuid4()),
                'direction': 'SENT',
                'content': 'Test'
            })
        
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.message, 'Data.conversation_id not specified')

    def test_create_message_invalid_conversation_id(self):
        """Testa criação de mensagem com conversation_id inválido"""
        data = {
            'id': str(uuid.uuid4()),
            'direction': 'SENT',
            'content': 'Test',
            'conversation_id': 'invalid-uuid'
        }
        
        with self.assertRaises(ValidationError) as context:
            Webhook.create_message(self.timestamp, data)
        
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("UUID v4 format", context.exception.message)

    def test_create_message_nonexistent_conversation(self):
        """Testa criação de mensagem para conversa inexistente"""
        data = {
            'id': str(uuid.uuid4()),
            'direction': 'SENT',
            'content': 'Test',
            'conversation_id': str(uuid.uuid4())
        }
        
        with self.assertRaises(ValidationError) as context:
            Webhook.create_message(self.timestamp, data)
        
        self.assertEqual(context.exception.status_code, 422)
        self.assertIn("does not exist", context.exception.message)

    def test_create_message_closed_conversation(self):
        """Testa criação de mensagem em conversa fechada"""
        # Cria e fecha uma conversa
        conversation_id = str(uuid.uuid4())
        conversation_data = {'id': conversation_id}
        Webhook.create_conversation(self.timestamp, conversation_data)
        Webhook.close_conversation(self.timestamp, conversation_data)
        
        # Tenta criar mensagem na conversa fechada
        message_data = {
            'id': str(uuid.uuid4()),
            'direction': 'SENT',
            'content': 'Test message',
            'conversation_id': conversation_id
        }
        
        with self.assertRaises(ValidationError) as context:
            Webhook.create_message(self.timestamp, message_data)
        
        self.assertEqual(context.exception.status_code, 422)
        self.assertIn("already been closed", context.exception.message)

    def test_create_message_duplicate_id(self):
        """Testa criação de mensagem com ID duplicado"""
        # Cria conversa e mensagem
        conversation_id = str(uuid.uuid4())
        conversation_data = {'id': conversation_id}
        Webhook.create_conversation(self.timestamp, conversation_data)
        
        message_id = str(uuid.uuid4())
        message_data = {
            'id': message_id,
            'direction': 'SENT',
            'content': 'Test message',
            'conversation_id': conversation_id
        }
        Webhook.create_message(self.timestamp, message_data)
        
        # Tenta criar outra mensagem com o mesmo ID
        with self.assertRaises(ValidationError) as context:
            Webhook.create_message(self.timestamp, message_data)
        
        self.assertEqual(context.exception.status_code, 422)
        self.assertIn("already exists", context.exception.message)

    def test_close_conversation_success(self):
        """Testa fechamento de conversa com sucesso"""
        # Cria uma conversa
        conversation_id = str(uuid.uuid4())
        conversation_data = {'id': conversation_id}
        Webhook.create_conversation(self.timestamp, conversation_data)
        
        # Fecha a conversa
        close_timestamp = timezone.now()
        response = Webhook.close_conversation(close_timestamp, conversation_data)
        
        self.assertEqual(response['status'], 'CLOSED')
        self.assertEqual(response['type'], 'CLOSE_CONVERSATION')
        self.assertEqual(str(response['id']), conversation_id)
        
        # Verifica se a conversa foi fechada
        conversation = api.models.Conversation.objects.get(id=conversation_id)
        self.assertEqual(conversation.status, 'CLOSED')
        self.assertEqual(conversation.edit_timestamp, close_timestamp)

    def test_close_conversation_missing_id(self):
        """Testa fechamento de conversa sem ID"""
        with self.assertRaises(ValidationError) as context:
            Webhook.close_conversation(self.timestamp, {})
        
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.message, 'Data.id not specified')

    def test_close_conversation_invalid_uuid(self):
        """Testa fechamento de conversa com UUID inválido"""
        data = {'id': 'invalid-uuid'}
        
        with self.assertRaises(ValidationError) as context:
            Webhook.close_conversation(self.timestamp, data)
        
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("UUID v4 format", context.exception.message)

    def test_close_conversation_nonexistent(self):
        """Testa fechamento de conversa inexistente"""
        data = {'id': str(uuid.uuid4())}
        
        with self.assertRaises(ValidationError) as context:
            Webhook.close_conversation(self.timestamp, data)
        
        self.assertEqual(context.exception.status_code, 422)
        self.assertIn("does not exist", context.exception.message)

    def test_process_webhook_new_conversation(self):
        """Testa process_webhook com tipo NEW_CONVERSATION"""
        conversation_id = str(uuid.uuid4())
        data = {'id': conversation_id}
        
        response = self.webhook.process_webhook('NEW_CONVERSATION', self.timestamp, data)
        
        self.assertTrue(response['status'])
        self.assertEqual(response['status_code'], 200)
        self.assertEqual(response['response']['type'], 'NEW_CONVERSATION')
        self.assertEqual(str(response['response']['id']), conversation_id)

    def test_process_webhook_new_message(self):
        """Testa process_webhook com tipo NEW_MESSAGE"""
        # Cria conversa primeiro
        conversation_id = str(uuid.uuid4())
        Webhook.create_conversation(self.timestamp, {'id': conversation_id})
        
        message_id = str(uuid.uuid4())
        data = {
            'id': message_id,
            'direction': 'RECEIVED',
            'content': 'Hello',
            'conversation_id': conversation_id
        }
        
        response = self.webhook.process_webhook('NEW_MESSAGE', self.timestamp, data)
        
        self.assertTrue(response['status'])
        self.assertEqual(response['status_code'], 200)
        self.assertEqual(response['response']['type'], 'NEW_MESSAGE')
        self.assertEqual(str(response['response']['id']), message_id)

    def test_process_webhook_close_conversation(self):
        """Testa process_webhook com tipo CLOSE_CONVERSATION"""
        # Cria conversa primeiro
        conversation_id = str(uuid.uuid4())
        Webhook.create_conversation(self.timestamp, {'id': conversation_id})
        
        data = {'id': conversation_id}
        close_timestamp = timezone.now()
        
        response = self.webhook.process_webhook('CLOSE_CONVERSATION', close_timestamp, data)
        
        self.assertTrue(response['status'])
        self.assertEqual(response['status_code'], 200)
        self.assertEqual(response['response']['type'], 'CLOSE_CONVERSATION')
        self.assertEqual(str(response['response']['id']), conversation_id)

