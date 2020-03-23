
from rai.actions import ListAction, EditAction
import rai.edit_handlers as eh
from rai.widgets import RAITextInput
import userinput.rai.filters as filters
    #RUBIONUserStatusFilter, RUBIONUserInstrumentFilter

    
class RAIUserDataListAction(ListAction):
    list_item_template = 'userinput/rubionuser/rai/list/item-in-list.html'
    list_filters = [
        filters.RUBIONUserStatusFilter,
        filters.RUBIONUserInstrumentFilter
    ]

class RAIProjectListAction(ListAction):
    list_filters = [
        filters.ProjectStatusFilter
    ]

class RAIWorkgroupListAction(ListAction):
    list_item_template = 'userinput/workgroup/rai/list/item-in-list.html'
    list_filters = [
        filters.WorkgroupStatusFilter
    ]


class RAIWorkgroupEditAction(EditAction):
    edit_handler = eh.RAIObjectList(
        [
            eh.RAIFieldRowPanel([
                eh.RAIFieldPanel('department_de'),
                eh.RAIFieldPanel('department_en'),
            ]),
#            eh.RAIFieldPanel('title'),
        ]
    )
