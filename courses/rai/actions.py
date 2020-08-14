from .edit_handlers import course_create_handler
from .filters import CoursesTimeFilter, CoursesFilter

from rai.actions import (
    ListAction, DetailAction, CreateAction
)

class CoursesDetailAction(DetailAction):
    label = 'Teilnehmer verwalten'
    icon = 'users'

class CoursesListAction(ListAction):
    list_filters = [
        CoursesTimeFilter,
        CoursesFilter
    ]
    list_item_template = 'courses/rai/course-dates/list-item.html'

class CourseCreateAction(CreateAction):
    edit_handler = course_create_handler
