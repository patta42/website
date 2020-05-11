from pprint import pprint as pp

from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

import random
import string
from wagtail.core.models import Page, PageRevision

register = template.Library()

@register.simple_tag( takes_context = True )
def render_object_in_list(context, obj, tpl, visible_fields):
    if tpl is None:
        tpl = 'rai/views/default/default-list-item.html'

    page_revision = None
    if issubclass(obj.__class__, Page):
        page_revision = PageRevision.objects.filter(page = obj).order_by('-created_at').first()
        

    return render_to_string(
        tpl,
        {
            'object' : obj,
            'last_revision':page_revision, 
            'visible_fields' : visible_fields,
            'item_actions' : context['item_actions']
        }
    )
        

@register.simple_tag( takes_context = True )
def render_list_filters(context):
    return render_to_string(
        'rai/views/default/list-filter-modal.html',
        {

        }
    )


@register.filter
def to_str(val):
    return str(val)

@register.filter
def tags2class(val):
    if val == 'debug':
        val = 'info'
    elif val == 'error':
        val = 'danger'
    return val


@register.filter
def rai_render_with_errors(bound_field, label):
    """
    Usage: {{ field|render_with_errors }} as opposed to {{ field }}.
    If the field (a BoundField instance) has errors on it, and the associated widget implements
    a render_with_errors method, call that; otherwise, call the regular widget rendering mechanism.
    """
    widget = bound_field.field.widget
    kwargs = { 'attrs' : {'id': bound_field.auto_id}}
    if hasattr(widget, 'requires_label') and widget.requires_label:
        kwargs.update({'label' : label})
    if bound_field.errors and hasattr(widget, 'render_with_errors'):
        kwargs.update({'errors': bound_field.errors})
        return widget.render_with_errors(
            bound_field.html_name,
            bound_field.value(),
            **kwargs

        )
    else:
        return widget.render(
            bound_field.html_name,
            bound_field.value(),
            **kwargs
        )



@register.filter
def render_disabled(bound_field):
    widget = bound_field.field.widget
    if hasattr(widget, 'render_disabled'):
        return widget.render_disabled(
            bound_field.html_name,
            bound_field.value(),
            attrs={'id': bound_field.auto_id},
        )
    else:
        return bound_field.as_widget()

@register.filter
def widget_requires_label(bound_field):
    return bound_field.field.widget.requires_label or False

@register.simple_tag
def rand_str():
    return ''.join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(10) 
    )


@register.filter
def pprint(obj):
    print('Output is:')
    try:
        pp(obj.__dict__)
    except AttributeError:
        pp(obj)
    return ""


@register.simple_tag(takes_context = True)
def show_for_instance(context, action, instance):
    if instance == True:
        return True

    request = context.get('request', None)
    return action['show_for_instance'](instance, request)

@register.filter
def save_htmldiff(change):
    try:
        return change.htmldiff()

    except Exception as e:
        return mark_safe("An dieser Stelle tritt ein Problem beim Vergleich der Werte auf. Das ist ein Fehler, der gemeldet werden sollte. Der Fehler lautete im Einzelnen:<br/><strong>{}:</strong> {}".format(type(e).__name__, str(e)))
