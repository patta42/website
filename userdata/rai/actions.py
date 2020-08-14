
from .edit_handlers import (
    create_staff_edit_handler, edit_staff_user_handler, edit_role_handler,
    beirat_group_edit_handler, beirat2staff_edit_handler, beirat_replace_edit_handler
)
from .filters import StaffUserStatusFilter
from .views import StaffUserRoleListView
from rai.actions import ListAction, CreateAction, EditAction

class RAIStaffUserListAction(ListAction):
    list_filters = [ StaffUserStatusFilter ]
    list_item_template = 'userdata/staffuser/rai/list/item-in-list.html'
    
class StaffUserCreateAction(CreateAction):
    edit_handler = create_staff_edit_handler

class StaffUserEditAction(EditAction):
    edit_handler = edit_staff_user_handler

class RolesEditAction(EditAction):
    edit_handler = edit_role_handler

class RolesCreateAction(CreateAction):
    edit_handler = edit_role_handler

class RolesPDFListAction(ListAction):
    label = 'Aufgabenliste exportieren'
    icon = 'file-pdf'
    icon_font = 'fas'
    action_identifier = 'staffrole-pdflist'
    list_item_template = 'userdata/rai/staff_user_role_list-item.html'
    
    def get_view(self):
        return StaffUserRoleListView.as_view(
            raiadmin = self.raiadmin,
            active_action = self
        )
    
class BeiratGroupEditAction(EditAction):
    edit_handler = beirat_group_edit_handler

class BeiratGroupCreateAction(CreateAction):
    edit_handler = beirat_group_edit_handler
    
class Beirat2StaffRelationEditAction(EditAction):
    edit_handler = beirat2staff_edit_handler

class Beirat2StaffRelationReplaceAction(EditAction):
    action_identifier = 'replace'
    label = 'Ändern'
    icon = 'sync-alt'
    edit_handler = beirat_replace_edit_handler

    def get_view(self):
        return self.raiadmin.replaceview.as_view(
            raiadmin = self.raiadmin,
            active_action = self
        )
    
    
class Beirat2StaffRelationCreateAction(CreateAction):
    edit_handler = beirat2staff_edit_handler
