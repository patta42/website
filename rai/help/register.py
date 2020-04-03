from django.urls import path, re_path, include

from rai.help.views import AjaxHelpView

from wagtail.core import hooks

@hooks.register('register_rai_url')
def rai_help_urls():
    return [
        path('rai/help-ajax/', include(
            [
                path('<str:hp>/', AjaxHelpView.as_view(), name = 'rai_help_page_ajax'),
                path('', AjaxHelpView.as_view(), name = 'rai_help_start_ajax')

            ]
        ))
    ]
                                 
