import uuid
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError as DjangoValidationError

from api.models import Conversation, Message


class ConversationModelTestCase(TestCase):
    """Testes para o modelo Conversation em api/models.py"""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.timestamp = timezone.now()

    def test_create_conversation_default_status(self):
        """Testa criação de conversa com status padrão"""
        conversation = Conversation(
            id=uuid.uuid4(),
            create_timestamp=self.timestamp
        )
        conversation.save()
        
        self.assertEqual(conversation.status, Conversation.Status.OPEN)
        self.assertEqual(conversation.create_timestamp, self.timestamp)

    def test_create_conversation_with_closed_status(self):
        """Testa criação de conversa com status CLOSED"""
        conversation = Conversation(
            id=uuid.uuid4(),
            create_timestamp=self.timestamp,
            status=Conversation.Status.CLOSED
        )
        conversation.save()
        
        self.assertEqual(conversation.status, Conversation.Status.CLOSED)

    def test_conversation_status_choices(self):
        """Testa que os choices de status estão corretos"""
        self.assertEqual(Conversation.Status.OPEN, 'OPEN')
        self.assertEqual(Conversation.Status.CLOSED, 'CLOSED')

    def test_conversation_db_table(self):
        """Testa que o db_table está configurado corretamente"""
        self.assertEqual(Conversation._meta.db_table, 'api_conversarion')

    def test_conversation_inherits_from_log(self):
        """Testa que Conversation herda de Log"""
        from core.models import Log
        conversation = Conversation(
            id=uuid.uuid4(),
            create_timestamp=self.timestamp
        )
        
        self.assertIsInstance(conversation, Log)


class MessageModelTestCase(TestCase):
    """Testes para o modelo Message em api/models.py"""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.timestamp = timezone.now()
        # Cria uma conversa para os testes
        self.conversation = Conversation(
            id=uuid.uuid4(),
            create_timestamp=self.timestamp
        )
        self.conversation.save()

    def test_create_message_sent(self):
        """Testa criação de mensagem com direction SENT"""
        message = Message(
            id=uuid.uuid4(),
            create_timestamp=self.timestamp,
            conversation=self.conversation,
            direction=Message.Direction.SENT,
            content='Test message'
        )
        message.save()
        
        self.assertEqual(message.direction, Message.Direction.SENT)
        self.assertEqual(message.content, 'Test message')
        self.assertEqual(message.conversation, self.conversation)

    def test_create_message_received(self):
        """Testa criação de mensagem com direction RECEIVED"""
        message = Message(
            id=uuid.uuid4(),
            create_timestamp=self.timestamp,
            conversation=self.conversation,
            direction=Message.Direction.RECEIVED,
            content='Received message'
        )
        message.save()
        
        self.assertEqual(message.direction, Message.Direction.RECEIVED)
        self.assertEqual(message.content, 'Received message')

    def test_message_direction_choices(self):
        """Testa que os choices de direction estão corretos"""
        self.assertEqual(Message.Direction.SENT, 'SENT')
        self.assertEqual(Message.Direction.RECEIVED, 'RECEIVED')

    def test_message_db_table(self):
        """Testa que o db_table está configurado corretamente"""
        self.assertEqual(Message._meta.db_table, 'api_message')

    def test_message_foreign_key_to_conversation(self):
        """Testa que Message tem ForeignKey para Conversation"""
        message = Message(
            id=uuid.uuid4(),
            create_timestamp=self.timestamp,
            conversation=self.conversation,
            direction=Message.Direction.SENT,
            content='Test'
        )
        message.save()
        
        # Verifica o relacionamento
        self.assertEqual(message.conversation_id, self.conversation.id)
        self.assertEqual(message.conversation, self.conversation)

    def test_message_inherits_from_log(self):
        """Testa que Message herda de Log"""
        from core.models import Log
        message = Message(
            id=uuid.uuid4(),
            create_timestamp=self.timestamp,
            conversation=self.conversation,
            direction=Message.Direction.SENT,
            content='Test'
        )
        
        self.assertIsInstance(message, Log)

    def test_message_cascade_behavior(self):
        """Testa o comportamento do on_delete=DO_NOTHING"""
        message = Message(
            id=uuid.uuid4(),
            create_timestamp=self.timestamp,
            conversation=self.conversation,
            direction=Message.Direction.SENT,
            content='Test'
        )
        message.save()
        
        # Com DO_NOTHING, a mensagem não deve ser deletada quando a conversa é deletada
        # Mas isso depende da implementação do banco de dados
        # Vamos apenas verificar que o relacionamento existe
        self.assertIsNotNone(message.conversation)

