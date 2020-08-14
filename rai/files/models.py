from django.db import models
from django.conf import settings

from wagtail.core.models import CollectionMember, Collection
from wagtail.documents.models import AbstractDocument 


class RAICollection(Collection):
    display_name = models.CharField(
        max_length = 128,
        blank = True
    )

    def __str__(self):
        return '{} ({})'.format(self.display_name, self.name)

class RAIDocument(AbstractDocument):
    description = models.CharField(
        blank = True,
        max_length = 256
    )
    @classmethod
    def from_document(self, document):
        return RAIDocument(
            title = document.title,
            file =  document.file,
            uploaded_by_user = document.uploaded_by_user,
            collection = document.collection
        )

    @property
    def url(self):
        return self.file.url
        
class RAIDocumentModelRelation(CollectionMember, models.Model):
    class Meta:
        abstract = True
        verbose_name = 'Verknüpfte Dokumente'

    doc = models.ForeignKey(
        RAIDocument,
        on_delete = models.CASCADE,
        #related_name = 'documents'
    )
    
class RAIOnDemandDocumentModelRelation(RAIDocumentModelRelation):
    class Meta:
        abstract = True
        verbose_name = 'Automatisch erzeugte Dokumente'
        
    key = models.CharField(
        max_length = 128,
    )

    
