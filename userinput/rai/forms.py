from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.html import format_html

from userdata.models import StaffUser
from userinput.models import RUBIONUser, WorkGroup

from rai.widgets import RAITypeAndSelect, RAIRadioSelect, RAITextInput, RAISelect

from rubauth.rai.forms import RUBLoginIdField

class MoveToWorkgroupForm(forms.Form):
    workgroup = forms.ChoiceField(
        widget = RAITypeAndSelect(
            attrs = {
                'label': 'Neue Arbeitsgruppe',
                'class': "required"
            }
        )
    )
        
    def __init__(self, workgroups, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['workgroup'].choices = [
            (wg.pk, "{}|Leiter: {}".format(wg.title_de, wg.get_head())) for wg in workgroups
        ]
        
def get_users():
    users = RUBIONUser.objects.active().filter(is_leader = False)
    for_choices = [('', '-------')]
    # for user in users:
    #     for_choices.append()
    
    return  [('', '-' * 30)] + [
        ( user.pk,
          '{} {}|Derzeitige Arbeitsgruppe: {}'.format(
              user.first_name, user.last_name, user.get_workgroup()
          )
        ) for user in users 
    ]

def get_staff():
    staff_list = []
    staff_users = StaffUser.objects.active()
    for staff in staff_users:
        if not RUBIONUser.objects.filter(linked_user = staff.user).exists():
            staff_list.append((staff.pk, '{} {}'.format(staff.first_name, staff.last_name)))
    return  [('', '-' * 30)]  + staff_list

class GroupLeaderForm(forms.Form):
    leader_source = forms.ChoiceField(
        choices = [
            ('new_external_user', 'Neuen externen Nutzer anlegen'),
            ('new_rub_user', 'Neuen Nutzer aus der Ruhr-Universität anlegen'),
            ('rubion_user', 'Existierenden Nutzer aus anderer Arbeitsgruppe als Leiter dieser Arbeitsgruppe übernehmen'),
            ('staff_user', 'RUBION-Mitarbeiter als Leiter dieser Arbeitsgruppe übernehmen'),
            
        ],
        label = 'Quelle für den Gruppenleiter aussuchen',
        help_text = 'Eine Arbeitsgruppe benötigt zwingend einen Gruppenleiter.',
        widget = RAIRadioSelect
    )
    rub_id = forms.CharField(
        widget = RAITextInput,
        required = False
    )
    rubion_user = forms.ChoiceField(
        widget = RAITypeAndSelect,
        choices = get_users, 
        required = False,
        label = 'Bestehenden Nutzer auswählen',
        help_text = (
            'Bitte beachten: '+
            '1) Nutzer, die bereits Leiter einer Arbeitsgruppe sind, können '+
            'nicht Leiter einer zweiten Arbeitsgruppe werden. '+
            '2) Der Leiter der Arbeitsgruppe, aus dem der neue AG-Leiter '+
            'ausgewählt wird, wird per E-Mail darüber benachrichtigt, dass '+
            'sein Mitarbeiter nicht mehr Mitglied seiner Arbeitsgruppe ist.'
        )
    )
    staff_user = forms.ChoiceField(
        required = False,
        widget = RAITypeAndSelect,
        choices = get_staff,
        label = 'Mitarbeiter auswählen',
        help_text = 'Bitte beachten: RUBION-Mitarbeiter, die auch als Nutzer gelistet sind, sind in der Nutzerliste aufgeführt.'
    )
    new_user_last_name = forms.CharField(
        required = False,
        widget = RAITextInput,
        label = 'Name',
        help_text = 'Nachname des Gruppenleiters',
        
    )
    new_user_first_name = forms.CharField(
        required = False,
        widget = RAITextInput,
        label = 'Vorname',
        help_text = 'Vorname des Gruppenleiters',
    )
    new_user_email = forms.CharField(
        required = False,
        widget = RAITextInput,
        label = 'E-Mail-Adresse',
        help_text = 'E-Mail-Adresse des Gruppenleiters',
    )
    new_user_salutation = forms.ChoiceField(
        choices = (
            ('male', 'Herr'),
            ('female', 'Frau')
        ),
        required = False,
        widget = RAISelect,
        label = 'Anrede',
        help_text = 'Anrede des Gruppenleiters',
    )
    new_user_academic_title = forms.ChoiceField(
        choices = (
            ('profdr', 'Prof. Dr.'),
            ('prof', 'Prof.'),
            ('dr', 'Dr.'),
            ('msc', 'MSc'),
            ('bsc', 'BSc'),
            ('', '-'*30) 
        ),
        required = False,
        widget = RAISelect,
        label = 'Titel',
        help_text = 'Der akademische Titel des Gruppenleiters',
    )

    def clean(self):
        cleanded_data = super().clean()

        return cleaned_data


class WorkgroupStatusForm(forms.Form):
    status = forms.ChoiceField(
        choices = (
            ('apply', 'Antrag auf Aufnahme gestellt'),
            ('accepted', 'Antrag auf Aufnahme bereits genehmigt'),
        ),
        widget = RAIRadioSelect
    )

class RUBIONUserWorkgroupForm(forms.Form):
    workgroup = forms.ChoiceField(
        label = 'In welcher Arbeitsgruppe ist der neue Nutzer tätig?',
        widget = RAITypeAndSelect,
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        groups = WorkGroup.objects.active().order_by('title_de')
        self.fields['workgroup'].choices = [
            (group.pk, '{}|Gruppenleiter: {}'.format(group.specific.title_de, group.get_head())) for group in groups
        ]
class RUBIONUserSourceForm(forms.Form):
    source = forms.ChoiceField(
        choices = (
            ('rub', 'Neuen RUB-Nutzer einrichten'),
            ('ext', 'Externen Nutzer einrichten')
        ),
        widget = RAIRadioSelect,
        label = 'Ist der neue Nutzer ein RUB-Mitglied oder ein externer Nutzer?'
    )
    
    rub_id = RUBLoginIdField(
        required = False,
        label = 'RUB-Id',
        check_existance = True
    )

    ext_last_name  = forms.CharField(
        required = False,
        label = 'Nachname',
        widget = RAITextInput
    )
    ext_first_name  = forms.CharField(
        required = False,
        label = 'Vorname',
        widget = RAITextInput
    )
    ext_email = forms.CharField(
        required = False,
        label = 'E-Mail-Adresse',
        widget = RAITextInput,
        help_text = 'Der Nutzer kann sich mit der angegebenen E-Mail-Adresse in die RUBION-Webseite einloggen. Eine E-Mail zum Setzen des Passworts wird verschickt.'   
    )

    def user_exists_msg(self, ruser, item):
        url = reverse('rai_userinput_rubionuser_edit', args=[ruser.pk])
        return format_html(
            'Ein Nutzer mit dieser {item} ist bereits registriert:<p><address><a href="{url}" class="alert-link"><i class="fas fa-pen"></i> <strong class="ml-1">{name}, {first}</strong></a><br />{ag}<br/>Status: {status}</p>',
            url=url,
            name = ruser.name_db or ruser.linked_user.last_name,
            first = ruser.first_name_db or ruser.linked_user.first_name,
            ag = ruser.get_workgroup(),
            status = 'aktiv' if ruser.linked_user.is_active else 'inaktiv',
            item = item
        )

    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['source'] == 'rub':
            self.fields['rub_id'].required = True
            try:
                self.fields['rub_id'].validate(cleaned_data.get('rub_id', ''))
                error = False
            except ValidationError as e:
                self.add_error('rub_id', e)
                error = True
            if not error:
                if RUBIONUser.objects.filter(linked_user__username = cleaned_data['rub_id']).exists():
                    ruser = RUBIONUser.objects.get(linked_user__username = cleaned_data['rub_id'])

                    self.add_error(
                        'rub_id', self.user_exists_msg(ruser, 'RUB-ID')
                    )
        if cleaned_data['source'] == 'ext':
            self.fields['ext_last_name'].required = True
            self.fields['ext_first_name'].required = True
            self.fields['ext_email'].required = True
            try:
                self.fields['ext_last_name'].validate(cleaned_data.get('ext_last_name', ''))
            except ValidationError as e:
                self.add_error('ext_last_name', e)
            try:
                self.fields['ext_first_name'].validate(cleaned_data.get('ext_first_name', ''))
            except ValidationError as e:
                self.add_error('ext_first_name', e)
            try:
                self.fields['ext_email'].validate(cleaned_data.get('ext_email', ''))
                error = False
            except ValidationError as e:
                self.add_error('ext_email', e)
                error = True
            if not error:
                if RUBIONUser.objects.filter(linked_user__username = cleaned_data['ext_email']).exists():
                    self.add_error(
                        'ext_email',
                        self.user_exists_msg(
                            RUBIONUser.objects.get(linked_user__username = cleaned_data['ext_email']),
                            'E-Mail-Adresse'
                        )
                    )
        return cleaned_data
    
    
