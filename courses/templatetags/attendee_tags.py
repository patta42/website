from django import template

register = template.Library()

@register.filter
def at_last_name(obj):
    '''Nachname'''
    return obj.last_name

@register.filter
def at_first_name(obj):
    '''Vorname'''
    return obj.first_name

@register.filter
def at_full_academic_name(obj):
    '''Vor- und Nachname inkl. akademischer Titel (automatisch übersetzt)'''
    if obj.academic_title:
        return '{} {} {}'.format(
            obj.get_academic_title_display(),
            obj.first_name,
            obj.last_name
        )
    else:
        return '{} {}'.format(
            obj.first_name,
            obj.last_name
        )

@register.filter
def course_title(obj):
    '''Titel des Kurses'''
    return obj.related_course.get_parent().specific.title_trans

@register.filter
def course_date(obj):
    '''Datum des Kurses (bei mehreren Tagen start – ende)'''
    course = obj.related_course
    if course.end:
        return '{} – {}'.format(
            course.start.strftime('%d. %m. %Y'),
            course.end.strftime('%d. %m. %Y')
        )
    else:
        return course.start.strftime('%d. %m. %Y')

@register.filter
def course_start(obj):
    '''Start-Datum des Kurses'''
    return obj.related_course.start.strftime('%d. %m. %Y')

@register.filter
def course_end(obj):
    '''End-Datum des Kurses (wenn vorhanden)'''
    if obj.related_course.end:
        return obj.related_course.end.strftime('%d. %m. %Y')
    else:
        None

@register.filter
def result(obj):
    '''Note'''
    return obj.result

@register.filter
def result_2nd(obj):
    '''Note der Nachklausur'''
    return obj.result_2nd

@register.filter
def student_id(obj):
    '''Matrikelnummer (wenn Student, sonst leer)'''
    obj = obj.specific
    return getattr(obj, 'student_id', '')
