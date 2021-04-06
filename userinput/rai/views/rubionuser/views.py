from pprint import pprint

from .forms import (
    UserAndStaffInactivationForm, WorkgroupInactivationForm,
    ActivateUserWorkgroupChoiceForm, AddInstructionsForm
)

import datetime

from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.db.models import Q, Max
from django.forms import formset_factory
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.views.generic.edit import FormView
from django.views.generic.detail import BaseDetailView

from rai.comments.models import RAIComment
from rai.default_views import EditView, InactivateView, HistoryView, ActivateView, ListView
from rai.default_views.generic import RAIAdminView, PageMenuMixin, FilterSettingsView
from rai.default_views.multiform_create import  MultiFormCreateView
from rai.files.models import RAIDocument

from rubauth.auth import fetch_user_info

from userdata.models import (
    StaffUser, SafetyInstructionsSnippet, SafetyInstructionUserRelation,
    SafetyInstruction2StaffRelation, SafetyInstruction2UserRelation
)
from userinput.models import (
    RUBIONUser, WorkGroup, Project, RUBIONUserCommentDecoration,
    RUBIONUserOnDemandDocumentRelation, MemberContainer
)

from userinput.pdfhandling import RUBIONBadge

from wagtail.admin.compare import M2MFieldComparison, ChildRelationComparison
from wagtail.core.models import Page

