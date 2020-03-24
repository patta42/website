
from .generic import SingleObjectMixin
from .create import CreateView


class EditView(CreateView, SingleObjectMixin):
    template_name = 'rai/views/default/edit.html'
    formclass = None

    def dispatch(self, request, **kwargs):
        self.obj = self.get_object()
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
