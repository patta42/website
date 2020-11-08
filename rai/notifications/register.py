from .edit_handlers import RAINotificationTemplateEditor
from .models import NotificationTemplate
from .views import render_template_preview

from django.urls import path

from rai.actions import ListAction, EditAction
from rai.base import RAIModelAdmin, RAIAdminGroup
from rai.default_views import EditView
from rai.edit_handlers import (
    RAICollectionPanel, RAIFieldPanel, RAICollapsablePanel, RAIObjectList,
    RAIPillsPanel
)

from wagtail.core import hooks

@hooks.register('register_rai_url')
def notifications_ulrs():
    return [
        path(
            'rai/notifications/render_template_preview/',
            render_template_preview,
            name = 'rai_notifications_render_preview'
        )
    ]

class RAINotificationEditView(EditView):
    template_name = 'rai/notifications/views/edit.html'

class RAINotificationListAction(ListAction):
    list_item_template = 'rai/notifications/views/list/item-in-list.html'
    
class RAINotificationEditAction(EditAction):
    edit_handler = RAIPillsPanel([
        RAICollapsablePanel([
            RAIFieldPanel('subject', label = "Betreff"),
            RAINotificationTemplateEditor(),
        ], heading = 'deutsch'),
        RAICollapsablePanel([
            RAIFieldPanel('subject_en', label = "Betreff"),
            RAINotificationTemplateEditor(lang = 'en')
        ], heading = 'englisch')
    ])

class RAINotificationTemplate(RAIModelAdmin):
    model = NotificationTemplate
    menu_icon_font = 'fas'
    menu_icon = 'file-code'
    menu_label = 'E-Mail-Vorlagen'
    editview = RAINotificationEditView
    group_actions = [
        RAINotificationListAction
    ]
    item_actions = [
        RAINotificationEditAction
    ]
    default_action = RAINotificationListAction
    
class RAINotificationsGroup(RAIAdminGroup):
    components = [
        RAINotificationTemplate
    ]
    menu_label = 'Benachrichtigungen'
