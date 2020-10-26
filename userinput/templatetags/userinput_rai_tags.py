import datetime

from django import template
from django.template.loader import render_to_string

from userdata.models import SafetyInstructionUserRelation
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

@register.simple_tag
def get_last_instruction( ruser, instruction ):
    qs = ruser.rubion_user_si.filter(instruction = instruction).order_by('-date') 
    if qs.count() > 0:
        return qs[0]
    return None

@register.simple_tag
def get_last_instruction_percentage(t, instruction):
    valid_for = instruction.is_valid_for * 365
    today = datetime.date.today()
    delta = (today - t).days
    rel = min(1,float(delta)/float(valid_for))
    return int(rel*100)

@register.simple_tag
def get_last_instruction_indicator_css(t, instruction):
    valid_for = instruction.is_valid_for * 365
    today = datetime.date.today()
    delta = (today - t).days
    rel = min(1,float(delta)/float(valid_for))
    if rel < .75:
        bgcolor = '00c000'
    elif rel < .9:
        bgcolor = 'c0c000'
    else:
        bgcolor = 'c00000'
        

    return 'background-color:#{};width:{}%'.format(bgcolor, rel*100)
