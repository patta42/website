
#from .filters import RUBIONUserStatusFilter, RUBIONUserInstrumentFilter

import datetime

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _l

from rai.actions import ListAction, CreateAction, EditAction, DetailAction, HistoryAction
from rai.base import RAIModelAdmin, RAIAdminGroup
from rai.default_views import HistoryView

from userinput.models import RUBIONUser, WorkGroup, Project, Nuclide
import userinput.rai.actions as actions
from userinput.rai.views.generic import MoveToWorkgroupView

from userinput.rai.views.rubionuser.views import (
    RUBIONUserEditView, RUBIONUserInactivateView, RUBIONUserHistoryView
)

from userinput.rai.permissions import MovePermission, InactivatePermission

from wagtail.core import hooks


@hooks.register('register_rai_permissions')
def permissions_fur_rubionuser():
    return ('userinput', 'rubionuser', [MovePermission, InactivatePermission])

@hooks.register('register_rai_permissions')
def permissions_fur_projects(): 
    return ('userinput', 'project', [MovePermission, InactivatePermission])

@hooks.register('register_rai_permissions')
def permissions_fur_workgroups():
    return ('userinput', 'workgroup', [InactivatePermission])


class RAIUserData(RAIModelAdmin):
    model = RUBIONUser
    menu_label = 'Nutzer'
    menu_icon_font = 'fas'
    menu_icon = 'user'
    group_actions = [
        actions.RAIUserDataListAction,
        CreateAction
    ]
    default_action = actions.RAIUserDataListAction
    item_actions = [
        actions.RUBIONUserDataEditAction,
        DetailAction,
        actions.RUBIONUserInactivateAction,
        actions.RUBIONUserMoveAction,
        HistoryAction
    ]
    editview = RUBIONUserEditView
    inactivateview = RUBIONUserInactivateView
    moveview = MoveToWorkgroupView
    historyview = RUBIONUserHistoryView


class RAIWorkGroups(RAIModelAdmin):
    model = WorkGroup
    menu_label = _l('Workgroups')
    menu_icon_font = 'fas'
    menu_icon = 'users'
    group_actions = [
        actions.RAIWorkgroupListAction,
        actions.RAIWorkgroupCreateAction
    ]
    default_action = actions.RAIWorkgroupListAction
    item_actions = [
        actions.RAIWorkgroupEditAction,
        actions.RAIWorkgroupDetailAction,
        actions.UserinputInactivateAction,
        HistoryAction
    ]
    
    historyview = HistoryView

    
class RAIProjects(RAIModelAdmin):
    model = Project
    menu_label = _l('Projects')
    menu_icon_font = 'fas'
    menu_icon = 'project-diagram'
    group_actions = [actions.RAIProjectListAction, CreateAction]
    default_action = actions.RAIProjectListAction
    item_actions = [
        actions.RAIProjectEditAction,
        DetailAction,
        actions.UserinputInactivateAction,
        actions.MoveToWorkgroupAction,
        HistoryAction
    ]

    moveview =  MoveToWorkgroupView
    historyview = HistoryView
    
class RAIUserInputGroup(RAIAdminGroup):
    components = [
        RAIUserData, RAIWorkGroups, RAIProjects, 
    ]
    menu_label = _l("User data")

class RAIRadiationSafetyDosemeter(RAIModelAdmin):
    model = RUBIONUser
    identifier = 'radiation_safety'
    sub_identifier = 'rubionuser-dosemeter'
    menu_label = 'Dosimeter'
    menu_icon = 'tablet-alt'
    menu_icon_font = 'fas'

class RAIRadiationSafetyKeys(RAIModelAdmin):
    model = RUBIONUser
    identifier = 'radiation_safety'
    sub_identifier = 'rubionuser-keys'
    menu_label = 'Schlüssel'
    menu_icon = 'key'
    menu_icon_font = 'fas'

    
class RAINuclides(RAIModelAdmin):
    model = Nuclide
    identifier = 'radiation_safety'
    sub_identifier = 'nuclides'
    menu_label = 'Nuklide'
    menu_icon = 'radiation-alt'
    menu_icon_font = 'fas'
    
class RAIRadiationSafetyGroup(RAIAdminGroup):
    components = [
        RAIRadiationSafetyDosemeter,
        RAIRadiationSafetyKeys,
        RAINuclides
    ]
    menu_label = 'Strahlenschutz & Labororganisation'

