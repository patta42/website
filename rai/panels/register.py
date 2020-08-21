from .views import add_panel

from django.urls import path
from wagtail.core import hooks

@hooks.register('register_rai_url')
def rai_panel_urls():
    return [
        path('rai/panels/add/', add_panel, name = 'rai_panels_add_panel')
    ]
