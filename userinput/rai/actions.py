
from rai.actions import ListAction, EditAction, DetailAction, CreateAction
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
    list_item_template = 'userinput/project/rai/list/item-in-list.html'
    list_filters = [
        filters.ProjectStatusFilter
    ]
class RAIProjectEditAction(EditAction):
    edit_handler = eh.RAIObjectList([
        eh.RAIUserDataPanel([
            eh.RAITranslatedContentPanel(
                {'de':'german', 'en':'english'},
                ['title', 'summary']
            ),
        ], heading = 'Project information', is_expanded = False),
        eh.RAIUserDataPanel([
            eh.RAIFieldPanel('is_confidential'),
        ], heading = 'Project visibility', is_expanded = False),
        eh.RAIUserDataPanel([
            eh.RAIMultiFieldPanel([
                eh.RAIFieldPanel('uses_gmos', classname="col-md-3"),
                eh.RAIFieldPanel('gmo_info', classname="col-md-9"),
            ], heading="Info on GMOs", classname='form-row'),
            eh.RAIMultiFieldPanel([
                eh.RAIFieldPanel('uses_chemicals', classname="col-md-3"),
                eh.RAIFieldPanel('chemicals_info', classname="col-md-9"),
            ],  heading="Info on chemicals", classname='form-row'),
            eh.RAIMultiFieldPanel([
                eh.RAIFieldPanel('uses_hazardous_substances', classname="col-md-3"),
                eh.RAIFieldPanel('hazardous_info', classname="col-md-9"),
            ], heading="Info on hazardous substance", classname='form-row'),
            eh.RAIMultiFieldPanel([
                eh.RAIFieldPanel('biological_agents', classname="col-md-3"),
                eh.RAIFieldPanel('bio_info', classname="col-md-9"),
            ], heading="Info on biological substances", classname='form-row')
        ], heading = 'Safety information', is_expanded = True),
        eh.RAICollapsablePanel([
            eh.RAIFieldPanel('internal_rubion_comment')
        ], heading = 'Internal remarks')
    ])
    
class RAIWorkgroupListAction(ListAction):
    list_item_template = 'userinput/workgroup/rai/list/item-in-list.html'
    list_filters = [
        filters.WorkgroupStatusFilter
    ]

workgroup_edit_handler = eh.RAIObjectList([
    eh.RAIUserDataPanel([
        eh.RAITranslatedContentPanel(
            {'de':'german', 'en':'english'},
            ['title', 'department', 'institute']
        ),
        eh.RAIFieldPanel('homepage')
    ], heading = 'User data', is_expanded = False),
    eh.RAICollapsablePanel([
        eh.RAIFieldPanel('internal_rubion_comment')
    ], heading = 'Internal comment', is_expanded = True)
])


class RAIWorkgroupEditAction(EditAction):
    edit_handler = workgroup_edit_handler

class RAIWorkgroupDetailAction(DetailAction):
    edit_handler = workgroup_edit_handler

class RAIWorkgroupCreateAction(CreateAction):
    edit_handler = workgroup_edit_handler
