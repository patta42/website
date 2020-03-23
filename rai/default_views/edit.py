
from .generic import RAIAdminView, SingleObjectMixin
from rai.edit_handlers import convert_from_wagtail
from rai.forms import RAIAdminModelForm, rai_modelform_factory

from django.forms.models import modelform_factory

class EditView(RAIAdminView, SingleObjectMixin):
    template_name = 'rai/views/default/edit.html'
    formclass = None

    media = {
        'css' : [ 'css/admin/edit_handlers.css']
    }

    def dispatch(self, request, **kwargs):
        self.obj = self.get_object()
        if hasattr(self.active_action, 'edit_handler'):
            edit_handler = self.active_action.edit_handler
        elif hasattr(self.raiadmin.model, 'edit_handler'):
            edit_handler = convert_from_wagtail(self.raiadmin.model.edit_handler)
        else:
            # TODO provide edit handler for models without specification
            pass
        self.edit_handler = edit_handler.bind_to(model=self.raiadmin.model)
        self.formclass = self.edit_handler.get_form_class()
        self.request = request
        return super().dispatch(request, **kwargs)
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.formclass(instance = self.obj)
        edit_handler = self.edit_handler.bind_to(
            instance = self.obj, form = form, request = self.request
        )

        context['object'] = self.obj
        context['icon'] = self.raiadmin.menu_icon
        context['icon_font'] = self.raiadmin.menu_icon_font
        context['form'] = form
        context['edit_handler'] = edit_handler
        return context
