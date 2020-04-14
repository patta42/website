from rai.notifications.base import RAINotification
from userdata.models import StaffUser 
from userinput.models import RUBIONUser
import userinput.templatetags.rubionuser_notification_tags as ru_tags
import userdata.templatetags.staff_notification_tags as staff_tags

def get_preview_users():
    return RUBIONUser.objects.active()

class RUBIONUserChangedNotification(RAINotification):
    model = RUBIONUser
    signal = 'page_published'
    internal = True
    title = 'Nutzer: Nutzerdaten wurden geändert.'
    identifier = 'rubionuser.data_changed'
    description = 'Wird versendet, wenn sich die persönlichen Daten eines Nutzers geändert haben.'
    template_name = 'userinput/rubionuser/rai/notifications/rubionuser-changed.html'
    help_text = ''
    context_definition = {
        'staff' : {
            'tags' : staff_tags,
            'label' : 'Empfänger',
            'prefix' : 'staff',
            'preview_model' : StaffUser
        },
        'user' : {
            'tags' : ru_tags,
            'label' : 'Geänderter Nutzer',
            'prefix' : 'user',
            'preview_options_callback': get_preview_users
        }
    }
