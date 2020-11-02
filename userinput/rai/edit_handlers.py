
from .definitions import RUBIONUserInfoPanel, WorkgroupInformationPanel
from .forms import (
    GroupLeaderForm,  WorkgroupStatusForm, RUBIONUserSourceForm,
    RUBIONUserWorkgroupForm, ProjectWorkgroupForm, ProjectMethodsForm,
    ProjectStatusForm, ProjectNuclidesForm
)

#from django.urls import reverse

from userinput.models import RUBIONUser, Project
from userinput.rai.widgets import (
    UserinputPublicationWidget, UserinputThesisWidget
)

import rai.edit_handlers as eh
from rai.widgets import (
    RAIRadioInput, RAISelectMultiple, RAISelect,
    RAIRadioSelect, RAISelectMultipleSelectionLists,
    RAIExtendedFileInput, RAISwitchInput,
    RAISelectMultipleCheckboxes, RAITextarea,
    RAINuclideSelect
)
from rai.comments.edit_handlers import CommentPanel

from rai.edit_handlers.extended import RAIDependingFieldPanel
from rai.edit_handlers.multiform import (
    RAIMultiFormEditHandler, RAISubFormEditHandler, RAIModelMultiFormEditHandler
)


from rai.files.edit_handlers import FileListPanel, OnDemandFileListPanel

from userinput.rai.collections import RUBIONUserDocumentCollection

from website.models import SentMail
from website.rai.edit_handlers import SentMailPanel


project_edit_handler = eh.RAIPillsPanel([
    eh.RAIUserDataPanel([
        eh.RAIObjectList([
            eh.RAICollapsablePanel([
                eh.RAITranslatedContentPanel(
                    {'de':'german', 'en':'english'},
                    ['title', 'summary'],
                    heading ="Projekt-Angaben"
                ),
            ], heading="Projekt-Informationen", is_expanded=True),
            eh.RAICollapsablePanel([
                eh.RAIFieldPanel('is_confidential', classname="col-md-12"),
            ], heading = "Einstellungen"), 
        ], heading = 'öffentliche Informationen'),#, is_expanded = False),
        
    ], heading = 'Nutzer-Angaben'),#, is_expanded = False),
    eh.RAIInlinePanel('related_methods', panels=[
        eh.RAIFieldPanel('page')
    ], heading="benutzte Methoden", show_all_options = True),
    eh.RAIInlinePanel('related_nuclides', panels=[
        eh.RAIFieldRowPanel([
            eh.RAIFieldPanel('snippet', classname = 'col-md-12', widget = RAINuclideSelect),
            eh.RAIFieldPanel('room', classname = 'col-md-4'),
            eh.RAIFieldPanel('max_order', classname = 'col-md-4', label="Maximale Bestellmenge", help_text="Angabe in MBq"),
            eh.RAIFieldPanel('amount_per_experiment', classname = 'col-md-4', label="Menge pro Experiment", help_text="Angabe in MBq"),
        ],heading = 'Nuklidangaben',)
    ], heading='Benutzte Nuklide', add_button_label = 'Weiteres Nuklid hinzufügen'),
    
    eh.RAIUserDataPanel([
        eh.RAIMultiFieldPanel([
            eh.RAIFieldPanel('uses_gmos', classname="col-md-12", widget=RAISwitchInput),
            eh.RAIFieldPanel('gmo_info', classname="col-md-12"),
        ], heading="Info on GMOs", classname='form-row'),
        eh.RAIMultiFieldPanel([
            eh.RAIFieldPanel('uses_chemicals', classname="col-md-12"),
            eh.RAIFieldPanel('chemicals_info', classname="col-md-12"),
        ],  heading="Info on chemicals", classname='form-row'),
    eh.RAIMultiFieldPanel([
        eh.RAIFieldPanel('uses_hazardous_substances', classname="col-md-12"),
        eh.RAIFieldPanel('hazardous_info', classname="col-md-12"),
    ], heading="Info on hazardous substance", classname='form-row'),
        eh.RAIMultiFieldPanel([
            eh.RAIFieldPanel('biological_agents', classname="col-md-12"),
            eh.RAIFieldPanel('bio_info', classname="col-md-12"),
        ], heading="Info on biological substances", classname='form-row')
    ], heading = 'Safety information', is_expanded = True),
    CommentPanel(heading="Kommentare"),
    eh.RAICollectionPanel([
        eh.RAIFieldRowPanel([
            eh.RAIFieldPanel('expire_at', classname="col-md-6", label="Projektende"),
            eh.RAIFieldPanel('first_published_at', classname="col-md-6", label="Projektbeginn"),
        ], heading = 'Start und Ende'),
        eh.RAIFieldRowPanel([
            eh.RAIFieldPanel('max_prolongations', classname="col-md-6",
                             help_text="Wie oft darf das Projekt ohne Angaben zu einer Publikation oder Förderung verlängert werden?"),
            eh.RAIFieldPanel('cnt_prolongations', classname="col-md-6")
            
        ], heading = 'Einstellungen')
    ], heading = 'Laufzeiten & Verlängerung'),
    eh.RAIObjectList([
        eh.RAIInlinePanel(
            'related_publications',
            panels = [
                eh.RAIFieldRowPanel(
                    [
                        eh.RAIFieldPanel(
                            'snippet',
                            classname = 'col-md-12',
                            widget = UserinputPublicationWidget,
                            label="Bekannte Publikation"
                        )
                    ],
                    heading = 'Ausgewählte Publikation')
            ],
            heading="Publikation",
            add_button_label = 'Weitere Publikation hinzufügen'),
        eh.RAIInlinePanel(
            'related_theses',
            panels = [
                eh.RAIFieldRowPanel(
                    [
                        eh.RAIFieldPanel(
                            'snippet',
                            classname = 'col-md-12',
                            widget = UserinputThesisWidget,
                            label="Ausgewählte Abschlussarbeit"
                        )
                    ],
                    heading="Abschlussarbeiten")
            ],
            heading = 'Abschlussarbeit',
            add_button_label = 'Weitere Abschlussarbeit hinzufügen'),
        #eh.RAIInlinePanel('related_publications'),
    ], heading="wissenschaftliche Resultate")
])


