from django.db import models
from django.utils import timezone
import uuid


class Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    edited_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    create_timestamp = models.DateTimeField(help_text='Original event create timestamp')
    edit_timestamp = models.DateTimeField(help_text='Original event edit timestamp', null=True)

    class Meta:
        managed = False
        abstract = True

    def save(self, *args, **kwargs):
        if self.created_at is None:
            self.created_at = timezone.now()

        else:
            self.edited_at = timezone.now()

        super(Log, self).save(*args, **kwargs)
