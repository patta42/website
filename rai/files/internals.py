from wagtail.core import hooks

REGISTERED_COLLECTIONS = {}

for fn in hooks.get_hooks('rai_document_collection'):
    collection = fn()
    REGISTERED_COLLECTIONS.update(collection)
    
