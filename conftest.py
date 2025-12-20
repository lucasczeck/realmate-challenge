"""
Configuração global do pytest com fixtures compartilhadas.
"""
import uuid
import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from unittest.mock import MagicMock

from api.models import Conversation, Message


@pytest.fixture
def api_client():
    """Fixture para APIClient do DRF."""
    return APIClient()


@pytest.fixture
def timestamp():
    """Fixture que retorna um timestamp atual."""
    return timezone.now()


@pytest.fixture
def conversation_id():
    """Fixture que retorna um UUID para conversa."""
    return str(uuid.uuid4())


@pytest.fixture
def message_id():
    """Fixture que retorna um UUID para mensagem."""
    return str(uuid.uuid4())


@pytest.fixture
def conversation(timestamp, conversation_id, db):
    """
    Fixture que cria e retorna uma conversa.
    
    Uso:
        @pytest.mark.django_db
        def test_something(conversation):
            assert conversation.status == Conversation.Status.OPEN
    """
    conv = Conversation(
        id=uuid.UUID(conversation_id),
        create_timestamp=timestamp
    )
    conv.save()
    return conv


@pytest.fixture
def closed_conversation(conversation, timestamp, db):
    """
    Fixture que cria e retorna uma conversa fechada.
    
    Uso:
        @pytest.mark.django_db
        def test_something(closed_conversation):
            assert closed_conversation.status == Conversation.Status.CLOSED
    """
    conversation.status = Conversation.Status.CLOSED
    conversation.edit_timestamp = timestamp
    conversation.save()
    return conversation


@pytest.fixture
def message(conversation, timestamp, message_id, db):
    """
    Fixture que cria e retorna uma mensagem.
    
    Uso:
        @pytest.mark.django_db
        def test_something(message):
            assert message.direction == Message.Direction.SENT
    """
    msg = Message(
        id=uuid.UUID(message_id),
        create_timestamp=timestamp,
        conversation=conversation,
        direction=Message.Direction.SENT,
        content='Test message'
    )
    msg.save()
    return msg


@pytest.fixture
def mock_user_agent():
    """
    Fixture que retorna um mock de user_agent.
    
    Uso:
        def test_something(mock_user_agent):
            request.user_agent = mock_user_agent
    """
    mock = MagicMock()
    mock.browser.family = 'Chrome'
    mock.browser.version_string = '120.0'
    mock.device.family = 'Desktop'
    mock.device.model = 'PC'
    mock.os.family = 'Windows'
    mock.os.version_string = '10'
    mock.is_bot = False
    mock.is_email_client = False
    mock.is_mobile = False
    mock.is_pc = True
    mock.is_tablet = False
    mock.is_touch_capable = False
    return mock


@pytest.fixture
def webhook_data_new_conversation(conversation_id, timestamp):
    """Fixture que retorna dados de webhook para nova conversa."""
    return {
        'type': 'NEW_CONVERSATION',
        'timestamp': timestamp.isoformat(),
        'data': {
            'id': conversation_id
        }
    }


@pytest.fixture
def webhook_data_new_message(conversation, message_id, timestamp):
    """Fixture que retorna dados de webhook para nova mensagem."""
    return {
        'type': 'NEW_MESSAGE',
        'timestamp': timestamp.isoformat(),
        'data': {
            'id': message_id,
            'direction': 'SENT',
            'content': 'Hello, world!',
            'conversation_id': str(conversation.id)
        }
    }


@pytest.fixture
def webhook_data_close_conversation(conversation, timestamp):
    """Fixture que retorna dados de webhook para fechar conversa."""
    return {
        'type': 'CLOSE_CONVERSATION',
        'timestamp': timestamp.isoformat(),
        'data': {
            'id': str(conversation.id)
        }
    }
