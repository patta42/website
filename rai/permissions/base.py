import rai.permissions.permissions as perm

from wagtail.core import hooks

# this is how to register a single permission
@hooks.register('register_rai_permission')
def register_default_permission():
    return ('__all__', '__all__', perm.NonePermission)

# and this is how to register multiple permissions
@hooks.register('register_rai_permissions')
def register_default_permissions():
    return ('__all__', '__all__', [
        perm.ViewPermission,
        perm.EditPermission,
        perm.CreatePermission,
        perm.DeletePermission
    ])


    
