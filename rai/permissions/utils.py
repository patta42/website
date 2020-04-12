from .models import RAIPermission, RAIGroup
from .permissions import (
    DeletePermission, CreatePermission, EditPermission, ViewPermission,
    NonePermission
)
from userdata.models import StaffUser

_permission_cache = {}
_permission_cache_requests = {}

def _get_cached_permission(rid, user, rai_id):
    cached_rid = _permission_cache_requests.get(user, None)
    if not cached_rid or cached_rid != rid:
        _permission_cache.pop(user, None)
        return None
    
    cached_user_perms = _permission_cache.get(user, None)
    if not cached_user_perms:
        return None
    return cached_user_perms.get(rai_id, None)

def _cache_permission(rid, user, rai_id, value):
    perm = {rai_id : value}
    cached_user_perms = _permission_cache.get(user, None)
    if not cached_user_perms:
        _permission_cache.update({user: perm})
    else:
        cached_perm = cached_user_perms.get(rai_id, None)
        if not cached_perm:
            _permission_cache[user].update(perm)
    _permission_cache_requests.update({user:rid})
    
def user_has_permission(request, rai_id, permission):
    perm = None
    staff = None
    if request.user.is_superuser:
        spy = request.GET.get('spy', None)
        if not spy:
            # superusers not acting as another user have all permissions
            return True
        else:
            staff = StaffUser.objects.get(pk = spy)
            perm = _get_cached_permission(id(request), staff.user.id, rai_id)
    else:
        perm = _get_cached_permission(id(request), request.user.id, rai_id)
            
    if not perm and not staff:
        staff = StaffUser.objects.get(user = request.user)
    if not perm:

        perm = (RAIPermission.objects
                .filter(rai_id = rai_id, group__in = staff.rai_group.all())
                .order_by('-value').first())
        if not perm:
            perm = NonePermission
        _cache_permission(id(request), staff.user.id, rai_id, perm.value)

    try:
        value = perm.value
    except AttributeError:
        value = perm
        
    tf = False
    if perm:
        tf = value >= permission.value

    return tf

def user_can_view(request, rai_id):
    return user_has_permission(request, rai_id, ViewPermission)
def user_can_create(request, rai_id):
    return user_has_permission(request, rai_id, CreatePermission)
def user_can_edit(request, rai_id):
    return user_has_permission(request, rai_id, EditPermission)
def user_can_delete(request, rai_id):
    return user_has_permission(request, rai_id, DeletePermission)
