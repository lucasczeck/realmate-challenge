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

        return response

    @staticmethod
    def create_conversation(timestamp, data):
        if not data.get('id'):
            raise ValidationError('Data.id not specified', status_code=400)

        try:
            uuid_obj = uuid.UUID(data['id'])
        except ValueError:
            raise ValidationError("The 'id' field must be in UUID v4 format.", status_code=400)

        new_conversation = api.models.Conversation(id=uuid_obj, create_timestamp=timestamp)
        new_conversation.save()

        response = {'status': 'CREATED', 'id': new_conversation.id, 'type': 'NEW_CONVERSATION'}

        return response
