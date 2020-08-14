from pprint import pprint 


from .generic import SingleObjectMixin
from .create import CreateView


from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.template.loader import render_to_string

from django.utils.translation import ugettext_lazy as _


class EditView(CreateView, SingleObjectMixin):
    template_name = 'rai/views/default/edit.html'
    formclass = None
        
    def get_actions(self):
        return self.get_group_actions() + self.get_item_actions()
    
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

    def form_for_post_hook(self, request):
        '''
        Sets up the form and formsets for post.
        returns the form and sets self.formset
        '''
        form = self.formclass(request.POST, request.FILES,
                              instance = self.obj, user = request.user)
        self.formsets = {}
        for key, formset_class in self.formset_classes.items():
            self.formsets.update({
                key : formset_class(
                    request.POST, request.FILES,
                    prefix=key, form_kwargs={'user': request.user}
                )
            })
        return form

    def save_post_hook(self, request, form, add_messages = True):
        saved_something = False
        if form.has_changed():
            form.save()
            saved_something = True
                
        for formset in self.formsets.values():
            for subform in formset.forms:
                if subform.has_changed():
                    subform.save()
                    saved_something = True
        if add_messages:
            if saved_something:
                messages.success(request, _('The data was updated.'))
            else:
                messages.info(request, _('The data contained not changes and therefore was not updated.'))
        return saved_something
    
    def post(self, request, *args, **kwargs):
        '''
        This default post method calls two hooks:
        
        form_for_post_hook:
          setup the forms required for this post
        save_post_hook:
           called when everythin is valid
        '''
        self.edit_handler = self.edit_handler.bind_to(instance = self.obj)
        form = self.form_for_post_hook(request)
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
            edit_handler = self.edit_handler.bind_to(
                form = form,
                formsets = self.formsets,
                request = self.request,
                instance = self.obj
                
            )
            context = super().get_context_data()
            context.update({
                'edit_handler': edit_handler,
                'form': form,
                'object' : self.obj
            })
            messages.warning(request, _('The data could not be saved due to errors.'))
            return self.render_to_response(context)
        else:
            self.save_post_hook(request, form)
                
        return redirect(self.raiadmin.default_action(self.raiadmin).get_url_name())