def get_members(wg):
    qs = RUBIONUser.objects.active().descendant_of(wg)
    return qs

def get_projects(wg):
    return Project.objects.active().descendant_of(wg)

workgroup_edit_handler = eh.RAIPillsPanel([
    WorkgroupInformationPanel(heading = 'Übersicht'), 
    eh.RAIUserDataPanel([
        eh.RAITranslatedContentPanel(
            {'de':'german', 'en':'english'},
            ['title', 'department', 'institute']
        ),
        eh.RAIFieldPanel('homepage')
    ], heading = 'User data', is_expanded = False),
    eh.RAICollapsablePanel([
        eh.RAIFieldPanel('internal_rubion_comment')
    ], heading = 'Internal comment', is_expanded = True),
    eh.RAIQueryInlinePanel(
        'members', RUBIONUser, get_members,
        [
            eh.RAIMultiFieldPanel([

                eh.RAIReadOnlyPanel('name_db', classname="col-md-3", disabled = True, label = "Name" ),
                eh.RAIReadOnlyPanel('first_name_db', classname="col-md-3", disabled = True, label = "Vorname"),
                eh.RAIFieldPanel('is_leader', classname="col-md-2", widget = RAIRadioInput),
                eh.RAIFieldPanel('may_create_projects', classname="col-md-2"),
                eh.RAIFieldPanel('may_add_members', classname="col-md-2"),
            ], classname = 'display-as-table-row')
        ] , heading="Members", long_heading = "Mitglieder der Arbeitsgruppe", allow_add = True, classname="display-as-table unique--is_leader"
    ),
    eh.RAIQueryInlinePanel(
        'projects', Project, get_projects,
        [
            eh.RAITranslatedContentPanel(
                {'de':'german', 'en':'english'},
                [
                    'title'
                ], classname="display-as-table-row"
            )
        ] , heading="Projects", allow_add = True, classname="display-as-table"
    )
])

