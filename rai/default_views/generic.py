from pprint import pprint

from collections import OrderedDict

from django.contrib import messages
from django.urls import resolve, reverse
from django.http import QueryDict, HttpResponseForbidden
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.views.generic import TemplateView

import json

from rai.settings.models import ListFilterSettings, AdminMenuSettings, ListViewSettings
from rai.markdown.widgets import RAIMarkdownWidget
import re

from wagtail.core import hooks

class RAIView(TemplateView):
    """ 
    A generic view for RAI which implements rendering the admin menu.
    Does *not* require a RAIAdmin definition
    """
    media = {
        'css' : [
            'css/admin/edit_handlers.css',
            'js/admin/third-party/jquery-ui-1.12.1.custom/jquery-ui.min.css',
            'js/admin/third-party/tempus-dominus/tempusdominus-bootstrap-4.min.css',
        ],
        'js' : [
            # 'js/admin/third-party/jquery-ui-1.12.1.custom/jquery-ui.min.js',
            # 'js/admin/RUBIONeditor.js',
            # 'js/admin/RAIWidgets.js',
            # 'js/admin/third-party/mark.js-8.11.1/jquery.mark.min.js',
            # 'js/admin/third-party/moment/moment.min.js',
            # 'js/admin/third-party/tempus-dominus/tempusdominus-bootstrap-4-fa5-fix.js',
            # 'js/admin/third-party/bsCustomFileInput.js',
            # 'js/admin/views/list.js',
            
            
            
        ]
    }

    inline_media = {
        'js'  : [],
        'css' : []
    }


    def dispatch(self, request, *args, **kwargs):
        self.request = request
        return super().dispatch(request, *args, **kwargs)
    def error_message(self, msg):
        messages.error(self.request, msg)
    def warning_message(self, msg):
        messages.warning(self.request, msg)

    def success_message(self, msg):
        messages.success(self.request, msg)
    def debug_message(self, msg):
        messages.debug(self.request, msg)
    def info_message(self, msg):
        messages.info(self.request, msg)
        
    def get_main_admin_menu(self):
        request = getattr(self, 'request', None)
        try:
            user_settings = AdminMenuSettings.objects.get(user__pk = request.user.pk)
            user_settings = user_settings.as_dict()
        except AdminMenuSettings.DoesNotExist:
            user_settings = None


        items = []
        for fn in hooks.get_hooks('rai_menu_group'):
            group = fn()
            components = [];
            if group.show(request):
                for Component in group.components:
                    component = Component()
                    url = component.get_default_url()
                    if user_settings:
                        user_label = user_settings['item_labels'].get(
                            url, 
                            component.menu_label
                        )
                    else:
                        user_label = component.menu_label
                        
                    if component.show(request):
                        components.append({
                            'label' : component.menu_label,
                            'user_label' : user_label,
                            'icon' : component.menu_icon,
                            'icon_font' : component.menu_icon_font,
                            'url' : url
                        })
                # only show the group if there are any components in it
                if components:
                    if user_settings:
                        user_label = user_settings['group_item_labels'].get(
                            group.menu_label,
                            group.menu_label
                        )
                    else:
                        user_label = group.menu_label
                    items.append({
                        'label' : group.menu_label,
                        'user_label' : user_label,
                        'components' : components
                    })
        if user_settings:
            group_order = user_settings.get('group_order', None)
        else:
            group_order = None
        if group_order:
            items_sorted = []
            items_copy = items
            if group_order:
                items = items_copy
                for group in group_order:
                    count = 0
                    for item in items:
                        if item['label'] == group:
                            items_copy.pop(count)
                            items_sorted.append(item)
                            break
                        count += 1
                items = items_sorted + items_copy
                        
            
        return render_to_string(
            'rai/menus/main_admin_menu.html',
            {
                'admin_menu_settings_url': reverse('rai_settings_admin_menu'),
                'items' : items
            }
        )
    def get_help_editor(self):
        widget = RAIMarkdownWidget({}, attrs = {
            'id' : 'id_helpMarkdownEditor'
        })
        return widget.render('helpMarkdownEditor', '', {})
    
    def get_context_data(self, **kwargs):
        """
        adds the main admin menu to the Context object
        """
        context = super().get_context_data(**kwargs)
        
        context.update({
            'media' : self.media,
            'inline_media' : self.inline_media,
            'main_admin_menu' : self.get_main_admin_menu(),
            'help_editor' : self.get_help_editor(),
            'user_pk' : self.request.user.pk 
        })
        return context


