

from django.http import JsonResponse
from django.utils.html import mark_safe, format_html    

import json

from rai.settings.models import PanelSettings

def add_panel(request):
    if not request.is_ajax():
        pass
    else:
        if request.method == 'POST':
            try:
                p_settings = PanelSettings.objects.get(user = request.user)
            except PanelSettings.DoesNotExist:
                p_settings = PanelSettings(user = request.user)

            try:
                settings = json.loads(p_settings.settings)
            except json.decoder.JSONDecodeError:
                settings = []

            panel_id = request.POST.get('panelId', None)
            settings.append({
                'key' : panel_id 
            })
            p_settings.settings = settings
            p_settings.save()    
                
            
            from .internals import REGISTERED_PANELS
            
            # return the rendered panel
            panel = REGISTERED_PANELS.get(panel_id)

            
            
            return JsonResponse({
                'html' : mark_safe(panel.render())
            })
            
