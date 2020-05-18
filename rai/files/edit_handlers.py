from pprint import pprint

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from rai.edit_handlers import RAIInlinePanel, RAIFieldPanel, RAICollectionPanel, RAIMultiFieldPanel
from rai.widgets import RAIFileInput

class FileListPanel(RAIInlinePanel):
    template = 'rai/files/edit_handlers/file-list-panel.html'
    def __init__(self, *args, **kwargs):
        self.panels = [
            FileFieldPanel('doc'),
        ]
        self.collection = kwargs.pop('collection', None)
        kwargs.update({'panels' : self.panels})
        
        super().__init__(*args, **kwargs)

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs['collection'] = self.collection
        return kwargs
    
    def on_request_bound(self):
        super().on_request_bound()
        add_file_panel = AddFileFieldPanel('doc')
        add_file_panel = add_file_panel.bind_to(model = self.model, request = self.request)
        self.children.append(add_file_panel)
        
    def on_instance_bound(self):
        children = []
        for child in self.children:
            if isinstance(child, AddFileFieldPanel):
                children.append(
                    child.bind_to(
                        model = self.model,
                        request=self.request,
                        instance=self.instance)
                )
            else:
                children.append(child)
        self.children = children
        
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

    def render_as_field(self):
        return mark_safe(render_to_string(self.field_template, {
            'instance' : self.instance,
            'classes' : self.classes(),
            'model' : self.model,
            'self' : self
        }))
