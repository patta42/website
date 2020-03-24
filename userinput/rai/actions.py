
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
class RAIProjectAction(EditAction):
    edit_handler = eh.RAIObjectList([
        
    ])
    
class RAIWorkgroupListAction(ListAction):
    list_item_template = 'userinput/workgroup/rai/list/item-in-list.html'
    list_filters = [
        filters.WorkgroupStatusFilter
    ]


class RAIWorkgroupEditAction(EditAction):
    edit_handler = eh.RAIObjectList([
        eh.RAIUserDataPanel([
            eh.RAITranslatedContentPanel(
                {'de':'german', 'en':'english'},
                ['department', 'institute']
            ),
            eh.RAIFieldPanel('homepage')
        ], heading = 'User data', is_expanded = False),
        eh.RAICollapsablePanel([
            eh.RAIFieldPanel('internal_rubion_comment')
        ], heading = 'Internal comment', is_expanded = True)
    ])

