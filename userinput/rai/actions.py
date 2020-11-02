from pprint import pprint

from collections import OrderedDict

from django.utils.html import mark_safe, format_html
import datetime
import locale

from rai.actions import (
    RAIAction,
    ListAction, EditAction, DetailAction, CreateAction,
    InactivateAction, ActivateAction, SpecificAction
)
import rai.edit_handlers as eh
from rai.permissions.utils import user_has_permission
from rai.widgets import RAIRadioInput, RAISelectMultiple, RAISelect

from userdata.models import StaffUser

from userinput.models import (
    Project2FundingRelation, Project2ThesisRelation, Project2PublicationRelation
)

import userinput.rai.filters as filters
from userinput.rai.permissions import MovePermission, InactivatePermission

from userinput.rai.edit_handlers import (
    project_edit_handler, workgroup_edit_handler, workgroup_create_edit_handler, rubionuser_edit_handler,
    rubionuser_create_handler, project_create_handler
)

from userinput.rai.views.rubionuser.views import AddInstructionsDatesView
from wagtail.core.models import PageRevision

# an  action for moving from one group to another
# used by projects and rubionuser
class MoveToWorkgroupAction(SpecificAction):
    label = 'Anderer Gruppe zuordnen'
    icon = 'arrow-alt-circle-right'
    icon_font = 'fas'
    action_identifier = 'move'

    def get_view(self):
        return self.raiadmin.moveview.as_view(
            raiadmin = self.raiadmin,
            active_action = self
        )
    def show(self, request):
        return user_has_permission(request, self.get_rai_id(), MovePermission)

class UserinputInactivateAction(InactivateAction):
    def show(self, request):
        return user_has_permission(request, self.get_rai_id(), InactivatePermission)

class UserinputActivateAction(ActivateAction):
    def show(self, request):
        return user_has_permission(request, self.get_rai_id(), InactivatePermission)

    
def _is_rubion_user_active(instance):
    return (
        instance.linked_user is None or
        instance.expire_at is None or
        instance.expire_at >= datetime.datetime.now()
    )

class RUBIONUserOnlyWhenActiveMixin:
    def show_for_instance(self, instance, request=None):
        return _is_rubion_user_active(instance)

class RUBIONUserMoveAction(RUBIONUserOnlyWhenActiveMixin, MoveToWorkgroupAction):
    def show_for_instance(self, instance, request=None):
        return super().show_for_instance(instance, request) and not instance.is_leader
      
    
class RUBIONUserInactivateAction(RUBIONUserOnlyWhenActiveMixin, UserinputInactivateAction):
    pass

class RUBIONUserActivateAction(RUBIONUserOnlyWhenActiveMixin, UserinputActivateAction):
    def show_for_instance(self, instance, request=None):
        return not super().show_for_instance(instance, request)

class RUBIONUserCreateAction(CreateAction):
    edit_handler = rubionuser_create_handler
    
