from pprint import pprint


from django.contrib.auth import get_user_model
from django.template.response import TemplateResponse
from django.urls import reverse, resolve
from django.utils.text import slugify


from rai.default_views import ListView, EditView
from rai.default_views.multiform_create import  MultiFormCreateView

from userdata.models import (
    StaffUser, StaffUser2RoleRelation, Beirat2StaffRelation, BeiratGroups,
    StaffRoles, UserContainer
)
from userdata.rai.forms import BeiratMemberReplaceForm
from userinput.models import RUBIONUser

from wagtail.core.models import Page


class StaffUserCreateView(MultiFormCreateView):
    def prepare_next_form(self, prefix):
        if prefix == 'staffuser_data':
            # we might have a login_id
            user_id = self.session_store['user_source']['form'].get('rub_login_id', None)
            if user_id:
                User = get_user_model()
                try:
                    user = User.objects.get(username = user_id)
                except User.DoesNotExist:
                    user = None
                if user:
                    try:
                        ruser = RUBIONUser.objects.get(linked_user = user)
                    except RUBIONUser.DoesNotExist:
                        ruser = None
                    if ruser:
                        initial = {
                            'email' : ruser.email,
                            'first_name' : ruser.first_name,
                            'last_name' : ruser.last_name,
                            'phone' : ruser.phone,
                            'sex' : ruser.sex,
                            'grade': ruser.get_academic_title_display(),
                            'key_number': ruser.key_number
                        }
                        self.info_message('Unter dem RUB-Login {} ist ein Nutzer bekannt. Die Felder wurden vorausgefüllt.'.format(user_id))
                        self.form = self.formclass(initial = initial)
                    
    def finalize(self, request):
        pprint (self.session_store)
        parent_page = Page.objects.get(pk = self.session_store['parent']['form']['parent_page'])
        user_data = self.session_store['staffuser_data']['form']
        staff_user = StaffUser()

        # Make website user
        if self.session_store['user_source']['form']['make_user_from'] == 'is_staff':
            login_id = self.session_store['user_source']['form']['rub_login_id']
            User = get_user_model()
            
            try:
                user = User.objects.get(username = login_id)
            except User.DoesNotExist:
                user = User()
                for field in ['last_name', 'first_name', 'email']:
                    setattr(user, field, user_data.get(field))
                user.username = login_id
                user.is_staff = True
                user.is_active = True
                user.save()
                
            staff_user.user = user

        # make StaffUser
        user_data.update(self.session_store['staffuser_contract']['form'])
        print(staff_user)
        del(user_data['multiform_step_counter'])
        for field, value in user_data.items():
            setattr(staff_user, field, value)
        staff_user.title = '{} {}'.format(user_data['first_name'], user_data['last_name'])
        staff_user.title_de = '{} {}'.format(user_data['first_name'], user_data['last_name'])
        staff_user.slug = slugify(staff_user.title)
        parent_page.add_child(instance = staff_user)
        revision = staff_user.save_revision(user = request.user)
        revision.publish()
        # staff_user is saved now, should have a pk
        staff_user = revision.as_page_object().specific
        pprint(self.session_store)
        for formset_data in self.session_store['staffuser_contract']['formsets']['roles']:
            rel = StaffUser2RoleRelation(
                role = formset_data['role'], roles = staff_user
            )
            rel.save()
        self.success_message(
            'Der Mitarbeiter {} {} wurde hinzugefügt.'
            .format(user_data['first_name'], user_data['last_name']))
        # clear session
        request.session[self.session_key] = {}
        return self.redirect_to_default() 

class StaffUserRoleListView(ListView):
    template_name = 'userdata/rai/staff_user_role_list.html'

    def post(self, request):
        # generates a PDF from the list
        pass

