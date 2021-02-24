from .actions import (
    RAIStaffUserListAction, StaffUserCreateAction, StaffUserEditAction,
    RolesEditAction, RolesCreateAction, RolesPDFListAction,
    BeiratGroupEditAction, BeiratGroupCreateAction,
    Beirat2StaffRelationEditAction, Beirat2StaffRelationCreateAction,
    Beirat2StaffRelationReplaceAction
)
from .notifications import CRSNewDosemeter, CRSNoDosemeter, CRSUserInactivated
from .events import RUBIONUserWithDosemeterInactivated
from .views import StaffUserCreateView, BeiratView, BeiratPositionReplaceView


    
from django.utils.translation import ugettext as _

from rai.actions import (
    ListAction, CreateAction, EditAction, DetailAction, InactivateAction, DeleteAction,
    HistoryAction
)
from rai.base import RAIModelAdmin, RAIAdminGroup
from rai.default_views import HistoryView
from rai.mail.base import register_mail_collection, RAIModelAddressCollection
from rai.notifications.base import register_notification


from userdata.models import StaffUser, StaffRoles, BeiratGroups, Beirat2StaffRelation

from userinput.rai.events import NewOfficialDosemeter, NoMoreOfficialDosemeter

class RAIStaffUser(RAIModelAdmin):
    model = StaffUser
    menu_label = _('Staff')
    menu_icon_font = 'fas'
    menu_icon = 'users-cog'
    createview = StaffUserCreateView
    historyview = HistoryView
    default_action = RAIStaffUserListAction
    group_actions = [RAIStaffUserListAction, StaffUserCreateAction]
    item_actions = [
        StaffUserEditAction, DetailAction, InactivateAction, DeleteAction, HistoryAction
    ]

class RAIBeiratGroups(RAIModelAdmin):
    model = BeiratGroups
    menu_label = 'Beiratsgruppen'
    menu_icon = 'user-friends'
    menu_icon_font = 'fas'
    default_action = ListAction
    group_actions = [ListAction, BeiratGroupCreateAction]
    item_actions = [BeiratGroupEditAction, DeleteAction]

class RAIBeirat(RAIModelAdmin):
    model = Beirat2StaffRelation
    menu_label = 'Beirat'
    menu_icon = 'user-tie'
    menu_icon_font = 'fas'
    default_action = ListAction
    listview = BeiratView
    replaceview = BeiratPositionReplaceView
    group_actions = [ListAction, Beirat2StaffRelationCreateAction]
    item_actions = [
        Beirat2StaffRelationEditAction,
        DeleteAction, Beirat2StaffRelationReplaceAction]
    
class RAIStaffRoles(RAIModelAdmin):
    model = StaffRoles
    menu_label = 'Aufgaben'
    menu_icon = 'tasks'
    menu_icon_font = 'fas'
    group_actions = [ListAction, RolesCreateAction]#, RolesPDFListAction]
    default_action = ListAction
    item_actions = [RolesEditAction, DeleteAction]

class RAIStaffRolePDFList(RAIModelAdmin):
    model = StaffRoles
    group_actions = [RolesPDFListAction]
    default_action = RolesPDFListAction
    menu_label = 'Aufgaben als PDF exportieren'
    menu_icon = 'file-pdf'
    menu_icon_font = 'fas'
    
class RAIStaffGroup(RAIAdminGroup):
    components = [
        RAIStaffUser,
        RAIStaffRoles,
#        RAIStaffRolePDFList,
        RAIBeiratGroups,
        RAIBeirat
    ]
    menu_label = _('RUBION internals')

class RAIBeiratMailCollection(RAIModelAddressCollection):
    model = Beirat2StaffRelation
    label = 'Beirat'

    def format_as_mail_string(self, instance):
        if instance is None:
            return ''
        if instance.email:
            email = instance.email
        else:
            email = instance.user.email
        return '{} {} <{}>'.format(
            instance.first_name,
            instance.last_name,
            email
        )
    
    def get_for_instance(self, instance):
        return self.format_as_mail_string(instance.member)

    def get_mail_addresses(self):
        addresses = [] 
        for obj in self.get_objects():
            if obj.member is not None:
                addresses.append(self.get_for_instance(obj))

        return addresses

class RAIStaffMailCollection(RAIModelAddressCollection):
    model = StaffUser
    label = 'Mitarbeiter'
    def get_for_instance(self, instance):
        return self.format_as_mail_string(instance)

    
register_mail_collection(RAIStaffMailCollection)
register_mail_collection(RAIBeiratMailCollection)
register_notification(CRSNewDosemeter, event = NewOfficialDosemeter)
register_notification(CRSNoDosemeter, event = NoMoreOfficialDosemeter)
register_notification(CRSUserInactivated, event = RUBIONUserWithDosemeterInactivated)