class RAIUserDataListAction(ListAction):
    # list_item_template = 'userinput/rubionuser/rai/list/item-in-list.html'
    list_filters = [
        filters.RUBIONUserStatusFilter,
        filters.RUBIONUserInstrumentFilter
    ]
    item_provides = OrderedDict([
        ('email', {
            'label' : 'E-Mail',
            'desc' : ' Die E-Mail-Adresse des Nutzers',
            'field' : 'email',
            'icon' : ['fas', 'fa-envelope']
        }),
        ('phone',  {
            'label' : 'Telefonnummer',
            'desc' : 'Die Telefonnummer des Nutzers',
            'field' : 'phone',
            'searchable' : True,
            'searchable_title': 'Telefonnummer',
            'icon' : ['fas', 'fa-phone']
        }),
        ('workgroup',  {
            'label' : 'Arbeitsgruppe',
            'desc' : 'Die Arbeitsgruppe, der der Nutzer angehört',
            'func' : 'get_workgroup',
            'searchable' : True,
            'searchable_title': 'Arbeitsgruppe'
        }),
        ('badges', {
            'label' : 'Hinweise',
            'desc': 'Kurze Hinweise in Form eines farblich hinterlegten Feldes', 
            'type' : 'group'
        }),
        ('needs_key', {
            'label' : 'Schlüssel beantragt?',
            'desc' : 'Hinweis, dass für den Nutzer ein Schlüssel beantragt wurde, aber noch kein Schlüssel vergeben ist',
            'type' : ['badge','badge-danger'],
            'callback' : 'needs_key',
            'group': 'badges',
            'help_url' : 'userinput:rubionuser:needs_key'
        }),
        ('validated', {
            'label' : 'Validierungsstatus',
            'desc' : 'Hinweis, wenn der Nutzer noch nicht bestätigt hat, dass er als RUBION-Nutzer geführt werden möchte (inklusive Bestätigung der Nutzungsbedingungen)',
            'type' : ['badge', 'badge-danger'],
            'callback': 'is_validated',
            'group': 'badges',
            'help_url' : 'userinput:rubionuser:not_validated'
        }),
        ('group_leader', {
            'label' : 'Gruppenleiter',
            'desc' : 'Hinweis, wenn der Nutzer der Leiter der Arbeitsgruppe ist',
            'type' : ['badge', 'badge-info'],
            'callback': 'is_leader',
            'group': 'badges'
        }),
        ('safety', {
            'label' : 'Sicherheitshinweise',
            'desc': 'Kurze Hinweise in Form eines farblich hinterlegten Feldes', 
            'type' : 'group'
        }),
        ('nuclides', {
            'label' : 'Nuklide',
            'desc' : 'Auflistung der Nuklide, die genutzt werde',
            'type' : ['badge','badge-info'],
            'callback' : 'nuclides',
            'group': 'safety',
            'selected': False,
            'use_label': False
        }),
        ('instructions', {
            'label' : 'Unterweisungen',
            'desc' : 'Auflistung der benötigten Sicherheitsunterweisungen',
            'type' : ['badge','badge-info'],
            'callback' : 'instructions',
            'group': 'safety',
            'selected': False
        }),
        ('staff', {
            'label' : 'Hinweise bzgl. des Mitarbeiter-Status',
            'desc': 'Kurze Hinweise in Form eines farblich hinterlegten Feldes', 
            'type' : 'group'
        }),
        ('is_staff', {
            'label' : 'Ist RUBION-Mitarbeiter',
            'desc' : 'Hinweis, wenn der Nutzer auch Mitarbeiter im RUBION ist',
            'type' : ['badge','badge-info'],
            'callback' : 'is_staff',
            'group': 'staff',
            'selected': True
        }),
        ('staff_group', {
            'label' : 'Mitarbeiter-Gruppe',
            'desc' : 'Hinweis, welcher Mitarbeiter-Gruppe der Nutzer angehört',
            'type' : ['badge','badge-info'],
            'callback' : 'staff_group',
            'group': 'staff',
            'selected': False
        }),
        ('last_revision', {
            'label': 'Letzte Änderung',
            'desc': 'Wann und durch wen die letzte Änderung an den Daten durchgeführt wurde.',
            'callback' : 'get_last_revision',
            'type' : ['text-muted']
        })
        
    ])

    def needs_key(self, obj):
        if obj.needs_key and not obj.key_number:
            return "offener Schlüsselantrag"
        return None

    def get_last_revision(self, obj):
        locale.setlocale(locale.LC_ALL, 'de_DE')
        pr = PageRevision.objects.filter(page = obj).order_by('-created_at').first()
        if pr:
            if pr.user:
                return 'Letzte Änderung am {:%d. %B %Y um %H:%M} von {} {}.'.format(pr.created_at, pr.user.first_name, pr.user.last_name)
            else:
                return 'Letzte Änderung am {:%Y-%m-%d %H:%M} von Unbekannt'.format(pr.created_at)
        else:
            return 'Noch keine Änderung vorhanden'

    def is_staff(self, obj):
        if StaffUser.objects.filter(user = obj.linked_user).exists():
            return "RUBION-Mitarbeiter"
        return False

    def staff_group(self, obj):
        if not obj.linked_user:
            return False
        try:
            staff = StaffUser.objects.filter(user = obj.linked_user).get()
        except StaffUser.DoesNotExist:
            return False
        return staff.get_parent().specific.title_trans

    def is_validated(self, obj):
        if not obj.is_validated:
            return 'Nicht validiert'
        else:
            return None

    def is_leader(Self, obj):
        if obj.is_leader:
            return 'Gruppenleiter'
        else:
            return None

    def nuclides(self, obj):
        wg = obj.get_workgroup()
        nuclides = []
        for project in wg.get_projects():
            for rel in project.related_nuclides.all():
                nuclides.append('{}-{}'.format(rel.snippet.mass, rel.snippet.element))
        return nuclides

    def instructions(self, obj):
        instructions = []
        for inst in obj.safety_instructions.all():
            instructions.append(inst.instruction)
        return instructions
        

