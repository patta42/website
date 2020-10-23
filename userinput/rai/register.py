
#from .filters import RUBIONUserStatusFilter, RUBIONUserInstrumentFilter

import datetime

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _l

from rai.actions import ListAction, CreateAction, EditAction, DetailAction, HistoryAction, DeleteAction
from rai.base import RAIModelAdmin, RAIAdminGroup
from rai.default_views import HistoryView

from rai.files.base import (
    register_collection, RAIDocumentCollection,
    RAIDocumentOnDemand, rai_register_documents_on_demand
)
from rai.mail.base import register_mail_collection, RAIModelAddressCollection
from rai.panels.base import register_panels

from userinput.models import (
    RUBIONUser, WorkGroup, Project, Nuclide, FundingSnippet, ThesisSnippet,
    PublicationSnippet
)    

import userinput.rai.actions as actions

from userinput.rai.documents import RubionUserBadgeDocument
from userinput.rai.panels import (
    WorkgroupApplicationPanel, ProjectApplicationPanel, UserStatsPanel
)

from userinput.rai.views.generic import MoveToWorkgroupView
from userinput.rai.views.projects.views import ProjectCreateView
from userinput.rai.views.rubionuser.views import (
    RUBIONUserEditView, RUBIONUserInactivateView, RUBIONUserHistoryView,
    RUBIONUserCreateBadgeView, RUBIONUserCreateView, RUBIONUserActivateView
)

from userinput.rai.views.workgroup.views import WorkgroupCreateView

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
        actions.RUBIONUserCreateAction
    ]
    default_action = actions.RAIUserDataListAction
    item_actions = [
        actions.RUBIONUserDataEditAction,
        DetailAction,
        actions.RUBIONUserInactivateAction,
        actions.RUBIONUserActivateAction,
        actions.RUBIONUserMoveAction,
        HistoryAction
    ]
    editview = RUBIONUserEditView
    inactivateview = RUBIONUserInactivateView
    activateview = RUBIONUserActivateView
    moveview = MoveToWorkgroupView
    historyview = RUBIONUserHistoryView
    createview = RUBIONUserCreateView


class RAIWorkGroups(RAIModelAdmin):
    model = WorkGroup
    menu_label = 'Arbeitsgruppen'
    menu_icon_font = 'fas'
    menu_icon = 'users'
    createview = WorkgroupCreateView
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
    group_actions = [actions.RAIProjectListAction, actions.RAIProjectCreateAction]
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
    createview = ProjectCreateView
    
class RAIUserInputGroup(RAIAdminGroup):
    components = [
        RAIUserData, RAIWorkGroups, RAIProjects, 
    ]
    menu_label = "Nutzerdaten"

class RAIFunding(RAIModelAdmin):
    model = FundingSnippet
    identifier = 'scientific_output'
    sub_identifier = 'funding'
    menu_label = 'Förderungen'
    menu_icon = 'money-bill-wave'
    menu_icon_font = 'fas'
    item_actions = []
    group_actions = [actions.RAIFundingListAction]

class RAIThesis(RAIModelAdmin):
    model = ThesisSnippet
    identifier = 'scientific_output'
    sub_identifier = 'thesis'
    menu_label = 'Abschlussarbeiten'
    menu_icon = 'book'
    menu_icon_font = 'fas'
    item_actions = []
    group_actions = [actions.RAIThesisListAction]

class RAIPublication(RAIModelAdmin):
    model = PublicationSnippet
    identifier = 'scientific_output'
    sub_identifier = 'publication'
    menu_label = 'Veröffentlichungen'
    menu_icon = 'scroll'
    menu_icon_font = 'fas'
    item_actions = [DeleteAction]
    group_actions = [actions.RAIPublicationListAction]

    
class RAIScientificOutputGroup(RAIAdminGroup):
    components = [
        RAIFunding, RAIThesis, RAIPublication
    ]
    menu_label = 'Wissenschaftlicher Output'
    
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

class RAIWorkgroupMailCollection(RAIModelAddressCollection):
    label = 'aktive Nutzer nach Arbeitsgruppen'
    model = WorkGroup
    multiple_for_instance = True
    
    def get_for_instance(self, instance):
        title = '{} ({})'.format(instance.title_de, instance.get_head())
#        title = '{}'.format(instance.title_de)#, instance.get_head())
        return {
            'title':title,
            'pk' : instance.pk,
            'id' : self.__class__.__name__
        }

    def get_all_for_pk(self, pk):
        wg = WorkGroup.objects.get(pk = pk)
        mails = []
        for member in wg.get_members():
            mails.append(self.format_as_mail_string(member))

        return mails

    
class RAIUserMailCollection(RAIModelAddressCollection):
    label = 'alle aktiven Nutzer'
    model = RUBIONUser
    multiple_for_instance = False

    def get_for_instance(self, instance):
        return self.format_as_mail_string(instance)
    def get_objects(self):
        return self.model.objects.active()

    
class RAIInactiveUserMailCollection(RAIUserMailCollection):
    label = 'alle inaktiven Nutzer'
    def get_objects(self):
        return self.model.objects.inactive()

class RAIGroupLeaderRUBMailCollection(RAIUserMailCollection):
    label = 'Teilnehmer der Nutzerversammlung'
    def get_objects(self):
        return super().get_objects().filter(is_rub = True, is_leader = True)

register_mail_collection(RAIWorkgroupMailCollection)
register_mail_collection(RAIUserMailCollection)
register_mail_collection(RAIInactiveUserMailCollection)
register_mail_collection(RAIGroupLeaderRUBMailCollection)
    
rai_register_documents_on_demand([RubionUserBadgeDocument])
register_panels([WorkgroupApplicationPanel, ProjectApplicationPanel, UserStatsPanel])
