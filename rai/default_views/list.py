from .generic import RAIAdminView, ViewSettingsFilterSettingsView, PageMenuMixin


from django.http import HttpResponseForbidden, QueryDict
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import resolve, reverse


class ListView(PageMenuMixin, ViewSettingsFilterSettingsView):
    template_name = 'rai/views/default/list.html'
    
    # def post(self, request):
    #     """
    #     Handles a POST-request
        
    #     For this view, a POST request is sent if the users wants to save some view-specific settings,
    #     here list or filter settings.

    #     This saves the respective settings and redirects to the view.
    #     """
        
    #     return super().post(request)

    
    
    # def get_page_menu(self):
    #     actions = []
    #     request = getattr(self, 'request', None)
    #     for Action in self.raiadmin.group_actions:
    #         action = Action(self.raiadmin)
    #         if (action.action_identifier != self.active_action.action_identifier) and (action.show(request)):
    #             actions.append({
    #                 'icon' : action.icon,
    #                 'icon_font' : action.icon_font,
    #                 'label' : action.label,
    #                 'url' : action.get_href(),
    #                 'show_for_instance':action.show_for_instance,
    #             })
    #     return render_to_string(
    #         'rai/menus/group_menu.html',
    #         {
    #             'actions' : actions,
    #             'settings_menu' : self.get_settings_menu(),
    #             'sort_button' : True,
    #             'filter_button' : True,
    #             'request' : self.request
                
    #         }
    #     )
    def get_settings_menu(self):
        settings_action = self.active_action.settings_action
        return {
            'icon' : settings_action.icon,
            'icon_font' : settings_action.icon_font,
            'label' : settings_action.label,
            
        }

    def get_actions(self):
        return self.get_group_actions()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = getattr(self, 'request', None)
        # item_actions = []
        # for Action in self.raiadmin.item_actions:
        #     action = Action(self.raiadmin)
        #     if action.show(request):
        #         item_actions.append({
        #             'label' : action.label,
        #             'icon_font' : action.icon_font,
        #             'icon': action.icon,
        #             'urlname': action.get_url_name(),
        #             'show_for_instance' : action.show_for_instance
        #         })
        context.update({
            'title' : self.raiadmin.menu_label,
            'objects' : self.get_queryset(), 
            'page_menu' : self.get_page_menu(),
            'item_template' : self.active_action.list_item_template,
            'active_action': self.active_action,
            'visible_fields' : [], 
            'orders' : self.active_action.list_orders,
            'item_actions' : self.get_item_actions(for_list = True),
            
        })
        return context


