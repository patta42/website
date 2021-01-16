from pprint import pprint

from .models import NotificationTemplate

from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage
from django.conf import settings as DJANGO_SETTINGS 

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver, Signal

from django.template import Template, Context
from django.template.loader import get_template


from inspect import getmembers, isfunction, getmodulename, getfile

from userinput.signals import (
    post_page_move, pre_page_move
)



from wagtail.core import hooks
from wagtail.core.models import Page, PageRevision
from wagtail.core.signals import (
    page_published, page_unpublished,
)

from website.models import SentMail



class NotificationTemplateMixin:
    template = None
    template_en = None
    template_name = None
    template_name_en = None
    identifier = None
    
    context_definition = {}

    @classmethod
    def register_template(Kls):
        """
        Adds the notification template to the database to allow
        editing.
        """
        
        try:
            NotificationTemplate.objects.get(notification_id = Kls.identifier)
        except NotificationTemplate.DoesNotExist:
            if not Kls.template_name:
                template_string = Kls.template
            else:
                template = get_template(Kls.template_name)
                template_string = template.template.source
            if not Kls.template_name_en:
                template_string_en = Kls.template_en or ""
            else:
                template_en = get_template(Kls.template_name_en)
                template_string_en = template.template.source

            
            nt = NotificationTemplate(
                notification_id = Kls.identifier,
                template = template_string,
                template_en = template_string_en
            )
            nt.save()

    def get_template(self, lang = 'de'):
        nt = NotificationTemplate.objects.get(notification_id = self.identifier)
        if lang == 'de':
            tpl = nt.template
        if lang == 'en':
            tpl = nt.template_en
        return '{{% language \'{lang}\' %}}{tpl}{{% endlanguage %}}'.format(lang=lang, tpl = tpl)
            
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
        tags2load = ['i18n']
        context = {}
        for key, definition in self.context_definition.items():
            tags2load.append(getmodulename(getfile(definition['tags'])))
            context.update({
                definition['prefix'] : kwargs.get(definition['prefix'], None)
            })
        template = '{{% load {} %}}{}'.format(' '.join(tags2load), template)
        tpl = Template(template)
        return tpl.render(Context(context))
        
    def render_preview(self, template, lang = 'de', **kwargs):
        render_kwargs = {}
        for key, definition in self.context_definition.items():
            pk = kwargs.get(definition['prefix'], None)
            if pk:
                query = self._get_query_from_definition(definition)
                render_kwargs.update({definition['prefix'] : query.get(pk = pk) })
        return self.render_template(
            '{{% language \'{lang}\' %}}{tpl}{{% endlanguage %}}'.format(tpl = template, lang = lang),
            **render_kwargs
        )
        
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
        if not hasattr(self, 'mails_to_send'):
            self.mails_to_send = []
            
        self.mails_to_send.append({
            'receivers' : receivers,
            'text' : text,
            'subject' : subject
        })

    def process(self):
        from rai.settings.internals import get_rai_setting
        use_rai_noties = get_rai_setting('rai.notifications.active')
        if use_rai_noties:
            use_rai_noties = use_rai_noties()
            
        for mailinfo in self.mails_to_send:
            mail = EmailMessage(
                mailinfo['subject'],
                mailinfo['text'],
                DJANGO_SETTINGS.RUBION_MAIL_FROM,
                mailinfo['receivers']
            )
            if DJANGO_SETTINGS.DEBUG or use_rai_noties.value == True:
                mail.send()
            SentMail.from_email_message(mail).save()
    
    
class RAINotification(NotificationTemplateMixin):
    title = None
    label = None
    help_text = None

    internal = False

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)
        self.kwargs_list = kwargs.keys()
    @classmethod
    def register(Kls, Event = None):
    #    super().register()
        Kls.register_template()
        Kls.register_with_wagtail()
        if Event:
            Event.add_callback(Kls.on_event)
        
    @classmethod
    def register_with_wagtail(Kls):
        @hooks.register('rai_notification')
        def register_notification():
            return Kls
        
    @classmethod
    def on_event(Kls, **kwargs):
        # initiate object
        print('\n\nEvent happend.\n\n')
        print('kwargs are')
        print(kwargs)
        instance = Kls(**kwargs)
        instance.prepare(**kwargs)
        instance.process()
        
