from .models import RAICollection

from django.urls import path

from wagtail.core import hooks


        
class RAIBaseCollection:
    collection_id = 'rai-files'
    collection_name = 'RAI Files'

    def get_path(self):
        mro = self.__class__.mro()
        mro.reverse()
        p = []
        for cls in mro:
            if hasattr(cls, 'collection_id'):
                p.append(cls.collection_id)
        return p

    def get_id(self):
        return '.'.join(self.get_path())

    def get_pk(self):
        rc = self.get_obj()
        return rc.pk

    def get_obj(self):
        rc = RAICollection.objects.get(name = self.get_id())
        return rc
    
    def register(self):
        collection_id = ''
        parent_collection = None
        for path in self.get_path():
            if collection_id != '':
                collection_id += '.'
            collection_id += path
            try:
                parent_collection = RAICollection.objects.get(name = collection_id)
            except RAICollection.DoesNotExist:
                collection = RAICollection(
                    display_name = self.collection_name,
                    name = collection_id
                )
                if not parent_collection:
                    collection = RAICollection(
                        name = collection_id,
                        display_name = self.collection_name
                    )
                    RAICollection.add_root(instance = collection)
                else:
                    parent_collection.add_child(instance = collection)
                parent_collection = collection
        # Register with wagtail
        @hooks.register('rai_document_collection')
        def register_collection():
            return {self.get_id(): self}
        
class RAIDocumentCollection(RAIBaseCollection):
    """
    A class that generates a collection, if not already available
    """
    collection_name = 'Documents'
    collection_id = 'documents'

    # def get_path(self):
    #     path = super().get_path()
    #     path.append(self.collection_id)
    #     print (path)
    #     return path


class RAIOnDemandDocumentCollection(RAIBaseCollection):
    collection_name = 'Documents on demand'
    collection_id = 'on_demand_documents'
            
def register_collection(Collection_class):
    collection = Collection_class()
    collection.register()


class RAIDocumentOnDemand:
    """
    A class for documents that are generated by the server on demand
    """
    # An identifier which identifies the subclass
    identifier = None

    # a view that is called by ajax that generates the document
    createview = None

    # the relation model
    relation = None

    # title for the document 
    title = None

    # description for the document
    description = None

    # collection for the documents
    collection = RAIOnDemandDocumentCollection

    # icon info
    icon = 'fa-file'
    icon_font = 'fas'

    
    def create_url(self):
        return 'rai/automatic_files/'+self.identifier+'/<pk>/'
    def create_url_name(self):
        return 'rai_automatic_files_'+self.identifier
    def register(self):
        print('Registering {}'.format(self))
        @hooks.register('rai_document_on_demand')
        def register_with_wagtail():
            return (self.identifier, self)
        @hooks.register('register_rai_url')
        def register_url_with_wagtail():
            return [
                path(
                    self.create_url(),
                    self.createview.as_view(),
                    name = self.create_url_name()
                )
            ]
        

def rai_register_document_on_demand(kls):
    cls = kls()
    cls.register()

def rai_register_documents_on_demand(lst):
    for item in lst:
        rai_register_document_on_demand(item)

