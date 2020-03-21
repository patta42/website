import datetime

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _l

from rai.actions import ListAction, CreateAction, EditAction, DetailAction, InactivateAction
from rai.base import RAIModelAdmin, RAIAdminGroup
from rai.filters import RAIFilter, RAIFilterOption


from userinput.models import RUBIONUser, WorkGroup, Project

class RUBIONUserStatusFilter(RAIFilter):
    label = _l('User status')
    filter_id = 'user_status'
    is_mutual_exclusive = True
    help_text = _l('Filters users by their active/inactive status.')
    options = [
        RAIFilterOption(_l('all'), 'all', help_text=_l('Show all users (independent from their status).')),
        RAIFilterOption(_l('active'), 'active', help_text=_l('Show only active users.'), default = True),
        RAIFilterOption(_l('inactive'), 'inactive', help_text=_l('Show inactive users only.'))
    ]

    def get_queryset(self):
        td = datetime.datetime.today()
        if self.value == 'all':
            return self.qs
        if self.value == 'active':
            return self.qs.filter(Q(exclude_at__isnull = True) | Q(exclude_at__gte = td))
        if self.value == 'inactive':
            return self.qs.filter(exclude_at__lt = td)

        return self.qs


class RUBIONUserInstrumentFilter(RAIFilter):
    label = _l('Used instruments')
    filter_id = 'user_instrument'
    is_mutual_exclusive = False
    help_text = _l('Filter users by their usage of instruments')
    options = [
        RAIFilterOption(_l('i1'), 'i1', help_text=_l('Show users using i1')),
        RAIFilterOption(_l('i2'), 'i2', help_text=_l('Show users using i2')),
        RAIFilterOption(_l('i3'), 'i3', help_text=_l('Show users using i3')),
        RAIFilterOption(_l('i4'), 'i4', help_text=_l('Show users using i4'))
    ]

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
