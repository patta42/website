from .models import RAIComment
from .edit_handlers import CommentContentPanel

from django import forms
from django.http import JsonResponse, HttpResponseForbidden

import markdown


def comment_delete(request, pk):
    if request.method == 'POST' and request.is_ajax():
        comment = RAIComment.objects.get(pk=pk)
        if request.user.is_superuser or request.user == comment.owner:
            comment.delete()
            return JsonResponse({'status':200})

class CommentModelForm(forms.ModelForm):
    class Meta:
        model = RAIComment
        fields = ['comment']
        

def comment_edit(request, pk):
    if request.is_ajax():
        comment = RAIComment.objects.get(pk=pk)
            
        if request.method == 'GET':
            form = CommentModelForm(instance = comment)
            edit_handler = CommentContentPanel('comment')
            edit_handler = edit_handler.bind_to(model=RAIComment, form = form, instance=comment)
            return JsonResponse({'status' : 200, 'html' : edit_handler.render_as_field()})
        elif request.method == 'POST':
            form = CommentModelForm(request.POST)
            if form.is_valid():
                comment.comment = request.POST['comment']
                comment.save()
                kwargs = {
                    'extensions' : ['def_list'],
                    'output_format' : 'html5',
                }

                return JsonResponse({
                    'status': 200,
                    'html': markdown.markdown(comment.comment, **kwargs)
                })
            else:
                return JsonResponse({
                    'status': 410,
                    'errors' : form.errors.as_json()
                })
    return HttpResponseForbidden()
            
