from .internals import REGISTERED_NOTIFICATIONS

from django.http import JsonResponse


def render_template_preview(request):
    if request.method == 'POST' and request.is_ajax():
        notification = REGISTERED_NOTIFICATIONS[request.POST['notification_id']]
        kwargs = {}
        for key, definition in notification.context_definition.items():
            pk = request.POST.get(definition['prefix'], None)
            if pk:
                kwargs.update({definition['prefix']: pk})
        
        return JsonResponse({
            'preview': notification.render_preview(request.POST['template'], **kwargs)
        })
