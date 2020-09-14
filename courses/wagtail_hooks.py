from .admin_views import AddCourseChooseCourseInfoView, CourseDateInspectView, ScriptView
from .filters import CoursesDateFilter, CoursesOrgaFilter
from .helpers import AttendeeButtonHelper, CourseButtonHelper
from .models import (
    Course, CourseInformationPage, ListOfCoursesPage, SskStudentAttendee,
    SskRubMemberAttendee, SskHospitalAttendee, SskExternalAttendee, SskExternalStudentUARuhr,
    StudentAttendee
)


from django.conf.urls import url

from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _l

from rubionadmin.admin import HiddenModelAdmin


from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register
)

from wagtail.contrib.modeladmin.helpers import PagePermissionHelper

from wagtail.admin.menu import MenuItem
from wagtail.core.models import PageViewRestriction




class CourseModelAdminMenuItem(MenuItem):
    # It is annoying to create a new class just for adding a (hardcoded!) parameter to the URL.
    # But it works.
    def __init__(self, model_admin, order):

        self.model_admin = model_admin
        url = model_admin.url_helper.index_url + '?status=upcoming'
        classnames = 'icon icon-%s' % model_admin.get_menu_icon()
        super(CourseModelAdminMenuItem, self).__init__(
            label=model_admin.get_menu_label(), url=url,
            classnames=classnames, order=order)

    def is_shown(self, request):
        return self.model_admin.permission_helper.user_can_list(request.user)


class ListOfCoursesPageMA( HiddenModelAdmin ):
    exclude_from_explorer = True
    model = ListOfCoursesPage

modeladmin_register(ListOfCoursesPageMA)

class CoursePermissionHelper( PagePermissionHelper ):
    def user_can_inspect_obj(self, usr, obj):
        return self.user_can_edit_obj(usr, obj)

class CourseModelAdmin(ModelAdmin):
    model = Course
    menu_label = _l('Course dates')
    menu_icon = ' icon-fa-graduation-cap'  
    menu_order = 200  
    add_to_settings_menu = False  
    exclude_from_explorer = True
    list_display = ('course_info', 'start', 'end', 'attendees', 'free_slots', 'data_sharing')
    list_filter = (CoursesDateFilter, CoursesOrgaFilter, )
    inspect_view_enabled = True
    inspect_view_class = CourseDateInspectView
    
    choose_parent_view_class = AddCourseChooseCourseInfoView
    choose_parent_template_name = 'courses/admin/choose_course.html'
    
    button_helper_class = CourseButtonHelper

    permission_helper_class = CoursePermissionHelper

    def course_info( self, obj ):
        return obj.get_parent().specific.title_trans
    course_info.short_description = _l('Course')

    def attendees( self, obj ):
        attendees = []
        for at, num in obj.registered_attendees_stats.items():
            attendees.append("{}: {}".format(at, num) )
        return mark_safe("<br/>".join( attendees ))
    
    attendees.short_description = _l('Attendees')
            
    def free_slots( self, obj ):
        pass
    
    def get_menu_item(self, order=None):
        return CourseModelAdminMenuItem(self, order or self.get_menu_order())                

    def data_sharing(self, obj):
        dsp = obj.get_data_sharing_page()
        if dsp:
            pvr = PageViewRestriction.objects.filter(page = dsp).first()
            if pvr:
                return pvr.password
            else:
                return None
        else:
            return mark_safe('<em>{}</em>'.format(_l('No data sharing')))

    def script_view(self, request, instance_pk):
        kwargs = { 'model_admin' : self, 'instance_pk' : instance_pk }
        return ScriptView.as_view(**kwargs)(request)
        
    def get_admin_urls_for_registration(self):
        urls = super(CourseModelAdmin,self).get_admin_urls_for_registration()
        return urls + (
            url(
                self.url_helper.get_action_url_pattern('script'),
                self.script_view,
                name = self.url_helper.get_action_url_name('script')
            ),
        )

class CourseInformationPageModelAdmin( ModelAdmin ):
    model = CourseInformationPage
    menu_label = _l('courses')
    menu_icon = 'fa-calendar'
    exclude_from_explorer = True
    list_display = ('_title',)

    
    def _title( self, obj):
        return obj.title_trans
    _title.short_description = _('Title')
    
class StudentAttendeeMA( ModelAdmin ):
    model = StudentAttendee
    button_helper_class = AttendeeButtonHelper
    
class SskStudentAttendeeMA( ModelAdmin ):
    model = SskStudentAttendee
    button_helper_class = AttendeeButtonHelper
    
class SskExternalAttendeeMA( ModelAdmin ):
    model = SskExternalAttendee
    button_helper_class = AttendeeButtonHelper

class SskHospitalAttendeeMA( ModelAdmin ):
    model = SskHospitalAttendee
    button_helper_class = AttendeeButtonHelper

class SskRubMemberAttendeeMA( ModelAdmin ):
    model = SskRubMemberAttendee
    button_helper_class = AttendeeButtonHelper

class SskExternalStudentUARuhrMA( ModelAdmin ):
    model = SskExternalStudentUARuhr
    button_helper_class = AttendeeButtonHelper


class CoursesModelAttendeesGroup ( ModelAdminGroup ):
    menu_label = _l('Attendees')
    menu_order = 40
    menu_icon = 'fa-graduation-cap'  
    items = (SskStudentAttendeeMA, )    


class CoursesModelAdminGroup ( ModelAdminGroup ):
    menu_label = _l('Teaching')
    menu_order = 40
    menu_icon = 'fa-graduation-cap'  
    items = (
        CourseInformationPageModelAdmin, CourseModelAdmin, 
        SskStudentAttendeeMA, SskExternalAttendeeMA,
        SskHospitalAttendeeMA, SskRubMemberAttendeeMA, SskExternalStudentUARuhrMA,
        StudentAttendeeMA
    )


# Now you just need to register your customised ModelAdmin class with Wagtail
modeladmin_register(CoursesModelAdminGroup)
# RAI

from rai.base import rai_register
from rai.mail.base import register_mail_template

from courses.rai.mail import CourseResultMail
from courses.rai.register import RAITeachingGroup

rai_register(RAITeachingGroup)
register_mail_template(CourseResultMail)
