from pprint import pprint

from django import forms
from django.utils.safestring import mark_safe

from rai.widgets import (
    RAIRadioSelect, RUBLoginIdInput,  RAISelectMultipleSelectionLists, RAITextInput,
    RAITypeAndSelect
)
from rai.permissions.models import RAIGroup

from userdata.forms import UserAndStaffChoiceField
import re

def _get_groups():
    groups = RAIGroup.objects.all()
    return ((group.pk, group.name) for group in groups) 

class UserSourceSelectionForm(forms.Form):
    make_user_from = forms.ChoiceField(
        choices = (
            ('is_staff', mark_safe(
                'Der/die neue Mitarbeiter(in) besitzt eine RUB-ID '
                'und soll sich in RUBIONtail anmelden können')
            ),
            ('is_rub', mark_safe(
                'Der/die neue Mitarbeiter(in) besitzt zwar eine RUB-ID, '
                'soll sich aber <strong>nicht</strong> in RUBIONtail anmelden können')
            ),
            ('is_external', mark_safe(
                'Der/die neue Mitarbeiter(in) besitzt keine RUB-ID und '
                'soll sich auch <strong>nicht</strong> in RUBIONtail anmelden können')
            )
        ),
        widget = RAIRadioSelect,
        label = 'Was soll der/die neue Mitarbeiter im Verwaltungstool RUBIONtail dürfen?',
        help_text = ('Üblicherweise haben neuen Mitarbeiter/innen Zugang zu dieser '
                     'Verwaltungssoftware und nutzen ihre RUB-Login-ID, um sich  '
                     'anzumelden. Wir führen jedoch auch Mitarbeiter externer Firmen '
                     '(z.B. Reinigungspersonal) in unserer Mitarbeiter-Liste. Diese '
                     'Mitarbeiter sollten keinen Zugang zu dem Verwaltungstool haben.') 
    )
    rub_login_id = forms.CharField(
        label = 'RUB-Login-ID',
        help_text = ('Die RUB-Login-ID des/der neuen Mitarbeiters/Mitarbeiterin'),
        widget = RUBLoginIdInput,
        required = False
    )

    groups = forms.MultipleChoiceField(
        label = 'Aufgaben-Gruppen innerhalb des RUBIONtail-Verwaltungstools',
        choices = _get_groups,
        widget =  RAISelectMultipleSelectionLists,
        required = False
    )

    def clean_rub_login_id(self):
        login_id = self.cleaned_data['rub_login_id']
        if login_id == '':
            return login_id
        if not re.match('^[a-z0-9]{8}$', login_id):
            self.add_error(
                'rub_login_id',
                forms.ValidationError(
                    "Die RUB-ID ist nicht korrekt  (8 Zeichen, nur Kleinbuchstaben und Ziffern)"
                )
            )
        return login_id

    def clean(self):
        cleaned_data = super().clean()
        login_id = self.cleaned_data.get('rub_login_id', None)
        make_user_from = self.cleaned_data.get('make_user_from', None)
        if make_user_from in ['is_staff', 'is_rub']:
            if not login_id:
                self.add_error('rub_login_id', 'Aufgrund der obigen Auswahl muss die RUB-Login-ID angegeben werden')
    

class BeiratMemberReplaceForm(forms.Form):
    source = forms.ChoiceField(
        choices = (
            ('new_user', 'Neuen Nutzer anlegen'),
            ('existent_user', 'Nutzer aus Nutzer- und Mitarbeiterliste auswählen')
        ),
        label = 'Quelle für das Beiratsmitglied auswählen.',
        widget = RAIRadioSelect,
        required = True
    )

    first_name = forms.CharField(
        label = 'Vorname',
        required = False,
        widget = RAITextInput
    )
    last_name = forms.CharField(
        label = 'Nachname',
        required = False,
        widget = RAITextInput
    )
    email = forms.EmailField(
        label = 'E-Mail-Adresse',
        required = False,
        widget = RAITextInput
    )
    phone = forms.CharField(
        label = 'Telefonnummer',
        required = False,
        widget = RAITextInput
    )

    member_selection = UserAndStaffChoiceField(
        label = 'Auswahl aus Mitarbeitern und Nutzern',
        required = False,
        widget = RAITypeAndSelect
    )
    # the form may get an instance passed 
    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        
    def clean(self):
        cleaned_data = super().clean()
        source = cleaned_data.get('source', None)
        if not source:
            return cleaned_data
        if source == 'existent_user':
            if not cleaned_data.get('member_selection', None):
                self.add_error('member_selection', 'Dieses Feld muss ausgefüllt werden,')
        elif source == 'new_user':
            last_name = cleaned_data.get('last_name', None)
            if not last_name:
                self.add_error('last_name', 'Dieses Feld muss ausgefüllt werden.')
            elif len(last_name) < 2:
                self.add_error('last_name', 'Der Nachname muss mindestens zwei Zweichen lang sein.')

            first_name = cleaned_data.get('first_name', None)
            if not first_name:
                self.add_error('first_name', 'Dieses Feld muss ausgefüllt werden.')
            elif len(first_name) < 2:
                self.add_error('first_name', 'Der Vorname muss mindestens zwei Zweichen lang sein.')

            email = cleaned_data.get('email')
            errors = self.errors.as_data()
            if not email and not errors.get('email', None):
                self.add_error('email', 'Dieses Feld muss ausgefüllt werden.')

            phone= cleaned_data.get('phone', None)
            if not phone:
                self.add_error('phone', 'Dieses Feld muss ausgefüllt werden.')
            
            
        return cleaned_data
