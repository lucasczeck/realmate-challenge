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


# Testes para GET /conversations/
@pytest.mark.django_db
def test_conversations_get_all_success(api_client, timestamp):
    """Testa GET para listar todas as conversas sem filtros."""
    import uuid
    from api.models import Conversation
    
    # Cria duas conversas independentes
    conv1 = Conversation(
        id=uuid.uuid4(),
        create_timestamp=timestamp,
        status=Conversation.Status.OPEN
    )
    conv1.save()
    
    conv2 = Conversation(
        id=uuid.uuid4(),
        create_timestamp=timestamp,
        status=Conversation.Status.CLOSED,
        edit_timestamp=timestamp
    )
    conv2.save()
    
    response = api_client.get('/conversations/')
    
    assert response.status_code == status.HTTP_200_OK
    response_data = json.loads(response.content)
    assert response_data['status'] is True
    assert response_data['status_code'] == 200
    assert 'conversations' in response_data
    assert len(response_data['conversations']) == 2
    assert all('id' in conv for conv in response_data['conversations'])
    assert all('status' in conv for conv in response_data['conversations'])
    assert all('create_timestamp' in conv for conv in response_data['conversations'])


@pytest.mark.django_db
def test_conversations_get_empty_list(api_client):
    """Testa GET quando não há conversas."""
    response = api_client.get('/conversations/')
    
    assert response.status_code == status.HTTP_200_OK
    response_data = json.loads(response.content)
    assert response_data['status'] is True
    assert response_data['status_code'] == 200
    assert 'conversations' in response_data
    assert len(response_data['conversations']) == 0


@pytest.mark.django_db
def test_conversations_get_filter_by_status_open(api_client, timestamp):
    """Testa GET filtrando por status OPEN."""
    import uuid
    from api.models import Conversation
    
    # Cria conversa aberta
    conv_open = Conversation(
        id=uuid.uuid4(),
        create_timestamp=timestamp,
        status=Conversation.Status.OPEN
    )
    conv_open.save()
    
    # Cria conversa fechada
    conv_closed = Conversation(
        id=uuid.uuid4(),
        create_timestamp=timestamp,
        status=Conversation.Status.CLOSED,
        edit_timestamp=timestamp
    )
    conv_closed.save()
    
    response = api_client.get('/conversations/', {'status': 'OPEN'})
    
    assert response.status_code == status.HTTP_200_OK
    response_data = json.loads(response.content)
    assert response_data['status'] is True
    assert len(response_data['conversations']) == 1
    assert response_data['conversations'][0]['status'] == 'OPEN'
    assert str(response_data['conversations'][0]['id']) == str(conv_open.id)


@pytest.mark.django_db
def test_conversations_get_filter_by_status_closed(api_client, timestamp):
    """Testa GET filtrando por status CLOSED."""
    import uuid
    from api.models import Conversation
    
    # Cria conversa aberta
    conv_open = Conversation(
        id=uuid.uuid4(),
        create_timestamp=timestamp,
        status=Conversation.Status.OPEN
    )
    conv_open.save()
    
    # Cria conversa fechada
    conv_closed = Conversation(
        id=uuid.uuid4(),
        create_timestamp=timestamp,
        status=Conversation.Status.CLOSED,
        edit_timestamp=timestamp
    )
    conv_closed.save()
    
    response = api_client.get('/conversations/', {'status': 'CLOSED'})
    
    assert response.status_code == status.HTTP_200_OK
    response_data = json.loads(response.content)
    assert response_data['status'] is True
    assert len(response_data['conversations']) == 1
    assert response_data['conversations'][0]['status'] == 'CLOSED'
    assert str(response_data['conversations'][0]['id']) == str(conv_closed.id)


@pytest.mark.django_db
def test_conversations_get_filter_by_invalid_status(api_client):
    """Testa GET com status inválido."""
    response = api_client.get('/conversations/', {'status': 'INVALID'})
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    response_data = json.loads(response.content)
    assert response_data['status'] is False
    assert response_data['status_code'] == 422
    assert 'status does not exist' in response_data['description']


@pytest.mark.django_db
def test_conversations_get_filter_by_date(api_client, timestamp, conversation_id):
    """Testa GET filtrando por data."""
    from datetime import date
    from api.models import Conversation
    import uuid
    
    # Cria conversa com data específica
    test_date = date(2024, 1, 15)
    test_timestamp = timestamp.replace(year=2024, month=1, day=15)
    conv = Conversation(
        id=uuid.UUID(conversation_id),
        create_timestamp=test_timestamp
    )
    conv.save()
    
    response = api_client.get('/conversations/', {'date': '2024-01-15'})
    
    assert response.status_code == status.HTTP_200_OK
    response_data = json.loads(response.content)
    assert response_data['status'] is True
    assert len(response_data['conversations']) == 1
    assert str(response_data['conversations'][0]['id']) == conversation_id