class RUBIONUserDataEditAction(RUBIONUserOnlyWhenActiveMixin, EditAction):
    edit_handler = rubionuser_edit_handler
    text_style = 'secondary'

class RAIProjectListAction(ListAction):
    list_item_template = 'userinput/project/rai/list/item-in-list.html'
    list_filters = [
        filters.ProjectStatusFilter
    ]
class RAIProjectEditAction(EditAction):
    edit_handler = project_edit_handler

class RAIProjectCreateAction(CreateAction):
    edit_handler = project_create_handler
    
    
class RAIWorkgroupListAction(ListAction):
    list_item_template = 'userinput/workgroup/rai/list/item-in-list.html'
    list_filters = [
        filters.WorkgroupStatusFilter
    ]
    item_provides = OrderedDict([
        ('group_leader', {
            'label' : 'Gruppenleiter',
            'desc' : 'Der Leiter der Arbeitsgruppe',
            'type' : 'group',
            'use_label': True
        }),
        ('gl_name', {
            'label': 'Name, Vorname',
            'desc' : 'Vollständiger Name des Gruppenleiters',
            'callback' : 'get_gl_name',
            'type' : 'inline',
            'group' : 'group_leader',
            'searchable' : True,
            'searchable_title': 'Gruppenleiter',

        }),
        ('gl_email', {
            'label' : 'E-Mail',
            'desc' : 'E-Mail-Adresse des Gruppenleiters',
            'icon' : ['fas', 'fa-envelope'],
            'callback' : 'get_gl_email',
            'type' : 'inline',
            'group' : 'group_leader'
        }),
        ('gl_phone', {
            'label' : 'Telefonnummer',
            'desc' : 'Telefonnummer des Gruppenleiters',
            'icon' : ['fas', 'fa-phone'],
            'callback' : 'get_gl_phone',
            'type' : 'inline',
            'group' : 'group_leader'
        }),
        ('address', {
            'label' : 'Adresse',
            'desc' : 'Die Anschrift der Arbeitsgruppe',
            'callback' : 'get_address',
        }),
        ('additional', {
            'label' : 'Weitere Informationen',
            'desc' : 'Weitere Informationen zu Mitgliedern und Projekten',
            'type' : 'group'
        }),
        ('n_members', {
            'label' : 'Anzahl Mitglieder',
            'desc' : 'Anzahl der aktiven Mitglieder der Arbeitsgruppe',
            'group' : 'additional',
            'type' : ['badge', 'badge-info'],
            'callback' : 'get_n_members'
        }),
        ('n_projects', {
            'label' : 'Anzahl Projekte',
            'desc' : 'Anzahl der aktiven Projekte',
            'group' : 'additional',
            'type' : ['badge', 'badge-info'],
            'callback' : 'get_n_projects'
        }),
        ('nuclides', {
            'label': 'Nuklide',
            'desc': 'Die von der Arbeitsgruppe verwendeten Nuklide.',
            'callback' : 'get_nuclides',
            'type' : ['badge','badge-info'],
            'use_label' : True
        }),
        ('last_revision', {
            'label': 'Letzte Änderung',
            'desc': 'Wann und durch wen die letzte Änderung an den Daten durchgeführt wurde.',
            'callback' : 'get_last_revision',
            'type' : ['text-muted']
        })
    ])
    def get_n_members(self, obj):
        return format_html('Aktive Mitglieder: {}', obj.get_members().count())

    def get_n_projects(self, obj):
        return format_html('Aktive Projekte: {}', obj.get_projects().count())
    
    def get_gl_name(self, obj):
        head = obj.get_head()
        if not head:
            return mark_safe('<a href="help::userinput:workgroup:no_group_leader" data-toggle="modal" data-target="#helpModal"><span class="badge badge-danger">Diese Gruppe hat keinen Gruppenleiter <i class="fas fa-question-circle"></i></span></a>')
        return head.title
    
    def get_gl_email(self, obj):
        head = obj.get_head()
        if not head:
            return None
        return head.specific.email
    
    def get_gl_phone(self, obj):
        head = obj.get_head()
        if not head:
            return None
    
        return head.specific.phone

    def get_address(self, obj):
        if obj.department:
            department = format_html('{}<br />', obj.department)
        else:
            department = ''

        if obj.homepage:
            homepage = format_html('<br /> {}', obj.homepage)
        else:
            homepage = ''
        return format_html(
            '<address class="text-primary">'+
            '{department}'+
            '{institute}<br />'+
            '<span data-rubion-searchable="true" data-rubion-searchable-title="Universität">{university}</span>'+
            '{homepage}'+
            '</address>',
            institute = obj.institute, department = department, university = obj.university, homepage = homepage)
    
    def get_last_revision(self, obj):
        locale.setlocale(locale.LC_ALL, 'de_DE')
        pr = PageRevision.objects.filter(page = obj).order_by('-created_at').first()
        if pr:
            if pr.user:
                return 'Letzte Änderung am {:%d. %B %Y um %H:%M} von {} {}.'.format(pr.created_at, pr.user.first_name, pr.user.last_name)
            else:
                return 'Letzte Änderung am {:%Y-%m-%d %H:%M} von Unbekannt'.format(pr.created_at)
        else:
            return 'Noch keine Änderung vorhanden'

    def get_nuclides(self, obj):
        nuclides = []
        for pr in obj.get_projects():
            for nuc_rel in pr.specific.related_nuclides.all():
                nuclides.append(
                    format_html('<sup>{mass}</sup>{element}', mass = nuc_rel.snippet.mass, element = nuc_rel.snippet.element)
                )
        return list(set(nuclides))

