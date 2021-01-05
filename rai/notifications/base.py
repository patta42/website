from pprint import pprint

from .models import NotificationTemplate

from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage
from django.conf import settings as DJANGO_SETTINGS 
from django.db.models.signals import pre_save, post_save
from django.template import Template, Context
from django.template.loader import get_template


from inspect import getmembers, isfunction, getmodulename, getfile

from userinput.signals import (
    post_page_move, pre_page_move
)

from wagtail.core import hooks
from wagtail.core.models import Page 
from wagtail.core.signals import (
    page_published, page_unpublished,
)

from website.models import SentMail

class RAIListener:
    model = None
    identifier = None
    signal = None
    needs_old_instance = True
    old_instance = None

    
    def register(self):
        self.register_signal()
        
    def register_signal(self, weak = True):
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
        if self.signal == 'pre_page_move':
            signal = pre_page_move
        if self.signal == 'post_page_move':
            signal = post_page_move
            
        if signal:
            signal.connect(
                self.signal_received, sender=self.model,
                dispatch_uid = self.identifier,
                weak = weak
            )

    def signal_received(self, **kwargs):
        self.new_instance = kwargs['instance']
        self.signal_kwargs = kwargs 
        if issubclass(self.new_instance.__class__, Page):
            self.new_instance = self.new_instance.specific
        if self.needs_old_instance:
            if self.signal == 'page_published':
                revisions = self.new_instance.revisions.order_by('-created_at')
                self.old_instance = revisions[1].as_page_object()
                self.changing_user = revisions[0].user
            elif self.signal in  ['pre_page_move', 'post_page_move']:
                self.old_workgroup = kwargs['parent_page_before'].get_parent().specific
                self.new_workgroup = kwargs['parent_page_after'].get_parent().specific
            else:
                self.old_instance = self.model.objects.get(pk = self.new_instance.pk)
            if self.signal == 'post_page_move':
                revisions = self.new_instance.revisions.order_by('-created_at')
                self.changing_user = revisions[0].user
        if self.trigger_check():
            self.process()

    def trigger_check(self):
        """
        trigger_check is called to decide whether the listener should
        execute self.process()

        this method reads the corresponding setting, checks if django runs in debug mode and
        returns True or False, accordingly. Subclasses should call this and implememnt their 
        own logic.
        """
        if DJANGO_SETTINGS.DEBUG:
            return True
        
        from .register import UseRAINotifications
        setting =  UseRAINotifications()
        return setting.value 
        
        
    def process(self):
        # subclasses should implement this
        pass

class RAIFieldChangedListenerMixin:
    fields = []

    def trigger_check(self):
        if super().trigger_check():
            for field in self.fields:
                old = getattr(self.old_instance, field)
                new = getattr(self.new_instance, field)
                if  old != new: 
                    return True
        return False
                
class NotificationTemplateMixin:
    template = None
    template_en = None
    template_name = None
    template_name_en = None
        
    context_definition = {}
    mails_to_send = []
    
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

    def get_template(self, lang = 'de'):
        nt = NotificationTemplate.objects.get(notification_id = self.identifier)
        if lang == 'de':
            return nt.template
        if lang == 'en':
            return nt.template_en
    def get_subject(self, lang = 'de'):
        nt = NotificationTemplate.objects.get(notification_id = self.identifier)
        if lang == 'de':
            return nt.subject
        if lang == 'en':
            return nt.subject_en
    def _get_query_from_definition(self, definition):
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
                    '  \'preview_options_callback\' : <callback> '
                    'entry.'
                )
        return query

    def render_template(self, template, **kwargs):
        tags2load = []
        context = {}
        for key, definition in self.context_definition.items():
            tags2load.append(getmodulename(getfile(definition['tags'])))
            context.update({
                definition['prefix'] : kwargs.get(definition['prefix'], None)
            })
        template = '{{% load {} %}}{}'.format(' '.join(tags2load), template)
        tpl = Template(template)
        return tpl.render(Context(context))
        
    def render_preview(self, template, **kwargs):
        render_kwargs = {}
        for key, definition in self.context_definition.items():
            pk = kwargs.get(definition['prefix'], None)
            if pk:
                query = self._get_query_from_definition(definition)
                render_kwargs.update({definition['prefix'] : query.get(pk = pk) })
        return self.render_template(template, **render_kwargs)
        
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
            query = self._get_query_from_definition(definition)
            options.update({
                definition['label'] : {
                    'prefix' : definition['prefix'],
                    'options' : [(o.pk, o) for o in query]
                }
            })
        return options

    def add_mail(self, receivers, text, subject):
        self.mails_to_send.append({
            'receivers' : receivers,
            'text' : text,
            'subject' : subject
        })

    def process(self):
        for mailinfo in self.mails_to_send:
            mail = EmailMessage(
                mailinfo['subject'],
                mailinfo['text'],
                DJANGO_SETTINGS.RUBION_MAIL_FROM,
                mailinfo['receivers']
            )
            mail.send()
            SentMail.from_email_message(mail).save()
    
    
class RAINotification(NotificationTemplateMixin, RAIListener):
    title = None
    label = None
    help_text = None
    

    internal = False
    
    def register(self):
        super().register()
        self.register_template()
        self.register_with_wagtail()


    def register_with_wagtail(self):
        @hooks.register('rai_notification')
        def register_notification():
            return self

    

    
def register_listener(Listener):
    listener = Listener()
    listener.register()
