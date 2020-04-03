from django import template
from django.template.loader import render_to_string
from django.urls import reverse

from wagtail.core.models import Page, PageRevision

register = template.Library()


@register.simple_tag
def help_uri():
    return reverse('rai_help_start_ajax')

@register.simple_tag
def help(path, text):
    return render_to_string(
        'rai/help/help_link.html', {'path' : path, 'text' : text }
    )

