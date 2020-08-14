from pprint import pprint

from .create import CreateView
import datetime

from django.shortcuts import redirect
from django.template.response import TemplateResponse

from rai.utils import get_model_verbose_name

class MultiFormCreateView(CreateView):
    form = None
    template = 'rai/views/default/multi-form/multi-form-view.html'
    session_expire_time = 45 * 60 # in seconds
    session_key_prefix = 'multiform_create'

    @property
    def session_key(self):
        return '{}_{}'.format(self.session_key_prefix, self.request.user.pk)

    def prepare_next_form(self, prefix):
        # hook for derived views to insert data into the next form
        # self.form is empty, self.formclass holds the formclass
        #
        # prefix is the prefix of the current form
        pass
    
    def dispatch(self, request, *args, **kwargs):
        self.request = request
        # prepare_edit_handler binds to model
        self.prepare_edit_handler()
        # bind to request now
        self.edit_handler = self.edit_handler.bind_to(request = self.request)
        # edit_handler should delivier the correct form
        self.formclass = self.edit_handler.get_form_class()
        session_key = self.session_key
        self.session_store = request.session.get(session_key, {})
            
        if request.method == 'POST':
            return self.post(request, *args, **kwargs)
        if request.method == 'GET':
            return self.get(request, *args, **kwargs)

    def get_context_data(self, *kwargs):
        context = {
            'media' : self.media,
            'inline_media' : self.inline_media,
            'main_admin_menu' : self.get_main_admin_menu(),
            'help_editor' : self.get_help_editor(),
            'user_pk' : self.request.user.pk,
            'icon' : self.raiadmin.menu_icon,
            'icon_font': self.raiadmin.menu_icon_font,
            'edit_handler' : self.edit_handler,
            'model_name' : get_model_verbose_name(self.raiadmin.model),
            'page_menu' : self.get_page_menu()
        }
        return context

    def prepare_cleaned_data(self, data, prefix):
        # Use this to change the form.cleaned_data if it cannot be serialized
        return data

    def prepare_formsets(self, formsets, prefix):
        # use this to prepare the formsets for serialization
        return formsets
    
    def post(self, request, *args, **kwargs):
        session_key = 'multiform_create_{}'.format(request.user.pk)
        form = self.formclass(request.POST)
        if not form.is_valid():
            self.form = form
        else:
            now = int(datetime.datetime.now().timestamp())
            if self.session_store:
                expires = self.session_store.get('expires', None)
                if expires and expires < now:
                    self.warning_message('Die Zeit, um die Daten anzugeben, ist abgelaufen.')
                    request.session[session_key] = {}
                    return redirect(self.active_action.get_url_name())
            else:
                self.session_store = {}
                    
            expires = now + self.session_expire_time
                
            formsets = {}
            if hasattr(form, 'formsets'):
                for key, formset in form.formsets.items():
                    formsets[key] = [subform.cleaned_data for subform in formset.forms]

            current_prefix = self.edit_handler.get_current_prefix()
            self.session_store.update({
                'expires': expires,
                current_prefix : {
                    'form' : self.prepare_cleaned_data(form.cleaned_data, current_prefix),
                    'formsets' : self.prepare_formsets(formsets, current_prefix)
                }
                
            })
            request.session[session_key] = self.session_store
            if self.edit_handler.is_last_form():
                return self.finalize(request)
            else:
                self.edit_handler = self.edit_handler.proceed()
                self.edit_handler = self.edit_handler.bind_to(model = self.raiadmin.model)
                self.formclass = self.edit_handler.get_form_class()            
                self.prepare_next_form(self.edit_handler.get_current_prefix())
        return self.get(request)
        
    def get(self, request, *args, **kwargs):
        # self.form is either populated with the current form with error or empty
        if not self.form:
            prefix = self.edit_handler.get_current_prefix()
            initial = self.session_store.get(prefix, {})
            if initial:
                form = self.formclass(initial = initial)
            else:
                form = self.formclass()
        else:
            form = self.form
        self.edit_handler = self.edit_handler.bind_to(form = form)
        if not self.edit_handler.is_last_form():
            self.save_button = False
            self.proceed_button = True
            self.proceed_button_label = 'Zum nächsten Schritt' 
        context = self.get_context_data()
        
        return TemplateResponse(request, self.template, context)
        
    def finalize(self, request):
        # in finalize, all save logic should be implemented
        # the last form is still available as self.form
        pass