class RAIAdminView(RAIView):
    """
    A view which requires a RAIAdmin definition and an active RAIAction object

    Furthermore, implements some simple media interface for adding view-specific js and css.
    [Note: The latter might already be implemented in the TemplateView, I'm not sure.]
    """
    
    raiadmin = None
    active_action = None


class FilterSettingsView(RAIAdminView):
    """
    implements handling Filters and Filter settings
    """

    filter_form_template = 'rai/views/default/forms/list-filter-form.html'

    
    #
    # overwritten methods
    #

    def dispatch(self, request, *args, **kwargs):
        """
        sets self.view_name and self.user
        """
        self.view_name = resolve(self.request.path_info).url_name
        self.user = self.request.user
        
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """
        sets the self.filter_spec
        sets the queryset
        """
        self.queryset = self.raiadmin.model._default_manager.get_queryset()
        self.filter_spec = self.get_filter_spec(request.GET)
        return super().get(request)
    
    def post(self, request):
        """
        Handles a POST-request
        
        For this view, a POST request is sent if the users wants to save filter settings.

        This saves the respective settings and redirects to the view.
        """
        self.update_filter_settings(request)
        return redirect(request.path_info)

    def get_context_data(self, **kwargs):
        """
        adds a rendered filter form to the Context
        adds count of the unfiltered queryset to the Context
        """
        context = super().get_context_data(**kwargs)
        context['filter_form'] = self.get_filter_form()
        context['original_object_count'] = self.queryset.count()
        return context

    def get_queryset(self):
        """
        Applies the filters
        """
        return self.apply_filters(self.queryset)
    
    #
    # additional methods
    #
    
    def get_filter_spec(self, qd):
        """
        Gets the filter specifications for this request.
          
        First tries request.GET or, if that does not contain a filter spec, tries to fetch
        it from th DB

        returns the result of self.parse_querydict_for_filters
        """
        
        filters = self.parse_querydict_for_filters(qd)
        if not filters:
            dbres = ListFilterSettings.objects.filter(user = self.user, view_name = self.view_name)
            if dbres:
                filters = self.parse_querydict_for_filters(QueryDict(dbres.get().filter_spec))

        return filters


    def parse_querydict_for_filters( self, qd ):
        """
        Extracts the filter definitions from the query dict.
        a filter definition has a key of the following scheme:
          filter<number>__<filterId>

        returns a dict like this:
        { <filterId> : { 'num' : <number>, 'value' : <value of qd>} } or {}
        """
        
        filters = {}
        for k in qd.keys():
            if k.startswith('filter'):
                result = re.match(r'^filter(?P<num>\d+)__(?P<name>\w+)$', k)
                if result is not None:
                    filters[result.group('name')] = {
                        'num' : int(result.group('num')),
                        'value' : qd.getlist(k)
                    }
        return filters

    def update_filter_settings(self, request):
        """
        updates (or creates) the filter settings in the DB.
        Is called by self.post() 
        """

        # get ListFilterSettings from db or create a new one
        try:
            filter_settings = ListFilterSettings.objects.filter(
                user = request.user,
                view_name = self.view_name
            ).get()
        except ListFilterSettings.DoesNotExist:
            if not request.user.is_staff and not request.user.has_perm('wagtailadmin.access_admin'):
                return HttpResponseForbidden()
            filter_settings = ListFilterSettings(
                user = request.user,
                view_name = self.view_name
            )

        # remove all entries in POST that are not filter specs
        qd = self.request.POST.copy()
        for k in self.request.POST.keys():
            if not k.startswith('filter'):
                del(qd[k])

        # update and save ListFilterSettings
        filter_settings.filter_spec = qd.urlencode()
        filter_settings.save()

    def get_filter_form(self):
        """
        renders a form for the current filter settings
        """
        
        filters = []
        for Fl in self.active_action.list_filters:
            options = []
            for Opt in Fl.options:
                options.append({
                    prop : getattr(Opt, prop) for prop in ['label','help_text', 'value']
                })
            filt = { 'options' : options }
            filt.update({
                prop : getattr(Fl, prop) for prop in ['label','help_text', 'is_mutual_exclusive', 'filter_id'] 
            })
            flt = self.filter_spec.get(Fl.filter_id)
            try:
                value = flt.get('value', [])
            except AttributeError:
                value = []
            if not value:
                value = Fl.get_default_value()
            filt.update({
                'type' : 'radio' if Fl.is_mutual_exclusive else 'checkbox',
                'value' : value 
            })
            filters.append(filt)
            
                
        return render_to_string(self.filter_form_template, {'filters': filters})

    def get_filters_sorted(self):
        """
        sorts the filters in their order of application and returns them
        """
        filters = [None] * len(self.filter_spec)
        for Filter in self.active_action.list_filters:
            try:
                filters[self.filter_spec[Filter.filter_id]['num']] = Filter
            except KeyError:
                pass

        return filters

    def apply_filters (self, qs):
        """
        applies the filters on qs
        """
        filters = self.get_filters_sorted()
        
        for Fl in filters:
            val = self.filter_spec[Fl.filter_id]['value']
            fl = Fl(qs, value = val)
            qs = fl.get_queryset()
        return qs


