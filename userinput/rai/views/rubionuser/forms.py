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
    fieldsets = [
        {
            'id' : 'workgroup_choice_fieldset',
            'legend' : 'Der Nutzer ist Leiter einer Arbeitsgruppe',
            'help_path':'userinput:rubionuser:inactivate:is_group_leader',
            'fields' : ['workgroup_choice'],
            'intro' : 'Bitte entscheide, was mit der Gruppe <strong>»{{workgroup}}«</strong> und ggf. ihren Mitgliedern und Ihren Projekten geschehen soll.',
            'fieldsets' : [{
                'id': 'new_leader',
                'legend':'Wer soll neuer Leiter der Arbeitsgruppe werden?',
                'fields':['new_leader'],
                'depends_on_field':'workgroup_choice',
                'show_at_value':'new_leader' 
            }]
        }
    ]

    fieldsets = [
        
    ]
    workgroup_choice = forms.ChoiceField(
        choices = (
            ('inactivate', 'Die Gruppe inaktivieren'),
            ('new_leader', 'Anderen Nutzer zum AG-Leiter ernennen (andere Nutzer und Projekte werden beibehalten)'),
        ), 
        required = True,
        widget = RAIRadioSelect
    )

    def __init__(self, members = None, projects = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if members and members.count() > 0:
            self.fields['new_leader'] = forms.ChoiceField(
                required = False,
                choices = (
                    (member.pk, '{}, {}'.format(member.specific.last_name, member.specific.first_name))
                    for member in members),
                widget = RAIRadioSelect
            )
        else:
            #self.fields.pop('workgroup_choice')
            self.fields['workgroup_choice'] = forms.BooleanField(
                disabled = True,
                required = True,
                label = 'Die Arbeitsgruppe hat keine weiteren Mitglieder und wird inaktiviert.',
                widget = RAICheckboxInput(
                    attrs = {
                        'checked': True,
                        'label': 'Die Arbeitsgruppe hat keine weiteren Mitglieder und wird inaktiviert.'
                    }
                ) ,
                
            )
        

class MemberDecisionForm(RAIForm):
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



