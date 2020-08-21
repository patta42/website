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
                eh.RAIFieldRowPanel([
                    eh.RAIFieldPanel('key_number', classname="col-md-6"),
                    eh.RAIFieldPanel('gate_key_number', classname="col-md-6"),
                ], heading = "Schlüssel"),
                

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
                        help_text = 'Bei permanenten Mitarbeitern dieses Feld leer lassen.',
                    ),
                ], heading = 'Vertragsstatus'),
                eh.RAIInlinePanel('roles', panels=[
                    eh.RAIFieldPanel('role'),
                ], heading = 'Aufgaben im RUBION', show_all_options = True)
            ],
        )
    ], heading = 'Angaben zum neuen Mitarbeiter/zur neuen Mitarbeiterin'
    )


])

edit_staff_user_handler = eh.RAIPillsPanel([
    eh.RAIObjectList([
        eh.RAICollapsablePanel([
            eh.RAIFieldRowPanel([
                eh.RAIFieldPanel ('last_name', classname="col-md-5"),
                eh.RAIFieldPanel ('first_name', classname="col-md-5"),
                eh.RAIFieldPanel ('sex', classname="col-md-2", widget=RAISelect),
                eh.RAIFieldPanel ('email', classname="col-md-4"),
                eh.RAIFieldPanel ('room', classname="col-md-4"),
                eh.RAIFieldPanel ('phone', classname="col-md-4"),
            ])
        ], heading = 'Kontaktdaten'),
        eh.RAICollapsablePanel([
            eh.RAIInlinePanel('roles', panels = [
                eh.RAIFieldPanel('role')
            ])
        ], heading = 'Aufgaben im RUBION')
 
    ], heading ="öffentliche Angaben"),
    eh.RAIObjectList([
        eh.RAIInlinePanel('safety_instructions', panels=[
            eh.RAIFieldPanel('instruction', label="Unterweisung"),
            eh.RAIFieldPanel('as_required', label="nur bei Bedarf"),
        ], show_all_options = True, heading="Sicherheitsunterweisungen")
    ], heading = 'Strahlenschutz'),
    eh.RAIObjectList([
        eh.RAICollapsablePanel([
            eh.RAIFieldPanel( 'key_number' )
        ], heading = "Schlüssel"),
        eh.RAICollapsablePanel([
            eh.RAIFieldPanel('hired_by_rubion'),
            eh.RAIFieldPanel(
                'expire_at',
                label = 'Vertrag bis',
                help_text = 'Bei permanent angestellten Mitarbeitern bitte leer lassen')
        ], heading = "Vertragsdaten")
    ], heading = 'Interna')
    
])

edit_role_handler = eh.RAIObjectList([
    eh.RAIFieldPanel('role_de'),
    eh.RAIFieldPanel('role_en'),
    eh.RAIFieldPanel('is_beirat')
])

beirat_group_edit_handler = eh.RAIObjectList([
    eh.RAIFieldPanel('title_de'),
    eh.RAIFieldPanel('title_en'),
    eh.RAIFieldPanel('order'),
    eh.RAIFieldPanel('has_sub_groups'),
])

beirat2staff_edit_handler = eh.RAIFieldList([
        eh.RAIFieldPanel('beirat_group'),
        eh.RAIFieldPanel('member'),
        eh.RAIFieldPanel('is_head'),
        eh.RAIFieldPanel('is_surrogate'),
        eh.RAIFieldPanel('faculty_group', widget = RAISelect),
], heading = "Angaben zur Mitgliedschaft im Beirat" )

beirat_replace_edit_handler = eh.RAIFieldList([
    eh.RAIFieldPanel('source'),
    eh.RAIFieldPanel('member_selection'),
    eh.RAIFieldRowPanel([
        eh.RAIFieldPanel('first_name', classname="col-md-6"),
        eh.RAIFieldPanel('last_name', classname="col-md-6"),
        eh.RAIFieldPanel('email', classname="col-md-6"),
        eh.RAIFieldPanel('phone', classname="col-md-6"),
    ], heading="Angaben zur Person")
], heading =" Angaben zum neuen Beiratsmitglied")
