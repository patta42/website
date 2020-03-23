from .generic import RAIBaseFormEditHandler, RAIBaseCompositeEditHandler

from django.core.exceptions import ImproperlyConfigured

import random
import string
import uuid

class RAITabbedInterface(RAIBaseFormEditHandler):
    template = "wagtailadmin/edit_handlers/tabbed_interface.html"

    def __init__(self, *args, **kwargs):
        
        self.base_form_class = kwargs.pop('base_form_class', None)
        super().__init__(*args, **kwargs)


    
    def clone(self):
        new = super().clone()
        new.base_form_class = self.base_form_class
        return new
    
class RAIObjectList(RAIBaseFormEditHandler):
    template = 'rai/edit_handlers/object-list.html'
    def __init__(self, *args, **kwargs):
        self.base_form_class = kwargs.pop('base_form_class', None)
        super().__init__(*args, **kwargs)
    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs.update({'base_form_class': self.base_form_class})
        return kwargs
    
    
class RAIFieldRowPanel(RAIBaseFormEditHandler):
    template = "rai/edit_handlers/field-row-panel.html"

class RAICollapsablePanel(RAIBaseFormEditHandler):
    is_collapsable = True
    template = 'rai/edit_handlers/collapsable-panel.html'
    
    def __init__(self, *args, **kwargs):
        self.is_collapsed = kwargs.pop('is_collapsed', True)
        self.collapse_id = kwargs.pop('collapse_id', uuid.uuid4())
        self.is_expanded = kwargs.pop('is_expanded', False)
        

        heading = kwargs.pop('heading', None)
        if heading is None:
            raise ImproperlyConfigured(
                "The attribute `heading` is required for {0}".format(
                    self.__class__.__name__
                )
            )            
        super().__init__( heading = heading, *args, **kwargs)

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs.update({
            'collapse_id' : self.collapse_id,
            'is_expanded' : self.is_expanded
        })
        return kwargs
        
class RAIUserDataPanel(RAICollapsablePanel):
    """
    A panel that shows information that is entered by external users.
    Issues a visual warning to avoid editing
    """
    template = 'rai/edit_handlers/userdata-panel.html'
class RAICollectionPanel(RAIBaseFormEditHandler):
    template = 'rai/edit_handlers/collection-panel.html'
    
class RAIPillsPanel(RAIBaseFormEditHandler):
    template = 'rai/edit_handlers/pills-panel.html'

    def __init__(self, *args, **kwargs):
        self.unique_id = kwargs.pop(
            'unique_id',
            ''.join(
                random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(10)
            )
        )
        super().__init__(*args, **kwargs)
    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs.update({
            'unique_id' : self.unique_id
        })
        return kwargs
