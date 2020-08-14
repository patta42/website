from wagtail.core import hooks

REGISTERED_COLLECTIONS = {}

for fn in hooks.get_hooks('rai_document_collection'):
    collection = fn()
    REGISTERED_COLLECTIONS.update(collection)

REGISTERED_ONDEMAND_DOCUMENTS = {}

for fn in hooks.get_hooks('rai_document_on_demand'):
    key, doc = fn()
    relation = doc.relation.__name__

    docs = REGISTERED_ONDEMAND_DOCUMENTS.get(relation, {})
    docs.update({key:doc})
    REGISTERED_ONDEMAND_DOCUMENTS.update({relation: docs})
    
    
    
