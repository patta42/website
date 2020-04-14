from wagtail.core import hooks

REGISTERED_NOTIFICATIONS = {}

for fn in hooks.get_hooks('rai_notification'):
    notification = fn()
    REGISTERED_NOTIFICATIONS.update({notification.identifier : notification})
