from .widgets import EMailToSelect

from django import forms
from django.conf import settings
from django.utils.html import mark_safe

from rai.widgets import (
    RAITextInput, RAITextarea, RAIRadioSelect, RAICheckboxInput,
    RAISwitchInput, RAISelect, RAIFileInput, RAIPasswordInput
)

from userdata.models import StaffUser

class RAIEMailForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        # usually, we should have only admins and Staff members in the admin
        # interface. Thus, it might be safe to check if the username complies with
        # the RUB-ID rules and if the email ends with @rub.de or @ruhr-uni-bochum.de
        #
        # It might, however, be easier to check if a StaffUser is connected to the user 
        
        try:
            StaffUser.objects.get(user = self.user)
            staff_user = True
        except StaffUser.DoesNotExist:
            staff_user = False
            
            
        super().__init__(*args, **kwargs)
        choices =  [
            ('auto', settings.RUBION_MAIL_FROM)
        ]
        if staff_user:
            choices.append((
                'user', '{} {} <{}>'.format(
                    self.user.first_name,
                    self.user.last_name,
                    self.user.email,
                ),
            ))
            self.fields['pwd'].label = mark_safe(self.fields['pwd'].label + ' <code>' + self.user.username + '</code>')
        else:
            del(self.fields['pwd'])
            
        self.fields['from_'].choices = choices
        
    from_ = forms.ChoiceField(
        label = 'Absender',
        widget = RAISelect
    )

    pwd = forms.CharField(
        label = "Passwort für die RUB-ID",
        widget = RAIPasswordInput,
        required = False
        
    )

    copy = forms.BooleanField(
        label = "Kopie an meine E-Mail-Adresse",
        widget = RAISwitchInput,
        required = False,
        initial = True
    )
    to = forms.CharField(
        label = 'Empfänger',
        widget = EMailToSelect
    )

    subject = forms.CharField(
        label = 'Betreff',
        widget = RAITextInput
    )
    body = forms.CharField(
        label = 'Text der E-Mail',
        widget = RAITextarea
    )
    attachements = forms.FileField(
        label = 'Dateianhänge',
        widget = RAIFileInput(attrs = {'multiple':True}),
        required = False
    )
    
    def clean(self):
        cleaned_data = super().clean()
        from_ = cleaned_data.get('from_', None)
        pwd = cleaned_data.get('pwd', None)

        if from_ == 'user' and not pwd:
            self.add_error('pwd', 'Aufgrund der Auswahl des Absenders muss das Passwort angegeben werden.')
        return cleaned_data

    def clean_subject(self):
        subject = self.cleaned_data['subject']
        if "\n" in subject:
            raise forms.ValidationError("Der Betreff der E-Mail darf keine neue Zeile enthalten.")
        return subject
