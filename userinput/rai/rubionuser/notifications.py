from .triggers import InactivatedTrigger, ActivatedTrigger

from django.db.models import Q

import datetime, dateutils
import logging

from rai.notifications.base import RAINotification
from random import randint

from userdata.models import StaffUser, SafetyInstructionsSnippet 
from userinput.models import RUBIONUser, WorkGroup
import userinput.templatetags.rubionuser_notification_tags as ru_tags
import userinput.templatetags.workgroup_notification_tags as wg_tags
import userdata.templatetags.staff_notification_tags as staff_tags
import userdata.templatetags.si_notification_tags as si_tags


def get_preview_users():
    return RUBIONUser.objects.active()

def get_wg_leaders():
    return get_preview_users().filter(is_leader = True)

def get_preview_staff():
    '''only show staff that has any permissions in RUBIONtail'''
    return StaffUser.objects.filter(rai_group__isnull = False).distinct().order_by('last_name')

class RUBIONUserNotification(RAINotification):
    '''
    A notification send to a RUBIONUser
    '''
    
    template_name = 'userinput/rubionuser/rai/notifications/rubionuser-changed.html'
    help_text = ''
    internal = False
    
    context_definition = {
        'user' : {
            'tags' : ru_tags,
            'label' : 'Nutzer',
            'prefix' : 'user',
            'preview_options_callback': get_preview_users
        }
    }

    def get_mail_kwargs(self):
        return { 'user' : self.new_instance }

    def prepare(self, **kwargs):
        language = self.new_instance.preferred_language or 'de'
        self.add_mail(
            receivers = [self.new_instance.email],
            text = self.render_template(self.get_template(lang = language), **self.get_mail_kwargs()),
            subject = self.get_subject(lang = language)
        )
        super().prepare(**kwargs)

class RUBIONUserReceivedKeyNotification(RUBIONUserNotification):
    title = 'Nutzer: Dem Nutzer wurde ein Schlüssel zugewiesen.'
    identifier = 'rubionuser.received_key'
    description = 'Wird versendet, wenn einem Nutzer ein Schlüssel zugewiesen wird.'
    template_name = 'userinput/rubionuser/rai/notifications/rubionuser-changed.html'
    help_text = ''



class RUBIONUserChangedNotification(RUBIONUserNotification):
    internal = True
    title = 'Nutzer: Nutzerdaten wurden geändert.'
    identifier = 'rubionuser.data_changed'
    description = 'Wird versendet, wenn sich die persönlichen Daten eines Nutzers geändert haben.'
    context_definition = {
        'staff' : {
            'tags' : staff_tags,
            'label' : 'Empfänger',
            'prefix' : 'staff',
            'preview_model' : StaffUser
        },
        ** RUBIONUserNotification.context_definition
    }
    


class RUBIONUserInactivateNotification(RUBIONUserNotification):
    identifier = 'rubionuser.inactivated_by_AG'
    description = 'Wird an den Nutzer versendet, wenn er durch die Gruppenleitung (oder eine von ihr beauftragte Person) inaktiviert wurde.'
    title = 'Nutzer: Nutzer wurde durch AG-Mitglied aus der Arbeitsgruppe entfernt.'

    context_definition = {
        ** RUBIONUserNotification.context_definition, 
        'iuser' : {
            'tags' : ru_tags,
            'label' : 'Nutzer, der die Inaktivierung veranlasst',
            'prefix' : 'iuser',
            'preview_options_callback': get_preview_users
        },
    }

    def get_mail_kwargs(self):
        kwargs = super().get_mail_kwargs()
        kwargs['iuser'] = self.user.rubionuser_set.get()
        return kwargs

class RUBIONUserInactivatedByRUBIONNotification(RUBIONUserNotification):
    identifier = 'rubionuser.inactivated_by_RUBION'
    description = 'Wird an den Nutzer versendet, wenn er durch das RUBION inaktiviert wurde.'
    title = 'Nutzer: Nutzer wurde durch RUBION inaktiviert.'
    context_definition = {
        ** RUBIONUserNotification.context_definition, 
        'staff' : {
            'tags' : staff_tags,
            'label' : 'Mitarbeiter, der die Inaktivierung veranlasst',
            'prefix' : 'staff',
            'preview_options_callback': get_preview_staff
        },
    }
    

    def get_mail_kwargs(self):
        kwargs = super().get_mail_kwargs()
        kwargs['staff'] = self.user.staffuser_set.get()
        return kwargs


