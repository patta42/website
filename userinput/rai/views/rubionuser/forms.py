from pprint import pprint

from django import forms
from django.forms.formsets import BaseFormSet
from django.forms.widgets import HiddenInput


from rai.forms import RAIForm, RAIAdminModelForm
from rai.edit_handlers import RAIFieldPanel, RAIObjectList
from rai.widgets import (
    RAIRadioSelect, RAISelect, RAIRadioSelectTable,
    RAICheckboxInput, RAIDateInput, RAISelectMultipleCheckboxes,
    RAISelectMultipleSelectionLists
)

from userdata.models import (
    SafetyInstructionsSnippet, StaffUser, SafetyInstructionUserRelation
)
from userinput.models import WorkGroup, RUBIONUser

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
#g                disabled = True,
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



class ActivateUserWorkgroupChoiceForm(RAIForm):
    
    workgroup_choice = forms.ChoiceField(
        required = True,
        widget = RAIRadioSelect
    )

    def __init__(self, instance = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = []
        for wg in WorkGroup.objects.order_by('-expire_at', 'title_de'):
            if wg.is_inactivated():
                choices.append((wg.pk, '{} (nicht mehr aktiv)'.format(wg.specific.title_de)))
            else:
                choices.append((wg.pk, wg.specific.title_de))
                
        self.fields['workgroup_choice'].choices = choices
        wg = instance.get_workgroup()
        if not self.fields['workgroup_choice'].initial:
            self.fields['workgroup_choice'].initial = wg.pk
        

class AddInstructionsForm(RAIForm):
    instructions = forms.MultipleChoiceField(
        label = 'Unterweisung',
        widget = RAISelectMultipleCheckboxes
    )
    
    date = forms.DateField(
        label = 'Unterweisungstermin',
        widget = RAIDateInput
    )

    participants = forms.MultipleChoiceField(
        label = 'Teilnehmer',
        widget = RAISelectMultipleSelectionLists
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['instructions'].choices = [
            (si.pk, si) for si in SafetyInstructionsSnippet.objects.all()
        ]
        excl_pk = StaffUser.objects.filter(user__isnull = False).values_list('user', flat = True)
        
        p_choices = [(
            's{}'.format(staff.pk), '{}, {}'.format(staff.last_name, staff.first_name)
        ) for staff in StaffUser.objects.all()]

        p_choices += [(
            'r{}'.format(ruser.pk), '{}, {}'.format(ruser.last_name, ruser.first_name)
        ) for ruser in RUBIONUser.objects.exclude(linked_user__pk__in = excl_pk)]

        p_choices.sort(key=lambda tup: tup[1])
        self.fields['participants'].choices = p_choices

    def save(self):
        for p_pk in self.cleaned_data['participants']:
            utype = p_pk[0]
            pk = int(p_pk[1:])
            if utype == 'r':
                model = RUBIONUser
                field = 'rubion_user'
            elif utype == 's':
                model = StaffUser
                field = 'rubion_staff'

            user = model.objects.get(pk = pk)
            for instruction_pk in self.cleaned_data['instructions']:
                inst = SafetyInstructionsSnippet.objects.get(pk = instruction_pk)
                rel = SafetyInstructionUserRelation(
                    date = self.cleaned_data['date'],
                    instruction = inst
                )
                setattr(rel, field, user)
                
                rel.save()

