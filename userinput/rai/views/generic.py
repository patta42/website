from django.template.response import TemplateResponse

from rai.default_views import InactivateView

from userinput.models import WorkGroup
from userinput.rai.forms import MoveToWorkgroupForm


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
        
            