class BeiratView(ListView):
    template_name = 'userdata/rai/beirat-list.html'

    def beirat_as_groups(self):
        """
        Sorts the beirat2staff relations 
        
        It will return a list of dicts, an a single ditc looks either like this

        { 'name' : <group name>, 'members' : <group members> }

        or, if the group is divided into sub-groups

        { 'name' : <group name>, 'subgroups' : <list of sub-groups> }

        where <list of subgroups> is a list of dicts with

        {'name' : <sub-group name>, 'members' : <members> }

        
        """

        # There should be only one Beirat head, but programmatically, we can have more than one.
        # Or None...
        heads = Beirat2StaffRelation.objects.filter(is_head = True)

        # The head of the Beirat is a member of the professors group, but this is not ensured
        # programmatically. I might have any group here...
        head_groups_pk = [] 
        for head in heads:
            if head.beirat_group.pk not in head_groups_pk:
                head_groups_pk.append(head.beirat_group.pk)

        # now loop through groups, the head_groups first, the others second

        head_groups = BeiratGroups.objects.filter(pk__in = head_groups_pk).order_by('order')
        other_groups = BeiratGroups.objects.exclude(pk__in = head_groups_pk).order_by('order')

        # the list that will be returned
        groups = []

        # get the choices for the subgroups only once:

        choices = Beirat2StaffRelation._meta.get_field('faculty_group').choices
        
        # loop through groups (| is the set union operator):
        for dbgroup in head_groups | other_groups:
            group = {'name' : dbgroup.title}
            if not dbgroup.has_sub_groups:
                # the simple way.
                # The members should be ordered by 'is_surrogate'
                # If everything is entered correctly (on the front-end level), this should
                # yield the member and its surrogate in correct order
                relations = Beirat2StaffRelation.objects.filter(beirat_group = dbgroup).order_by('is_surrogate')
                members = []
                for relation in relations:
                    group.update({})
                    if relation.member is None:
                        members.append({
                            'not_set' : True,
                            'relation_pk' : relation.pk,
                            'is_surrogate' : relation.is_surrogate,
                            'relation' : relation
                        })
                    else:
                        members.append({
                            'not_set' : False,
                            'first_name' : relation.member.first_name,
                            'last_name' : relation.member.last_name,
                            'is_surrogate' : relation.is_surrogate,
                            'is_head' : relation.is_head,
                            'relation_pk' : relation.pk,
                            'email' : relation.member.email,
                            'phone' : relation.member.phone,
                            'relation' : relation
                        })
                group.update(members = members)
            else:
                # subgroups are based on the choices property of the relation.faculty_group field
                # and have been retrieved above
                subgroups = []
                for value, name in choices:
                    subgroup = {'name' : name}
                    relations = Beirat2StaffRelation.objects.filter(beirat_group = dbgroup, faculty_group = value).order_by('is_surrogate')
                    members = []
                    for relation in relations:
                        if relation.member is None:
                            members.append({
                                'not_set' : True,
                                'relation_pk' : relation.pk,
                                'is_surrogate' : relation.is_surrogate,
                                'relation' : relation
                            })
                        else:
                            members.append({
                                'not_set' : False,
                                'first_name' : relation.member.first_name,
                                'last_name' : relation.member.last_name,
                                'email' : relation.member.email,
                                'phone' : relation.member.phone,
                                'is_surrogate' : relation.is_surrogate,
                                'is_head' : relation.is_head,
                                'relation_pk' : relation.pk,
                                'relation' : relation
                            })
                        subgroup.update(members = members)
                        
                    subgroups.append(subgroup)
                group.update(subgroups = subgroups)
            groups.append(group)
        return groups
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = self.beirat_as_groups()
        return context