class ListViewSetting:
    '''
    A class that defines a setting. Provides a general get() method to 
    get the corresponding value
    '''

    def get(self, obj):
        pass
    
class ViewSettingsFilterSettingsView(FilterSettingsView):
    '''
    Adds user-configurable items to the list and and an appropriate Form
    '''
    list_settings_form_template = 'rai/views/default/forms/list-settings-form.html'
    #
    # overridden methods
    #
    def post(self, request):
        # the settings form sends action=update_view_settings,
        # while the FilterForm does not send any action
        action = request.POST.get('action', None)
        if not action:
            # call parent
            return super().post(request)
        else:
            if action == 'update_view_settings':
                self.update_view_settings(request)
                self.success_message('Die Einstellungen wurden geändert.')
            return redirect(request.path_info)

    def get(self, request):
        # before calling super().get(), get the current view settings.
        self.ordered_settings = self.get_ordered_settings(request)
        
        return super().get(request)

    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        context['settings_form'] = self.get_settings_form()
        context['settings'] = getattr(self, 'ordered_settings', None)
        return context

    #
    # additional methods
    #

    def update_view_settings(self, request):
        # make a copy of of request.POST
        post = request.POST.copy()
        # remove entries that don't start with 'setting'
        
        for key in request.POST.keys():
            if not key.startswith('setting'):
                del(post[key])
        try:
            user_settings = ListViewSettings.objects.get(
                user = request.user,
                view_name = self.view_name
            )
        except ListViewSettings.DoesNotExist:
            user_settings = ListViewSettings(
                user = request.user,
                view_name = self.view_name
            )

        user_settings.settings = post.urlencode()
        user_settings.save()
        
    def get_settings_spec(self, request):
        # It is slightly more complex here than for the filters
        # since it is perfectly valid to unselect all options,
        # which will result in an empty query string.
        # However, the action field will be send. If it is present in
        # request.GET, we have querystring representing a valid settings_spec
        action = request.GET.get('action', None)
        settings_spec = None
        if action and action == 'update_view_settings':
            settings_spec = self.parse_querydict(request.GET)
        else:
            try:
                saved_settings = ListViewSettings.objects.get(
                    user = request.user,
                    view_name = self.view_name
                )
                
            except ListViewSettings.DoesNotExist:
                saved_settings = None

            if saved_settings:
                settings_spec = self.parse_querydict(QueryDict(
                    saved_settings.settings
                ))
        return settings_spec
        
    def parse_querydict(self, qd):
        spec = {}
        keyword = 'settings__'
        l = len(keyword)
        for key in qd.keys():
            if key.startswith(keyword):
                spec[key[l:]] = int(qd[key])

        return spec
    
    def get_default_settings(self):
        # get default settings from active action
        raw_settings = getattr(self.active_action, 'item_provides', None)

        # make an item with
        # - label
        # - descripton
        # for each settings that is not a group. for groups, make the same for children 

        settings = OrderedDict()
        group_items = OrderedDict()
        if raw_settings:
            # we will need to loop twice through the dict. First, create groups and settings,
            # second, populate groups. Well, second time, the dict is smaller...

            for key, rs in raw_settings.items():
                group  = rs.get('group', None)
                if not group: # item does not belong to a group
                    settings[key] = {
                        'label': rs['label'],
                        'desc': rs['desc'],
                        'selected' : rs.get('selected', True),
                        'children' : [], # even if it's not a group, it does
                                         # not hurt to implement this,
                        'selected_children_count' : 0,
                        'unselected_children_count' : 0,
                    }
                else:
                    group_items[key] = rs
            for key, rs in group_items.items():
                group  = rs.get('group', None)
                # cannot be None due to the above loop
                settings[group]['children'].append({
                    'label' : rs['label'],
                    'desc': rs['desc'],
                    'selected' : rs.get('selected', True),
                    'key' : key
                })
                if rs.get('selected', True):
                    settings[group]['selected_children_count'] += 1
                else:
                    settings[group]['unselected_children_count'] += 1
        return settings
    
    def get_ordered_settings(self, request):
        default_settings = self.get_default_settings()
        if not default_settings:
            return None
        
        settings_spec = self.get_settings_spec(request)
        if settings_spec is None:
            return default_settings
        else:
            keys = default_settings.keys()
            ordered = [None] * len(keys)
            # for unselected items, order does not matter, fill from end to start
            count = len(keys) - 1
            for key in keys:
                if key not in settings_spec:
                    item = default_settings[key]
                    item['selected'] = False
                    for child in item['children']:
                        child['selected'] = False
                    item['selected_children_count'] = 0
                    item['unselected_children_count'] = len(item['children'])