class RAIWorkgroupEditAction(EditAction):
    edit_handler = workgroup_edit_handler

class RAIWorkgroupDetailAction(DetailAction):
    edit_handler = workgroup_edit_handler

class RAIWorkgroupCreateAction(CreateAction):
    edit_handler = workgroup_create_edit_handler
    text_type = 'secondary'


class AbstractScientificOutputListAction(ListAction):
    RelationModel = None
    related_name = None
    
    def get_project(self, obj):
        rels = self.RelationModel.objects.filter(snippet = obj)
        return '<br />'.join([r.project_page.title_de for r in rels])

    def get_created_at(self, obj):
        rels = self.RelationModel.objects.filter(snippet = obj)
        if rels.count() == 0:
            return ''
        
        for r in rels:
            project = r.project_page
            revisions = PageRevision.objects.filter(page = project).order_by('-created_at')
            for rev in revisions:
                revision_page = rev.as_page_object()
                rel_qs = getattr(revision_page, self.related_name)
                fundings = [p2fr.snippet for p2fr in rel_qs.all()]
                if obj not in fundings:
                    next_rev = rev.get_next()
                    break

        if not next_rev.user:
            return format_html(
                'Hinzugefügt am: {day}. {month} <span data-rubion-sortable="Hinzugefügt im Jahr" data-rubion-groupby="Hinzugefügt im Jahr" data-rubion-group-title="Hinzugefügt in {year}">{year}</span> von unbekanntem Nuzter',
                year = next_rev.created_at.year,
                day = next_rev.created_at.day,
                month = next_rev.created_at.strftime('%B'),
            )
        
        return format_html(
            'Hinzugefügt am: {day}. {month} <span data-rubion-sortable="Hinzugefügt im Jahr" data-rubion-groupby="Hinzugefügt im Jahr" data-rubion-group-title="Hinzugefügt in {year}">{year}</span> von {firstname} {lastname}',
            year = next_rev.created_at.year,
            day = next_rev.created_at.day,
            month = next_rev.created_at.strftime('%B'),
            firstname = next_rev.user.first_name,
            lastname = next_rev.user.last_name,
        )
    