workgroup_create_edit_handler = RAIMultiFormEditHandler([
    
    RAIModelMultiFormEditHandler('workgroup_data_de',[
        eh.RAICollectionPanel([
            eh.RAIMultiFieldPanel(
                [
                    eh.RAIFieldPanel(
                        'title_de',
                        label="Name der Arbeitsgruppe"
                    ),
                    eh.RAIFieldPanel('department_de', label="Abteilung"),
                    eh.RAIFieldPanel('institute_de',label="Institut"),
                    eh.RAIFieldPanel('university_de', label="Universität"),
                ],
                heading = "Name und Adresse in deutscher Sprache",
                classname ="input-language input-language-german"
            ),
            eh.RAIFieldPanel(
                'homepage',
                heading ="Homepage der Arbeitsgruppe",
                
            )
        ])
    ], heading = "Angaben zur neuen Arbeitsgruppe in deutscher Sprache"),
    
    RAIModelMultiFormEditHandler('workgroup_data_en',[
        eh.RAICollectionPanel([
            eh.RAIMultiFieldPanel(
                [
                    eh.RAIFieldPanel('title', label="Name der Arbeitsgruppe", help_text=None),
                    eh.RAIFieldPanel('department_en'),
                    eh.RAIFieldPanel('institute_en'),
                    eh.RAIFieldPanel('university_en'),
                ],
                heading = "Name und Adresse in englischer Sprache",
                classname ="input-language input-language-english"
            )
        ])
    ], heading = "Angaben zur neuen Arbeitsgruppe in englischer Sprache"),
    
    RAISubFormEditHandler(
        'group_leader', [
            eh.RAIFieldPanel('leader_source'),
            RAIDependingFieldPanel('rub_id', depends_on = {
                'leader_source': ['new_rub_user']
            }),
            RAIDependingFieldPanel('rubion_user', depends_on = {
                'leader_source': ['rubion_user']
            }),
            RAIDependingFieldPanel('staff_user', depends_on = {
                'leader_source': ['staff_user']
            }),
            eh.RAICollectionPanel([
                eh.RAIFieldRowPanel([
                    eh.RAIFieldPanel('new_user_first_name', classname="col-md-6"),
                    eh.RAIFieldPanel('new_user_last_name', classname="col-md-6"),
                    eh.RAIFieldPanel('new_user_email', classname="col-md-6"),
                    eh.RAIFieldPanel('new_user_salutation', classname="col-md-3"),
                    eh.RAIFieldPanel('new_user_academic_title', classname="col-md-3"),
                ], heading = "Angaben zum neu anzulegenden Nutzer")
            ], depends_on = {
                'leader_source': ['new_external_user']
            })
        ],
        heading = "Angaben zum Leiter der Arbeitsgruppe",
        formclass = GroupLeaderForm
    ),
    RAISubFormEditHandler('workgroup_status', [
        eh.RAIFieldPanel('status')
    ], formclass = WorkgroupStatusForm, heading ="Status der neuen Arbeitsgruppe")                          
])


def get_sent_mail(ruser):
    q = SentMail.objects.filter(to__icontains = ruser.email).order_by('-sent_at')
    return q

rubionuser_edit_handler = eh.RAIPillsPanel([
    RUBIONUserInfoPanel(heading = 'Übersicht'), 
    eh.RAIObjectList([
        eh.RAICollapsablePanel([
            eh.RAIFieldPanel('dosemeter', widget=RAISelect, classname="col-md-12"),
            eh.RAIInlinePanel('safety_instructions', panels = [
                eh.RAIFieldPanel('instruction', label="Unterweisung"),
                eh.RAIFieldPanel('as_required', label="Nur bei Bedarf"),
            ], show_all_options = True, heading="Benötigte Sicherheitsunterweisungen"),
        ], heading = 'Strahlenschutz'),
        eh.RAICollapsablePanel([
            eh.RAIInputGroupCollectionPanel([
                eh.RAIFieldPanel('needs_key'),
                eh.RAIFieldPanel('key_number')
                
            ], heading="Schlüssel"),
            eh.RAIFieldRowPanel([
                eh.RAIFieldPanel('labcoat_size', classname = 'col-md-6', widget=RAISelect),
                eh.RAIFieldPanel('overshoe_size',classname = 'col-md-6', widget=RAISelect),
                eh.RAIFieldPanel('entrance', classname = 'col-md-12', widget=RAISelect),
            ], classname = 'justify-content-between', heading="Sicherheitsausrüstung und Laboreingang" )
        ], heading = 'Labor-Organisation'),
        eh.RAIUserDataPanel([
            eh.RAIFieldRowPanel([
                eh.RAIFieldPanel('name_db', classname = 'col-md-6'),
                eh.RAIFieldPanel('first_name_db', classname = 'col-md-6'),
                eh.RAIFieldPanel('academic_title', classname = 'col-md-6', widget=RAISelect),
                eh.RAIFieldPanel('sex', classname = 'col-md-6', widget=RAISelect),
            
            ], heading = "Angaben zu Namen und Anrede"),
            eh.RAIFieldRowPanel([
                eh.RAIFieldPanel('email_db', classname = 'col-md-6'),
                eh.RAIFieldPanel('phone',  classname = 'col-md-6'),
            ], heading = 'Kontaktinforamtionen')                
                
            
        ], heading = 'Persönliche Nutzerdaten')
        
    ], heading = 'Daten'),
    eh.RAIObjectList([
        OnDemandFileListPanel('automatic_documents', heading = 'Automatsch erzeugte Dateien'), 
        FileListPanel('documents', collection = RUBIONUserDocumentCollection, heading = 'Verknüpfte Dateien'),
    ], heading = 'Dateien'),
        
    SentMailPanel('sent_mail', get_sent_mail, heading = 'E-Mails'),
    CommentPanel(heading = 'Kommentare')
    
])

