

from django.http import JsonResponse, HttpResponse
from django.utils.html import mark_safe, format_html    

import json

from rai.settings.models import PanelSettings

def _get_panel_settings_for_user(user):
    try:
        p_settings = PanelSettings.objects.get(user = user)
    except:
        p_settings = PanelSettings(user = user)
    return p_settings

def _parse_p_settings(p_settings):
    try:
        settings = json.loads(p_settings.settings)
    except json.decoder.JSONDecodeError:
        settings = []
    return settings

def change_settings(request):
    if not request.is_ajax():
        return HttpResponse(status = 405)
    else:
        if request.method == 'POST':
            keys = ['position', 'width', 'height', 'settings']
            p_settings = _get_panel_settings_for_user(request.user)
            settings = _parse_p_settings(p_settings)
            print('Anfrage: {}'.format(request.POST))
            print('Liste: {}'.format(request.POST.getlist('data')))
            print('\nvorher: {}'.format(settings))

            panel_id = request.POST.get('panelId', None)
            data = []
            if panel_id:
                data[0] = {'panelId' : panel_id}
                for k in keys:
                    v = request.POST.get(k, None)
                    if v:
                        data[0][k] = v
            else:
                data = request.POST.get('data', None)

            if not data:
                return HttpResponse(status = 400)
            else:
                data = json.loads(data)
            for item in data:
                panel_setting = None
                for setting in settings:
                    if setting['key'] == item.get('panelId'):
                        panel_setting = setting
                        break
                if not panel_setting:
                    panel_setting = {'key':item.get('panelId')}
                for k in keys:
                    v = item.get(k, None)
                    if v:
                        panel_setting[k] = v

            p_settings.settings = json.dumps(settings)
            p_settings.save()
            return JsonResponse({'status' : 200})
                
def add_panel(request):
    if not request.is_ajax():
        return HttpResponse(status = 405)
        
    else:
        if request.method == 'POST':
            p_settings = _get_panel_settings_for_user(request.user)
            settings = _parse_p_settings(p_settings)
            panel_id = request.POST.get('panelId', None)
            if not panel_id:
                return HttpResponse(status = 400)
                
            position = request.POST.get('position', None) or len(settings)+1
            settings.append({
                'key' : panel_id,
                'position' : position
            })
            p_settings.settings = settings
            p_settings.save()    
                
            
            from .internals import REGISTERED_PANELS
            
            # return the rendered panel
            panel = REGISTERED_PANELS.get(panel_id)

            return JsonResponse({
                'registered' : ','.join(REGISTERED_PANELS.keys()),
                'html' : mark_safe(panel.__class__(request = request).render()),
                'panelId' : panel_id
            })
            
def remove_panel(request):
    if not request.is_ajax():
        return HttpResponse(status = 405)
        
    else:
        if request.method == 'POST':
            p_settings = _get_panel_settings_for_user(request.user)
            settings = _parse_p_settings(p_settings)
            panel_id = request.POST.get('panelId', None)
            if not panel_id:
                return HttpResponse(status = 400)
            newsettings = []
            position = 0
            for s in settings:
                if s['key'] != panel_id:
                    s['position'] = position
                    newsettings.append(s)
                    position += 1
            p_settings.settings = newsettings
            p_settings.save()
            return JsonResponse({
                'status' : 200,
                'panelId' : panel_id
            })
            
