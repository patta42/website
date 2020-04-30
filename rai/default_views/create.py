from pprint import pprint as print

from .generic import RAIAdminView, PageMenuMixin

from django.template.loader import render_to_string
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

from rai.edit_handlers.utils import convert_from_wagtail, make_edit_handler_for_model
from rai.utils import get_model_verbose_name

class CreateView(RAIAdminView, PageMenuMixin):
    template_name = 'rai/views/default/create.html'
    save_button = True
    formclass = None

    def get_actions(self):
        return self.get_group_actions()
    
    def get_settings_menu(self):
        settings_action = self.active_action.settings_action
        return {
            'icon' : settings_action.icon,
            'icon_font' : settings_action.icon_font,
            'label' : settings_action.label,
            
        }

    def prepare_edit_handler(self):
        if hasattr(self.active_action, 'edit_handler'):
            edit_handler = self.active_action.edit_handler
        elif hasattr(self.raiadmin.model, 'edit_handler'):
            edit_handler = convert_from_wagtail(self.raiadmin.model.edit_handler)
        else:
            edit_handler = make_edit_handler_for_model(self.raiadmin.model)

        self.edit_handler = edit_handler.bind_to(model=self.raiadmin.model)

    def dispatch(self, request, *args, **kwargs):
        self.prepare_edit_handler()
        if not self.formclass:
            self.formclass = self.edit_handler.get_form_class()
            self.formset_classes = self.edit_handler.get_additional_formset_classes()
        self.formsets = {}
        for key,formset_class in self.formset_classes.items():
            self.formsets.update({key : formset_class(prefix = key)})
        
        self.request = request
        return super().dispatch(request, *args, **kwargs)

    def redirect_to_default(self):
        return redirect(self.raiadmin.default_action(self.raiadmin).get_url_name())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.formclass()
        #formsets = {#
        #     key : { formset_class( prefix = key ) }
        #     for key, formset_class in self.formset_classes.items()
        # }
        edit_handler = self.edit_handler.bind_to(
            form = form, request = self.request
        )
        
        context.update({
            'icon': self.raiadmin.menu_icon,
            'icon_font': self.raiadmin.menu_icon_font,
            'form': form,
            'edit_handler': edit_handler,
            'model_name' : get_model_verbose_name(self.raiadmin.model),
            'page_menu' : self.get_page_menu()
        })
            
        return context

            
    def post(self, request):
        form = self.formclass(request.POST, request.FILES, user = request.user)
        self.formsets = {}
        for key, formset_class in self.formset_classes.items():
            self.formsets.update({
                key : formset_class(
                    request.POST, request.FILES,
                    prefix=key, form_kwargs={'user': request.user}
                )
            })
        all_valid = True
        if not form.is_valid():
            all_valid = False
        for formset in self.formsets.values():
            try:
                if not formset.is_valid():
                    all_valid = False
            except ValidationError:
                raise
        if not all_valid:
            edit_handler = self.edit_handler.bind_to(form = form, formsets = self.formsets)
            context = super().get_context_data()
            context.update({
                'edit_handler': edit_handler,
                'form': form
            })
            messages.warning(request, _('The data could not be saved due to errors.'))
            return self.render_to_response(context)
        else:
            form.save()
            for formset in self.formsets.values():
                subform.save()
            messages.success(request, _('The data was saved.'))
        return self.redirect_to_default()