rubionuser_create_handler = RAIMultiFormEditHandler([
    RAISubFormEditHandler(
        'workgroup',
        [
            eh.RAIFieldPanel('workgroup'),
        ],
        heading = 'Arbeitsgruppe auswählen',
        formclass = RUBIONUserWorkgroupForm
    ),
    RAISubFormEditHandler(
        'new_user_src', [
            eh.RAIFieldPanel('source'),
            RAIDependingFieldPanel('rub_id', depends_on = {
                'source': ['rub']
            }),
            eh.RAICollectionPanel(
                [
                    eh.RAIFieldRowPanel(
                        [
                            eh.RAIFieldPanel('ext_last_name', classname="col-md-6"),
                            eh.RAIFieldPanel('ext_first_name', classname="col-md-6"),
                            eh.RAIFieldPanel('ext_email'),
                        ],
                        heading = "Angaben zum externen Nutzer"
                    )
                ],
                depends_on = {
                    'source': ['ext']
                }
            ),
        ],
        heading = "Angaben zum neuen Nutzer",
        formclass = RUBIONUserSourceForm
    ),
    RAIModelMultiFormEditHandler(
        'contact_data',
        [
            eh.RAICollectionPanel([
                eh.RAIFieldRowPanel(
                    [
                        eh.RAIFieldPanel('academic_title', classname="col-md-4", widget=RAISelect),
                        eh.RAIFieldPanel(
                            'sex',
                            classname="col-md-4",
                            widget=RAISelect,
                            label="Geschlecht",
                            help_text='Wird für die korrekte Anrede in E-Mails benötigt.'
                        ),
                        eh.RAIFieldPanel('phone', classname="col-md-4")
                    ]
                )
            ])
        ],
        heading = "Optionale Kontaktdaten"
    ),
    RAIModelMultiFormEditHandler(
        'safety_information',
        [
            eh.RAICollectionPanel([
                eh.RAIFieldPanel('dosemeter', widget = RAISelect),
                eh.RAIFieldPanel('needs_safety_instructions', widget=RAISelectMultipleCheckboxes),
                
            ])
        ],
        heading = "Angaben zum Strahlenschutz"
    ),
    RAIModelMultiFormEditHandler(
        'lab_organization',
        [
            eh.RAICollectionPanel([
                eh.RAIFieldRowPanel([
                    eh.RAIFieldPanel('labcoat_size', classname = 'col-md-6', widget=RAISelect),
                    eh.RAIFieldPanel('overshoe_size', classname = 'col-md-6', widget=RAISelect),
                    eh.RAIFieldPanel('entrance', classname = 'col-md-12', widget=RAISelect),
                ]),
                eh.RAIFieldPanel('needs_key'),
                eh.RAIFieldPanel('key_number')
                
            ])
        ],
        heading = 'Labor-Organisation'
    )
    
])

