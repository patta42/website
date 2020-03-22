
from .filters import StaffUserStatusFilter 
from rai.actions import ListAction

class RAIStaffUserListAction(ListAction):
    list_filters = [ StaffUserStatusFilter ]
    
