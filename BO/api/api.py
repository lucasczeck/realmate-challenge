import uuid

import api.models

from BO.base.decorator import Response
from BO.base.exception import ValidationError


class Webhook:

    @Response(desc_error='Error processing request')
    def process_webhook(self, type_webhook, timestamp, data):
        if not type_webhook:
            raise ValidationError('Type not specified', status_code=400)

        if not timestamp:
            raise ValidationError('Timestamp not specified', status_code=400)

        if not data:
            raise ValidationError('Data not specified', status_code=400)

        if type_webhook == 'NEW_CONVERSATION':
            response = self.create_conversation(timestamp, data)

        elif type_webhook == 'NEW_MESSAGE':
            response = self.create_message(timestamp, data)

        elif type_webhook == 'CLOSE_CONVERSATION':
            response = self.close_conversation(timestamp, data)

        else:
            raise ValidationError("The 'type' field only accepts NEW_CONVERSATION or NEW_MESSAGE or "
                                  "CLOSE_CONVERSATION.", status_code=422)

        return response

    @staticmethod
    def create_conversation(timestamp, data):
        if not data.get('id'):
            raise ValidationError('Data.id not specified', status_code=400)

        try:
            uuid_obj = uuid.UUID(data['id'])
        except ValueError:
            raise ValidationError("The 'id' field must be in UUID v4 format.", status_code=400)

        if api.models.Conversation.objects.filter(id=uuid_obj).exists():
            raise ValidationError("A conversation already exists with that ID; it's not possible to create another "
                                  "one.", status_code=422)

        new_conversation = api.models.Conversation(id=uuid_obj, create_timestamp=timestamp)
        new_conversation.save()

        response = {'status': 'CREATED', 'id': new_conversation.id, 'type': 'NEW_CONVERSATION'}

        return response

    @staticmethod
    def create_message(timestamp, data):
        if not data.get('id'):
            raise ValidationError('Data.id not specified', status_code=400)

        if not data.get('direction'):
            raise ValidationError('Data.direction not specified', status_code=400)

        if data['direction'] not in ('RECEIVED', 'SENT'):
            raise ValidationError("The 'direction' field only accepts RECEIVED or SENT.", status_code=422)

        if not data.get('content'):
            raise ValidationError('Data.content not specified', status_code=400)

        if not data.get('conversation_id'):
            raise ValidationError('Data.conversation_id not specified', status_code=400)

        try:
            id_uuid = uuid.UUID(data['id'])
        except ValueError:
            raise ValidationError("The 'id' field must be in UUID v4 format.", status_code=400)

        try:
            conversation_id_uuid = uuid.UUID(data['conversation_id'])
        except ValueError:
            raise ValidationError("The 'conversation_id' field must be in UUID v4 format.", status_code=400)

        conversation = api.models.Conversation.objects.filter(id=conversation_id_uuid).values().first()
        if not conversation:
            raise ValidationError("The indicated conversation does not exist.", status_code=422)
        else:
            if conversation['status'] == 'CLOSED':
                raise ValidationError("You are not allowed to add a message to a conversation that has already been"
                                      " closed.", status_code=422)

        if api.models.Message.objects.filter(id=id_uuid).exists():
            raise ValidationError("A message with the indicated ID already exists.", status_code=422)

        new_message = api.models.Message(id=id_uuid, create_timestamp=timestamp, conversation_id=conversation_id_uuid,
                                         direction=data['direction'], content=data['content'])
        new_message.save()

        response = {'status': 'CREATED', 'id': new_message.id, 'type': 'NEW_MESSAGE'}

        return response

    @staticmethod
    def close_conversation(timestap, data):
        if not data.get('id'):
            raise ValidationError('Data.id not specified', status_code=400)

        try:
            id_uuid = uuid.UUID(data['id'])
        except ValueError:
            raise ValidationError("The 'id' field must be in UUID v4 format.", status_code=400)

        conversation = api.models.Conversation.objects.filter(id=id_uuid).first()

        if not conversation:
            raise ValidationError("The indicated conversation does not exist.", status_code=422)

        conversation.edit_timestamp = timestap
        conversation.status = 'CLOSED'
        conversation.save()

        response = {'status': 'CLOSED', 'id': conversation.id, 'type': 'CLOSE_CONVERSATION'}

        return response