@pytest.mark.django_db
def test_conversations_get_filter_by_invalid_date_format(api_client):
    """Testa GET com formato de data inválido."""
    response = api_client.get('/conversations/', {'date': '15-01-2024'})
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_data = json.loads(response.content)
    assert response_data['status'] is False
    assert 'format YYYY-MM-DD' in response_data['description']


@pytest.mark.django_db
def test_conversations_get_filter_by_status_and_date(api_client, timestamp, conversation_id):
    """Testa GET com filtros combinados de status e data."""
    from datetime import date
    from api.models import Conversation
    import uuid
    
    # Cria conversa OPEN com data específica
    test_date = date(2024, 1, 15)
    test_timestamp = timestamp.replace(year=2024, month=1, day=15)
    conv = Conversation(
        id=uuid.UUID(conversation_id),
        create_timestamp=test_timestamp,
        status=Conversation.Status.OPEN
    )
    conv.save()
    
    response = api_client.get('/conversations/', {'status': 'OPEN', 'date': '2024-01-15'})
    
    assert response.status_code == status.HTTP_200_OK
    response_data = json.loads(response.content)
    assert response_data['status'] is True
    assert len(response_data['conversations']) == 1
    assert response_data['conversations'][0]['status'] == 'OPEN'
    assert str(response_data['conversations'][0]['id']) == conversation_id


# Testes para GET /conversations/<uuid>/
@pytest.mark.django_db
def test_conversation_detail_get_success(api_client, conversation):
    """Testa GET para obter detalhes de uma conversa existente."""
    response = api_client.get(f'/conversations/{conversation.id}/')
    
    assert response.status_code == status.HTTP_200_OK
    response_data = json.loads(response.content)
    assert response_data['status'] is True
    assert response_data['status_code'] == 200
    assert 'conversation' in response_data
    conv_data = response_data['conversation']
    assert str(conv_data['id']) == str(conversation.id)
    assert conv_data['status'] == conversation.status
    assert 'created_at' in conv_data
    assert 'closed_at' in conv_data
    assert 'messages' in conv_data
    assert isinstance(conv_data['messages'], list)


@pytest.mark.django_db
def test_conversation_detail_get_with_messages(api_client, conversation, message):
    """Testa GET para obter detalhes de uma conversa com mensagens."""
    response = api_client.get(f'/conversations/{conversation.id}/')
    
    assert response.status_code == status.HTTP_200_OK
    response_data = json.loads(response.content)
    assert response_data['status'] is True
    conv_data = response_data['conversation']
    assert len(conv_data['messages']) == 1
    assert str(conv_data['messages'][0]['id']) == str(message.id)
    assert conv_data['messages'][0]['content'] == message.content
    assert conv_data['messages'][0]['direction'] == message.direction
    assert 'created_at' in conv_data['messages'][0]


@pytest.mark.django_db
def test_conversation_detail_get_with_multiple_messages(api_client, conversation, timestamp, message_id):
    """Testa GET para obter detalhes de uma conversa com múltiplas mensagens."""
    from api.models import Message
    import uuid
    
    # Cria múltiplas mensagens
    message1 = Message(
        id=uuid.UUID(message_id),
        create_timestamp=timestamp,
        conversation=conversation,
        direction=Message.Direction.SENT,
        content='First message'
    )
    message1.save()
    
    message2_id = str(uuid.uuid4())
    message2 = Message(
        id=uuid.UUID(message2_id),
        create_timestamp=timestamp,
        conversation=conversation,
        direction=Message.Direction.RECEIVED,
        content='Second message'
    )
    message2.save()
    
    response = api_client.get(f'/conversations/{conversation.id}/')
    
    assert response.status_code == status.HTTP_200_OK
    response_data = json.loads(response.content)
    assert response_data['status'] is True
    conv_data = response_data['conversation']
    assert len(conv_data['messages']) == 2


@pytest.mark.django_db
def test_conversation_detail_get_closed_conversation(api_client, closed_conversation):
    """Testa GET para obter detalhes de uma conversa fechada."""
    response = api_client.get(f'/conversations/{closed_conversation.id}/')
    
    assert response.status_code == status.HTTP_200_OK
    response_data = json.loads(response.content)
    assert response_data['status'] is True
    conv_data = response_data['conversation']
    assert conv_data['status'] == 'CLOSED'
    assert conv_data['closed_at'] is not None


@pytest.mark.django_db
def test_conversation_detail_get_not_found(api_client):
    """Testa GET para conversa inexistente."""
    import uuid
    non_existent_id = uuid.uuid4()
    
    response = api_client.get(f'/conversations/{non_existent_id}/')
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_data = json.loads(response.content)
    assert response_data['status'] is False
    assert response_data['status_code'] == 400
    assert 'no conversation' in response_data['description'].lower()


@pytest.mark.django_db
def test_conversation_detail_get_invalid_uuid(api_client):
    """Testa GET com UUID inválido."""
    response = api_client.get('/conversations/invalid-uuid/')
    
    # Django retorna 404 para UUID inválido na URL
    assert response.status_code == status.HTTP_404_NOT_FOUND