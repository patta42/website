from .models import RAIPermission, RAIGroup
from userdata.models import StaffUser

def user_has_permission(request, rai_id, permission):
    if request.user.is_superuser:
        spy = request.GET.get('spy', None)
        if not spy:
            # superusers not acting as another user have all permissions
            return True
        else:
            staff = StaffUser.objects.get(pk = spy)
    else:
        staff = StaffUser.objects.get(user = request.user)
    
    perm = (RAIPermission.objects
            .filter(rai_id = rai_id, group__in = staff.rai_group.all())
            .order_by('-value').first())
    tf = False
    if perm:
        tf = perm.value >= permission.value

    return tf
