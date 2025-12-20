"""
Testes para a classe Webhook em BO/api/api.py usando pytest.
"""
import uuid
import pytest
from django.utils import timezone

from BO.api.api import Webhook
from BO.base.exception import ValidationError
import api.models


def test_process_webhook_missing_type(timestamp):
    """Testa process_webhook sem o campo type."""
    webhook = Webhook()
    response = webhook.process_webhook(None, timestamp, {'id': str(uuid.uuid4())})
    
    assert response['status'] is False
    assert response['status_code'] == 400
    assert response['description'] == 'Type not specified'


def test_process_webhook_missing_timestamp():
    """Testa process_webhook sem o campo timestamp."""
    webhook = Webhook()
    response = webhook.process_webhook('NEW_CONVERSATION', None, {'id': str(uuid.uuid4())})
    
    assert response['status'] is False
    assert response['status_code'] == 400
    assert response['description'] == 'Timestamp not specified'


def test_process_webhook_missing_data(timestamp):
    """Testa process_webhook sem o campo data."""
    webhook = Webhook()
    response = webhook.process_webhook('NEW_CONVERSATION', timestamp, None)
    
    assert response['status'] is False
    assert response['status_code'] == 400
    assert response['description'] == 'Data not specified'


def test_process_webhook_invalid_type(timestamp):
    """Testa process_webhook com tipo inválido."""
    webhook = Webhook()
    response = webhook.process_webhook('INVALID_TYPE', timestamp, {'id': str(uuid.uuid4())})
    
    assert response['status'] is False
    assert response['status_code'] == 422
    assert "The 'type' field only accepts" in response['description']


@pytest.mark.django_db
def test_create_conversation_success(timestamp, conversation_id):
    """Testa criação de conversa com sucesso."""
    data = {'id': conversation_id}
    
    response = Webhook.create_conversation(timestamp, data)
    
    assert response['status'] == 'CREATED'
    assert response['type'] == 'NEW_CONVERSATION'
    assert str(response['id']) == conversation_id
    
    # Verifica se a conversa foi criada no banco
    conversation = api.models.Conversation.objects.get(id=conversation_id)
    assert conversation.status == 'OPEN'
    assert conversation.create_timestamp == timestamp


def test_create_conversation_missing_id(timestamp):
    """Testa criação de conversa sem ID."""
    with pytest.raises(ValidationError) as exc_info:
        Webhook.create_conversation(timestamp, {})
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.message == 'Data.id not specified'


def test_create_conversation_invalid_uuid(timestamp):
    """Testa criação de conversa com UUID inválido."""
    data = {'id': 'invalid-uuid'}
    
    with pytest.raises(ValidationError) as exc_info:
        Webhook.create_conversation(timestamp, data)
    
    assert exc_info.value.status_code == 400
    assert "UUID v4 format" in exc_info.value.message


@pytest.mark.django_db
def test_create_conversation_duplicate_id(timestamp, conversation_id):
    """Testa criação de conversa com ID duplicado."""
    data = {'id': conversation_id}
    
    # Cria a primeira conversa
    Webhook.create_conversation(timestamp, data)
    
    # Tenta criar outra com o mesmo ID
    with pytest.raises(ValidationError) as exc_info:
        Webhook.create_conversation(timestamp, data)
    
    assert exc_info.value.status_code == 422
    assert "already exists" in exc_info.value.message


@pytest.mark.django_db
def test_create_message_success(conversation, timestamp, message_id):
    """Testa criação de mensagem com sucesso."""
    message_data = {
        'id': message_id,
        'direction': 'SENT',
        'content': 'Test message',
        'conversation_id': str(conversation.id)
    }
    
    response = Webhook.create_message(timestamp, message_data)
    
    assert response['status'] == 'CREATED'
    assert response['type'] == 'NEW_MESSAGE'
    assert str(response['id']) == message_id
    
    # Verifica se a mensagem foi criada no banco
    message = api.models.Message.objects.get(id=message_id)
    assert message.direction == 'SENT'
    assert message.content == 'Test message'
    assert str(message.conversation_id) == str(conversation.id)


@pytest.mark.django_db
def test_create_message_missing_id(conversation, timestamp):
    """Testa criação de mensagem sem ID."""
    with pytest.raises(ValidationError) as exc_info:
        Webhook.create_message(timestamp, {'direction': 'SENT', 'content': 'Test'})
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.message == 'Data.id not specified'


@pytest.mark.django_db
def test_create_message_missing_direction(conversation, timestamp, message_id):
    """Testa criação de mensagem sem direction."""
    with pytest.raises(ValidationError) as exc_info:
        Webhook.create_message(timestamp, {'id': message_id, 'content': 'Test'})
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.message == 'Data.direction not specified'


@pytest.mark.django_db
def test_create_message_invalid_direction(conversation, timestamp, message_id):
    """Testa criação de mensagem com direction inválido."""
    data = {
        'id': message_id,
        'direction': 'INVALID',
        'content': 'Test',
        'conversation_id': str(conversation.id)
    }
    
    with pytest.raises(ValidationError) as exc_info:
        Webhook.create_message(timestamp, data)
    
    assert exc_info.value.status_code == 422
    assert "only accepts RECEIVED or SENT" in exc_info.value.message


@pytest.mark.django_db
def test_create_message_missing_content(conversation, timestamp, message_id):
    """Testa criação de mensagem sem content."""
    with pytest.raises(ValidationError) as exc_info:
        Webhook.create_message(timestamp, {
            'id': message_id,
            'direction': 'SENT'
        })
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.message == 'Data.content not specified'


