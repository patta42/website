from .actions import CoursesListAction, CoursesDetailAction, CourseCreateAction
from .views import (
    CourseAttendeeView, DeleteAttendees, edit_attendee, import_results,
    CourseCreateView, AttendeeMoveView, pdf_nameplate, pdf_certificate,
    send_results_view, send_2nd_results_view

)
from courses.models import CourseInformationPage, Course

from django.urls import path

from rai.base import RAIModelAdmin, RAIAdminGroup

from wagtail.core import hooks


class RAICourses(RAIModelAdmin):
    model = CourseInformationPage
    menu_label = 'Lehrangebot'
    menu_icon_font = 'fas'
    menu_icon = 'chalkboard-teacher'

class RAICourseDates(RAIModelAdmin):
    model = Course
    menu_label = 'Kurstermine'
    menu_icon_font = 'fas'
    menu_icon = 'calendar-day'
    detailview = CourseAttendeeView
    createview = CourseCreateView
    group_actions = [
        CoursesListAction, CourseCreateAction
    ]
    default_action = CoursesListAction
    item_actions = [
        CoursesDetailAction
    ]

    
class RAITeachingGroup(RAIAdminGroup):
    components = [
        RAICourseDates,
        RAICourses
    ]
    menu_label = 'Lehre'

@hooks.register('register_rai_url')
def rai_courses_urls():
    return [
        path('courses/attendees/delete/', DeleteAttendees.as_view(), name = 'rai_courses_attendees_delete'),
        path('courses/attendees/ajax_edit/<pk>/<field>/', edit_attendee, name = 'rai_courses_attendee_ajax_edit'),
        path('courses/attendees/ajax_edit_generic/', edit_attendee, name = 'rai_courses_attendee_ajax_edit_generic'),
        path('courses/attendees/import_results/', import_results, name = 'rai_courses_attendees_import_results'),
        path('courses/attendees/move/', AttendeeMoveView.as_view(), name = 'rai_courses_attendees_move'),
        path('courses/attendees/pdf/nameplate/', pdf_nameplate, name = 'rai_courses_attendees_pdf_nameplate'),
        path('courses/attendees/pdf/certificate/', pdf_certificate, name = 'rai_courses_attendees_pdf_certificate'),
        path('courses/attendees/ajax_send_results_mail/', send_results_view, name = 'rai_courses_ajax_send_results'),
        path('courses/attendees/ajax_send_2nd_results_mail/', send_2nd_results_view, name = 'rai_courses_ajax_send_2nd_results')
    ]
    

    
