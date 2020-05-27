from userinput.models import RUBIONUser, Project

import rai.edit_handlers as eh
from rai.widgets import (
    RAIRadioInput, RAISelectMultiple, RAISelect,
    RAIRadioSelect, RAISelectMultipleSelectionLists,
    RAIExtendedFileInput, RAISwitchInput,
    RAISelectMultipleCheckboxes
)
from rai.comments.edit_handlers import CommentPanel
from rai.files.edit_handlers import FileListPanel

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
    ], heading="benutzte Methoden"),
    eh.RAIInlinePanel('related_nuclides', panels=[
        eh.RAIMultiFieldPanel([
            eh.RAIFieldPanel('room', classname = 'col-md-2'),
            eh.RAIFieldPanel('snippet', classname = 'col-md-2', widget = RAISelect),
            eh.RAIFieldPanel('max_order', classname = 'col-md-4'),
            eh.RAIFieldPanel('amount_per_experiment', classname = 'col-md-4'),
        ],heading = 'Nuclide spec', classname = 'form-row')
    ], heading='Benutzte Nuklide'),
    
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
        eh.RAIInlinePanel('related_publications', panels = [
            eh.RAIFieldPanel('snippet')
        ], heading="Publikationen"),
        eh.RAIInlinePanel('related_theses', panels = [
            eh.RAIFieldPanel('snippet')
        ] , heading="Abschlussarbeiten"),
        #eh.RAIInlinePanel('related_publications'),
    ], heading="wissenschaftliche Resultate")
])


def get_members(wg):
    qs = RUBIONUser.objects.active().descendant_of(wg)
    return qs

def get_projects(wg):
    return Project.objects.active().descendant_of(wg)

workgroup_edit_handler = eh.RAIPillsPanel([
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

def get_sent_mail(ruser):
    q = SentMail.objects.filter(to__icontains = ruser.email).order_by('-sent_at')
    return q

rubionuser_edit_handler = eh.RAIPillsPanel([
    eh.RAIObjectList([
        eh.RAICollapsablePanel([
            eh.RAIFieldRowPanel([
                eh.RAIFieldPanel('dosemeter', widget=RAISelect, classname="col-md-12"),
                eh.RAIFieldPanel('needs_safety_instructions', widget=RAISelectMultipleCheckboxes)#, panels = [
                # eh.RAIFieldPanel('title_de')
                # ])# Unterweisungen hier
            ], heading = "Dosimeter und Sicherheitsunterweisungen")
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
    FileListPanel('documents', collection = RUBIONUserDocumentCollection, heading = 'Dateien'),
    SentMailPanel('sent_mail', get_sent_mail, heading = 'E-Mails'),
    CommentPanel(heading = 'Kommentare')
    
])
