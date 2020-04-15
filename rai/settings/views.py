from pprint import pprint

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
        user_settings = admin_settings.as_dict()

        # group order can be overrideen
        group_order = request.POST.get('group_order', None)
        if group_order:
            user_settings['group_order'] = group_order


        for key in ['item_labels', 'group_item_labels']:
            labels = request.POST.get(key, None)
            if labels:
                labels = json.loads(labels)
                user_settings[key].update(labels)

        admin_settings.update(user_settings)
        admin_settings.save()
        return JsonResponse({'status':'ok'})

        
