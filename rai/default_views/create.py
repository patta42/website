from .generic import RAIAdminView
from rai.edit_handlers.utils import convert_from_wagtail, make_edit_handler_for_model


class CreateView(RAIAdminView):
    template_name = 'rai/views/default/create.html'
    media = {
        'css' : [ 'css/admin/edit_handlers.css']
    }

    
    def dispatch(self, request, **kwargs):
        
        if hasattr(self.active_action, 'edit_handler'):
            edit_handler = self.active_action.edit_handler
        elif hasattr(self.raiadmin.model, 'edit_handler'):
            edit_handler = convert_from_wagtail(self.raiadmin.model.edit_handler)
        else:
            edit_handler = make_edit_handler_or_model(self.raiadmin.model)

        self.edit_handler = edit_handler.bind_to(model=self.raiadmin.model)
        self.formclass = self.edit_handler.get_form_class()
        self.request = request
        return super().dispatch(request, **kwargs)

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.formclass()
        edit_handler = self.edit_handler.bind_to(
            form = form, request = self.request
        )

        context['icon'] = self.raiadmin.menu_icon
        context['icon_font'] = self.raiadmin.menu_icon_font
        context['form'] = form
        context['edit_handler'] = edit_handler
        context['model_name'] = self.raiadmin.model.get_verbose_name()
        return context

