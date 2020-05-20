from .models import RAICollection
from .internals import REGISTERED_COLLECTIONS

from pprint import pprint

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from rai.edit_handlers import RAIInlinePanel, RAIFieldPanel, RAICollectionPanel, RAIMultiFieldPanel
from rai.widgets import RAIFileInput


class FileListPanel(RAIInlinePanel):
    template = 'rai/files/edit_handlers/file-list-panel.html'
    children = []
    
    def __init__(self, *args, **kwargs):
        self.panels = [
            FileFieldPanel('doc'),
        ]
        self.collection = kwargs.pop('collection', None)
        kwargs.update({'panels' : self.panels})
        
        super().__init__(*args, **kwargs)

    def required_formsets(self):
        return {}
        
    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs['collection'] = self.collection
        return kwargs

    def on_form_bound(self):
        if not hasattr(self, 'children'):
            self.children= []
            
    def render(self):
        return render_to_string(self.template, {
            'self' : self
        })
                                
    
    def on_request_bound(self):
        super().on_request_bound()
        add_file_panel = AddFileFieldPanel('doc')
        add_file_panel = add_file_panel.bind_to(model = self.model, request = self.request)
        if not self.children:
            self.children.append(add_file_panel)
        
    def on_instance_bound(self):
        children = []
        self.db_field = self.instance._meta.get_field(self.relation_name)
        objects = self.db_field.related_model.objects.filter(decorated_model = self.instance)
        child_edit_handler = self.get_child_edit_handler()
        form_class = child_edit_handler.get_form_class()
        form = form_class()
        
        for obj in objects:
            children.append(
                child_edit_handler.bind_to(model = self.db_field.related_model, form = form, instance=obj)
            )

        new_children = []
        for child in children + self.children:
            if isinstance(child, AddFileFieldPanel):
                new_children.append(
                    child.bind_to(
                        model = self.model,
                        request=self.request,
                        instance=self.instance)
                )
            else:
                new_children.append(child)
        self.children = new_children

    
        
class FileFieldPanel(RAIFieldPanel):
    # object_template = 'rai/files/edit_handlers/file-field-panel_as-object.html'
    field_template = 'rai/files/edit_handlers/file-field-panel_as-field.html'
    
    def render_as_field(self):
        return mark_safe(render_to_string(self.field_template, {
            'instance' : self.instance,
            'classes' : self.classes()
        }))

    
class AddFileFieldPanel(RAIFieldPanel):
    field_template = 'rai/files/edit_handlers/add-file-field-panel.html'

    def classes(self):
        if self.classname:
            return [self.classname]
        return []

    def render_form_content(self):
        return self.render_as_field()
    
    def render_as_field(self):
        return mark_safe(render_to_string(self.field_template, {
            'instance' : self.instance,
            'classes' : self.classes(),
            'model' : self.model,
            'self' : self
        }))
