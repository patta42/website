from django.utils.translation import ugettext_lazy as _l

from wagtail.core import hooks

class RAINothingPermission:
    """
    This is a permission meant as a abstract base, since any valid user
    is allowed to do nothing.
    """
    key = 'nothing'
    score = 0
    label = _l('Users can do nothing')
    
    def user_has_perm(self, obj, user):
        # superuser has all permissions
        if user.is_superuser:
            return True

        if not (user.is_staff and user.is_active):
            return False

        return check_permission(self, obj, user)

    def check_permission(self, obj, user):
        # Since any user has at least no permission, this is always true
        
        return True
        
@hooks.register('rai_permission')
def rai_nothing_permission():
    return RAINothingPermission


class RAIViewPermission(RAINothingPermission):
    key = 'view'
    score = 2
    label = _l('Users can view')

@hooks.register('rai_permission')
def rai_view_permission():
    return RAIVIewPermission

class RAIEditPermission(RAINothingPermission):
    key = 'edit'
    score = 4
    label = _l('Users can edit')
    
@hooks.register('rai_permission')
def rai_edit_permission():
    return RAIEditPermission
    
class RAICreatePermission(RAINothingPermission):
    key = 'create'
    score = 6
    label = _l('Users can create')

@hooks.register('rai_permission')
def rai_create_permission():
    return RAICreatePermission

class RAIDeletePermission(RAINothingPermission):
    key = 'delete'
    score = 8
    label = _l('Users can delete')

@hooks.register('rai_permission')
def rai_delete_permission():
    return RAIDeletePermission




    
