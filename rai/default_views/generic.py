from django.urls import resolve, reverse
from django.http import QueryDict, HttpResponseForbidden
from django.template.loader import render_to_string
from django.views.generic import TemplateView

from rai.models import ListFilterSettings

import re

from wagtail.core import hooks

class RAIView(TemplateView):
    """ 
    A generic view for RAI which implements rendering the admin menu.
    Does *not* require a RAIAdmin definition
    """
    def get_main_admin_menu(self):
        items = []
        for fn in hooks.get_hooks('rai_menu_group'):
            item = fn()
            components = [];
            for Component in item.components:
                component = Component()
                components.append({
                    'label' : component.menu_label,
                    'icon' : component.menu_icon,
                    'icon_font' : component.menu_icon_font,
                    'url' : component.get_default_url()
                })
                    
            items.append({
                'label' : item.menu_label,
                'components' : components
            })
            
        return render_to_string(
            'rai/menus/main_admin_menu.html',
            {
                'items' : items
            }
        )
    
    def get_context_data(self, **kwargs):
        """
        adds the main admin menu to the Context object
        """
        context = super().get_context_data(**kwargs)
        context['main_admin_menu'] = self.get_main_admin_menu()
        return context



class RAIAdminView(RAIView):
    """
    A view which requires a RAIAdmin definition and an active RAIAction object

    Furthermore, implements some simple media interface for adding view-specific js and css.
    [Note: The latter might already be implemented in the TemplateView, I'm not sure.]
    """
    
    raiadmin = None
    active_action = None
    media = {
        'js'  : [],
        'css' : []
    }
    inline_media = {
        'js'  : [],
        'css' : []
    }

    def get_context_data(self, **kwargs):
        """
        adds the media to the Context object
        in 'media', file names are stored which should be inserted in the template via {% static %}
        in 'inline_media', inline definitions are stored which should be enclosed in <style></style> or <script></script>
        """
        context = super().get_context_data(**kwargs)
        context.update({
            'media' : self.media,
            'inline_media' : self.inline_media
        })

        return context



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
        """
        
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
        """
        context = super().get_context_data(**kwargs)
        context['filter_form'] = self.get_filter_form()

        return context
    
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
                view_name = view_name
            ).get()
            
        except ListFilterSettings.DoesNotExist:
            if not request.user.is_staff:
                return HttpResponseForbidden()
            filter_settings = ListFilterSettings(
                user = request.user,
                view_name = view_name
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
                
            filt.update({
                'type' : 'radio' if Fl.is_mutual_exclusive else 'checkbox',
                'value' : value 
            })
            filters.append(filt)
            
                
        return render_to_string(self.filter_form_template, {'filters': filters})
