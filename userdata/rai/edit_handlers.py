from .forms import UserSourceSelectionForm

from django.db.models import Max
import rai.edit_handlers as eh
from rai.edit_handlers.multiform import (
    RAIMultiFormEditHandler, RAISubFormEditHandler, RAIModelMultiFormEditHandler
)
from rai.edit_handlers.pages import RAIChooseParentHandler
from rai.edit_handlers.extended import RAIDependingFieldPanel
from rai.permissions.extended_edit_handlers import GroupSelectionPanel
from rai.widgets import RAISelect, RAITextInput

class ChooseStaffGroupHandler(RAIChooseParentHandler):
    # We do have a container that allows StaffUsers and Containers as children
    # but we don't want the parent container

    def compute_choices(self):
        super().compute_choices()
        max_depth = self.page_choices.aggregate(Max('depth'))
        self.page_choices = self.page_choices.filter(depth = max_depth['depth__max'])

create_staff_edit_handler = RAIMultiFormEditHandler([
    ChooseStaffGroupHandler(
        'parent',
        label = (
            'Welcher Mitarbeiter-Gruppe soll der neue Mitarbeiter/die neue Mitarbeiterin '
            'zugeordnet werden?'),
        heading = 'Mitarbeiter-Gruppe auswählen'
    ),
    RAISubFormEditHandler(
        'user_source',
        [
            eh.RAIFieldPanel('make_user_from'),
            RAIDependingFieldPanel('rub_login_id', depends_on = {
                'make_user_from' : ['is_staff', 'is_rub']
            }, widget = RAITextInput),
            GroupSelectionPanel('groups', depends_on = {
                'make_user_from' : ['is_staff']
            })
        ],
        formclass = UserSourceSelectionForm,
        heading="Aufgaben innerhalb des RUBIONtail-Verwaltungstools"
    ),
    RAIModelMultiFormEditHandler('staffuser_data', [
        eh.RAICollectionPanel(
            [
                eh.RAIFieldRowPanel([
                    eh.RAIFieldPanel('first_name', classname="col-md-6"),
                    eh.RAIFieldPanel('last_name', classname="col-md-6"),
                    eh.RAIFieldPanel('grade', classname="col-md-6"),

                    eh.RAIFieldPanel('sex', classname="col-md-6", widget = RAISelect),
                    
                ], heading = "Angaben zur Person"),
                eh.RAIFieldRowPanel([
                    eh.RAIFieldPanel('email', classname="col-md-12"),
                    eh.RAIFieldPanel('phone', classname="col-md-4"),
                    eh.RAIFieldPanel('room', classname="col-md-4"),
                    eh.RAIFieldPanel('fax', classname="col-md-4", widget = RAITextInput),
                ], heading = "Angaben zur Erreichbarkeit"),


            ],
        )
    ], heading = 'Angaben zum neuen Mitarbeiter/zur neuen Mitarbeiterin'
    ),
    RAIModelMultiFormEditHandler('staffuser_contract', [
        eh.RAICollectionPanel(
            [
                eh.RAIFieldRowPanel([
                    eh.RAIFieldPanel(
                        'hired_by_rubion',
                        classname="",
                        label = 'Ist der neue Mitarbeiter/die neue Mitarbeiterin durch das RUBION angestellt?',
                    ),

                    eh.RAIFieldPanel(
                        'expire_at',
                        classname="",
                        label='Vertragsende',
                        help_text = 'Bei permanenten Mitarbeitern dieses Feld leer lassen.'),
                ], heading = 'Vertragsstatus'),
                eh.RAIInlinePanel('roles', panels=[
                    eh.RAIFieldPanel('role'),
                ], heading = 'Aufgaben im RUBION', show_all_options = True)
            ],
        )
    ], heading = 'Angaben zum neuen Mitarbeiter/zur neuen Mitarbeiterin'
    )


])
