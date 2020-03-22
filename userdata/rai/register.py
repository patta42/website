from .actions import RAIStaffUserListAction

from django.utils.translation import ugettext as _

from rai.actions import ListAction, CreateAction, EditAction, DetailAction, InactivateAction
from rai.base import RAIModelAdmin, RAIAdminGroup

from userdata.models import StaffUser

class RAIStaffUser(RAIModelAdmin):
    model = StaffUser
    menu_label = _('Staff')
    menu_icon_font = 'fas'
    menu_icon = 'users-cog'
    group_actions = [RAIStaffUserListAction, CreateAction]
    item_actions = [EditAction, DetailAction, InactivateAction]

class RAIStaffGroup(RAIAdminGroup):
    components = [
        RAIStaffUser
    ]
    menu_label = _('RUBION internals')
