from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _l


from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register)
from wagtail.core import hooks

from .models import SentMail, BugOrWish



@hooks.register('insert_editor_css')
def editor_css():
    return format_html(
        '<link rel="stylesheet" href="{}">',
        static('css/admin/editor-changes.css')
    )


class SentMailModelAdmin(ModelAdmin):
    model = SentMail
    menu_label = _l('Sent Mails')
    menu_icon = ' icon-fa-envelope fa'  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    list_display = ('to', 'subject', 'sent_at')
    search_fields = ('to','subject',)
    inspect_view_enabled=True
    inspect_view_fields = ['sender', 'sent_at', 'to', 'subject', 'body']
    inspect_view_extra_css = ['css/admin/sent-mail-inspect.css']

modeladmin_register(SentMailModelAdmin)

class BugOrWishModelAdmin( ModelAdmin ):
    model = BugOrWish
    menu_label = _l('Bugs/Wishes')
    menu_icon = ' icon-fa-bug fa'
    list_display = ('_title', '_description')
    list_filter = ('closed', )
    def _title ( self, obj ):
        if obj.closed:
            return mark_safe('<del>{}</del>'.format(obj.title))
        else:
            return obj.title

    def _description ( self, obj ):
        return mark_safe(obj.description)
    
modeladmin_register( BugOrWishModelAdmin )
