from django.template.loader import render_to_string
from django.utils.html import mark_safe

from wagtail.core import hooks

class FrontPanel:
    template = None
    max_cols = 1
    max_rows = 1
    min_rows = 1
    min_cols = 1
    pos_x = 1
    pos_y = 1
    title = ''
    identifier = 'rai.basefrontpanel'
    multiple_allowed = False
    
    def __init__(self, rows = 1, cols = 1, position = None, request = None):
        self.rows = rows
        self.cols = cols
        self.position = position
        self.request = request
    
    def get_context(self):
        context = {
            'width' : self.cols,
            'height' : self.rows,
            'position' : self.position or '0',
            'max_width' : self.max_cols,
            'max_height' : self.max_rows,
            'min_width' : self.min_cols,
            'min_height' : self.min_rows
        }
        return context
    
    def render(self):
        return mark_safe(render_to_string(self.template, self.get_context()))

    def to_html(self):
        return self.render()
    
    def register(self):
        @hooks.register('rai_front_panel')
        def panel_registration():
            return {self.identifier : self}


class EmptyPanel(FrontPanel):
    identifier = 'rai.emptypanel'
    template = 'rai/panels/empty.html'

    def get_available_panels(self):
        from .internals import REGISTERED_PANELS
        panels = []
        for k, panel in REGISTERED_PANELS.items():
            panels.append({'key':k, 'title':panel.title, 'desc':panel.desc})

        return panels
    
    def get_context(self):
        context = super().get_context()
        context['available_panels'] = self.get_available_panels()

        return context

def register_panel(Panel):
    panel = Panel()
    panel.register()

def register_panels(PanelList):
    for P in PanelList:
        register_panel(P)
