from django import template
from django.template.loader import render_to_string

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
    print(context)
    return render_to_string(
        'rai/views/default/list-filter-modal.html',
        {

        }
    )

@register.filter
def to_str(val):
    return str(val)

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


    
