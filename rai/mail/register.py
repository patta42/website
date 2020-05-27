from .views import EMailView, fetch_mail_list
from .collections import RAIMailFileCollection
from django.urls import path

from wagtail.core import hooks
from rai.files.base import register_collection

register_collection(RAIMailFileCollection)

@hooks.register('register_rai_url')
def rai_mail_urls():
    return [
        path('rai/mail/', EMailView.as_view(), name = 'rai_mail_compose'),
        path('rai/mail/fetch_list/', fetch_mail_list, name='rai_mail_fetch_list')
    ]
