from .filters import StaffUserStatusFilter
from .edit_handlers import create_staff_edit_handler, edit_staff_user_handler
from rai.actions import ListAction, CreateAction, EditAction

class RAIStaffUserListAction(ListAction):
    list_filters = [ StaffUserStatusFilter ]
    list_item_template = 'userdata/staffuser/rai/list/item-in-list.html'
    
class StaffUserCreateAction(CreateAction):
    edit_handler = create_staff_edit_handler

class StaffUserEditAction(EditAction):
    edit_handler = edit_staff_user_handler
