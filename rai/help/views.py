from pprint import pprint

from .models import HelpText

from django.http import JsonResponse, HttpResponse
from django.views.generic import View
from django.forms.models import modelform_factory


import markdown

class AjaxHelpView(View):
    has_object = False
    obj = None
    model = HelpText
    not_found = False
    obj_expected = False
    hp = None
    exclude = ['id', 'depth', 'path', 'numchild']

    def set_object_state(self, *args, **kwargs):
        if 'hp' in kwargs.keys():
            self.obj_expected = True
            self.hp = kwargs.pop('hp')
            try:
                self.obj = self.model.objects.get(identifier = self.hp)
                self.has_object = True
            except self.model.DoesNotExist:
                self.not_found = True
                # we don't have a proper instance, but we can build a faked one.
                # allows to call get_breadcrumb with true page names, if available
                self.obj = self.model(identifier = self.hp)

    
    def dispatch(self, request, *args, **kwargs):
        # check if there is an instance available
        self.set_object_state(self, *args, **kwargs)

        return super().dispatch( request, *args, **kwargs)
        

    def post(self, request, *args, **kwargs):
        print ('POST data')
        print(request.POST)
        print ('Object expected: {}'.format(self.obj_expected))
        print ('Has Object: {}'.format(self.has_object))
        form_class = modelform_factory(self.model, exclude = self.exclude)
        if self.obj_expected and self.has_object:
            # we do an update
            form = form_class(request.POST, instance=self.obj)
        else:
            form = form_class(request.POST)
        if form.is_valid():
            instance = form.save(commit = False)
            instance.save()
            return JsonResponse({'msg' : 'Die Änderungen wurden gespeichert'}, status=201)
        else:
            print(form.errors)
            return JsonResponse({}, status=422)
            print(form.errors)


    def get_context_object(self):
        md_kwargs = {
            'extensions' : ['def_list'],
            'output_format' : 'html5',
        }

        pth, page = self.obj.get_help_path()

        context = {
            'content_markdown' : self.obj.content or '',
            'content_html' : markdown.markdown(self.obj.content or '', **md_kwargs),
            'breadcrumb' : self.obj.get_breadcrumb(),
            'title' : self.obj.title or page,
            'editable' : True
        }

        return context
    

    def get_context_root(self):
        context = {}
        return context

    
    def get(self,  request, *args, **kwargs):
        """
        If a page is not founr, don't return a 404 since that is processed by the 
        locale middleware and might lead to a redirection to an url prefixed with a 
        language code. 
        Of course, this page is not available and thus a 404 is thrown, but not as 
        a JsonResponse.

        Took me a while to figure that out.
        """
        if self.obj_expected:
            if self.not_found:
                context = self.get_context_object()
                context.update({
                    'not_found' : True,
                    'is_empty' : True,
                })
                return JsonResponse(context)
            else:
                context = self.get_context_object()
                context.update({
                    'not_found' : False,
                    'is_empty' : False,
                })
                if getattr(self.obj, 'is_empty', None):
                    if self.obj.is_empty():
                        context.update({'is_empty' : True})
                return JsonResponse(context)
        else:
            # show the full tree of root_nodes
            root_nodes = self.model.get_root_nodes()
            return JsonResponse(self.get_context_root())

