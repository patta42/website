from django import template

register = template.Library()

@register.filter
def ru_last_name(obj):
    '''Nachname'''
    return obj.name_db

@register.filter
def ru_first_name(obj):
    '''Vorname'''
    return obj.first_name_db

@register.filter
def ru_full_academic_name(obj):
    '''Vor- und Nachname inkl. akademischer Titel (automatisch übersetzt)'''
    if obj.academic_title:
        return '{} {} {}'.format(
            obj.get_academic_title_display(),
            obj.first_name,
            obj.last_name
        )
