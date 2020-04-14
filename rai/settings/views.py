from .models import AdminMenuSettings

from django.contrib.auth import get_user_model
from django.http import JsonResponse

import json

def admin_menu_settings(request):
    if request.method == 'POST' and request.is_ajax():
        pk = request.POST.get('user', None)
        if not pk:
            return JsonResponse({'error':'no user provided'}, status = 500)
        try:
            admin_settings =  AdminMenuSettings.objects.get(user__pk = pk)
        except AdminMenuSettings.DoesNotExist:
            user = get_user_model().objects.get(pk = pk)
            admin_settings = AdminMenuSettings(
                user = user
            )

        for item in ['group_order', 'item_labels', 'group_item_labels']:
            val = request.POST.get(item, None)
            if val:
                setattr(admin_settings, item, val)
            
        admin_settings.save()
        return JsonResponse({'status':'ok'})

        
