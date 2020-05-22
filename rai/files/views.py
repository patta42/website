from pprint import pprint

from django.forms.models import modelform_factory
from django.http import JsonResponse, HttpResponseForbidden
from django.urls import reverse


from .models import RAIDocument, RAICollection


def document_edit(request, pk):
    if request.method == 'POST' and request.is_ajax():
        field = request.POST.get('field', None)
        value = request.POST.get('value', None)
        doc = RAIDocument.objects.get(pk = pk)
        if field:
            if field == 'title':
                doc.title = value
                doc.save()
            if field == 'description':
                doc.description = value
                doc.save()
            
        return JsonResponse({'status': 200})

def add_document(request, rai_collection, collection_pk, obj_pk):
    from .internals import REGISTERED_COLLECTIONS
    if request.method == 'POST' and request.is_ajax():
        print(REGISTERED_COLLECTIONS)
        relation = REGISTERED_COLLECTIONS.get(rai_collection, None)
        if not relation:
            return  JsonResponse({
                'status' : 500,
                'error' : 'Could not find {}'.format(rai_collection),
                
            })
        
        collection = RAICollection.objects.get(pk = collection_pk)
        form_class = modelform_factory(
            RAIDocument,
            fields = ['file', 'title', 'description']
        )
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit = False)
            instance.collection = collection
            instance.uploaded_by_user = request.user
            instance.save()
            model = relation.model._meta.get_field('decorated_model').related_model
            obj = model.objects.get(pk = obj_pk)
            rel = relation.model(
                decorated_model = obj,
                doc = instance
            )
            rel.save()
            return JsonResponse({
                'status' : 200,
                'pk' : instance.pk,
                'title' : instance.title,
                'description' : instance.description,
                'edit_url' : reverse('rai_file_edit', args = [instance.pk]),
                'delete_url': reverse('rai_file_delete', args = [instance.pk]),
                'created_at': instance.created_at,
                'uploaded_by': '{} {}'.format(instance.uploaded_by_user.first_name, instance.uploaded_by_user.last_name)
            })
        else:
            return JsonResponse(
                {
                    'status' : 500,
                    'errors' : form.errors.as_json()
                })

def delete_document(request, pk):
    if request.method == 'POST' and request.is_ajax():
        document = RAIDocument.objects.get(pk = pk)
        if request.user == document.uploaded_by_user or request.user.is_superuser:
            document.delete()
            return JsonResponse({'status': 200})
        else:
            return JsonResponse({'status': 403})
