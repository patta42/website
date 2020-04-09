import datetime

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from userdata.models import StaffUser
from rai.fields import RAIItemsField
from rai.markdown.fields import MarkdownField

def get_choices():
    return (
        (
            models.Q(expire_at__isnull= True)
            |
            models.Q(expire_at__gte = datetime.datetime.today())
        ) &
        models.Q(user__is_active = True)
    )

class RAIGroup(models.Model):
    class Meta:
        verbose_name = _('Permission group for RAI.')
        
    name = models.CharField(
        max_length = 64,
        verbose_name = _('Name of the group')
    )
    description = MarkdownField(
        max_length = 512,
        verbose_name = _('Short description of the group'),
        blank = True,
        null = True
    )
    members = models.ManyToManyField(
        StaffUser,
        verbose_name = 'Mitarbeiter in dieser Gruppe',
        limit_choices_to=get_choices
    )

    def __repr__(self): 
        return self.name
    def __str__(self):
        return self.name


class RAIPermission( models.Model ):
     rai_id = RAIItemsField(
         max_length = 128,
         verbose_name = _('Identifier of the RAI (Model) Admin'),
         help_text = _('Identifier is identifier.sub_identifier of the RAIAdmin.'),
     )
     value = models.IntegerField(
         verbose_name = _('Value code of the permission')
     )
     human_readable = models.CharField(
         max_length = 48,
         verbose_name = _('Human readable representation of the permission'),
         blank = True
     )
     group = models.ForeignKey(
         RAIGroup,
         verbose_name = 'verknüpfte Gruppe',
         on_delete = models.CASCADE

     )
    
     