class BeiratPositionReplaceView(EditView):
    formclass = BeiratMemberReplaceForm

    def form_for_post_hook(self, request):
        return self.formclass(request.POST)
    
    def remove_old_member(self, request):
        if self.obj.member:
            parent = self.obj.member.get_parent()
            if not parent.specific.show_in_list:
                self.obj.member.inactivate(user=request.user, inactivate_website_user = False)
            else:
                # remove Beirat label
                for obj in StaffUser2RoleRelation.find(
                        roles = self.obj.member,
                        role__in = beirat_labels
                ):
                    obj.delete()
            self.obj.member.save_revision(user = request.user)
            self.success_message('Die Beiratsposition wurde gespeichert.')
            
    def save_no_user(self, request, form):
        self.remove_old_member(request)
        self.obj.member = None
        self.obj.save()
            
    def save_new_user(self, request, form):
        self.remove_old_member(request)
        beirat_labels = StaffRoles.objects.filter(is_beirat = True)
        member = StaffUser(
            first_name = form.cleaned_data['first_name'],
            last_name = form.cleaned_data['last_name'],
            email = form.cleaned_data['email'],
            phone = form.cleaned_data.get('phone', None),
            title = '{} {}'.format(form.cleaned_data['first_name'], form.cleaned_data['last_name']),
            title_de = '{} {}'.format(form.cleaned_data['first_name'], form.cleaned_data['last_name']),
            slug = slugify('{} {}'.format(
                form.cleaned_data['first_name'], form.cleaned_data['last_name']))
        )
        container = UserContainer.objects.filter(show_in_list = False)[0]
        container.add_child(instance = member)
        for label in beirat_labels:
            rel = StaffUser2RoleRelation(roles = member, role = label)
            rel.save()
        revision = member.save_revision(user = request.user)
        revision.publish()
        self.obj.member = member
        self.obj.save()
        self.success_message('Das Beiratsmitglied wurde gespeichert.')

    def save_existent_user(self, request, form):
        beirat_labels = StaffRoles.objects.filter(is_beirat = True)
        user_pk = form.cleaned_data['member_selection']
        if self.obj.member:
            old_member_pk = self.obj.member.pk
            if old_member_pk == user_pk:
                # old one is new one...
                self.infomessage('Die Angaben haben sich nicht geändert.')
                return
            else:
                self.remove_old_member(request)

        new_user = Page.objects.get(pk = user_pk).specific
        if isinstance(new_user, RUBIONUser):
            # make sure there is no existing (and maybe inactivated) StaffUSer for the RUBIONUser. 
            # Otherwise, use the staff user
            try:
                new_user = StaffUser.objects.get(user = new_user.linked_user)
                if new_user.locked:
                    new_user.activate(user = request.user, activate_website_user = False)
            except StaffUser.DoesNotExist:
                pass
            

        
        if isinstance(new_user, StaffUser):
            self.obj.member = new_user
            for label in beirat_labels:
                rel = StaffUser2RoleRelation(roles = new_user, role = label)
                rel.save()
        elif isinstance(new_user, RUBIONUser):
            
            member = StaffUser(
                first_name = new_user.first_name,
                last_name = new_user.last_name,
                user = new_user.linked_user,
                email = new_user.email,
                sex = new_user.sex,
                phone = new_user.phone,
                title = '{} {}'.format(new_user.first_name, new_user.last_name),
                title_de = '{} {}'.format(new_user.first_name, new_user.last_name),
                slug = slugify('{} {}'.format(new_user.first_name, new_user.last_name))
            )
            container = UserContainer.objects.filter(show_in_list = False)[0]
            container.add_child(instance = member)
            for label in beirat_labels:
                rel = StaffUser2RoleRelation(roles = member, role = label)
                rel.save()
            revision = member.save_revision(user = request.user)
            revision.publish()
            self.obj.member = member
        self.success_message('Das Beiratsmitglied wurde gespeichert.')
        self.obj.save()

        
            
    def save_post_hook(self, request, form):
        if form.cleaned_data['source'] == 'new_user':
            self.save_new_user(request, form)
        elif form.cleaned_data['source'] == 'existent_user':
            self.save_existent_user(request, form)
        elif form.cleaned_data['source'] == 'no_user':
            self.save_no_user(request, form)
