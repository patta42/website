import datetime

from django import template
register = template.Library()

@register.inclusion_tag(
    'tags/connections.html'
)
def render_connections( user ):
    return {
        'user' : user
    }

@register.simple_tag
def get_last_instruction( staff, instruction ):
    qs = staff.staff_user_si.filter(instruction = instruction).order_by('-date') 
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
