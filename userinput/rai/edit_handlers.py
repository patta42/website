from userinput.models import RUBIONUser, Project

import rai.edit_handlers as eh
from rai.widgets import (
    RAIRadioInput, RAISelectMultiple, RAISelect,
    RAIRadioSelect, RAISelectMultipleSelectionLists
)
from website.models import SentMail
from website.rai.edit_handlers import SentMailPanel

project_edit_handler = eh.RAIObjectList([
       eh.RAIUserDataPanel([
           eh.RAITranslatedContentPanel(
               {'de':'german', 'en':'english'},
               ['title', 'summary']
           ),
       ], heading = 'Project information', is_expanded = False),
        eh.RAIInlinePanel('related_methods', panels=[
            eh.RAIFieldPanel('page')
        ], heading="Methods used"),
       eh.RAIInlinePanel('related_nuclides', panels=[
           eh.RAIMultiFieldPanel([
               eh.RAIFieldPanel('room',classname = 'col-md-2'),
               eh.RAIFieldPanel('snippet',classname = 'col-md-2', widget = RAISelect),
               eh.RAIFieldPanel('max_order',classname = 'col-md-4'),
               eh.RAIFieldPanel('amount_per_experiment',classname = 'col-md-4'),
           ],heading = 'Nuclide spec', classname = 'form-row')
       ], heading='Nuclide specifications', classname="foo bar baz"),
       eh.RAIUserDataPanel([
           eh.RAIFieldPanel('is_confidential'),
       ], heading = 'Project visibility', is_expanded = False),
       eh.RAIUserDataPanel([
           eh.RAIMultiFieldPanel([
               eh.RAIFieldPanel('uses_gmos', classname="col-md-3"),
               eh.RAIFieldPanel('gmo_info', classname="col-md-9"),
           ], heading="Info on GMOs", classname='form-row'),
           eh.RAIMultiFieldPanel([
               eh.RAIFieldPanel('uses_chemicals', classname="col-md-3"),
               eh.RAIFieldPanel('chemicals_info', classname="col-md-9"),
           ],  heading="Info on chemicals", classname='form-row'),
           eh.RAIMultiFieldPanel([
               eh.RAIFieldPanel('uses_hazardous_substances', classname="col-md-3"),
               eh.RAIFieldPanel('hazardous_info', classname="col-md-9"),
           ], heading="Info on hazardous substance", classname='form-row'),
           eh.RAIMultiFieldPanel([
               eh.RAIFieldPanel('biological_agents', classname="col-md-3"),
               eh.RAIFieldPanel('bio_info', classname="col-md-9"),
           ], heading="Info on biological substances", classname='form-row')
       ], heading = 'Safety information', is_expanded = True),
       eh.RAICollapsablePanel([
           eh.RAIFieldPanel('internal_rubion_comment')
       ], heading = 'Internal remarks')
    ])


def get_members(wg):
    qs = RUBIONUser.objects.active().descendant_of(wg)
    return qs

def get_projects(wg):
    return Project.objects.active().descendant_of(wg)

workgroup_edit_handler = eh.RAIObjectList([
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
                eh.RAIFieldPanel('is_leader', classname="col-md-2", widget = RAIRadioInput),
                eh.RAIReadOnlyPanel('name_db', classname="col-md-3", disabled = True),
                eh.RAIReadOnlyPanel('first_name_db', classname="col-md-3", disabled = True),
                eh.RAIFieldPanel('may_create_projects', classname="col-md-2"),
                eh.RAIFieldPanel('may_add_members', classname="col-md-2"),
            ], classname = 'form-row', )
        ] , heading="Members", allow_add = True
    ),
    eh.RAIQueryInlinePanel(
        'projects', Project, get_projects,
        [
            eh.RAITranslatedContentPanel(
                {'de':'german', 'en':'english'},
                [
                    'title'
                ]
            )
        ] , heading="Projects", allow_add = True
    )
])

def get_sent_mail(ruser):
    q = SentMail.objects.filter(to = ruser.email).order_by('-sent_at')
    return q

rubionuser_edit_handler =eh.RAIPillsPanel([
    eh.RAIObjectList([
        eh.RAICollapsablePanel([
            eh.RAIMultiFieldPanel([
                eh.RAIFieldPanel('dosemeter', classname = 'col-md-6', widget=RAISelect),
                eh.RAIFieldPanel('needs_safety_instructions', widget=RAISelectMultipleSelectionLists)#, panels = [
                # eh.RAIFieldPanel('title_de')
                # ])# Unterweisungen hier
            ])
        ], heading = 'Strahlenschutz'),
        eh.RAICollapsablePanel([
            eh.RAIFieldRowPanel([
                eh.RAIFieldPanel('needs_key', classname="col-md-2"),
                eh.RAIFieldPanel('key_number', classname="col-md-2")
                
            ]),
            eh.RAIFieldRowPanel([
                eh.RAIFieldPanel('labcoat_size', classname = 'col-md-4', widget=RAISelect),
                eh.RAIFieldPanel('overshoe_size',classname = 'col-md-4', widget=RAISelect),
                eh.RAIFieldPanel('entrance', classname = 'col-md-4', widget=RAISelect),
            ], classname = 'justify-content-between' )
        ], heading = 'Labor-Organisation'),
        eh.RAIUserDataPanel([
            eh.RAIFieldRowPanel([
                eh.RAIFieldPanel('name_db', classname = 'col-md-4'),
                eh.RAIFieldPanel('first_name_db', classname = 'col-md-4'),
                eh.RAIFieldPanel('academic_title', classname = 'col-md-2', widget=RAISelect),
                eh.RAIFieldPanel('sex', classname = 'col-md-2', widget=RAIRadioSelect),
            ]),
            eh.RAIFieldRowPanel([
                eh.RAIFieldPanel('email_db'),
                eh.RAIFieldPanel('phone'),
                
                
            ])
        ], heading = 'Persönliche Nutzerdaten')
        
    ], heading = 'Daten'),
    eh.RAIObjectList([], heading = 'Dateien'),
    SentMailPanel('sent_mail', get_sent_mail, heading = 'E-Mails')
])
