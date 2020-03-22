import datetime


from django import template
from django.template.loader import render_to_string

from userinput.models import RUBIONUser

register = template.Library()

@register.simple_tag
def workgroup_render_members(wg):
    td = datetime.datetime.today()
    active_users = RUBIONUser.objects.descendant_of(wg).active()
    inactive_users = RUBIONUser.objects.descendant_of(wg).inactive()
    return render_to_string(
        'userinput/workgroup/rai/list/group-members-in-list.html',
        {
            'active_users' : active_users,
            'inactive_users' : inactive_users
        }
    )
