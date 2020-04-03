from .generic import RAIAdminView, SingleObjectMixin, PageMenuMixin

from django.contrib import messages
from django.shortcuts import redirect
from django.template.loader import render_to_string


class InactivateView(RAIAdminView, SingleObjectMixin, PageMenuMixin):
    template_name = 'rai/views/default/inactivate.html'

    def dispatch(self, request, *args, **kwargs):
        self.obj = self.get_object()
        return super().dispatch(request, *args, **kwargs)
    
    def get_buttons(self):
        return {
            'cancel' : {
                'id' : 'cancelBtn',
                'label' : 'Abbrechen',
                'type' : 'a',
                'value' : self.raiadmin.default_action(self.raiadmin).get_url_name(),
                'btnClass' : 'btn-secondary'
            },
            'okay' : {
                'id' : 'okayBtn',
                'label' : 'Inaktivieren',
                'type' : 'submit',
                'value' : 'inactivate',
                'name' : 'action',
                'btnClass' : 'btn-danger'
            }
        }

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'object' : self.obj,
            'page_menu' : self.get_page_menu(),
            'buttons' : self.get_buttons()
        })
        return context


    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', None)
        if action and action == 'inactivate':
            self.obj.inactivate(user = request.user)
            messages.success(request, 'Inaktivierung erfolgreich')
        else:
            messages.warning(request, 'Es ist etwas schief gegangen. Inaktivierung hat nicht geklappt.')
        
        return redirect(self.raiadmin.default_action(self.raiadmin).get_url_name())
