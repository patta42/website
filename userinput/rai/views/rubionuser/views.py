from .forms import (
    UserAndStaffInactivationForm, WorkgroupInactivationForm,
)

import datetime

from django.db.models import Q
from django.forms import formset_factory
from django.utils.functional import cached_property

from rai.default_views import EditView, InactivateView

from userdata.models import StaffUser
from userinput.models import RUBIONUser, WorkGroup, Project

from wagtail.core.models import Page

class RUBIONUserEditView(EditView):
    template_name = 'userinput/rubionuser/rai/edit/edit.html'


class ExtendedRUBIONUserInformationMixin:
    """
    This mixin  separates getting all the related information of the
    user from the view logic

    This mixin assumes self.obj and self.raiadmin to be set
    """

    # query string to get the obj
    @cached_property
    def _obj_qs(self):
        return self.raiadmin.model.objects.get(pk = self.obj.pk)

    # inactivate a user
    _user_inactivated = False
    def inactivate_user(self):
        if not self._user_inactivated:
            self.obj.inactivate(user = self.request.user)
            self.success_message('Nutzer erfolgreich inaktiviert.')
            self._user_inactivated = True
            
    # Staff related 
    # query to the staff user
    @cached_property
    def _staff_qs(self):
        return StaffUser.objects.filter(user = self.obj.linked_user)
        
    # query to the staff user
    @cached_property
    def is_staff(self):
        return self.obj.linked_user is not None and self._staff_qs.count() > 0

    @cached_property
    def staff_user(self):
        return self._staff_qs[0]

    @cached_property
    def staff_group(self):
        if not self.is_staff:
            return ''
        return self._staff_qs.first().get_parent().specific.title_trans

    _staff_inactivated = False
    def inactivate_staff(self):
        staff = self.staff
        # inactivate staff user and website user
        staff.inactivate(user = request.user, inactivate_website_user = True)
        self.success_message('Mitarbeiter erfolgreich inaktiviert.')


    # Workgroup related
    @property
    def is_group_leader(self):
        return self.obj.is_leader == True
    
    @cached_property
    def workgroup(self):
        return self._obj_qs.get_parent().get_parent()

    @cached_property
    def workgroup_members(self):
        if not self.is_group_leader:
            return None
        else:
            qs = (
                self._obj_qs.get_siblings().
                exclude(pk = self.obj.pk).filter(content_type = self.obj.content_type).
                filter(RUBIONUser.active_filter())
            )
            return qs
    @cached_property
    def target_workgroups(self):
        return WorkGroup.objects.active().exclude(pk = self.obj.pk)

    def target_workgroups_for_choices(self):
        return [( wg.pk, wg.specific.title_trans) for wg in self.target_workgroups ]
    
    # Project related
    @cached_property
    def projects(self):
        return (
            self.workgroup.get_descendants()
            .filter(content_type = Project().content_type)
            .filter(Project.active_filter())
        )



class RUBIONUserInactivateView(InactivateView, ExtendedRUBIONUserInformationMixin):
    template_name = 'userinput/rubionuser/rai/views/inactivate.html'
    staff_form = None
    group_leader_form = None
    member_decision_formset = None
    project_decision_formset = None
    
    def dispatch(self, request, *args, **kwargs):
        self.obj = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    # Change button label for submit button
    def get_buttons(self):
        buttons = super().get_buttons().copy()
        if self.is_staff:
            buttons['okay']['label'] = 'Nutzer mit den obigen Einstellungen inaktivieren'

        return buttons

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_staff'] = self.is_staff
        context['staff_group'] = self.staff_group
        context['staff_form'] = self.staff_form
        context['group_leader_form'] = self.group_leader_form

        return context


            
    def get(self, request, *args, **kwargs):
        if self.is_staff:
            self.staff_form = UserAndStaffInactivationForm()
        if self.is_group_leader:
            members = self.workgroup_members
            self.group_leader_form = WorkgroupInactivationForm(members)
            
        return super().get(request, *args, **kwargs)
    
    
    def post(self, request, *args, **kwargs):
        # Check action

        if request.POST.get('action', None) != 'inactivate':
            self.warning_message('Inaktivierung nicht erfolgreich.')
            self.debug_message('POST.action not inactivate') 
            return self.redirect_to_default()

        # if its only a user, it's simple
        if not self.is_staff and not self.is_group_leader:
            # inactivate the User
            self.inactivate_user()
            return self.redirect_to_default()
        
        # check if forms are okay

        # Staff first
        staff_valid = False
        if self.is_staff:
            self.staff_form = UserAndStaffInactivationForm(request.POST)
            if self.staff_form.is_valid():
                staff_valid = True

        # leader
        leader_valid = False
        if self.is_group_leader:
            members = self.workgroup_members
            self.group_leader_form = WorkgroupInactivationForm(members, request.POST)
            if self.group_leader_form.is_valid():
                leader_valid = True
            

        all_valid = (not self.is_staff or staff_valid) and (not self.is_group_leader or leader_valid)
        if not all_valid:
            # don't do anything, render the form with errors again:
            return super().get(request, *args, **kwargs)
        else:
            self.inactivate_user()
            if self.is_staff:
                if self.staff_form.cleaned_data['user_staff_choice'] == 'user_and_staff':
                    self.inactivate_staff()                                    
                if self.staff_form.cleaned_data['user_staff_choice'] in ['user_only', 'user_and_staff']:
                    self.inactivate_user()
                        
            if self.is_group_leader:
                if self.group_leader_form.cleaned_data.get('workgroup_choice') == 'inactivate':
                    self.workgroup.inactivate(user = self.request.user)
                    self.success_message('Die Arbeitsgruppe wurde inaktiviert')
                elif self.group_leader_form.cleaned_data.get('workgroup_choice') == 'new_leader':
                    self.inactivate_user()
                    self.obj.is_leader = False
                    self.obj.save_revision_and_publish(user=self.request.user)
                    new_leader = RUBIONUser.objects.get(pk = int(self.group_leader_form.cleaned_data.get('new_leader')))
                    new_leader.is_leader = True
                    new_leader.save_revision_and_publish(user = self.request.user)
                    self.success_message('{}, {} ist neuer Leiter der Arbeitsgruppe'.format(new_leader.last_name, new_leader.first_name))

                    
            return self.redirect_to_default()
                    
