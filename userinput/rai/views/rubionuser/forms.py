from pprint import pprint

from django import forms
from django.forms.formsets import BaseFormSet
from django.forms.widgets import HiddenInput

from rai.widgets import RAIRadioSelect, RAISelect,RAIRadioSelectTable

class UserAndStaffInactivationForm(forms.Form):
    user_staff_choice = forms.ChoiceField(
        choices =(
            ('user_only', 'Nur den Nutzer inaktivieren'),
            ('user_and_staff', 'Nutzer und Mitarbeiter inaktivieren'),
        ),
        required = True,
        widget = RAIRadioSelect,
        
    )


class WorkgroupInactivationForm(forms.Form):
    workgroup_choice = forms.ChoiceField(
        choices = (
            ('inactivate', 'Die Gruppe inaktivieren'),
            ('new_leader', 'Anderen Nutzer zum AG-Leiter ernennen (andere Nutzer und Projekte werden beibehalten)'),
        ),
        required = True,
        widget = RAIRadioSelect
    )

    def __init__(self, *args, **kwargs):
        members = kwargs.pop('members', None)
        super().__init__(*args, **kwargs)
        self.fields['new_leader'] = forms.ChoiceField(
            required = False,
            choices = (
                (member.pk, '{}, {}'.format(member.specific.last_name, member.specific.first_name))
                for member in members),
            widget = RAIRadioSelect
        )
        

class MemberDecisionForm(forms.Form):
    # fake field to get the user's name into the form
    name = forms.CharField(required = False)
    pk = forms.IntegerField(widget=HiddenInput)
    decision = forms.ChoiceField(
        choices = (
            ('inactivate', 'inaktivieren'), 
            ('move', 'andere Gruppe'),
        ),
        widget = RAIRadioSelectTable
    )
    target_group = forms.ChoiceField(choices = (), widget = RAISelect)
    

    def __init__(self, *args, **kwargs):
        groups = kwargs.pop('groups', [])
        super().__init__(*args, **kwargs)
        self.fields['target_group'].choices = groups


    
class ProjectDecisionForm(MemberDecisionForm):
    decision = forms.ChoiceField(
        choices = (
            ('inactivate', 'inaktivieren'), 
            ('move', 'andere Gruppe'),
        ),
        widget = RAIRadioSelectTable
    )



