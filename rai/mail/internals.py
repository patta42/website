from wagtail.core import hooks

REGISTERED_MAIL_COLLECTIONS = {}

for fn in hooks.get_hooks('rai_mail_collection'):
    collection = fn()
    REGISTERED_MAIL_COLLECTIONS.update({
        collection.__class__.__name__ : collection
    })