class RAIFundingListAction(AbstractScientificOutputListAction):
    RelationModel = Project2FundingRelation
    related_name = 'related_fundings'
    item_provides = OrderedDict([
        ('project', {
            'label' : 'Projekt',
            'desc' : 'Das zugehörige Projekt',
            'callback' : 'get_project',
        }),
        ('created_at', {
            'label' : 'Datum des Hinzufügens',
            'desc' : 'Datum, an dem die Förderung zum Projekt hinzugefügt wurde.',
            'callback' : 'get_created_at'
        }),
        ('additional', {
            'label' : 'Weitere Informationen',
            'desc' : 'Zusätzliche Informationen zur Förderung',
            'type' : 'group'
        }),
        ('funder', {
            'label' : 'Förderinstitution',
            'desc' : 'Die fördernde Institution',
            'group' : 'additional',
            'callback' : 'get_funder'
        }),
        ('funder_id', {
            'label' : 'Projektnummer',
            'desc' : 'Die Projektnummer bei der fördernden Institution',
            'group' : 'additional',
            'callback' : 'get_funding_id'
        }),
        ('url', {
            'label' : 'Projekt-Homepage',
            'desc' : 'Die Homepage des Förder-Projekts',
            'group' : 'additional',
            'callback' : 'get_funding_url'
        }),

    ])

    def get_funder(self, obj):
        return "Gefördert durch: {}".format(obj.agency)
    def get_funding_id(self, obj):
        return "Projektnummer: {}".format(obj.project_number)
    def get_funding_url(self, obj):
        return "Förder-Projekt-Homepage: {}".format(obj.project_url)
    
    
class RAIThesisListAction(AbstractScientificOutputListAction):
    RelationModel = Project2ThesisRelation
    related_name = 'related_theses'
    list_item_template = 'userinput/snippets/thesis/rai/list/item-in-list.html'
    
    item_provides = OrderedDict([
        ('project', {
            'label' : 'Projekt',
            'desc' : 'Das zugehörige Projekt',
            'callback' : 'get_project',
        }),
        ('created_at', {
            'label' : 'Datum des Hinzufügens',
            'desc' : 'Datum, an dem die Abschlussarbeit zum Projekt hinzugefügt wurde.',
            'callback' : 'get_created_at'
        })
    ])

class RAIPublicationListAction(AbstractScientificOutputListAction):
    RelationModel = Project2PublicationRelation
    related_name = 'related_publications'
    list_item_template = 'userinput/snippets/publication/rai/list/item-in-list.html'
    
    item_provides = OrderedDict([
        ('project', {
            'label' : 'Projekt',
            'desc' : 'Das zugehörige Projekt',
            'callback' : 'get_project',
        }),
        ('created_at', {
            'label' : 'Datum des Hinzufügens',
            'desc' : 'Datum, an dem die Publikation zum Projekt hinzugefügt wurde.',
            'callback' : 'get_created_at'
        }),
    ])


class RAISafetyInstructionAddAction(RAIAction):
    action_identifier = 'add'
    icon = 'plus'
    icon_font = 'fas'

    def get_view(self):
        return AddInstructionsDatesView.as_view(
            raiadmin = self.raiadmin,
            active_action = self
        )
