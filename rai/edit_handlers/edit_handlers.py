from .generic import RAIBaseFormEditHandler
from wagtail.admin.edit_handlers import FieldPanel


class RAITabbedInterface(RAIBaseFormEditHandler):
    template = "wagtailadmin/edit_handlers/tabbed_interface.html"

    def __init__(self, *args, **kwargs):
        
        self.base_form_class = kwargs.pop('base_form_class', None)
        super().__init__(*args, **kwargs)


    
    def clone(self):
        new = super().clone()
        new.base_form_class = self.base_form_class
        return new
    
class RAIObjectList(RAITabbedInterface):
    template = 'rai/edit_handlers/object-list.html'

class RAIFieldRowPanel(RAIBaseFormEditHandler):
    template = "rai/edit_handlers/field-row-panel.html"

    # def on_instance_bound(self):
    #     super().on_instance_bound()

    #     col_count = ' col%s' % (12 // len(self.children))
    #     # If child panel doesn't have a col# class then append default based on
    #     # number of columns
    #     for child in self.children:
    #         if not re.search(r'\bcol\d+\b', child.classname):
    #             child.classname += col_count
    
