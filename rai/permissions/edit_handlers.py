from .internals import PERMISSIONS, get_permissions
from .models import RAIPermission
from django import forms
from rai.forms import RAIAdminModelForm


from rai.edit_handlers import RAIMultiFieldPanel, RAIFieldPanel, RAIQueryInlinePanel
from rai.utils import add_css_class, remove_css_class
from rai.permissions.widgets import RAISelectRAIPermissions
from rai.widgets import RAISelectRAIItems


class PermissionForm(RAIAdminModelForm):
    rai_id = forms.CharField(widget = RAISelectRAIItems)
    value = forms.ChoiceField(widget = RAISelectRAIPermissions)
    group_id = forms.IntegerField(widget = forms.widgets.HiddenInput)
    model = RAIPermission
    
    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)
        
        
    def clean_group_id(self):
        if not self.cleaned_data['group_id']:
            return self.group.pk
        return self.cleaned_data['group_id']
        
class PermissionSelectionInlinePanel(RAIQueryInlinePanel):
    formset_formclass = PermissionForm
    def __init__ (self, name, rai_items, rai_permissions, **kwargs):
        self.name = name,
        self.rai_items = rai_items
        self.rai_permissions = rai_permissions
        children = [ PermissionSelectionPanel(rai_items, rai_permissions) ]
        super().__init__(name, RAIPermission, self.get_permissions, children, **kwargs)

    def clone(self):
        return self.__class__(
            self.name, self.rai_items, self.rai_permissions,
            **(self.clone_kwargs())
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

    
