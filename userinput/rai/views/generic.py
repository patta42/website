from django.http import Http404, JsonResponse
from django.template.response import TemplateResponse

from rai.default_views import InactivateView

from userinput.models import WorkGroup, Nuclide
from userinput.rai.forms import MoveToWorkgroupForm, AddNuclideForm


class MoveToWorkgroupView(InactivateView):

    template_name = 'userinput/rai/views/shared/move-to-workgroup.html'


    def get_buttons(self):
        buttons = super().get_buttons()
        buttons['okay']['label'] = 'Verschieben'
        buttons['okay']['value'] = 'move'
        return buttons
    def dispatch(self, request, *args, **kwargs): 
        self.obj = self.get_object()
        self.workgroup = self.obj.get_parent().get_parent()
        self.form = MoveToWorkgroupForm(WorkGroup.objects.active().exclude(pk = self.workgroup.pk))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'object' : self.obj,
            'page_menu' : self.get_page_menu(),
            'button': self.get_buttons(),
            'form' : self.form
        })
        return context
            
    def get(self, request, *args, **kwargs):
        return TemplateResponse(
            request,
            self.template_name,
            self.get_context_data()
        )

    def post(self, request, *args, **kwargs):
        if request.POST.get('action', None) != 'move':
            self.warning_message('Das Verschieben ist fehlgeschlagen.')
            self.debug_message('POST.action was not move.')
        self.form = MoveToWorkgroupForm(
            WorkGroup.objects.active().exclude(pk = self.workgroup.pk),
            request.POST
        )
        if self.form.is_valid():
            workgroup = WorkGroup.objects.get(pk = int(self.form.cleaned_data['workgroup']))
            for child in workgroup.get_children():
                if self.obj.can_move_to(child):
                    self.obj.move(child, pos='last-child')
                    self.obj = self.obj.__class__.objects.get(pk = self.obj.pk)
                    self.obj.save_revision_and_publish(user = request.user)
                    self.success_message(
                        '{} wurde erfolgreich der Gruppe {} zugeordnet.'.format(self.obj, workgroup)
                    )
                    return self.redirect_to_default()
            self.warning_message('Das Zuordnen zu einer neuen Gruppe ist fehlgeschlagen');
            return self.redirect_to_default()
        else:
            return self.get(request, *args, **kwargs)
        
            
def add_nuclide(request):
    if not request.is_ajax():
        raise Http404('Page does not exist')
    if request.method == 'GET':
        form = AddNuclideForm()
        return JsonResponse({'status': 200, 'html': form.as_p()})
    if request.method == 'POST':
        form = AddNuclideForm(request.POST)
        if form.is_valid():
            elem, mass = form.cleaned_data['nuclide'].split('-')
            if Nuclide.objects.filter(element = elem, mass = mass).exists():
                return JsonResponse({'status': 200, 'errors': True, 'html' : '<ul class="errorlist"><li>Das Nuklid existiert bereits</li></ul>'+form.as_p()})
            else:
                nuclide = Nuclide(
                    element = elem,
                    mass = mass
                )
                nuclide.save()
                return JsonResponse({'status': 200, 'errors': False, 'pk' : nuclide.pk, 'nuclide' : str(nuclide)})
        else:
            return JsonResponse({'status': 200, 'errors' : True, 'html' : form.as_p()})