class RUBIONUserReactivatedByRUBIONNotification(RUBIONUserNotification):
    identifier = 'rubionuser.reactivated'
    description = 'Wird an den Nutzer versendet, wenn er re-aktiviert wurde.'
    title = 'Nutzer: Ein inaktiver Nutzer wurde durch einen RUBION-Mitarbeiter re-aktiviert.'

    context_definition = {
        ** RUBIONUserNotification.context_definition, 
        'staff' : {
            'tags' : staff_tags,
            'label' : 'Mitarbeiter, der die Re-Aktivierung veranlasst',
            'prefix' : 'staff',
            'preview_options_callback': get_preview_staff
        },
    }
    def trigger_check(self):
        # check inactivating user...
        if self.changing_user.staffuser_set.count() > 0:
            return super().trigger_check()
        else:
            return False
        
    def get_mail_kwargs(self):
        return {
            'user' : self.new_instance,
            'staff' : self.changing_user.staffuser_set.get()
        }


class RUBIONUserChangedWorkGroupNotification(RUBIONUserNotification):
    identifier = 'rubionuser.changed_workgroup'
    signal = 'post_page_move'
    description = 'Wird an den Nutzer versendet, wenn er in eine andere AG verschoben wurde.'
    title = 'Nutzer: In andere AG verschoben.'
    context_definition = {
        ** RUBIONUserNotification.context_definition, 
        'staff' : {
            'tags' : staff_tags,
            'label' : 'Mitarbeiter, der die Verschiebung veranlasst',
            'prefix' : 'staff',
            'preview_options_callback': get_preview_staff
        },
        'old_wg' : {
            'tags' : wg_tags,
            'label' : 'alte AG',
            'prefix' : 'old_wg',
            'preview_model' : WorkGroup
        },
        'new_wg' : {
            'tags' : wg_tags,
            'label' : 'neue AG',
            'prefix' : 'new_wg',
            'preview_model' : WorkGroup
        }

    }

    def get_mail_kwargs(self):
        return {
            'user' : self.new_instance,
            'staff' : self.changing_user.staffuser_set.get(),
            'new_wg' : self.new_workgroup,
            'old_wg' : self.old_workgroup,
        }
    def trigger_check(self):
        return super().trigger_check() and self.old_workgroup != self.new_workgroup


class RUBIONUserChangedWorkGroupNotification2Leader(RUBIONUserNotification):
    identifier = 'rubionuser.changed_workgroup2leader'
    description = 'Wird an die AG-Verantwortlichen versendet, wenn ein Nutzer in diese AG verschoben wurde.'
    title = 'Nutzer: In andere AG verschoben (an die Verantwortlichen).'
    signal = 'post_page_move'
    
    context_definition = {
        'leader' : {
            'tags' : ru_tags,
            'label' : 'AG-Verantwortlicher',
            'prefix' : 'leader',
            'preview_options_callback': get_wg_leaders
            
        },
        ** RUBIONUserChangedWorkGroupNotification.context_definition
    }

    def process(self):
        leaders = self.new_workgroup.get_members().filter(
            Q(is_leader = True) | Q(may_add_members = True)
        )
        for leader in leaders:
            language = leader.preferred_language
            if not language:
                language = 'de'
            mail_kwargs = {
                'leader' : leader.specific,
                **self.get_mail_kwargs()
            }
            self.add_mail(
                receivers = [leader.email],
                text = self.render_template(self.get_template(lang = language), **mail_kwargs),
                subject = self.get_subject(lang = language)
            )
        super().process()

    def get_mail_kwargs(self):
        return {
            'user' : self.new_instance,
            'staff' : self.changing_user.staffuser_set.get(),
            'new_wg' : self.new_workgroup,
            'old_wg' : self.old_workgroup,
        }
    def trigger_check(self):
        return super().trigger_check() and self.old_workgroup != self.new_workgroup
    
    
class RUBIONUserSafetyInstructionNeverGivenNotification(RAINotification):
    identifier = 'rubionuser.si.never_given'
    description = 'Wird an einen Nutzer versendet, wenn eine Sicherheitsunterweisung erforderlich ist, der Nutzer diese aber noch nie erhalten hat. Frequenz: Alle zwei Wochen.'
    title = 'Nutzer: Sicherheitsunterweisung noch nie erhalten.'
    template_name = 'userinput/rubionuser/rai/notifications/rubionuser-changed.html'    
    context_definition = {
        'si' : {
            'tags' : si_tags,
            'label' : 'Unterweisungen',
            'prefix' : 'si',
            'preview_model': SafetyInstructionsSnippet
        
        },
        ** RUBIONUserNotification.context_definition
    }


    def prepare(self, **kwargs):
        self.add_mail(
            receivers = [self.user],
            text = self.render_template(
                self.get_template(lang = language),
                user = kwargs['user'],
                si = kwargs['instructions']
            ),
            subject = self.get_subject(lang = language)
        )

    
