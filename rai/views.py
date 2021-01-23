from pprint import pprint

from django.utils.html import mark_safe, format_html

# from django.core.exceptions import ImproperlyConfigured
# from django.http import JsonResponse
# from django.template.loader import render_to_string
# from django.views.generic import TemplateView

import json

from rai.default_views.generic import RAIView
from rai.settings.models import PanelSettings
from rai.panels.base import EmptyPanel

from wagtail.admin.views.account import LoginView as WALoginView
# from wagtail.core import hooks
# 



class JsonResponseMixin:
    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )
    
    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        return context

class HTMLElement:

    def __init__(self, tagName = '', classes = []):
            self.tagName = tagName
            self.classes = classes
            self.children = []
            self.data_attrs = {}
            
    def add(self, child):
        self.children.append(child)
        return self
    
    def addTo(self, parent):
        parent.add(self)
        return self

    def data(self, key, val):
        self.data_attrs[key] = val
    
    def to_html(self):
        html = ''
        data = ''
        for k,v in self.data_attrs.items():
            data += 'data-{}="{}" '.format(k,int(v))
        
        if self.tagName != '':
            html += mark_safe(format_html(
                '<{tagName} class="{classes}" {data}>',
                tagName = self.tagName,
                classes = ' '.join(self.classes),
                data = data
            ))
            for child in self.children:
                html += child.to_html()
            html += mark_safe(format_html('</{tagName}>', tagName = self.tagName))

        else:
            for child in self.children:
                html += child.to_html()
        return html
    
    def __repr__(self):
        return "<%s with tag=%s classes=%s children=%s id=%s>" % (
            self.__class__.__name__,
            self.tagName,
            ' '.join(self.classes),
            len(self.children),
            id(self)
        )
    
class BootstrapGrid(HTMLElement):
    def __init__(self):
        super().__init__()
        self.tagName = 'div'
        self.classes = ['panel-grid-wrapper']

class HomeView(RAIView):
    template_name = 'rai/home.html'

    def get_panels(self):
        panels = []
        try:
            p_settings = PanelSettings.objects.get(user = self.request.user)
        except PanelSettings.DoesNotExist:
            p_settings = None

        if p_settings:
            try:
                panel_settings = json.loads(p_settings.settings)
            except json.decoder.JSONDecodeError:
                panel_settings = []
                
            from rai.panels.internals import REGISTERED_PANELS
            
            for ps in panel_settings:
                PKlass = REGISTERED_PANELS[ps['key']].__class__
                del ps['key']
                panels.append(PKlass(**ps, request = self.request))
                
        panels = panels + [EmptyPanel(1,1, -1)]

        i_panels = []
        row = []
        count = 0
        
        for panel in panels:
            if callable(panel):
                row.append(panel(request = self.request))
            else:
                row.append(panel)
            count += 1
            if count == 3:
                i_panels.append(row)
                row = []
                count = 0

        if count < 3:
            i_panels.append(row)
            
        return i_panels


    def get_context_data(self):
        context = super().get_context_data()
        context['panels'] = self.get_panels()
        return context

class LoginView(WALoginView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username_field'] = 'RUB-ID'
        return context
