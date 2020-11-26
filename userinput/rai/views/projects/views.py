from .forms import ReallyRejectForm

import datetime
from dateutils import relativedelta

from django.utils.text import slugify
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from instruments.models import MethodPage

from rai.default_views.decision import AbstractDecisionView
from rai.default_views.multiform_create import  MultiFormCreateView

from userinput.models import (
    Project, WorkGroup, ProjectContainer, Nuclide, Project2MethodRelation,
    Project2NuclideRelation, UserComment, RUBIONUser
)
from userinput.rai.projects.notifications import ProjectAcceptedNotification

class ProjectCreateView(MultiFormCreateView):
    def prepare_formsets(self, formsets, prefix):
        if prefix == 'related_nuclides':
            nuclides = formsets.get('related_nuclides', [])
            new_related_nuclides = []
            for nuclide in nuclides:
                snippet = nuclide.get('snippet')
                nuclide.update({'snippet': snippet.pk})
                new_related_nuclides.append(nuclide)
            if nuclides:
                formsets.update({'related_nuclides': new_related_nuclides})
            
        return formsets

    def get_parent(self):
        workgroup_pk = self.session_store['workgroup']['form']['workgroup']
        wg = WorkGroup.objects.get(pk = workgroup_pk)
        return ProjectContainer.objects.child_of(wg).first()

    def make_project(self):
        project = Project()
        de_data = self.session_store['info_german']['form']
        en_data = self.session_store['info_english']['form']
        safety_data = self.session_store['safety_information']['form']
        public_data = {'public' : self.session_store['status']['form']['public']}

        for key, value in {**de_data, **en_data, **safety_data, **public_data}.items():
            setattr(project, key, value)
        project.slug = slugify(project.title)
        
        return project

    def make_relations(self, project):
        nuclides = self.session_store['related_nuclides']['formsets'].get('related_nuclides', [])
        methods = self.session_store['methods']['form'].get('methods', [])
        for method in methods:
            rel = Project2MethodRelation(
                project_page = project,
                page = MethodPage.objects.get(pk = method)
            )
            print('Project pk')
            print(project.pk)
            rel.save()

        for nuclide in nuclides:
            room = nuclide.get('room', '')
            max_order = nuclide.get('max_order', '')
            amount_per_experiment = nuclide.get('amount_per_experiment', '')
            rel = Project2NuclideRelation(
                snippet = Nuclide.objects.get(pk = nuclide['snippet']),
                room = room,
                max_order = max_order,
                amount_per_experiment = amount_per_experiment,
                project_page = project,
            )
            
            rel.save()
    
    def finalize(self, request):
        parent = self.get_parent()
        project = self.make_project()
        project = parent.add_child(instance = project)
        self.make_relations(project)
        # Setting status of project
        if self.session_store['status']['form']['status'] == 'accepted':
            now = datetime.datetime.now()
            next_year = now + relativedelta(years=+1)
            project.expire_at = next_year
            project.go_live_at = now
            revision = project.save_revision(user=request.user)
            revision.publish()
        if self.session_store['status']['form']['status'] == 'applied':
            project.save_revision(user=request.user, submitted_for_moderation = True)
        return redirect('rai_userinput_project_edit', pk = project.pk)


    
class ProjectDecisionView(AbstractDecisionView):
    
    info_template = 'userinput/project/rai/decision-info.html'
    reject_confirmation_template = 'userinput/project/rai/reject-confirmation.html'
    
    def get_info_context(self):
        context = super().get_info_context()
        qs = UserComment.objects.filter(page = self.obj)
        if qs.exists():
            comment = qs[0]
            context['comment'] = comment.text
        else:
            context['comment'] = None

        return context

    def reject(self, request):
        context = self.get_context_data()
        if request.POST.get('formflag', None):
            self.success_message('Das Projekt wurde abgelehnt.')
            self.obj.delete()
            return redirect('rai_mail_compose')
        else:
            form = ReallyRejectForm()
            del(context['buttons']['okay'])
            context['buttons']['cancel']['value'] = self.active_action.get_url_name()
            context['buttons']['cancel']['urlparams'] = self.obj.pk
            context['rev'] = self.obj.revisions.filter(submitted_for_moderation = True).order_by('-created_at').first()
            context['reject_form'] = form
            return TemplateResponse(
                request,
                self.reject_confirmation_template,
                context
            )
            
    def accept(self, request):
        noti = ProjectAcceptedNotification()
        rev = self.obj.revisions.filter(submitted_for_moderation = True).order_by('-created_at').first()
        ruser = RUBIONUser.objects.filter(linked_user = rev.user).first()
        if not ruser: # application has been filed by an admin-account, for example
            ruser = self.obj.get_workgroup().get_head()
        kwargs = {
            'project' : self.obj,
            'applicant' : ruser
        }
        lang = ruser.preferred_language
        if lang:
            kwargs['lang'] = lang
            
        noti.send([ruser.email], **kwargs)
        rev.approve_moderation()
        self.obj.save_revision(user = request.user)
        self.success_message('Das Projekt wurde angenommen.')

        return self.redirect_to_default()
        
