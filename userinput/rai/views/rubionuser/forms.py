from pprint import pprint

from django import forms
from django.forms.formsets import BaseFormSet
from django.forms.widgets import HiddenInput


from rai.forms import RAIForm
from rai.edit_handlers import RAIFieldPanel, RAIObjectList
from rai.widgets import (
    RAIRadioSelect, RAISelect, RAIRadioSelectTable,
    RAICheckboxInput
)

class UserAndStaffInactivationForm(RAIForm):
    user_staff_choice = forms.ChoiceField(
        choices =(
            ('user_only', 'Nur den Nutzer inaktivieren'),
            ('user_and_staff', 'Nutzer und Mitarbeiter inaktivieren'),
        ),
        required = True,
        widget = RAIRadioSelect,
        
    )
    edit_handler = RAIFieldPanel('user_staff_choice')


    
class WorkgroupInactivationForm(RAIForm):
    workgroup_choice = forms.ChoiceField(
        choices = (
            (
                'inactivate',
                'Die Gruppe inaktivieren. Alle Nutzer und Projekte der Gruppe werden ebenfalls inaktiviert.'),
            (
                'new_leader',
                'Anderen Nutzer zum AG-Leiter ernennen (andere Nutzer und Projekte werden beibehalten)'
            ),
        ), 
        required = True,
        widget = RAIRadioSelect
    )

    def __init__(self, members = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.members = members
        if members and members.count() > 0:
            self.fields['new_leader'] = forms.ChoiceField(
                required = False,
                choices = (
                    (member.pk, '{}, {}'.format(member.specific.last_name, member.specific.first_name))
                    for member in members),
                widget = RAIRadioSelect
            )
        else:
            self.fields['workgroup_choice'] = forms.BooleanField(
                disabled = True,
                required = True,
                widget = RAICheckboxInput(
                    attrs = {
                        'checked': True,
                        'label': 'Die Arbeitsgruppe hat keine weiteren Mitglieder und wird inaktiviert.'
                    }
                )
            )
            
    def clean(self):
        cleaned_data = super().clean()
        if self.members.count() > 0 and  cleaned_data.get('workgroup_choice', None) == 'new_leader':
            allowed_pks = [str(member.pk) for member in self.members]
            if cleaned_data.get('new_leader', '') not in allowed_pks:
                self.add_error('new_leader', forms.ValidationError('Wenn ein neuer Leiter benannt werden soll, muss dieser ausgewählt werden.','required'))
            
        return cleaned_data


