from wagtail.core import hooks

REGISTERED_COLLECTIONS = {}

for fn in hooks.get_hooks('rai_document_collection'):
    collection = fn()
    print('Collections before:')
    print(REGISTERED_COLLECTIONS)
    REGISTERED_COLLECTIONS.update(collection)
    print('Collections after:')
    print(REGISTERED_COLLECTIONS)
    
