from .views import admin_menu_settings

from django.urls import path
from wagtail.core import hooks

@hooks.register('register_rai_url')
def notifications_ulrs():
    return [
        path(
            'rai/settings/admin_menu_settings/',
            admin_menu_settings,
            name = 'rai_settings_admin_menu'
        )
    ]
