from django import forms
from rai.widgets import RAITypeAndSelect

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
        
