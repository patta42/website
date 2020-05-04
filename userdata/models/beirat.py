from django.db import models
from django.utils.translation import gettext as _

from website.models import TranslatedField
from userdata.models import StaffUser

class BeiratGroups(models.Model):
    title_de = models.CharField(
        max_length = 128,
        verbose_name = 'Gruppe innerhalb des Beirats (deutsch)'
    )
    title_en = models.CharField(
        max_length = 128,
        verbose_name = 'Gruppe innerhalb des Beirats (english)'
    )
    order = models.IntegerField(
        verbose_name = 'Anzeigeposition in der Beiratsliste'
    )
    has_sub_groups = models.BooleanField(
        default = False,
        help_text = _('Ist diese Gruppe in Untergruppen nach Bereichen unterteilt?') 
    )
    title = TranslatedField('title_en', 'title_de')

    def __str__(self):
        return self.title

class Beirat2StaffRelation(models.Model):
    beirat_group = models.ForeignKey(
        BeiratGroups,
        on_delete = models.CASCADE
    )
    member = models.ForeignKey(
        StaffUser,
        on_delete = models.CASCADE,
        null = True,
        blank = True
    )
    is_surrogate = models.BooleanField(
        default = False,
        help_text = _('Is this Beitrat member surrogate?')
    )
    is_head = models.BooleanField(
        default = False,
        help_text = _('Is the member head of the Beirat')
    )
    faculty_group = models.CharField(
        max_length = 64,
        choices = (
            ('natural', _('Natural Sciences')),
            ('engineering', _('Engineering')),
            ('medicine', _('Medicine'))
        ),
        blank = True,
        null = True
    )
    def __str__(self):
        return '{} ({})'.format(str(self.member), str(self.beirat_group))
