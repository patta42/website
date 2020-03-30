from pprint import pprint

from .generic import RAIAdminView, SingleObjectMixin

from django import forms
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

from rai.forms import RAIAdminForm
from rai.widgets import RAICheckboxInput
from rai.utils import get_model_verbose_name

class ConfirmationForm(RAIAdminForm):
    confirm_delete = forms.BooleanField(
        label=_('Really delete'),
        required = True,
        widget = RAICheckboxInput(
            attrs = {
                'label' : _('really delete') 
            }
        )
    )

    def is_confirmed(self):
        return self.is_valid() 
    
class DeleteView(RAIAdminView, SingleObjectMixin):
    template_name = 'rai/views/default/delete.html'
    confirmation_form = ConfirmationForm
    
    def dispatch(self, request, *args, **kwargs):
        self.obj = self.get_object()
        self.form = self.confirmation_form()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['form'] = self.form
        print('Form')
        pprint(self.form.__dict__)
        print('Field')
        pprint(self.form['confirm_delete'].__dict__)
        context['object'] = self.obj
        context['model_name'] = get_model_verbose_name(self.raiadmin.model)
        context['cancel_url'] = self.raiadmin.default_action(self.raiadmin).get_href()
        return context
        
    def get(self, request, *args, **kwargs):
        return super().get(request)

    def post(self, request, *args, **kwargs):
        self.form = self.confirmation_form(request.POST, request.FILES)
        if self.form.is_confirmed():
            self.obj.delete()
            messages.success(request, _('The data was deleted.'))
            return redirect(self.raiadmin.default_action(self.raiadmin).get_url_name())
        else:
            return self.get(request, *args, **kwargs)
        
            
