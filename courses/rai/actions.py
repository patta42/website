from .edit_handlers import course_create_handler
from .filters import CoursesTimeFilter, CoursesFilter

from rai.actions import (
    ListAction, DetailAction, CreateAction
)
from rai.permissions.utils import user_can_edit

class CoursesDetailAction(DetailAction):
    label = 'Teilnehmer verwalten'
    icon = 'users'
    def show(self, request):
        return user_can_edit(request, self.get_rai_id())


class CoursesListAction(ListAction):
    list_filters = [
        CoursesTimeFilter,
        CoursesFilter
    ]
    list_item_template = 'courses/rai/course-dates/list-item.html'

class CourseCreateAction(CreateAction):
    edit_handler = course_create_handler
