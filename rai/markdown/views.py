import markdown
from django.http import JsonResponse


def markdown2html(request):
    if request.method == 'POST' and request.is_ajax():
        markdown_code = request.POST['markdown']
        kwargs = {
            'extensions' : ['def_list'],
            'output_format' : 'html5',
        }
        return JsonResponse({
            'content' : markdown.markdown( markdown_code, **kwargs)
        })
    
