from .generic import RAIBaseFormEditHandler, RAIBaseCompositeEditHandler, RAIFieldPanel

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
        self.nav_label = kwargs.pop('nav_label', None)
        super().__init__(*args, **kwargs)
    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs.update({
            'unique_id' : self.unique_id,
            'nav_label' : self.nav_label
        })
        return kwargs

class RAITranslatedContentPanel(RAIPillsPanel):
    """
    A Panel which automatically builds a RAIPillsPanel for translated content.

    It simply uses RAIFieldPanels for the fields. For more complex layout, built a 
    RAIPillsPanel manually.
    """

    # It would be easier if I'd know a way to read the field_en and field_de properties
    # of website.models.TranslatedField. However, I don't know how to access them.
    #
    # Thus, I use a (reasonable) guess:
    #
    # If field is title, field_en = title and field_de = title_de
    # ion any other case, field_en = <foo>_en and field_de = <foo>_de

    def __init__(self, languages, fieldnames, *args, **kwargs):
        """
        languages should be a dict like {'de':'german', 'en':'english'}, that is, 
        suffix -> name

        fieldnames is a list of fieldnames without suffix.
        """
        nav_label = kwargs.pop('nav_label', 'Select language')
        kwargs.update({'nav_label':nav_label})

        
        children = []
        for suffix, lang in languages.items():
            grandchildren = []
            for field in fieldnames:
                if not(suffix == 'en' and field == 'title'):
                    field_name = "{field}_{suffix}".format(field = field, suffix = suffix)
                else:
                    field_name = field                    
                grandchildren.append(RAIFieldPanel(field_name))
            children.append(RAICollectionPanel(grandchildren, heading = lang))
        super().__init__(children, *args, **kwargs)        

    def clone(self):
        return RAIPillsPanel(**self.clone_kwargs())
