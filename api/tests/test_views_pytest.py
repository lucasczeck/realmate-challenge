"""
Exemplos de testes de views usando pytest.

Demonstra como usar fixtures e sintaxe pytest para testes de API.
"""
import json
import pytest
from rest_framework import status

from api.models import Conversation, Message


@pytest.mark.django_db
def test_webhook_post_new_conversation_success(api_client, webhook_data_new_conversation, conversation_id):
    """Testa POST para criar nova conversa usando fixtures."""
    response = api_client.post('/webhook/', webhook_data_new_conversation, format='json')
    
    assert response.status_code == status.HTTP_200_OK
    response_data = json.loads(response.content)
    assert response_data['status'] is True
    assert response_data['status_code'] == 200
    assert response_data['response']['type'] == 'NEW_CONVERSATION'
    assert str(response_data['response']['id']) == conversation_id
    
    # Verifica se foi criada no banco
    conversation = Conversation.objects.get(id=conversation_id)
    assert conversation is not None


@pytest.mark.django_db
def test_webhook_post_new_message_success(
    api_client, 
    conversation, 
    webhook_data_new_message, 
    message_id
):
    """Testa POST para criar nova mensagem."""
    response = api_client.post('/webhook/', webhook_data_new_message, format='json')
    
    assert response.status_code == status.HTTP_200_OK
    response_data = json.loads(response.content)
    assert response_data['status'] is True
    assert response_data['response']['type'] == 'NEW_MESSAGE'
    assert str(response_data['response']['id']) == message_id
    
    # Verifica se foi criada no banco
    message = Message.objects.get(id=message_id)
    assert message is not None


@pytest.mark.django_db
def test_webhook_post_close_conversation_success(
    api_client, 
    conversation, 
    webhook_data_close_conversation
):
    """Testa POST para fechar conversa."""
    response = api_client.post('/webhook/', webhook_data_close_conversation, format='json')
    
    assert response.status_code == status.HTTP_200_OK
    response_data = json.loads(response.content)
    assert response_data['status'] is True
    assert response_data['response']['type'] == 'CLOSE_CONVERSATION'
    
    # Verifica se foi fechada no banco
    conversation.refresh_from_db()
    assert conversation.status == 'CLOSED'


@pytest.mark.parametrize("missing_field,expected_error", [
    ('type', 'Type not specified'),
    ('timestamp', 'Timestamp not specified'),
    ('data', 'Data not specified'),
])
@pytest.mark.django_db
def test_webhook_post_missing_fields(api_client, timestamp, conversation_id, missing_field, expected_error):
    """Testa POST com campos faltando usando parametrização."""
    data = {
        'type': 'NEW_CONVERSATION',
        'timestamp': timestamp.isoformat(),
        'data': {'id': conversation_id}
    }
    data.pop(missing_field, None)
    
    response = api_client.post('/webhook/', data, format='json')
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_data = json.loads(response.content)
    assert response_data['status'] is False
    assert response_data['status_code'] == 400
    assert response_data['description'] == expected_error


@pytest.mark.django_db
def test_webhook_post_invalid_type(api_client, timestamp, conversation_id):
    """Testa POST com tipo inválido."""
    data = {
        'type': 'INVALID_TYPE',
        'timestamp': timestamp.isoformat(),
        'data': {'id': conversation_id}
    }
    
    response = api_client.post('/webhook/', data, format='json')
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    response_data = json.loads(response.content)
    assert response_data['status'] is False
    assert response_data['status_code'] == 422


@pytest.mark.django_db
def test_webhook_post_message_to_closed_conversation(
    api_client, 
    closed_conversation, 
    timestamp, 
    message_id
):
    """Testa POST de mensagem para conversa fechada."""
    message_data = {
        'type': 'NEW_MESSAGE',
        'timestamp': timestamp.isoformat(),
        'data': {
            'id': message_id,
            'direction': 'SENT',
            'content': 'Test',
            'conversation_id': str(closed_conversation.id)
        }
    }
    
    response = api_client.post('/webhook/', message_data, format='json')
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    response_data = json.loads(response.content)
    assert response_data['status'] is False
    assert 'already been closed' in response_data['description']
