from rai.notifications.base import RAINotification

# Notifications to the central radiation safety (CRS) officer

import userdata.templatetags.staff_notification_tags as staff_tags

from userinput.rai.rubionuser.notifications import (
    RUBIONUserNotification, get_preview_staff, get_preview_users
)

from userinput.rai.rubionuser.triggers import InactivatedTrigger

import userinput.templatetags.rubionuser_notification_tags as ru_tags

class CRSNotification(RUBIONUserNotification):
    internal = False
    template_name = 'userinput/rubionuser/rai/notifications/rubionuser-changed.html'
    help_text = ''
    context_definition = {
        'user' : {
            'tags' : ru_tags,
            'label' : 'Nutzer',
            'prefix' : 'user',
            'preview_options_callback': get_preview_users
        },
        'staff' : {
            'tags' : staff_tags,
            'label' : 'Mitarbeiter, der das Dosimeter eingetragen hat.',
            'prefix' : 'staff',
            'preview_options_callback': get_preview_staff
        },
    }


    
    def get_crs_mail(self):
        from rai.settings.internals import get_rai_setting
        return get_rai_setting('centralradiation.email')().value
    
    def add_mail(self, text, subject):
        super().add_mail(
            receivers = [self.get_crs_mail()],
            text = text,
            subject = subject
        )
    def process(self):
        self.add_mail(
            text = self.render_template(
                self.get_template(lang = 'de'),
                user = self.new_instance,
                staff = self.changing_user.staffuser_set.get(),
            ),
            subject = self.get_subject(lang = 'de')
        )
        super().process()

    
class CRSNewDosemeter(CRSNotification):
    identifier = 'crs.new-dosemeter'
    description = 'Wird an den zentralen Strahlenschutz versendet, wenn ein Nutzer ein offizielles Dosimeter benötigt.'
    title = 'Zentraler Strahlenschutz: Nutzer benötigt Dosimeter.'

    def trigger_check(self):
        return (
            super().trigger_check() and 
            self.new_instance.dosemeter == self.new_instance.OFFICIAL_DOSEMETER and
            self.old_instance.dosemeter != self.new_instance.OFFICIAL_DOSEMETER 
        )


class CRSNoDosemeter(CRSNotification):
    identifier = 'crs.no-dosemeter'
    description = 'Wird an den zentralen Strahlenschutz versendet, wenn ein Nutzer kein offizielles Dosimeter mehr benötigt.'
    title = 'Zentraler Strahlenschutz: Nutzer benötigt kein Dosimeter mehr.'

    def trigger_check(self):
        return (
            super().trigger_check() and 
            self.new_instance.dosemeter != self.new_instance.OFFICIAL_DOSEMETER and
            self.old_instance.dosemeter == self.new_instance.OFFICIAL_DOSEMETER 
        )
        
class CRSUserInactivated(InactivatedTrigger, CRSNotification):
    identifier = 'crs.user-inactivated'
    description = 'Wird an den zentralen Strahlenschutz versendet, wenn ein Nutzer mit einem offiziellen Dosimeter inaktiviert wird.'
    title = 'Zentraler Strahlenschutz: Nutzer inaktiviert.'
    
    def trigger_check(self):
        return (
            super().trigger_check() and
            self.new_instance.dosemeter == self.new_instance.OFFICIAL_DOSEMETER
        )