def test_create_message_missing_conversation_id(timestamp, message_id):
    """Testa criação de mensagem sem conversation_id."""
    with pytest.raises(ValidationError) as exc_info:
        Webhook.create_message(timestamp, {
            'id': message_id,
            'direction': 'SENT',
            'content': 'Test'
        })
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.message == 'Data.conversation_id not specified'


def test_create_message_invalid_conversation_id(timestamp, message_id):
    """Testa criação de mensagem com conversation_id inválido."""
    data = {
        'id': message_id,
        'direction': 'SENT',
        'content': 'Test',
        'conversation_id': 'invalid-uuid'
    }
    
    with pytest.raises(ValidationError) as exc_info:
        Webhook.create_message(timestamp, data)
    
    assert exc_info.value.status_code == 400
    assert "UUID v4 format" in exc_info.value.message


@pytest.mark.django_db
def test_create_message_nonexistent_conversation(timestamp, message_id):
    """Testa criação de mensagem para conversa inexistente."""
    data = {
        'id': message_id,
        'direction': 'SENT',
        'content': 'Test',
        'conversation_id': str(uuid.uuid4())
    }
    
    with pytest.raises(ValidationError) as exc_info:
        Webhook.create_message(timestamp, data)
    
    assert exc_info.value.status_code == 422
    assert "does not exist" in exc_info.value.message


@pytest.mark.django_db
def test_create_message_closed_conversation(closed_conversation, timestamp, message_id):
    """Testa criação de mensagem em conversa fechada."""
    message_data = {
        'id': message_id,
        'direction': 'SENT',
        'content': 'Test message',
        'conversation_id': str(closed_conversation.id)
    }
    
    with pytest.raises(ValidationError) as exc_info:
        Webhook.create_message(timestamp, message_data)
    
    assert exc_info.value.status_code == 422
    assert "already been closed" in exc_info.value.message


@pytest.mark.django_db
def test_create_message_duplicate_id(conversation, timestamp, message_id):
    """Testa criação de mensagem com ID duplicado."""
    message_data = {
        'id': message_id,
        'direction': 'SENT',
        'content': 'Test message',
        'conversation_id': str(conversation.id)
    }
    Webhook.create_message(timestamp, message_data)
    
    # Tenta criar outra mensagem com o mesmo ID
    with pytest.raises(ValidationError) as exc_info:
        Webhook.create_message(timestamp, message_data)
    
    assert exc_info.value.status_code == 422
    assert "already exists" in exc_info.value.message


@pytest.mark.django_db
def test_close_conversation_success(conversation, timestamp):
    """Testa fechamento de conversa com sucesso."""
    close_timestamp = timezone.now()
    conversation_data = {'id': str(conversation.id)}
    
    response = Webhook.close_conversation(close_timestamp, conversation_data)
    
    assert response['status'] == 'CLOSED'
    assert response['type'] == 'CLOSE_CONVERSATION'
    assert str(response['id']) == str(conversation.id)
    
    # Verifica se a conversa foi fechada
    conversation.refresh_from_db()
    assert conversation.status == 'CLOSED'
    assert conversation.edit_timestamp == close_timestamp


def test_close_conversation_missing_id(timestamp):
    """Testa fechamento de conversa sem ID."""
    with pytest.raises(ValidationError) as exc_info:
        Webhook.close_conversation(timestamp, {})
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.message == 'Data.id not specified'


def test_close_conversation_invalid_uuid(timestamp):
    """Testa fechamento de conversa com UUID inválido."""
    data = {'id': 'invalid-uuid'}
    
    with pytest.raises(ValidationError) as exc_info:
        Webhook.close_conversation(timestamp, data)
    
    assert exc_info.value.status_code == 400
    assert "UUID v4 format" in exc_info.value.message


@pytest.mark.django_db
def test_close_conversation_nonexistent(timestamp):
    """Testa fechamento de conversa inexistente."""
    data = {'id': str(uuid.uuid4())}
    
    with pytest.raises(ValidationError) as exc_info:
        Webhook.close_conversation(timestamp, data)
    
    assert exc_info.value.status_code == 422
    assert "does not exist" in exc_info.value.message


@pytest.mark.django_db
def test_process_webhook_new_conversation(timestamp, conversation_id):
    """Testa process_webhook com tipo NEW_CONVERSATION."""
    webhook = Webhook()
    data = {'id': conversation_id}
    
    response = webhook.process_webhook('NEW_CONVERSATION', timestamp, data)
    
    assert response['status'] is True
    assert response['status_code'] == 200
    assert response['response']['type'] == 'NEW_CONVERSATION'
    assert str(response['response']['id']) == conversation_id


@pytest.mark.django_db
def test_process_webhook_new_message(conversation, timestamp, message_id):
    """Testa process_webhook com tipo NEW_MESSAGE."""
    webhook = Webhook()
    data = {
        'id': message_id,
        'direction': 'RECEIVED',
        'content': 'Hello',
        'conversation_id': str(conversation.id)
    }
    
    response = webhook.process_webhook('NEW_MESSAGE', timestamp, data)
    
    assert response['status'] is True
    assert response['status_code'] == 200
    assert response['response']['type'] == 'NEW_MESSAGE'
    assert str(response['response']['id']) == message_id


@pytest.mark.django_db
def test_process_webhook_close_conversation(conversation, timestamp):
    """Testa process_webhook com tipo CLOSE_CONVERSATION."""
    webhook = Webhook()
    data = {'id': str(conversation.id)}
    close_timestamp = timezone.now()
    
    response = webhook.process_webhook('CLOSE_CONVERSATION', close_timestamp, data)
    
    assert response['status'] is True
    assert response['status_code'] == 200
    assert response['response']['type'] == 'CLOSE_CONVERSATION'
    assert str(response['response']['id']) == str(conversation.id)
