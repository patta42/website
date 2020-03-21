from .filters import RUBIONUserStatusFilter, RUBIONUserInstrumentFilter

import datetime

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _l

from rai.actions import ListAction, CreateAction, EditAction, DetailAction, InactivateAction


from rai.base import RAIModelAdmin, RAIAdminGroup



from userinput.models import RUBIONUser, WorkGroup, Project


class RAIUserDataListAction(ListAction):
    list_item_template = 'userinput/rubionuser/rai/list/item-in-list.html'
    list_filters = [ RUBIONUserStatusFilter, RUBIONUserInstrumentFilter ]

    
class RAIUserData(RAIModelAdmin):
    model = RUBIONUser
    menu_label = _l('Users')
    menu_icon_font = 'fas'
    menu_icon = 'user'
    group_actions = [RAIUserDataListAction, CreateAction]
    default_action = RAIUserDataListAction
    item_actions = [EditAction, DetailAction, InactivateAction]

class RAIWorkGroups(RAIModelAdmin):
    model = WorkGroup
    menu_label = _l('Workgroups')
    menu_icon_font = 'fas'
    menu_icon = 'users'

class RAIProjects(RAIModelAdmin):
    model = Project
    menu_label = _l('Projects')
    menu_icon_font = 'fas'
    menu_icon = 'project-diagram'
    
class RAIUserInputGroup(RAIAdminGroup):
    components = [
        RAIUserData, RAIWorkGroups, RAIProjects
    ]
    menu_label = _l("User data")
