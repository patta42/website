from .models import RAIPermission, RAIGroup
from .permissions import (
    DeletePermission, CreatePermission, EditPermission, ViewPermission,
    NonePermission
)

from django.db.models import Max
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

def _cache_permission(rid, user, permissions):
    perms = {}
    for p in permissions:
        perms[p['rai_id']] = p['value']
    _permission_cache.update({user: perms})        
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
        permissions = RAIPermission.objects.filter(
            group__in = staff.rai_group.all()
        ).order_by().values('rai_id').annotate(value = Max('value'))
        _cache_permission(id(request), staff.user.id, permissions)
        perm = _get_cached_permission(id(request), request.user.id, rai_id)
        
        if not perm:
            perm = NonePermission
        

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
