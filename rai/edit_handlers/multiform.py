from .forms import rai_form_factory
from .generic import RAIBaseCompositeEditHandler

from django.utils.safestring import mark_safe

class RAIMultiFormEditHandler(RAIBaseCompositeEditHandler):
    template = 'rai/edit_handlers/multi-form.html'
    current_child = 0

    def __init__(self, panels, *args, **kwargs):
        self.panels = panels
        self.current_child = kwargs.pop('current_child', 0)
        self.child = self.panels[self.current_child]
        super().__init__(*args, **kwargs)

    def bind_to(self, model = None, request = None, form = None, instance = None):
        # important! binding to request comes before binding to form
        new = self.clone()
        new.model = self.model if model is None else model
        new.instance = self.instance if instance is None else instance
        new.request = self.request if request is None else request
        new.form = self.form if form is None else form

        if new.model is not None:
            new.on_model_bound()

        if new.request is not None:
            new.on_request_bound()

        if new.form is not None:
            new.on_form_bound()

        if new.instance is not None:
            new.on_instance_bound()


        return new


    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs['panels'] = self.panels
        kwargs['current_child'] = self.current_child
        return kwargs

    def required_fields(self):
        return self.child.required_fields()
    
    def render_form_content(self):
        return mark_safe(self.render_as_object() + self.render_missing_fields())

    def on_model_bound(self):
        self.child = self.panels[self.current_child].bind_to(
            model = self.model
        )
        
    def on_request_bound(self):
        if self.request.method == 'POST':
            self.current_child = int(self.request.POST.get('multiform_step_counter', 0))
        if self.request.method == 'GET':
            self.current_child = int(self.request.GET.get('multiform_step_counter', 0))

        self.child = self.panels[self.current_child].bind_to(
            model = self.model, request = self.request
        )
        
    def on_form_bound(self):
        self.form.fields['multiform_step_counter'].initial = self.current_child 
        self.child = self.child.bind_to(form = self.form)
        
    def get_form_class(self):
        return self.child.get_form_class()


    
    def get_next_form_class(self):
        try:
            handler_class = self.panels[self.current_child+1]
        except IndexError:
            return None
        handler_class.bind_to(model = self.model)
        return handler_class.get_form_class()
    
    def get_current_prefix(self):
        return self.panels[self.current_child].prefix
    
    def is_last_form(self):
        return self.current_child+1 == len(self.panels)
    
    def proceed (self):
        self.current_child += 1
        new = self.clone()
        if self.request:
            new.child.bind_to(request = self.request)

        return new
        

class RAISubFormEditHandler(RAIBaseCompositeEditHandler):
    template = 'rai/edit_handlers/multi-form/sub-form-handler.html'
    def __init__(self, prefix, children, formclass = None, *args, **kwargs):
        self.prefix = prefix
        self.formclass = formclass
        super().__init__(children = children, *args, **kwargs)

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs['prefix'] = self.prefix
        kwargs['formclass'] = self.formclass
        return kwargs
    
    def get_form_class(self):
        return rai_form_factory(
            '{}MultiForm'.format(self.formclass.__name__),
            fields = {},
            base = self.formclass,
            widgets = self.widget_overrides()
        )

    
class RAIModelMultiFormEditHandler(RAISubFormEditHandler):
    def get_form_class(self):
        formclass = self.children[0].get_form_class()
        return rai_form_factory(
            '{}MultiForm'.format(formclass.__name__),
            fields = {},
            base = formclass,
            widgets = self.widget_overrides()
        )
        
