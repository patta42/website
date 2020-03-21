from django.urls import reverse, path
from django.utils.translation import ugettext_lazy as _l

# from rai.views import ListSettingsView

class RAIAction:
    label = None
    icon = None
    icon_font = None
    action_identfier = None
    identifier = None
    
    def __init__(self, raiadmin):
        self.raiadmin = raiadmin
    
    def get_url(self):
        return "{identifier}/{action_identifier}/".format(
            identifier = self.identifier,
            action_identifier = self.action_identifier
        )

    def get_url_name(self):
        opts = self.raiadmin.model._meta
        return "rai_{app}_{model}_{identifier}".format(
            app = opts.app_label, 
            model = opts.model_name,
            identifier = self.action_identifier
        )
    
    def get_url_for_registration(self):
        urls = [
            path(self.get_url(), self.get_view(), name = self.get_url_name()), 
        ]
        return urls

    def get_href(self, *args):
        return reverse(self.get_url_name(), *args)
    
        

class ModelAction(RAIAction):
    def __init__(self, raiadmin):
        super().__init__(raiadmin)
        opts = self.raiadmin.model._meta
        self.identifier = '{app}/{model}'.format(
            app = opts.app_label,
            model = opts.model_name
        )

class SpecificAction(ModelAction):
    def get_url(self):
        return "{identifier}/<int:pk>/{action_identifier}/".format(identifier = self.identifier, action_identifier = self.action_identifier)

    
class ListAction(ModelAction):
    label = _l('List')
    icon = 'list'
    action_identifier = 'list'

    list_item_template = None
    configurable_display_fields = []
    list_orders = []
    list_filters = []

    def __init__(self, raiadmin):
        super().__init__(raiadmin)
        self.settings_action = ListSettingsAction(self.raiadmin, self.configurable_display_fields)
        
    
    def get_view(self):
        return self.raiadmin.listview.as_view(
            raiadmin = self.raiadmin,
            active_action = self
        )
    
    def get_url_for_registration(self):
        urls = super().get_url_for_registration()
        return urls + self.settings_action.get_url_for_registration()
    
class CreateAction(RAIAction):
    label = _l('Add')
    icon = 'plus'
    icon_font = 'fas'
    action_identifier = 'create'

    def get_view(self):
        return self.raiadmin.createview.as_view()

class DetailAction(SpecificAction):
    label = 'Details'
    icon = 'eye'
    icon_font = 'fas'
    action_identifier = 'detail'

    def get_view(self):
        return self.raiadmin.detailview.as_view()


class EditAction(SpecificAction):
    label = _l('Edit')
    icon = 'edit'
    icon_font = 'fas'
    action_identifier = 'edit'

    def get_view(self):
        return self.raiadmin.editview.as_view()
    
    
class InactivateAction(SpecificAction):
    label = _l('Inactivate')
    icon = 'power-off'
    icon_font = 'fas'
    action_identifier = 'inactivate'

    def get_view(self):
        return self.raiadmin.inactivateview.as_view()

class ListSettingsAction(ModelAction):
    label = _l('adjust view')
    icon = 'cogs'
    icon_font = 'fas'
    action_identifier = 'edit_list_settings'

    def __init__(self, raiadmin, configurable_display_fields):
        super().__init__(raiadmin)
        
    def get_view(self):
        pass #return ListSettingsView.as_view()

    def get_url_for_registration(self):
        #urls = super().get_url_for_registration()
        return []#urls + self.settings_action.get_url_for_registration()