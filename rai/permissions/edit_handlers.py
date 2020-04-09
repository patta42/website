from .internals import PERMISSIONS, get_permissions
from .models import RAIPermission
from django import forms


from rai.edit_handlers import RAIMultiFieldPanel, RAIFieldPanel, RAIQueryInlinePanel
from rai.utils import add_css_class, remove_css_class
from rai.permissions.widgets import RAISelectRAIPermissions
from rai.widgets import RAISelectRAIItems



class PermissionForm(forms.Form):
    identifier = forms.ChoiceField()
    sub_identifier = forms.ChoiceField()
    permission = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        items = []
        subitems = []
        permissions = []
        for item, subitem in REGISTERED_ITEMS.keys():
            items.append((item, item))
            for subitem in subitems:
                subitems.append('{}.{}'.format(item, subitem['id']), subitem['label'])
                for permission in get_permissions(item, sub):
                    permissions.append(
                        ('{}.{}.{}'.format(item,sub,permission.key), permission.description)
                    )
        self.fields['identifier'].choices = items
        self.fields['sub_identifier'].choices = subitems
        self.fields['permission'].choices = permissions

        
class PermissionSelectionInlinePanel(RAIQueryInlinePanel):
    def __init__ (self, name, rai_items, rai_permissions, **kwargs):
        self.name = name,
        self.rai_items = rai_items
        self.rai_permissions = rai_permissions
        children = [ PermissionSelectionPanel(rai_items, rai_permissions) ]
        super().__init__(name, RAIPermission, self.get_permissions, children, **kwargs)

    def clone(self):
        return self.__class__(
            self.name, self.rai_items, self.rai_permissions, **(self.clone_kwargs())
        )
    
    def get_permissions(self, instance):
        return RAIPermission.objects.filter(group = instance)
    
    def classes(self):
        classes = super().classes()
        classes.append("inline-panel-select-permissions")
        classes.remove('inline-panel')
        return classes
    
class PermissionSelectionPanel(RAIMultiFieldPanel):
    def __init__(self, rai_items, rai_permissions, classname = '', **kwargs):
        classname = add_css_class(classname, ['rai-permission-select', 'row'])
        children = [
            RAIFieldPanel(rai_items, widget = RAISelectRAIItems,
                          classname="col-md-6 rai-items-select"),
            RAIFieldPanel(rai_permissions, widget = RAISelectRAIPermissions,
                          classname="col-md-6 rai-permissions-select")
        ]
        super().__init__(children, classname=classname, **kwargs)
    def clone(self):
        return RAIMultiFieldPanel(**self.clone_kwargs())
