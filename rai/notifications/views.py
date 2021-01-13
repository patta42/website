from .internals import REGISTERED_NOTIFICATIONS

from django.http import JsonResponse
from django.template import TemplateSyntaxError

def render_template_preview(request):
    if request.method == 'POST' and request.is_ajax():
        notification = REGISTERED_NOTIFICATIONS[request.POST['notification_id']]
        if callable(notification):
            notification = notification()
        kwargs = {}
        for key, definition in notification.context_definition.items():
            pk = request.POST.get(definition['prefix'], None)
            if pk:
                kwargs.update({definition['prefix']: pk})
        try:
            preview = notification.render_preview(request.POST['template'], **kwargs)
            return JsonResponse({
                'status' : 200,
                'preview': preview
            })
        except TemplateSyntaxError as e:
            return JsonResponse({
                'status' : 500,
                'error' : e.template_debug['message']
            })
        
