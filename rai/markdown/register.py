from django.urls import reverse, path
from rai.markdown.views import markdown2html
from wagtail.core import hooks

@hooks.register('register_rai_url')
def rai_markdown_urls():
    return [
        path('rai/markdown/markdown2html/', markdown2html, name = 'rai_markdown_mardown2html')
    ]
