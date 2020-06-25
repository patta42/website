from django import template
from django.utils.html import format_html 
from courses.models import CourseAttendee

register = template.Library()

@register.simple_tag
def get_n_attendees(course):
    return CourseAttendee.objects.filter(related_course = course).count()

@register.simple_tag
def get_n_waitlist(course):
    return CourseAttendee.objects.filter(waitlist_course = course).count()

@register.filter
def format_student_id(sid):
    sid = str(sid)
    return format_html(
        '<span class="mr-1">{}</span>'+
        '<span class="mr-1">{}</span>'+
        '<span class="mr-1">{}</span>{}',
        sid[0:3], sid[3:6], sid[6:9], sid[9:12]
    )
