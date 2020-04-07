from pprint import pprint 

import datetime

from rai.actions import (
    ListAction, EditAction, DetailAction, CreateAction, InactivateAction, SpecificAction
)
import rai.edit_handlers as eh
from rai.widgets import RAIRadioInput, RAISelectMultiple, RAISelect

import userinput.rai.filters as filters
from userinput.rai.edit_handlers import (
    project_edit_handler, workgroup_edit_handler, rubionuser_edit_handler
)


# an  action for moving from one group to another
# used by projects and rubionuser
class MoveToWorkgroupAction(SpecificAction):
    label = 'Anderer Gruppe zuordnen'
    icon = 'arrow-alt-circle-right'
    icon_font = 'fas'
    action_identifier = 'move'

    def get_view(self):
        return self.raiadmin.moveview.as_view(
            raiadmin = self.raiadmin,
            active_action = self
        )


def _is_rubion_user_active(instance):
    return (
        instance.linked_user is None or
        instance.expire_at is None or
        instance.expire_at >= datetime.datetime.now()
    )
class RUBIONUserOnlyWhenActiveMixin:
    def show_for_instance(self, instance, request=None):
        return _is_rubion_user_active(instance)

class RUBIONUserMoveAction(RUBIONUserOnlyWhenActiveMixin, MoveToWorkgroupAction):
    def show_for_instance(self, instance, request=None):
        return super().show_for_instance(instance, request) and not instance.is_leader

class RUBIONUserInactivateAction(RUBIONUserOnlyWhenActiveMixin, InactivateAction):
    pass
        
class RAIUserDataListAction(ListAction):
    list_item_template = 'userinput/rubionuser/rai/list/item-in-list.html'
    list_filters = [
        filters.RUBIONUserStatusFilter,
        filters.RUBIONUserInstrumentFilter
    ]
class RUBIONUserDataEditAction(RUBIONUserOnlyWhenActiveMixin, EditAction):
    edit_handler = rubionuser_edit_handler




class RAIProjectListAction(ListAction):
    list_item_template = 'userinput/project/rai/list/item-in-list.html'
    list_filters = [
        filters.ProjectStatusFilter
    ]
class RAIProjectEditAction(EditAction):
    edit_handler = project_edit_handler
    
    
class RAIWorkgroupListAction(ListAction):
    list_item_template = 'userinput/workgroup/rai/list/item-in-list.html'
    list_filters = [
        filters.WorkgroupStatusFilter
    ]

    

class RAIWorkgroupEditAction(EditAction):
    edit_handler = workgroup_edit_handler

class RAIWorkgroupDetailAction(DetailAction):
    edit_handler = workgroup_edit_handler

class RAIWorkgroupCreateAction(CreateAction):
    edit_handler = workgroup_edit_handler
    text_type = 'secondary'