class RUBIONUserEditView(EditView):
    template_name = 'userinput/rubionuser/rai/edit/edit.html'

    def save_post_hook(self, request, form):
        saved_something = super().save_post_hook(request, form, add_messages = False)
        comment = request.POST.get('comment', None)
        if comment and comment != "" and comment != "None":
            new_comment = RAIComment(
                owner = request.user,
                comment = comment
            )
            new_comment.save()
            decoration = RUBIONUserCommentDecoration(
                decorated_model = self.obj,
                rai_model = new_comment
            )
            decoration.save()
            saved_something = True
        if saved_something:
            self.success_message('Die Daten wurden gespeichert')
        else:
            self.info_message('Die Daten enthielten keine Änderung und wurden daher nicht gespeichert')


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
        return self._staff_qs.first().get_parent().specific().title_trans

    _staff_inactivated = False
    def inactivate_staff(self):
        staff = self.staff_user
        # inactivate staff user and website user
        staff.inactivate(user = self.request.user, inactivate_website_user = True)
        self.success_message('Mitarbeiter erfolgreich inaktiviert.')


    # Workgroup related
    @property
    def is_group_leader(self):
        return self.obj.is_leader == True
    
    @cached_property
    def workgroup(self):
        return self._obj_qs.get_parent().get_parent().specific()

    @cached_property
    def workgroup_members(self):
        if not self.is_group_leader:
            return None
        else:
            qs = (
                self.raiadmin.model.objects.filter(
                    pk__in = self._obj_qs.get_siblings().
                    exclude(pk = self.obj.pk).filter(content_type = self.obj.content_type)
                ).
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


class RUBIONUserCreateView(MultiFormCreateView):
    def prepare_cleaned_data(self, data, prefix):
        if prefix == 'safety_information':
            qs = data['needs_safety_instructions']
            data_pks = []
            for si in qs:
                data_pks.append(si.pk)
            data.update({'needs_safety_instructions' : data_pks})
            return data
        else:
            return super().prepare_cleaned_data(data, prefix)

    def make_user(self):
        user = get_user_model()(is_staff = False)
        if self.session_store['new_user_src']['form'].get('source') == 'rub':
            userinfo = fetch_user_info(self.session_store['new_user_src']['form'].get('rub_id'))
            user.username = self.session_store['new_user_src']['form'].get('rub_id')
            user.first_name = userinfo['last_name']
            user.last_name = userinfo['first_name']
            user.email = userinfo['email']

        elif self.session_store['new_user_src']['form'].get('source') == 'ext':
            user.username = self.session_store['new_user_src']['form'].get('ext_email')
            user.first_name = self.session_store['new_user_src']['form'].get('ext_first_name')
            user.last_name = self.session_store['new_user_src']['form'].get('ext_last_name')
            user.email = self.session_store['new_user_src']['form'].get('ext_email')
        user.set_unusable_password()    
        user.save()
        return user
            
        
    def finalize(self, request):
        user = self.make_user()
        ruser = RUBIONUser(
            linked_user = user,
            name_db = user.last_name,
            first_name_db = user.first_name,
            email_db = user.email,
            slug = slugify('{} {}'.format(user.first_name, user.last_name)),
            title = '{} {}'.format(user.first_name, user.last_name),
            title_de = '{} {}'.format(user.first_name, user.last_name)
        )
        for key, val in self.session_store['lab_organization']['form'].items():
            setattr(ruser, key, val)
        for key, val in self.session_store['contact_data']['form'].items():
            setattr(ruser, key, val)

        sidata = self.session_store['safety_information']['form']
        ruser.dosemeter = sidata['dosemeter']
        sisnippets = []
        for sipk in sidata['needs_safety_instructions']:
            sisnippets.append(SafetyInstructionsSnippet.objects.get(pk = sipk))

        ruser.needs_safety_instructions = sisnippets
        workgroup = WorkGroup.objects.get(pk = self.session_store['workgroup']['form'].get('workgroup'))
        mc = MemberContainer.objects.child_of(workgroup).first()

        mc.add_child(instance = ruser)
        ruser.save_revision(user = request.user)
        self.success_message('Der neue Nutzer wurde erstellt.')
        return redirect('rai_userinput_rubionuser_edit', pk= ruser.pk)
    

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
                    

class RUBIONUserActivateView(ActivateView):
    template_name = 'userinput/rubionuser/rai/views/activate.html'    

    workgroup_choice_form = None

    def get_buttons(self):
        buttons = super().get_buttons().copy()
        buttons['okay']['label'] = 'Nutzer mit den obigen Einstellungen aktivieren'

        return buttons

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['workgroup_choice_form'] = self.workgroup_choice_form
        # context['staff_group'] = self.staff_group
        # context['staff_form'] = self.staff_form
        # context['group_leader_form'] = self.group_leader_form

        return context


    def get(self, request, *args, **kwargs):
        if not self.workgroup_choice_form:
            self.workgroup_choice_form = ActivateUserWorkgroupChoiceForm(self.obj)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.POST.get('action', None) != 'activate':
            self.warning_message('Aktivierung nicht erfolgreich.')
            self.debug_message('POST.action not activate') 
            return self.redirect_to_default()

        self.workgroup_choice_form = ActivateUserWorkgroupChoiceForm(self.obj, request.POST)

        if not self.workgroup_choice_form.is_valid():
            return self.get(request, *args, **kwargs)
        new_wg_pk = self.workgroup_choice_form.cleaned_data.get('workgroup_choice')
        current_wg = self.obj.get_workgroup()

        # move, if necessary
        if current_wg.pk != new_wg_pk:
            new_wg = WorkGroup.objects.get(pk = new_wg_pk)
            self.obj.move(new_wg.get_member_container(), 'last-child')
        else:
            new_wg = current_wg
            
        # activate wg and make user group_leader, if necessary
        if new_wg.is_inactivated():
            new_wg.activate(user = request.user)
            self.obj.is_leader = True

        # activate user
        self.obj.activate(user = request.user)

        return self.redirect_to_default()

    
class RUBIONUserHistoryView(HistoryView):
    additional_comparisons = HistoryView.additional_comparisons + [
        'may_create_projects',
        'may_add_members',
        'is_leader', #'rubion_user_si'
    ]
    comparators = {
        'rubion_user_si' : ChildRelationComparison
    }
    
class RUBIONUserCreateBadgeView( BaseDetailView ):

    def dispatch(self, request, pk):
        if not request.is_ajax():
            return HttpResponse(status = 500)
        else:
            try:
                self.instance = RUBIONUser.objects.get(pk = pk)
            except RUBIONUser.DoesNotExist:
                return HttpResponse(status = 404)
            return super().dispatch(request)

    def create_badge(self):
        if self.instance.academic_title:
            title = self.instance.get_academic_title_display()
        else:
            title = None

        if self.instance.labcoat_size:
            labcoat_size = self.instance.get_labcoat_size_display()
        else:
            labcoat_size = None

        if self.instance.overshoe_size:
            overshoe_size = self.instance.get_overshoe_size_display()
        else:
            overshoe_size = None

        if self.instance.entrance:
            entrance = self.instance.get_entrance_display()
        else:
            entrance = None

        return RUBIONBadge(
            self.instance.first_name, 
            self.instance.last_name,
            self.instance.get_workgroup(),
            title,
            labcoat_size,
            overshoe_size,
            entrance
        )

        
    def get( self, request ):
#        response = HttpResponse(content_type='application/pdf')
#        response['Content-Disposition'] = 'attachement; filename="badge-{}.pdf"'.format(self.instance.name)
        badge = self.create_badge()
        
        from userinput.rai.documents import RubionUserBadgeDocument
            
        filename='badge-{}.pdf'.format(self.instance.name)
        collection = RubionUserBadgeDocument.collection().get_obj()
        title = RubionUserBadgeDocument.title
        description = RubionUserBadgeDocument.description
        key = RubionUserBadgeDocument.identifier
        
        file = ContentFile(badge.for_content_file())
        doc = RAIDocument(
            title = title,
            collection = collection,
            description = description,
            uploaded_by_user = request.user,
        )
        doc.file.save(filename, file)
        rel = RubionUserBadgeDocument.relation(
            key = key,
            doc = doc,
            decorated_model = self.instance
        )
        rel.save()
        return JsonResponse({
            'status' : 200,
            'content': '<a class="btn" href="{}"><span><i class="fas fa-download"></i> Dokument herunterladen</span></a>'.format(doc.file.url)
        })
        # return badge.get_in_responseresponse)


class AddInstructionsDatesView(RAIAdminView, PageMenuMixin):
    template_name = 'userinput/rubionuser/rai/views/add-instructions.html'
    form = None
    save_button = True
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'form' : self.form,
            'page_menu' : self.get_page_menu()
        })

        return context
    
    def get(self, request, *args, **kwargs):
        if not self.form:
            self.form = AddInstructionsForm()

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.form = AddInstructionsForm(request.POST)
        if self.form.is_valid():
            self.form.save()
            self.success_message('Die Daten wurden gespeichert.')
            self.form = None
            
        return self.get(request)


