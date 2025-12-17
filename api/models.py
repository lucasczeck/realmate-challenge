from core.models import Log
from django.db import models


class Conversation(Log):
    class Status(models.TextChoices):
        OPEN = 'OPEN'
        CLOSED = 'CLOSED'

    status = models.CharField(max_length=6, choices=Status.choices, default=Status.OPEN)

    class Meta:
        db_table = 'api_conversarion'


class Message(Log):
    class Direction(models.TextChoices):
        SENT = 'SENT'
        RECEIVED = 'RECEIVED'

    direction = models.CharField(max_length=8, choices=Direction.choices)
    conversation = models.ForeignKey('Conversation', on_delete=models.DO_NOTHING)
    content = models.TextField()

    class Meta:
        db_table = 'api_message'
