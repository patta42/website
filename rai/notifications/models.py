from django.db import models
from django.contrib.auth import get_user_model

from rai.settings.fields import JsonField
from rai.settings.models import ModelWithJsonField

User = get_user_model()

class NotificationTemplate(models.Model):
    notification_id = models.CharField(
        help_text = 'Identifikationsstring der Benachrichtigung',
        max_length = 128,
        unique = True
    )
    template = models.TextField(
        help_text = 'Die Vorlage für die deutschsprachige E-Mail'
    )
    template_en = models.TextField(
        help_text = 'Die Vorlage für die englischsprachige E-Mail',
        blank = True
    )
    subject = models.CharField(
        help_text = 'Die Betreff-Zeile für die deutschsprachige E-Mail',
        blank = True,
        max_length = 512
    )
    subject_en = models.CharField(
        help_text = 'Die Betreff-Zeile für die englischsprachige E-Mail',
        blank = True,
        max_length = 512
    )
    def __str__ (self):
        from rai.notifications.internals import REGISTERED_NOTIFICATIONS
        noti = REGISTERED_NOTIFICATIONS.get(self.notification_id, None)
        if noti:
            return noti.title
        else:
            return "unbekannt"

class NotificationSentHelper(ModelWithJsonField):
    notification_id = models.CharField(
        help_text = 'Identifikationsstring der Benachrichtigung',
        max_length = 128,
    )
    user = models.ForeignKey(
        User,
        related_name = 'sent_notifications'
    )
    date = models.DateField(
        auto_now = True
    )
    info = JsonField( blank = True)
    
        
