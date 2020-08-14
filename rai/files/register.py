from .models import RAICollection

from .base import RAIOnDemandDocumentCollection, RAIDocumentCollection, register_collection
from .views import document_edit, add_document, delete_document

from django.urls import path

from wagtail.core import hooks

register_collection(RAIDocumentCollection)
register_collection(RAIOnDemandDocumentCollection)


@hooks.register('register_rai_url')
def rai_file_urls():
    return [
        path('rai/files/<pk>/edit/', document_edit, name = 'rai_file_edit'),
        path('rai/files/<pk>/delete/', delete_document, name = 'rai_file_delete'),
        path('rai/files/<rai_collection>/<collection_pk>/<obj_pk>/add', add_document, name = 'rai_files_add')
    ]
