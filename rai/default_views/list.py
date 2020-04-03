from .generic import RAIAdminView, FilterSettingsView


from django.http import HttpResponseForbidden, QueryDict
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import resolve, reverse


class ListView(FilterSettingsView):
    template_name = 'rai/views/default/list.html'
    
    def post(self, request):
        """
        Handles a POST-request
        
        For this view, a POST request is sent if the users wants to save some view-specific settings,
        here list or filter settings.

        This saves the respective settings and redirects to the view.
        """

        
        self.update_filter_settings(request)
        
        return redirect(request.path_info)

    
    
    def get_page_menu(self):
        actions = []
        request = getattr(self, 'request', None)
        for Action in self.raiadmin.group_actions:
            action = Action(self.raiadmin)
            if (action.action_identifier != self.active_action.action_identifier) and (action.show(request)):
                
                actions.append({
                    'icon' : action.icon,
                    'icon_font' : action.icon_font,
                    'label' : action.label,
                    'url' : action.get_href()
                })
        return render_to_string(
            'rai/menus/group_menu.html',
            {
                'actions' : actions,
                'settings_menu' : self.get_settings_menu(),
                'sort_button' : True,
                'filter_button' : True,
            }
        )
    def get_settings_menu(self):
        settings_action = self.active_action.settings_action
        return {
            'icon' : settings_action.icon,
            'icon_font' : settings_action.icon_font,
            'label' : settings_action.label,
            
        }
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = getattr(self, 'request', None)
        item_actions = []
        for Action in self.raiadmin.item_actions:
            action = Action(self.raiadmin)
            if action.show(request):
                item_actions.append({
                    'label' : action.label,
                    'icon_font' : action.icon_font,
                    'icon': action.icon,
                    'urlname': action.get_url_name()
                })
        context.update({
            'title' : self.raiadmin.menu_label,
            'objects' : self.get_queryset(), 
            'page_menu' : self.get_page_menu(),
            'item_template' : self.active_action.list_item_template,
            'configurable_display_fields' : self.active_action.configurable_display_fields,
            'visible_fields' : [], 
            'orders' : self.active_action.list_orders,
            'item_actions' : item_actions,
            
        })
        return context


