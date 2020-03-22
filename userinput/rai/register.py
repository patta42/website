import userinput.rai.actions as actions
#from .filters import RUBIONUserStatusFilter, RUBIONUserInstrumentFilter

import datetime

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _l

from rai.actions import ListAction, CreateAction, EditAction, DetailAction, InactivateAction

from rai.base import RAIModelAdmin, RAIAdminGroup

from userinput.models import RUBIONUser, WorkGroup, Project

    
class RAIUserData(RAIModelAdmin):
    model = RUBIONUser
    menu_label = _l('Users')
    menu_icon_font = 'fas'
    menu_icon = 'user'
    group_actions = [actions.RAIUserDataListAction, CreateAction]
    default_action = actions.RAIUserDataListAction
    item_actions = [EditAction, DetailAction, InactivateAction]

class RAIWorkGroups(RAIModelAdmin):
    model = WorkGroup
    menu_label = _l('Workgroups')
    menu_icon_font = 'fas'
    menu_icon = 'users'
    group_actions = [actions.RAIWorkgroupListAction, CreateAction]

class RAIProjects(RAIModelAdmin):
    model = Project
    menu_label = _l('Projects')
    menu_icon_font = 'fas'
    menu_icon = 'project-diagram'
    group_actions = [actions.RAIProjectListAction, CreateAction]
    default_action = actions.RAIProjectListAction
    
class RAIUserInputGroup(RAIAdminGroup):
    components = [
        RAIUserData, RAIWorkGroups, RAIProjects
    ]
    menu_label = _l("User data")
