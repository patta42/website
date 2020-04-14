from pprint import pprint

from .internals import REGISTERED_NOTIFICATIONS

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from rai.edit_handlers import RAIFieldPanel, RAICollectionPanel

class RAINotificationTemplateField(RAIFieldPanel):
    object_template = 'rai/notifications/edit_handlers/template-field.html'

class RAINotificationContextField(RAIFieldPanel):
    object_template = 'rai/notifications/edit_handlers/template-context-field.html'
    preview_fields_template = 'rai/notifications/edit_handlers/template-context-field-preview-fields.html'
    def render(self):
        template_tags = REGISTERED_NOTIFICATIONS[self.instance.notification_id].get_template_tags()
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
        preview_options = REGISTERED_NOTIFICATIONS[self.instance.notification_id].get_preview_options()
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = [
            RAINotificationContextField('notification_id'),
            RAINotificationTemplateField('template'),
        ]

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
                    'template' : self.children[1]
                }
            )
        )