project_create_handler = RAIMultiFormEditHandler([
    RAISubFormEditHandler(
        'workgroup',
        [
            eh.RAIFieldPanel('workgroup'),
        ],
        heading = 'Arbeitsgruppe auswählen',
        formclass = ProjectWorkgroupForm
    ),
    RAIModelMultiFormEditHandler(
        'info_german',
        [
            eh.RAICollectionPanel([
                eh.RAIFieldPanel('title_de',label="Titel des Projekts auf deutsch"),
                eh.RAIFieldPanel('summary_de', label="Zusammenfassung des Projekts"),
            ])
        ],
        heading = 'Projektinformationen auf deutsch',
    ),
    RAIModelMultiFormEditHandler(
        'info_english',
        [
            eh.RAICollectionPanel([
                eh.RAIFieldPanel('title',label="Titel des Projekts auf englisch"),
                eh.RAIFieldPanel('summary_en', label="Zusammenfassung des Projekts (in englisch)"),
            ])
        ],
        heading = 'Projektinformationen auf englisch',
        ),
    RAISubFormEditHandler(
        'methods',
        [
            eh.RAICollectionPanel([
                eh.RAIFieldPanel('methods', label="Genutzte Methoden"),
            ])
        ],
        heading = 'Angaben zu den verwendeten Methoden',
        formclass = ProjectMethodsForm
    ),
    RAIModelMultiFormEditHandler(
        'safety_information',
        [
            eh.RAICollectionPanel([
                eh.RAIFieldRowPanel([
                    eh.RAIFieldPanel(
                        'uses_gmos',
                        widget=RAISwitchInput,
                        label="Beinhaltet das Projekt die Arbeit mit genetisch veränderten Organismen?",
                        help_text=" ",
                        classname="col-md-12"
                    ),
                    RAIDependingFieldPanel(
                        'gmo_info',
                        widget = RAITextarea,
                        label="Angaben zu den verwendeten genetisch modifizierten Organismen",
                        help_text = " ",
                        classname="col-md-12",
                        depends_on = {
                            'uses_gmos': [':checked']
                        }
                    ),
                ], heading="Genetisch modifizierte Organismen"),
                eh.RAIFieldRowPanel([
                    eh.RAIFieldPanel(
                        'uses_chemicals',
                        classname="col-md-12",
                        widget=RAISwitchInput,
                        label = "Werden in dem Projekt Chemikalien verwendet?",
                        help_text = ' '
                    ),
                    RAIDependingFieldPanel(
                        'chemicals_info',
                        classname="col-md-12",
                        widget = RAITextarea,
                        label = "Angaben zu den verwendeten Chemikalien",
                        help_text = "Menge der jeweiligen Chemikalie, Sicherheitsvorschriften, etc.",
                        depends_on = {
                            'uses_chemicals': [':checked']
                        }
                    ),
                ],  heading="Chemikalien"),
                eh.RAIFieldRowPanel([
                    eh.RAIFieldPanel(
                        'uses_hazardous_substances',
                        classname="col-md-12",
                        widget=RAISwitchInput,
                        label = "Werden im Projekt Gefahrstoffe verwendet?",
                        help_text = " "
                    ),
                    RAIDependingFieldPanel(
                        'hazardous_info',
                        classname="col-md-12",
                        widget = RAITextarea,
                        label="Angaben zu den verwendeten Gefahrstoffen",
                        help_text= "Menge, Sicherheitsmaßnahmen, etc.",
                        depends_on = {
                            'uses_hazardous_substances': [':checked']
                        }
                    ),
                ], heading="Gefahrstoffe"),
                eh.RAIFieldRowPanel([
                    eh.RAIFieldPanel(
                        'biological_agents',
                        classname="col-md-12",
                        widget=RAISwitchInput,
                        label="Beinhaltet das Projekt Arbeiten, die unter die Biostoffverordnung fallen?",
                        help_text = " "
                    ),
                    RAIDependingFieldPanel(
                        'bio_info',
                        classname="col-md-12",
                        widget = RAITextarea,
                        label = "Angaben zu den Arbeiten unter Biostoffverordnung",
                        help_text = ' ',
                        depends_on = {
                            'biological_agents': [':checked']
                        }
                    ),
                ], heading="Biostoffverordnung")
            ])
    ], heading = 'Angaben zu Gefahrstoffen'),
    RAIModelMultiFormEditHandler(
        'related_nuclides',
        [
            eh.RAICollectionPanel([
                eh.RAIInlinePanel(
                    'related_nuclides',
                    [
                        eh.RAIFieldRowPanel([
                            eh.RAIFieldPanel('snippet', classname="col-md-12", widget = RAINuclideSelect),
                            eh.RAIFieldPanel('room', classname="col-md-4"),
                            eh.RAIFieldPanel('max_order', classname = 'col-md-4', label="Maximale Bestellmenge", help_text="Angabe in MBq"),
                            eh.RAIFieldPanel('amount_per_experiment', classname = 'col-md-4', label="Menge pro Experiment", help_text="Angabe in MBq"),
                        ],
                        heading = "Angaben zum Nuklid",
                        )
                    ],
                    add_button_label = 'Weiteres Nuklid hinzufügen'
                )
            ]),
        ],
        heading = "Im Projekt genutzte Nuklide",
        formclass = ProjectNuclidesForm            

    ),
    RAISubFormEditHandler(
        'status',
        [
            eh.RAICollectionPanel([
                eh.RAIFieldPanel('status'),
                eh.RAIFieldPanel('public')
            ])
        ],
        heading = 'Angaben zum Projektstatus',
        formclass = ProjectStatusForm
    ),

])
