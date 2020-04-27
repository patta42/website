from .actions import RAIStaffUserListAction, StaffUserCreateAction, StaffUserEditAction

from django.utils.translation import ugettext as _

from rai.actions import (
    ListAction, CreateAction, EditAction, DetailAction, InactivateAction, DeleteAction
)
from rai.base import RAIModelAdmin, RAIAdminGroup
from .views import StaffUserCreateView 

from userdata.models import StaffUser

class RAIStaffUser(RAIModelAdmin):
    model = StaffUser
    menu_label = _('Staff')
    menu_icon_font = 'fas'
    menu_icon = 'users-cog'
    createview = StaffUserCreateView 
    default_action = RAIStaffUserListAction
    group_actions = [RAIStaffUserListAction, StaffUserCreateAction]
    item_actions = [StaffUserEditAction, DetailAction, InactivateAction, DeleteAction]
    

class RAIStaffGroup(RAIAdminGroup):
    components = [
        RAIStaffUser
    ]
    menu_label = _('RUBION internals')
