import datetime
from dateutils import relativedelta
from django.utils.text import slugify
from django.shortcuts import redirect

from instruments.models import MethodPage

from rai.default_views.multiform_create import  MultiFormCreateView

from userinput.models import (
    Project, WorkGroup, ProjectContainer, Nuclide, Project2MethodRelation,
    Project2NuclideRelation
)

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
        if self.session_store['status']['form']['status'] == 'applied':
            now = datetime.datetime.now()
            next_year = now + relativedelta(years=+1)
            project.expire_at = next_year
            project.go_live_at = now
            revision = project.save_revision(user=request.user)
            revision.publish()
        if self.session_store['status']['form']['status'] == 'accepted':
            project.save_revision(user=request.user, submitted_for_moderation = True)
        return redirect('rai_userinput_project_edit', pk = project.pk)
