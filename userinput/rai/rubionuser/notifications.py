from .triggers import InactivatedTrigger, ActivatedTrigger

from django.db.models import Q

from rai.notifications.base import RAINotification

from userdata.models import StaffUser 
from userinput.models import RUBIONUser, WorkGroup
import userinput.templatetags.rubionuser_notification_tags as ru_tags
import userinput.templatetags.workgroup_notification_tags as wg_tags
import userdata.templatetags.staff_notification_tags as staff_tags


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