class RAIEvent:
    '''
    An event is a change in the data, like a new project or a modified user, or an 
    expiring safety instruction or similar. Notifications are bound to an Event.

    Events are similar to Signals, but more detailed. 
    '''
    
    # the model which undergoes some changes
    model = None

    # an internal verbose name for the related model
    _verbose_name = None
    
    # the django signal that is emitted, if any
    signal = None

    # an event has an id
    identifier = None

    # an Event might have a description for explanation
    description = None

    # and a human-readable title
    title = None

    # the class-variable store for callbacks
    _callbacks = {}
    
    @property
    def verbose_name(self):
        return self._verbose_name or self.model._meta.verbose_name
    
    @classmethod
    def register(Kls):
        # if an Event is connected to a signal, register `signal_received` as receiver function
        # otherwise, do nothing special.
        if Kls.signal:
            @receiver(Kls.signal, sender = Kls.model, weak = False, dispatch_uid = Kls.identifier)
            def receiver_fnc(sender, **kwargs):
                instance = Kls()
                instance.signal_received(sender, **kwargs)
                
    @classmethod
    def add_callback(Kls, func, uid = None, **kwargs):
        '''
        adds the callback `func` to the event. To prevent multiple registration, set `uid` to 
        some unique string. Additional arguments beside the ones from the Event passed to the 
        callback should be given as kwargs
        '''
        KlsId = Kls.identifier
        callbacks = Kls._callbacks.get(KlsId, [])
        # prevent multiple registration 
        for cb in callbacks:
            if cb.uid and cb.uid == uid:
                return
        callbacks.append({
            'uid' : uid,
            'func' : func,
            'kwargs' : kwargs
        })
        Kls._callbacks[KlsId] = callbacks

        
    def signal_received(self, sender, **kwargs):
        # since Signals are more general than Events, an Event may not occur if a Signal is emitted
        # In general, this method calls the the `check` method (which has to be defined by each Event)
        # and if that returns True, emits the Event
        if self.check(**kwargs):
            self.emit(**kwargs)

                
    def get_emit_kwargs(self, **kwargs):
        # a method which processes the kwargs received by emit (which are usually the ones received
        # by `signal_received`) and generates the kwargs used by the Event.
        return kwargs
    
    def emit(self, **kwargs):
        # emits the Event. This can be called by `signal_received`, but also semi-manually for
        # example by a cron job or similar. The kwargs usually provide additional information
        # and are processed by `get_emit_kwargs` to generate the kwargs send by the Event
        event_kwargs = self.get_emit_kwargs(**kwargs)
        for cb in self.__class__._callbacks.get(self.identifier, []):
            cb['func'](**{ **cb['kwargs'], **event_kwargs})
        



class PageContentChangedEvent(RAIEvent):
    ''' 
    An event that listens to the page_published signal.

    It emits `old_instance`, `new_instance`, `user` and `changed_fields`
    '''
    signal = page_published

    # cache emit kwargs is a flag which indicates whether the kwargs are stored in self._emit_kwargs
    # once get_emit_kwargs has been called. Particularly useful to check the `changed_fields` kwarg
    # without doing the logic twice

    cache_emit_kwargs = False

    def check(self, **kwargs):
        # To distinguish between update and create, check if there is a previous revision
        try:
            kwargs['revision'].get_previous()
            return True
        except PageRevision.DoesNotExist:
            return False
        
    def get_emit_kwargs(self, **kwargs):
        cache = getattr(self, 'cache_emit_kwargs', False)
        if cache and hasattr(self, '_emit_kwargs'):
            return self._emit_kwargs
        
        ekw = {
            'new_instance' : kwargs['instance'],
            'user' : kwargs['revision'].user,
            'changed_fields' : []
        }
        prev = kwargs['revision'].get_previous() 
        old = prev.page.specific_class.from_json(prev.content_json)
            
        ekw['old_instance'] = old
        excluded_fields = [
            'first_published_at', 'last_published_at', 'latest_revision_created_at',
            'live_revision', 'page_ptr'
        ]
        
        for field in self.model._meta.fields:
            if field.name in excluded_fields:
                continue
            if getattr(ekw['old_instance'], field.name, None) != getattr(ekw['new_instance'], field.name, None):
                ekw['changed_fields'].append(field.name)

        if cache:
            self._emit_kwargs = ekw
        return ekw

            
        
class ObjectMovedEvent(RAIEvent):
    '''
    An Event that listens to `post_page_move`
    '''
    signal = post_page_move
    
def register_listener(Listener):
    listener = Listener()
    listener.register()

def register_listeners(lst):
    for l in lst:
        register_listener(l)

def register_notification(Notification, event = None):
    Notification.register(event)
