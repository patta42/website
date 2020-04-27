from pprint import pprint

from django.contrib.auth import get_user_model
from django.utils.text import slugify
from rai.default_views.multiform_create import  MultiFormCreateView

from userdata.models import StaffUser, StaffUser2RoleRelation
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
