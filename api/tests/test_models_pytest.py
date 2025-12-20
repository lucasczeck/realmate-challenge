"""
Exemplos de testes usando pytest ao invés de unittest.TestCase.

Este arquivo demonstra como usar pytest com fixtures e sintaxe mais limpa.
Os testes unittest existentes continuam funcionando normalmente.
"""
import uuid
import pytest
from core.models import Log

from api.models import Conversation, Message


# ============================================
# Testes de Conversation usando pytest
# ============================================

@pytest.mark.django_db
def test_create_conversation_default_status(conversation):
    """Testa criação de conversa com status padrão usando fixture."""
    assert conversation.status == Conversation.Status.OPEN
    assert conversation.create_timestamp is not None


@pytest.mark.django_db
def test_create_conversation_with_closed_status(timestamp, conversation_id):
    """Testa criação de conversa com status CLOSED."""
    conversation = Conversation(
        id=uuid.UUID(conversation_id),
        create_timestamp=timestamp,
        status=Conversation.Status.CLOSED
    )
    conversation.save()
    
    assert conversation.status == Conversation.Status.CLOSED


def test_conversation_status_choices():
    """Testa que os choices de status estão corretos."""
    assert Conversation.Status.OPEN == 'OPEN'
    assert Conversation.Status.CLOSED == 'CLOSED'


def test_conversation_db_table():
    """Testa que o db_table está configurado corretamente."""
    assert Conversation._meta.db_table == 'api_conversarion'


@pytest.mark.django_db
def test_conversation_inherits_from_log(conversation):
    """Testa que Conversation herda de Log."""
    assert isinstance(conversation, Log)


# ============================================
# Testes de Message usando pytest
# ============================================

@pytest.mark.django_db
def test_create_message_sent(message):
    """Testa criação de mensagem com direction SENT usando fixture."""
    assert message.direction == Message.Direction.SENT
    assert message.content == 'Test message'
    assert message.conversation is not None


@pytest.mark.django_db
def test_create_message_received(conversation, timestamp, message_id):
    """Testa criação de mensagem com direction RECEIVED."""
    message = Message(
        id=uuid.UUID(message_id),
        create_timestamp=timestamp,
        conversation=conversation,
        direction=Message.Direction.RECEIVED,
        content='Received message'
    )
    message.save()
    
    assert message.direction == Message.Direction.RECEIVED
    assert message.content == 'Received message'


def test_message_direction_choices():
    """Testa que os choices de direction estão corretos."""
    assert Message.Direction.SENT == 'SENT'
    assert Message.Direction.RECEIVED == 'RECEIVED'


def test_message_db_table():
    """Testa que o db_table está configurado corretamente."""
    assert Message._meta.db_table == 'api_message'


@pytest.mark.django_db
def test_message_foreign_key_to_conversation(message, conversation):
    """Testa que Message tem ForeignKey para Conversation."""
    assert message.conversation_id == conversation.id
    assert message.conversation == conversation


@pytest.mark.django_db
def test_message_inherits_from_log(message):
    """Testa que Message herda de Log."""
    assert isinstance(message, Log)


# ============================================
# Testes parametrizados (vantagem do pytest)
# ============================================

@pytest.mark.parametrize("direction,expected", [
    (Message.Direction.SENT, 'SENT'),
    (Message.Direction.RECEIVED, 'RECEIVED'),
])
def test_message_direction_values(direction, expected):
    """Testa valores de direction usando parametrização."""
    assert direction == expected


@pytest.mark.parametrize("status,expected", [
    (Conversation.Status.OPEN, 'OPEN'),
    (Conversation.Status.CLOSED, 'CLOSED'),
])
def test_conversation_status_values(status, expected):
    """Testa valores de status usando parametrização."""
    assert status == expected
