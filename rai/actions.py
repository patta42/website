from django.urls import reverse, path
from django.utils.translation import ugettext_lazy as _l

from rai.permissions.utils import (
    user_can_view, user_can_edit, user_can_create, user_can_delete)

class RAIAction:
    label = None
    icon = None
    icon_font = None
    action_identfier = None
    identifier = None
    
    def __init__(self, raiadmin):
        self.raiadmin = raiadmin
    
    def get_url(self):
        return "{identifier}/{sub_id}/{action_identifier}/".format(
            identifier = self.raiadmin.identifier,
            sub_id = self.raiadmin.sub_identifier,
            action_identifier = self.action_identifier
        )

    def get_url_name(self):
        return "rai_{app}_{model}_{identifier}".format(
            app = self.raiadmin.identifier, 
            model = self.raiadmin.sub_identifier, 
            identifier = self.action_identifier
        )
    
    def get_url_for_registration(self):
        urls = [
            path(self.get_url(), self.get_view(), name = self.get_url_name()), 
        ]
        return urls

    def get_href(self, *args, **kwargs):
        return reverse(self.get_url_name(), args = args )

    def get_rai_id(self):
        return '{}.{}'.format(
            self.raiadmin.identifier, self.raiadmin.sub_identifier)
        
    def show(self, request = None):
        return True
    def show_for_instance(self, instance, request = None):
        return True
        

class ModelAction(RAIAction):
    model = None
#    def __init__(self, raiadmin):
#        super().__init__(raiadmin)
#        self.identifier = '{app}/{model}'.format(
#            app = self.identifier,
#            model = self.sub_identifier
#        )

class SpecificAction(ModelAction):
    def get_url(self):
        return "{identifier}/{sub_id}/<int:pk>/{action_identifier}/".format(
            identifier = self.raiadmin.identifier,
            sub_id = self.raiadmin.sub_identifier,
            action_identifier = self.action_identifier)
    
class ListAction(ModelAction):
    label = _l('List')
    icon = 'list'
    icon_font = "fas"
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

    def show(self, request):
        return user_can_view(request, self.get_rai_id())
    
class CreateAction(ModelAction):
    label = _l('Add')
    icon = 'plus'
    icon_font = 'fas'
    action_identifier = 'create'

    def get_view(self):
        return self.raiadmin.createview.as_view(
            raiadmin = self.raiadmin,
            active_action = self
        )
    def show(self, request):
        return user_can_create(request, self.get_rai_id())


class DetailAction(SpecificAction):
    label = 'Details'
    icon = 'eye'
    icon_font = 'fas'
    action_identifier = 'detail'

    def get_view(self):
        return self.raiadmin.detailview.as_view(
            raiadmin = self.raiadmin,
            active_action = self
        )
    def show(self, request):
        return user_can_view(request, self.get_rai_id())
  

class EditAction(SpecificAction):
    label = _l('Edit')
    icon = 'edit'
    icon_font = 'fas'
    action_identifier = 'edit'

    def get_view(self):
        return self.raiadmin.editview.as_view(
            raiadmin = self.raiadmin,
            active_action = self
        )
    def show(self, request):
        return user_can_edit(request, self.get_rai_id())
  
        
    
    
class InactivateAction(SpecificAction):
    label = _l('Inactivate')
    icon = 'ban'
    icon_font = 'fas'
    action_identifier = 'inactivate'
    text_type = 'danger'

    def get_view(self):
        return self.raiadmin.inactivateview.as_view(
            raiadmin = self.raiadmin,
            active_action = self
        )

    def show(self, request = None):
        inactivate = getattr(self.raiadmin.model, 'inactivate', None)
        if inactivate and callable(inactivate):
            return True
        return False

class DeleteAction(SpecificAction):
    label = _l('Delete')
    icon = 'trash'
    icon_font = 'fas'
    action_identifier = 'delete'
    text_type = 'danger'

    def get_view(self):
        return self.raiadmin.deleteview.as_view(
            raiadmin = self.raiadmin,
            active_action = self
        )   
    def show(self, request):
        return user_can_delete(request, self.get_rai_id())
    
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
