from rai.actions import ListAction, CreateAction, DetailAction, EditAction
from rai.default_views import (
    ListView, DetailView, EditView, DeleteView, InactivateView, HistoryView, CreateView
)

from wagtail.core import hooks


class RAIRegisterable:
    """
    Base class similar to modeladmin.WagtailRegisterable
    """

    def register_with_wagtail(self):
        @hooks.register('register_rai_url')
        def register_rai_urls():
            urls = self.get_urls_for_registration()
            return urls
    def register_with_rai(self):
        @hooks.register('register_rai_item')
        def get_rai_item():
            return (self.identifier, {'id' : self.sub_identifier, 'label': self.menu_label})

    def show(self, request = None):
        return True
        
class RAIAdmin (RAIRegisterable):
    group_actions = [ ListAction, CreateAction ]
    default_action = ListAction
    item_actions = [ DetailAction, EditAction ]
    menu_label = None
    menu_icon = None
    menu_icon_font = None
    identifier = None
    sub_identifier = None
    
    
    group_menu_template = 'rai/menus/groupmenu.html'
    
    def get_url_for_registration(self):
        urls = []
        for Action in self.group_actions:
            action = Action(self)
            urls = urls + action.get_url_for_registration()
        for Action in self.item_actions:
            action = Action(self)
            urls = urls + action.get_url_for_registration()

        return urls
    def get_default_url(self):
        action = self.default_action(self)
        return action.get_href()
    
class RAIModelAdmin (RAIAdmin):
    model = None
    treat_as_page = False
    listview = ListView
    createview = CreateView
    detailview = DetailView
    editview = EditView
    inactivateview = InactivateView
    deleteview = DeleteView

    def __init__(self):
        super().__init__()
        opts = self.model._meta
        self.identifier = self.identifier or opts.app_label
        self.sub_identifier = self.sub_identifier or opts.model_name

class RAIAdminGroup(RAIRegisterable):
    components = []
    menu_label = None
    menu_icon = None
    menu_icon_font = None

    def register_with_wagtail(self):
        super().register_with_wagtail()
        @hooks.register('rai_menu_group')
        def register_rai():
            return self

    def register_with_rai(self):
        for component in self.components:
            component().register_with_rai()

    def get_urls_for_registration(self):
        urls = []
        for Component in self.components:
            comp = Component()
            urls = urls + comp.get_url_for_registration()
        return urls

    
def rai_register(rai_class):
    """
    Method for registering an Item with RAI.
    """
    instance = rai_class()
    instance.register_with_wagtail()
    instance.register_with_rai()
    return rai_class



