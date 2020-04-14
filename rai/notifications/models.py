from django.db import models

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
        help_text = 'Die Vorlge für die englischsprachige E-Mail',
        blank = True
    )
    
