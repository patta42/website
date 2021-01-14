from pprint import pprint

from .internals import REGISTERED_NOTIFICATIONS

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.urls import reverse

from rai.edit_handlers import RAIFieldPanel, RAICollectionPanel

class RAINotificationTemplateField(RAIFieldPanel):
    object_template = 'rai/notifications/edit_handlers/template-field.html'

    
class RAINotificationContextField(RAIFieldPanel):
    object_template = 'rai/notifications/edit_handlers/template-context-field.html'
    preview_fields_template = 'rai/notifications/edit_handlers/template-context-field-preview-fields.html'
    def render(self):
        notification = REGISTERED_NOTIFICATIONS[self.instance.notification_id]
        if callable(notification):
            notification = notification()
        template_tags = notification.get_template_tags()
        return mark_safe(
            render_to_string(
                self.object_template,
                {
                    'notification_id' : self.instance.notification_id,
                    'template_tags' : template_tags
                }
            )
        )

    def render_preview_fields(self):
        notification = REGISTERED_NOTIFICATIONS[self.instance.notification_id]
        if callable(notification):
            notification = notification()
        preview_options = notification.get_preview_options()

        return mark_safe(
            render_to_string(
                self.preview_fields_template,
                {
                    'notification_id' : self.instance.notification_id,
                    'preview_options' : preview_options
                }
            )
        )

class RAINotificationTemplateEditor(RAICollectionPanel):
    template = 'rai/notifications/edit_handlers/template-editor.html'

    def __init__(self, lang = 'de', *args, **kwargs):
        super().__init__(*args, **kwargs)

        # lang might be None
        if not lang:
            lang = 'de'
            
        if lang == 'de':
            tpl_name = 'template'
        else:
            tpl_name = 'template' + '_' + lang
        self.lang = lang
        self.children = [
            RAINotificationContextField('notification_id'),
            RAINotificationTemplateField(tpl_name),
        ]

    def clone_kwargs(self): 
        kwargs = super().clone_kwargs()
        kwargs['lang'] = self.lang
        return kwargs

    def render_as_object(self):
        return self.render()
    def render_as_field(self):
        return self.render()
    
    def render(self):
        return mark_safe(
            render_to_string(
                self.template,
                {
                    'context':  self.children[0],
                    'template' : self.children[1],
                    'preview_url' : reverse('rai_notifications_render_preview'),
                    'notification_id' : self.instance.notification_id
                }
            )
        )

