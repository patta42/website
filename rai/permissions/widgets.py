
from rai.widgets import RAISelect

class RAISelectRAIPermissions(RAISelect):
    required_css_classes = ['select-rai-permissions'] + RAISelect.required_css_classes
    def optgroups(self, name, value, attrs = None):
        from rai.permissions.internals import get_permissions_as_choices
        self.choices = get_permissions_as_choices()
        return super().optgroups(name, value, attrs = None)