class SafetyInstructionView(ListView):
    template_name = 'userinput/safety_instructions/rai/list.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.raiadmin.model = SafetyInstructionUserRelation

    def get_queryset(self):
        # I have asked a question at SO for this:
        # https://stackoverflow.com/questions/65198595/filter-distinct-queryset-by-fields-of-a-foreignkey
        # but until now (same day as the question), the answer does not help.
        # Below are some approaches to get what I want. Since we do also have to find
        # something for "has never been instructed" this is the best way I can imagine.
        # However, it's annoyingly slow.

        # qs = (
        #     SafetyInstructionUserRelation.objects
        #     .filter(rubion_user__isnull = False)
        #     .distinct('instruction', 'rubion_user')
        #     .order_by('rubion_user', 'instruction', '-date')
        # )
        # su_qs = (
        #     SafetyInstructionUserRelation.objects
        #     .filter(rubion_staff__isnull = False)
        #     .distinct('instruction', 'rubion_staff')
        #     .order_by('rubion_staff', 'instruction', '-date')
        # )

        # rval = [
        #     data for data in qs.union(su_qs).order_by('date') \
        #     if (data.rubion_user and data.rubion_user.safety_instructions.filter(instruction = data.instruction, as_required=False).exists()) or (data.rubion_staff and data.rubion_staff.safety_instructions.filter(instruction = data.instruction, as_required=False).exists()) 
        # ]

        # Show only:
        #   -- users which are active
        user_list = RUBIONUser.objects.active()
        ruser_filter = Q(user__in = user_list)
        staff_list = StaffUser.objects.active()
        # we only want the staff that is not also a RUBIONUser.
        staff_list = staff_list.exclude(
            Q(user__pk__in = user_list.values('linked_user'))
        )
        staff_filter = Q(staff__in = staff_list)
        
        #   -- instructions which are required (as_required set to False)
        ruser_filter &= Q(as_required = False)
        staff_filter &= Q(as_required = False)

        #   -- only the selected instructions (filter user_safety_instructions)
        si_filter = self.filter_spec.get('user_safety_instructions', {})
        if si_filter and si_filter.get('value', []):
            ruser_filter &= Q(instruction__pk__in = si_filter['value'])
            staff_filter &= Q(instruction__pk__in = si_filter['value'])
        qs_rubion_user = SafetyInstruction2UserRelation.objects.filter(ruser_filter)
        qs_staff_user = SafetyInstruction2StaffRelation.objects.filter(staff_filter)
        result = []
        pks = []
        virtual_pks = []
        # if one wants to use a quick'n'dirty approach to get the number of database hits
        # for this, use the following
        
        # from django.db import connection
        # old = len(connection.queries)
        for obj in qs_rubion_user:
            try:
                result.append(
                    SafetyInstructionUserRelation.objects.filter(rubion_user = obj.user, instruction = obj.instruction).latest('date')
                )
                pks.append(result[-1].pk)
            except SafetyInstructionUserRelation.DoesNotExist:
                staff = None
                if obj.user.linked_user:
                    try:
                        staff = StaffUser.objects.get(user = obj.user.linked_user)
                    except StaffUser.DoesNotExist:
                        pass
                result.append(SafetyInstructionUserRelation(
                    rubion_user = obj.user,
                    rubion_staff = staff,
                    instruction = obj.instruction,
                    date = None,
                ))
                if obj.user.linked_user:
                    virtual_pks.append('{}__{}'.format(obj.user.linked_user.username, obj.instruction))
                
        for obj in qs_staff_user:
            try:
                tmp = SafetyInstructionUserRelation.objects.filter(rubion_staff = obj.staff, instruction = obj.instruction).latest('date')
                if tmp.pk not in pks:
                    result.append(tmp)
            except SafetyInstructionUserRelation.DoesNotExist:
                if obj.staff.user:
                    vpk = '{}__{}'.format(obj.staff.user.username, obj.instruction)
                else:
                    vpk = ''
                #if vpk not in virtual_pks:
                result.append(SafetyInstructionUserRelation(
                    rubion_staff = obj.staff,
                    instruction = obj.instruction,
                    date = None,
                ))


        # now, select (on python level) only those whose validity period is 
        # nearly (80%) over
        # maybe this could be done on the database level with F-expressions
        # https://docs.djangoproject.com/en/2.1/ref/models/expressions/#django.db.models.F
        today = datetime.date.today()

        result2 = []
        for res in result:

            if not res.date:
                result2.append(res)
            else:
                # validity in days without caring about leap years
                validity = 365 * res.instruction.is_valid_for * .2
                cutoff_date = today - datetime.timedelta(days = validity)
                if res.date < cutoff_date:
                    result2.append(res)
            
        # again for getting the database hits
        # new = len(connection.queries)
        # print('Queries: {}'.format(new-old))

        # return the results sorted by date (None first, then oldest)
        return sorted(result2, key = lambda item: (item.date is not None, item.date))
                    
