from pprint import pprint as print


from .generic import SingleObjectMixin
from .create import CreateView


from django.contrib import messages
from django.shortcuts import redirect
from django.template.loader import render_to_string

from django.utils.translation import ugettext_lazy as _


class EditView(CreateView, SingleObjectMixin):
    template_name = 'rai/views/default/edit.html'
    formclass = None

    def get_page_menu(self):
        actions = []
        for Action in self.raiadmin.group_actions:
            action = Action(self.raiadmin)
            if action.action_identifier != self.active_action.action_identifier:
                actions.append({
                    'icon' : action.icon,
                    'icon_font' : action.icon_font,
                    'label' : action.label,
                    'url' : action.get_href(),
                    'btn_type' : getattr(action,'btn_type', None),
                    'text_type': getattr(action,'text_type', None),
                    
                })
        for Action in self.raiadmin.item_actions:
            action = Action(self.raiadmin)
            if action.action_identifier != self.active_action.action_identifier:
                actions.append({
                    'icon' : action.icon,
                    'icon_font' : action.icon_font,
                    'label' : action.label,
                    'url' : action.get_href(self.obj.id),
                    'btn_type' : getattr(action,'btn_type', None),
                    'text_type': getattr(action,'text_type', None),
                    
                })
        return render_to_string(
            'rai/menus/group_menu.html',
            {
                'actions' : actions,
                'sort_button' : False,
                'filter_button' : False,
                'save_button': True,
                'icons_only' : True,
#                'settings_menu' : self.get_settings_menu()    
            }
        )

    
    def dispatch(self, request, *args, **kwargs):
        self.obj = self.get_object()
        return super().dispatch(request, *args, **kwargs)
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.formclass(instance = self.obj)
        
        edit_handler = self.edit_handler.bind_to(
            instance = self.obj,
            form = form,
            request = self.request
        )
        context['form'] = form
        context['edit_handler'] = edit_handler
        context['object'] = self.obj
        return context

    def post(self, request, *args, **kwargs):
        self.edit_handler = self.edit_handler.bind_to(instance = self.obj)        
        form = self.formclass(request.POST, request.FILES, instance = self.obj, user = request.user)
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
            saved_something = False
            if form.has_changed():
                form.save()
                saved_something = True
                
            for formset in self.formsets.values():
                for subform in formset.forms:
                    if subform.has_changed():
                        subform.save()
                        saved_something = True
            if saved_something:
                messages.success(request, _('The data was updated.'))
            else:
                messages.info(request, _('The data contained not changes and therefore was not updated.'))
                
        return redirect(self.raiadmin.default_action(self.raiadmin).get_url_name())
