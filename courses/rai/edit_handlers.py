from .forms import CourseChooseParentForm
from .widgets import RAIAttendeeSelectWidget

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

import rai.edit_handlers as eh
from rai.edit_handlers.extended import RAIStreamFieldPanel 
from rai.edit_handlers.multiform import (
    RAIMultiFormEditHandler, RAISubFormEditHandler, RAIModelMultiFormEditHandler
)
from rai.widgets import RAISwitchInput, RAISelect

class CourseSettingsPanel(eh.RAIFieldPanel):
    field_template = "courses/rai/edit_handlers/course-settings-panel_as-field.html"
    def __init__(self, field_name, parent_prefix, parent_id_field, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(field_name, *args, **kwargs)
        self.parent_prefix = parent_prefix
        self.parent_id_field = parent_id_field
        self.request = request


    def clone(self):
        print('Cloning CourseSettingsPanel')
        return super().clone()
    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs['parent_prefix'] = self.parent_prefix
        kwargs['parent_id_field'] = self.parent_id_field
        if self.request:
            kwargs['request'] = self.request 
        return kwargs
    
    
    def render_as_field(self):
        if self.instance and self.instance.pk:
            self.parent = self.instance.get_parent()
        else:
            self.parent = None
        return mark_safe(render_to_string(self.field_template, {
            'field': self.bound_field,
            'parent_field' : self.parent,
            'field_type': self.field_type(),
            'classes' : self.classes()
        }))        
        

course_create_handler = RAIMultiFormEditHandler([
    RAISubFormEditHandler(
        'parent',
        [
            eh.RAIFieldPanel('parent')
        ],
        formclass=CourseChooseParentForm,
        heading = 'Was für eine Veranstaltung soll angelegt werden?'
    ),
    RAIModelMultiFormEditHandler(
        'dates', [
            eh.RAICollectionPanel([
                eh.RAIFieldRowPanel([
                    eh.RAIFieldPanel('start', classname =" col-md-6", label="Beginn (Datum)"),
                    eh.RAIFieldPanel('end', classname =" col-md-6", label="Ende (Datum)", help_text="Bei eintägigen Veranstaltungen bitte leer lassen")
                ], heading="Start- und Enddatum der Veranstaltung"),
                eh.RAIFieldPanel('go_live_at', classname="col-md-6", label="Veröffentlichungszeitpunkt auf der Homepage", help_text=" Die Veröffentlichung erfolgt nicht exakt zum angegebenen Zeitpunkt, sondern zur jeweiligen vollen Stunde, die nach dem angegebenen Zeitpunkt liegt. Für sofortige Veröffentlichung bitte leer lassen.")
            ])
        ],
        heading = 'Von wann bis wann findet die Veranstaltung statt?'
    ),
    RAIModelMultiFormEditHandler(
        'settings',
        [
            eh.RAICollectionPanel(
                [
                    eh.RAIFieldPanel(
                        'register_via_website',
                        label = 'Sollen sich Teilnehmer über die Webseite regstrieren können?',
                        widget = RAISwitchInput
                    ),
                    eh.RAIFieldPanel('max_attendees', label = "Maximale Anzahl an Teilnehmern"),
                    eh.RAIFieldPanel(
                        'share_data_via_website',
                        label = "Soll der Datenaustausch zwischen den Teilnehmern über die Webseite ermöglicht werden?",
                        widget = RAISwitchInput
                    ),
                    eh.RAICollectionPanel([
                        eh.RAIInlinePanel(
                            'attendee_types',
                            [
                                eh.RAIFieldPanel('attendee', widget = RAIAttendeeSelectWidget),
                                eh.RAIFieldPanel('price', label="Teilnahmegebühr"),
                                eh.RAIFieldPanel('max_attendees', label="Maximale Teilnehmerzahl für diesen Teilnehmertyp"),
                                eh.RAIFieldPanel(
                                    'waitlist',
                                    label="Warteliste für diesen Teilnehmertyp aktivieren?",
                                    widget = RAISwitchInput
                                ),
#                                eh.RAIFieldPanel('attendee_name_en'),
#                                eh.RAIFieldPanel('attendee_name_de'),
#                                eh.RAIFieldPanel('description_en'),
#                                eh.RAIFieldPanel('description_de'),
                            ],
                            show_all_options = True,
                            label = "Teilnehmer-Typen und zu erfassende Daten"
                        )
                    ])
                ]
            )
        ], heading = 'Einstellungen'
    )
    # @TODO StreamField...
])


course_edit_script_handler = eh.RAIPillsPanel([
    eh.RAIObjectList([
        eh.RAIFieldPanel('script_title', label='Titel des Skripts'),
        eh.RAIFieldPanel('script_subtitle1', label='Untertitel des Skripts (Zeile 1)'),
        eh.RAIFieldPanel('script_subtitle2', label='Untertitel des Skripts (Zeile 2)'),
        eh.RAIFieldPanel('script_date', label = 'Sprache des Datums des Skripts (oder kein Datum)', widget=RAISelect),
    ], heading = 'Titelseite'),
    eh.RAIObjectList([
        RAIStreamFieldPanel('script')         
    ], heading = "Kapitel und Folien")
])

