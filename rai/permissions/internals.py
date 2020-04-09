from pprint import pprint

from wagtail.core import hooks


PERMISSIONS = {}

def _register_permission(identifier, sub_id, permission):
    sub_values = PERMISSIONS.pop(identifier, {})
    permissions = sub_values.pop(sub_id, [])
    permissions.append(permission)
    sub_values.update({sub_id : permissions})
    PERMISSIONS.update({identifier : sub_values})

def _populate_permissions():
    for fn in hooks.get_hooks('register_rai_permission'):
        identifier, sub_id, permission = fn()
        _register_permission(identifier, sub_id, permission)

    for fn in hooks.get_hooks('register_rai_permissions'):
        identifier, sub_id, permissions = fn()
        for permission in permissions:
            _register_permission(identifier, sub_id, permission)

_populate_permissions()

def get_permissions(identifier, sub):
    try:
        base_permissions = PERMISSIONS['__all__']['__all__']
    except KeyError:
        import rai.permissions.base
        _populate_permissions()
        base_permissions = PERMISSIONS['__all__']['__all__']
    item = PERMISSIONS.get(identifier, {})
    return base_permissions + item.get(sub, [])


def get_permissions_as_choices():
    from rai.internals import REGISTERED_ITEMS
    choices = []
    for major, subitems in REGISTERED_ITEMS.items():
        for subitem in subitems:
            choices.append(
                ( '{}.{}'.format(major, subitem['id']),
                  [
                      (perm.value, perm.description) for perm in get_permissions(major, subitem['id'])
                  ]
                )
            )
    return choices
