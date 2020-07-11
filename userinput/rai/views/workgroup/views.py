from django.contrib.auth import get_user_model
from django.utils.text import slugify

from rai.default_views.multiform_create import  MultiFormCreateView

from rubauth.auth import fetch_user_info

from userinput.models import WorkGroup, RUBIONUser, WorkGroupContainer

class WorkgroupCreateView(MultiFormCreateView):

    def create_workgroup(self):
        # There should be only one WorkGroupContainer instance
        parent = WorkGroupContainer.objects.all().first() 

        # create workgroup first
        
        data_de = self.session_store['workgroup_data_de']
        data_en = self.session_store['workgroup_data_en']

        wg = WorkGroup(**{**data_de, **data_en}, owner = request.user)

        parent.add_child(instance = wg)
        revision = wg.save_revision(user = self.request.user, submitted_for_moderation = True)
        if self.session_store['workgroup_status']['form'].get('status') == 'accepted':
            revision.approve_moderation()
            revision.publish()
        member_container = wg.add_member_container()
        wg.add_project_container()

        return member_container
    
    def finalize(self, request):

        member_container = self.create_workgroup()
        
        # create or move group leader 
        gl_source = self.session_store['group_leader']['form']['leader_source']

        if gl_source == 'rubion_user':
            try: 
                user = RUBIONUser.objects.get(
                    pk = self.session_store['group_leader']['form']['rubion_user'],
                )
            except RUBIONUser.DoesNotExist:
                user = None
            if user:
                
                user.move(member_container)
                user.is_leader = True
                user.save_revision(user = request.user)
            else:
                pass
        if gl_source == 'staff_user':
            try:
                staff_user = StaffUser.objects.get(
                    pk = self.session_session_store['group_leader']['form']['staff_user'],
                )
            except StaffUser.DoesNotExist:
                staff_user = None
            if staff_user:
                rubion_user = RUBIONUser(
                    name_db = staff_user.last_name,
                    first_name_db = staff_user.first_name,
                    email_db = staff_user.email,
                    sex = staff_user.sex,
                    phone = staff_user.phone,
                    linked_user = staff_user.user,
                    key_number = staff_user.key_number,
                    title = '{} {}'.format(staff_user.first_name, staff_user.last_name),
                    title_de = '{} {}'.format(staff_user.first_name, staff_user.last_name),
                    slug = slugify('{} {}'.format(staff_user.first_name, staff_user.last_name)),
                    is_leader = True
                )
                member_container.add_child(instance = rubion_user)
                rubion_user.save_revision(user = request.user)
            else:
                pass
        if gl_source == 'new_external_user':
            UserModel = get_user_model()
            form = self.session_store['group_leader']['form']
            user = UserModel.create_user(
                username = form['new_user_email'],
                first_name = form['new_user_first_name'],
                last_name = form['new_user_last_name'],
                email = form['new_user_email']
            )
            r_user = RUBIONUser(
                linked_user = user,
                first_name_db = form['new_user_first_name'],
                last_name_db = form['new_user_last_name'],
                title_de = '{} {}'.format(form['new_user_first_name'],form['new_user_last_name']),
                title = '{} {}'.format(form['new_user_first_name'],form['new_user_last_name']),
                slug = slugify('{} {}'.format(form['new_user_first_name'],form['new_user_last_name'])),
                is_leader = True
            )
            r_user = member_container.add_child(instance = r_user)
            r_user.save_revision(user = request.user)

        if gl_source == 'new_rub_user':
            pass
