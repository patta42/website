from pprint import pprint

from .models import NotificationTemplate

from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import pre_save, post_save
from django.template.loader import get_template

from inspect import getmembers, isfunction

from wagtail.core import hooks
from wagtail.core.models import Page 
from wagtail.core.signals import page_published, page_unpublished


class RAIListener:
    model = None
    identifier = None
    signal = None
    needs_old_instance = True
    old_instance = None

    def register(self):
        self.register_signal()
        
    def register_signal(self):
        """
        Registers the signal
        """
        signal = None
        if self.signal == 'pre_save':
            signal = pre_save
        if self.signal == 'post_save':
            signal = post_save
        if self.signal == 'page_published':
            signal = page_published
        if self.signal == 'page_unpublished':
            signal = page_unpublished
        if signal:
            print('Registering signal')
            signal.connect(
                self.signal_received, sender=self.model,
                dispatch_uid = self.identifier
            )

    def signal_received(self, **kwargs):
        self.new_instance = kwargs['instance']
        if issubclass(self.new_instance.__class__, Page):
            self.new_instance = self.new_instance.specific
        if self.needs_old_instance:
            if self.signal == 'page_published':
                revisions = self.new_instance.revisions.order_by('-created_at')
                self.old_instance = revisions[1].as_page_object()
            else:
                self.old_instance = self.model.objects.get(pk = self.new_instance.pk)
        if self.trigger_check():
            self.process()

    def trigger_check(self):
        """
        trigger_check is called to decide whether the listener should
        execute self.process()

        subclasses should implement this and return True or False
        """
        pass
        
    def process(self):
        # subclasses should implement this
        pass

class RAIFieldChangedListenerMixin:
    fields = []

    def trigger_check(self):
        for field in self.fields:
            old = getattr(self.old_instance, field)
            new = getattr(self.new_instance, field)
            if  old != new: 
                return True
        return False
                

    
class RAINotification(RAIListener):
    title = None
    label = None
    help_text = None
    template = None
    template_en = None
    template_name = None
    template_name_en = None
    
    context_definition = {}

    internal = False
    

    def register(self):
        super().register()
        self.register_template()
        self.register_with_wagtail()
    def register_template(self):
        """
        Adds the notification template to the database to allow
        editing.
        """
        
        try:
            NotificationTemplate.objects.get(notification_id = self.identifier)
        except NotificationTemplate.DoesNotExist:
            if not self.template_name:
                template_string = self.template
            else:
                template = get_template(self.template_name)
                template_string = template.template.source
            if not self.template_name_en:
                template_string_en = self.template_en or ""
            else:
                template_en = get_template(self.template_name_en)
                template_string_en = template.template.source

            
            nt = NotificationTemplate(
                notification_id = self.identifier,
                template = template_string,
                template_en = template_string_en
            )
            nt.save()

    def register_with_wagtail(self):
        @hooks.register('rai_notification')
        def register_notification():
            return self

    def get_template_tags(self):
        context_tags = {}
        for key, definition in self.context_definition.items():
            tags = []
            for fnc in getmembers(definition['tags'], isfunction):
                tags.append((fnc[1].__doc__, fnc[0]))
            context_tags.update({
                definition['label'] : {
                    'tags' : tags,
                    'prefix' : definition['prefix']
                }
            })
        return context_tags
    
    def get_preview_options(self):
        options = {}
        for key, definition in self.context_definition.items():
            # if we have a callback, use that
            cb = definition.get('preview_options_callback', None)
            if cb:
                query = cb()
            else:
                model = definition.get('preview_model', None)
                if model:
                    query = model.objects.all()
                else:
                    raise ImproperlyConfigured(
                        'Every entry in the context definition of a RAINotification '
                        'needs either a '
                        '  \'preview_model\' : <model> or a '
                        '  \'preview_options_callback\' : <callback>'
                        'entry.'
                    )
            options.update({
                definition['label'] : {
                    'prefix' : definition['prefix'],
                    'options' : [(o.pk, o) for o in query]
                }
            })
        return options
        
def register_listener(Listener):
    listener = Listener()
    listener.register()
