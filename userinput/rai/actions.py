from rai.actions import ListAction

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
    list_filters = [
        filters.WorkgroupStatusFilter
    ]