def _get_si(valid):
    # this is a not-so-nice (but funny!) workaround to allow a list (instead of a querset) 
    # as options for the preview. This list needs a get method (as for queryset.get(pk = ...))
    # let's make such a list:
    class ListWithGet(list):
        def get(self, **kwargs):
            pk = kwargs.get('pk', None)
            if not pk:
                # should through an error
                pass
            else:
                for o in self:
                    if o.pk == int(pk):
                        return o
    
    # the single items of the above list need a pk property and a __str__ method
    # and are lists themselves:

    class ListForPreview(list):
        def __init__(self, pk, title, lst = []):
            super().__init__(lst)
            self.pk = pk
            self.title = title
        def __str__(self):
            return self.title


    # just to have a nicer name in the preview option selector
    nums = ['Eine', 'Zwei', 'Drei']
    plural = ['', 'en', 'en']
    q = SafetyInstructionsSnippet.objects.all()

    # generate lists with one, two and three items
    max_obj = q.count() - 1
    opts = ListWithGet()
    for k in range(3):
        opts.append(
            ListForPreview(
                k, '{} zufällige Sicherheitsunterweisung{}'.format(nums[k], plural[k]),
                lst = [ {
                    'instruction' :  q[randint(0, max_obj)],
                    'valid_until' : valid
                } for i in range(k+1) ]
            ) 
        )
        
    return opts

def si_soon():
    return _get_si(datetime.datetime.now() + dateutils.relativedelta(weeks=+2))

def si_expired():
    return _get_si(datetime.datetime.now() + dateutils.relativedelta(weeks=-2))

def si_thisyear():
    return _get_si(datetime.datetime.now() + dateutils.relativedelta(months=+11))



class RUBIONUserSafetyInstructionExpiresSoonNotification(RUBIONUserSafetyInstructionNeverGivenNotification):
    identifier = 'rubionuser.si.expires_soon'
    description = 'Wird an einen Nutzer versendet, wenn eine Sicherheitsunterweisung bald (innerhalb der nächsten zwei Monate) abläuft. Frequenz: Alle zwei Wochen.'
    title = 'Nutzer: Sicherheitsunterweisung läuft bald ab.'
    context_definition = {
        ** RUBIONUserNotification.context_definition,
        'si' : {
            'tags' : si_tags,
            'label' : 'Liste der ablaufenden Unterweisungen',
            'prefix' : 'si',
            'preview_options_callback': si_soon
        }
    }

class RUBIONUserSafetyInstructionExpiredNotification(RUBIONUserSafetyInstructionNeverGivenNotification):
    identifier = 'rubionuser.si.expired'
    description = 'Wird an einen Nutzer versendet, wenn eine Sicherheitsunterweisung abgelaufen ist. Frequenz: Alle zwei Wochen, maximal drei.'
    title = 'Nutzer: Sicherheitsunterweisung abgelaufen.'
    context_definition = {
        ** RUBIONUserNotification.context_definition,
        'si' : {
            'tags' : si_tags,
            'label' : 'Liste der abgelaufenen Unterweisungen',
            'prefix' : 'si',
            'preview_options_callback': si_expired
        }
    }


class RUBIONUserSafetyInstructionExpiresThisYearNotification(RUBIONUserSafetyInstructionNeverGivenNotification):
    identifier = 'rubionuser.si.expires_thisyear'
    description = 'Wird an einen Nutzer versendet, wenn eine Sicherheitsunterweisung mit einer Gültigkeit von mehr als einem Jahr im kommenden Jahr abläuft. Frequenz: Alle drei Monate, maximal drei.'
    title = 'Nutzer: Sicherheitsunterweisung läuft dieses Jahr ab.'

    context_definition = {
        ** RUBIONUserNotification.context_definition,
        'si' : {
            'tags' : si_tags,
            'label' : 'Liste der ablaufenden Unterweisungen',
            'prefix' : 'si',
            'preview_options_callback': si_thisyear
        }
    }

    