#                    print('Setting {}'.format(count))
                    ordered[count] = (key, item)
                    count -= 1
                    
                else:
                    item = default_settings[key]
                    item['selected'] = True
                    ordered_children = [None] * len(item['children'])
                    count2 = len(item['children']) - 1
                    for child in item['children']:
                        subkey = '{}__{}'.format(key, child['key'])
                        if  subkey in settings_spec:
                            ordered_children[settings_spec[subkey]] = child
                            ordered_children[settings_spec[subkey]]['selected'] = True
                        else:
                            ordered_children[count2] = child
                            ordered_children[count2]['selected']  = False
                            count2 -= 1
                    item['children'] = ordered_children
                    item['selected_children_count'] = count2+1
                    item['unselected_children_count'] = len(item['children']) - (count2 + 1)
                    
                    # Workaround. It seems that sometimes (needs research!) settings_spec[key] is
                    # not unique
#                    print('Trying to set {}'.format(settings_spec[key]))
                    tmp = settings_spec[key]
                    if ordered[tmp] is not None:
                        tmp = 0
                        while ordered[tmp] is not None:
                            tmp = tmp + 1
#                    print('Will set {}'.format(tmp))
                    ordered[tmp] = (key, item)


            return OrderedDict(ordered)

    def get_settings_form(self):
        ordered_settings = self.ordered_settings
        return render_to_string(self.list_settings_form_template, {'settings' : ordered_settings})
        
                
class SingleObjectMixin:
    def get_object(self):
        qs = self.raiadmin.model._default_manager.get_queryset()
        try:
            return qs.get(pk = self.kwargs['pk'])
        except TypeError:
            return qs.get(id = self.kwargs['pk'])


class PageMenuMixin:
    save_button = False
    save_button_label = 'Save'
    save_button_icon = None
    proceed_button = False
    proceed_button_label = 'Proceed'
    sort_button = False
    filter_button = False
    icons_only = True
    
    def get_group_actions(self):
        request = getattr(self, 'request', None)
        actions = []
        for Action in self.raiadmin.group_actions:
            action = Action(self.raiadmin)
            if action.action_identifier != self.active_action.action_identifier and action.show(request):
                actions.append({
                    'icon' : action.icon,
                    'icon_font' : action.icon_font,
                    'label' : action.label,
                    'url' : action.get_href(),
                    'btn_type' : getattr(action,'btn_type', None),
                    'text_type': getattr(action,'text_type', None),
                    'show_for_instance': action.show_for_instance,
                    'object': getattr(self, 'obj', True)
                })
        return actions

    def get_item_actions(self):
        actions = []
        request = getattr(self, 'request', None)
        for Action in self.raiadmin.item_actions:
            action = Action(self.raiadmin)
            if action.action_identifier != self.active_action.action_identifier and action.show(request):
                actions.append({
                    'icon' : action.icon,
                    'icon_font' : action.icon_font,
                    'label' : action.label,
                    'url' : action.get_href(self.obj.id),
                    'btn_type' : getattr(action,'btn_type', None),
                    'text_type': getattr(action,'text_type', None),
                    'show_for_instance': action.show_for_instance,
                    'object' : getattr(self, 'obj', True),
                    'is_ajax' : getattr(action, 'is_ajax', False),
                    'get_params' : getattr(action, 'get_params', False)
                })
        return actions

    def get_actions(self):
        return self.get_group_actions() + self.get_item_actions()
    
    def get_page_menu(self):
        actions = self.get_actions()
        return render_to_string(
            'rai/menus/group_menu.html',
            {
                'actions' : actions,
                'sort_button' : self.sort_button,
                'filter_button' : self.filter_button,
                'save_button': self.save_button,
                'save_button_label' : self.save_button_label,
                'save_button_icon' : self.save_button_icon,
                'proceed_button': self.proceed_button,
                'proceed_button_label' : self.proceed_button_label,
                'icons_only' : self.icons_only,
                'request' : self.request
#                'settings_menu' : self.get_settings_menu()    
            }
        )

