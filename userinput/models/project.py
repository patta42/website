import datetime 

from dateutil.relativedelta import relativedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import models
from django.forms import modelform_factory
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _

from instruments.mixins import AbstractRelatedMethods

from modelcluster.fields import ParentalKey

from ugc.models import UserGeneratedPage2

from userinput.mixins import ActiveInactiveMixin, MoveMixin
from userinput.models.abstract import (
    AbstractFundingRelation, AbstractPublicationRelation, AbstractThesisRelation,
    AbstractNuclideRelation
)
from userinput.models.rubionuser import RUBIONUser
from userinput.models.snippets import ThesisSnippet, FundingSnippet, PublicationSnippet
from userinput.query import ActiveInactivePageManager

from wagtail.admin.edit_handlers import (
    FieldPanel, StreamFieldPanel, MultiFieldPanel,
    FieldRowPanel, InlinePanel, TabbedInterface, 
    ObjectList, PageChooserPanel 
)
from wagtail.contrib.routable_page.models import route

from website.models import TranslatedField
from website.widgets import StyledDOIWidget

class Project ( MoveMixin, UserGeneratedPage2, ActiveInactiveMixin ):
    
    # --- Settings 

    parent_page_types = [ 'userinput.ProjectContainer' ]
    subpage_types = []

    # --- Templates
    view_template = 'userinput/project_view.html'

    objects = ActiveInactivePageManager()
    
    # --- Fields
    summary_en = models.TextField(
        max_length = 1024,
        blank = False,
        null = False,
        verbose_name = _('project summary (en)'),
        help_text = _('Public summary of the project (in english).')
    )
    summary_de = models.TextField(
        max_length = 1024,
        blank = False,
        null = False,
        verbose_name = _('project summary (de)'),
        help_text = _('Public summary of the project (in german).')
    )

    is_confidential = models.BooleanField(
        default = False,
        verbose_name = _('hide project'),
        help_text = _('Is this project confidential? If you check this, it will not be visible to the public.')
    )

    uses_gmos = models.BooleanField(
        default = False,
        verbose_name = _('genetically modified organisms'),
        help_text = _('Does the project include working with genetically modified organisms?')
    )
    
    gmo_info = models.CharField(
        max_length = 1024,
        verbose_name = _('Information on GMOs'),
        help_text = _('Provide information about the GMOs you plan to use (safety level, cell type, ...)'),
        blank = True
    )

    uses_chemicals = models.BooleanField(
        default = False,
        verbose_name = _('Uses chemical compounds'),
        help_text = _('Does the project include working with chemical compounds'),
    )

    chemicals_info = models.CharField(
        max_length = 1024,
        verbose_name = _('Information on chemicals'),
        help_text = _('Provide information about the chemicals you plan to use (compound, amount, ...)'),
        blank = True
    )

    uses_hazardous_substances = models.BooleanField(
        default = False,
        verbose_name = _('Uses hazardous compounds'),
        help_text = _('Does the project include working with hazardous compounds'),

    )

    hazardous_info = models.CharField(
        max_length = 1024,
        verbose_name = _('Information on hazardous compunds'),
        help_text = _('Provide information about the hazardous compunds you plan to use (compound, amount, ...)'),
        blank = True
    )

    biological_agents = models.BooleanField(
        default = False,
        verbose_name = _('Ordinance on biological agents'),
        help_text = _('Does the project include work which underlies the Ordinance on Biological Agents')
    )
    
    bio_info = models.CharField(
        max_length = 1024,
        verbose_name = _('Information on biological agents'),
        help_text = _('Provide information about the biological agents you plan to use (agent, amount, ...)'),
        blank = True
    )
    

    funding_asked = models.BooleanField(
        default = False,
        verbose_name=_('has the user been asked to add funding?'),
        help_text =_('This is an auto-filled field. Do not change')
    )
    publications_asked = models.BooleanField(
        default = False,
        verbose_name=_('has the user been asked to add publications?'),
        help_text =_('This is an auto-filled field. Do not change')
    )
    theses_asked = models.BooleanField(
        default = False,
        verbose_name=_('has the user been asked to add theses?'),
        help_text =_('This is an auto-filled field. Do not change')
    )
    is_research = models.BooleanField(
        default = True,
        verbose_name=_('research'),
    )
    is_teaching = models.BooleanField(
        default = False,
        verbose_name=_('teaching'),
    )

    
    cnt_prolongations = models.IntegerField(
        default = 0,
        verbose_name = _('Prolongation counter'),
        help_text = ('How often the project has been prolongued without changes.' )
    )

    max_prolongations = models.IntegerField(
        default = 2,
        verbose_name = _('Maximum number of prolongations'),
        help_text = ('How often the project can be prolongued without changes.' )
    )

    @staticmethod
    def active_filter():
        return models.Q(locked = False)
    
    @property 
    def can_prolong( self ):
        return self.cnt_prolongations < self.max_prolongations

    @property
    def under_revision( self ):
        return self.has_unpublished_changes
    @property
    def is_active( self ):
        return not self.under_revision and (
            self.expire_at is None or self.expire_at >  datetime.datetime.today()
        )
    
    # --- TranslatedFields

    summary = TranslatedField('summary')

    # --- AdminInterface

    summary_panels = [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('is_research'),
                FieldPanel('is_teaching'),
            ])
        ], heading="Project type"),
        MultiFieldPanel([
            FieldPanel('title_de'),
            FieldPanel('summary_de'),
        ], heading = _('summary in german')),
        MultiFieldPanel([
            FieldPanel('title'),
            FieldPanel('summary_en'),
        ], heading = _('summary in english'))
    ]

    nuclide_panel = [
        InlinePanel('related_nuclides', label = _('Used Nuclides'))
    ]

    methods_panel = [
        InlinePanel('related_methods', label = _('methods'))
    ]

    related_items_panels = [
        InlinePanel('related_fundings', label = _('funding')),
        InlinePanel('related_publications', label = _('publications')),
        InlinePanel('related_theses', label = _('theses')),
    ]
    settings_panel = [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('go_live_at'),
                FieldPanel('expire_at'),
            ]),
            FieldRowPanel([
                FieldPanel('cnt_prolongations'),
                FieldPanel('max_prolongations'),
            ]),
#            FieldPanel('is_confidential')
        ], heading =_( 'Expiration' )),
    ]
    comment_panel = [
        FieldPanel('internal_rubion_comment')
    ]

    edit_handler = TabbedInterface([
        ObjectList( methods_panel, _('Resources') ),
        ObjectList( nuclide_panel, _('Nuclides') ),
        ObjectList( related_items_panels, _('related items')), 
        ObjectList( summary_panels, _('description') ),
        ObjectList( settings_panel, _('Settings') ),
        ObjectList( comment_panel, _('Internal comment'))
    ])



    # METHODS

    # --- restrict views
    def user_passes_test( self, user, what, test_for_lock = True ):
        if test_for_lock:
            if what == self.EDIT and self.locked:
               return False

        if user.is_superuser:
            return True

        try:
            r_user = RUBIONUser.objects.get( linked_user = user )        
            is_workgroup_member = r_user.get_workgroup() == self.get_workgroup()
        except:
            is_workgroup_member = False

        # Everyone may see the project unless it is_confidential or under_revision
        if what == self.VIEW:
            if self.is_confidential or self.under_revision:
                # restrict to members of this group and RUBION-staff
                if user.is_staff or is_workgroup_member:
                    return True
                else:
                    # raise a 404 instead of a 403 to avoid indicating the project exists
                    raise Http404()
            else:
                return True

        if what == self.EDIT:
            # We might not have an r_user instance in case of anonymous users
            # In that case, is_workgroup_member is False.
            if is_workgroup_member:
                return r_user.may('project')
            else:
                return False

    @staticmethod
    def user_passes_create_test( request, asking_page ):
        if request.user.is_superuser:
            return True
        if request.user.is_anonymous:
            return False

        # allowed if user is workgroup member and my create projects        

        r_user = RUBIONUser.objects.get( linked_user = request.user )        
        designated_wg = asking_page.get_parent().get_parent().specific
        is_workgroup_member = ( designated_wg == r_user.get_workgroup() )

        return is_workgroup_member and r_user.may('project')

    
    # --- Automatically adding data
    def clean ( self ):
        if not self.slug:
            self.slug = self._get_autogenerated_slug( slugify ( self.title ) )
    
    # --- Additional views
    
    def add_relation( self, request, Model, RelationModel, tpl, **kwargs):
        ''' 
        This method adds a relation_model between the project and a snippet. 
        If kwargs['has_been_asked_field'] is present, it updates the field to True 
        if it is False, ensuring that every relation has been asked at least once.
        '''
        try:
            has_been_asked_field = kwargs.pop('has_been_asked_field')
        except:
            has_been_asked_field = None

        try:
            proceed_with = kwargs.pop('proceed_with')
        except:
            proceed_with = None

        try:
            instance = kwargs.pop('instance')
            rel = RelationModel.objects.get(snippet_id = instance.id)
            if rel.project_page_id != self.id:
                raise PermissionDenied()
        except KeyError:
            instance = None
        has_been_asked = True
        if has_been_asked_field and getattr(self, has_been_asked_field) == False:
            has_been_asked = False
            setattr(self, has_been_asked_field, True)

        ModelForm = modelform_factory( Model, exclude = ['is_duplicate'], **kwargs )

        # An inline function for proceeding.
        def proceed():
            if proceed_with:
                try:
                    was_asked = getattr(self, proceed_with['field'])
                except AttributeError:
                    was_asked = True
                if not was_asked:
                    return redirect( self.full_url + self.reverse_subpage( proceed_with['target'] ) )
            return redirect( self.full_url )

            
        if request.method == 'POST':
            if request.POST['next'] == 'cancel':
                return proceed()
            if instance:
                form = ModelForm( request.POST, instance = instance )
            else:
                form = ModelForm(request.POST)
            if form.is_valid():
                inst = form.save()
                if not instance:
                    relation = RelationModel()
                    relation.project_page_id = self.id
                    relation.snippet_id = inst.id
                    relation.save()
                    
                    if not self.under_revision:
                        self.expire_at = datetime.datetime.now() + relativedelta(years=1)
                        self.cnt_prolongations = 0
                        self.save_revision_and_publish( user = request.user )
                    
                try:
                    msg_type = Model.verbose_name
                except AttributeError:
                    msg_type = 'data'
                if instance:
                    messages.success( request, 'The {} has been updated.'. format(msg_type) )
                else:
                    messages.success( request, 'The {} has been added to the project.'. format(msg_type) )
                nxt = request.POST.get('next')
                if nxt in ['add_publication', 'add_funding', 'add_thesis']:
                    return redirect (self.full_url + self.reverse_subpage( nxt ))
                else:
                    return proceed()
                    
            else:
                messages.error( request, _('An error occured.') )
        else:
            if instance:
                form = ModelForm( instance = instance )
            else:
                form = ModelForm()
        context = {}
        context['form'] = form
        context['page'] = self
        context['has_been_asked'] = has_been_asked 
        return TemplateResponse(
            request,
            tpl,
            context
        )
        



    @route(r'^edit_publication/(\d+)/$', name="edit_publication")
    @route(r'^add_publication/$')
    def add_publication( self, request, pk=None ):
        if self.user_passes_test(request.user, self.EDIT):
            kwargs = {}
            if pk:
                instance = get_object_or_404( PublicationSnippet, pk = pk)
                kwargs['instance'] = instance
            return self.add_relation( 
                request, 
                PublicationSnippet, 
                Project2PublicationRelation,
                'userinput/project_add_publications.html',
                widgets = {'doi' : StyledDOIWidget},
                has_been_asked_field = 'publications_asked',
                proceed_with = {
                    'field' : 'theses_asked',
                    'target': 'add_thesis'
                },
                **kwargs
            )
        else:
            raise PermissionDenied

    @route(r'^edit_funding/(\d+)/$', name="edit_funding")
    @route(r'^add_funding/$')
    def add_funding( self, request, pk = None ):
        if self.user_passes_test(request.user, self.EDIT):
            kwargs = {}
            if pk:
                instance = get_object_or_404( FundingSnippet, pk = pk)
                kwargs['instance'] = instance
            return self.add_relation( 
                request, 
                FundingSnippet, 
                Project2FundingRelation,
                'userinput/project_add_funding.html',
                has_been_asked_field = 'funding_asked',
                proceed_with = {
                    'field' : 'publications_asked',
                    'target': 'add_publication'
                },
                **kwargs
            )
        else:
            raise PermissionDenied

    @route(r'^edit_thesis/(\d+)/$', name="edit_thesis")
    @route(r'^add_thesis/$')
    def add_thesis( self, request, pk = None ):
        if self.user_passes_test(request.user, self.EDIT):
            kwargs = {}
            if pk:
                instance = get_object_or_404( ThesisSnippet, pk = pk)
                kwargs['instance'] = instance
            return self.add_relation( 
                request, 
                ThesisSnippet, 
                Project2ThesisRelation,
                'userinput/project_add_thesis.html',
                has_been_asked_field = 'theses_asked',
                **kwargs
            )
        else:
            raise PermissionDenied

    @route(r'^delete_theses/(\d+)/$', name="delete_thesis")
    def delete_thesis( self, request, pk ):
        if self.user_passes_test(request.user, self.EDIT):
            instance = get_object_or_404( ThesisSnippet, pk = pk )
            return self.delete_relation( 
                request,
                ThesisSnippet, 
                Project2ThesisRelation,
                instance,
                object_title = "{} ({}): {}".format(instance.author, instance.year, instance.title),
                object_type = _('thesis')
            )
        else:
            raise PermissionDenied

    @route(r'^delete_publication/(\d+)/$', name="delete_publication")
    def delete_publication( self, request, pk ):
        if self.user_passes_test(request.user, self.EDIT):
            instance = get_object_or_404( PublicationSnippet, pk = pk )
            return self.delete_relation( 
                request,
                PublicationSnippet, 
                Project2PublicationRelation,
                instance,
                object_title = "{}: {}. {} {}".format(instance.authors, instance.title, instance.journal, instance.year),
                object_type = _('publication')
            )
        else:
            raise PermissionDenied

    @route(r'^delete_funding/(\d+)/$', name="delete_funding")
    def delete_funding( self, request, pk ):
        if self.user_passes_test(request.user, self.EDIT):
            instance = get_object_or_404( FundingSnippet, pk = pk )
            return self.delete_relation( 
                request,
                FundingSnippet, 
                Project2FundingRelation,
                instance,
                object_title = "{}: {}".format(instance.agency, instance.title),
                object_type = _('funding')
            )
        else:
            raise PermissionDenied

    def delete_relation(self, request, SnippetModel, RelationModel, instance, **kwargs):
        rel = RelationModel.objects.get(snippet_id = instance.id)
        if rel.project_page_id != self.id:
            raise PermissionDenied()
        
        if request.method == 'GET':
            context = kwargs
            context['project_title'] = self.title_trans
            return TemplateResponse(
                request,
                'userinput/project_delete_relation.html',
                context
            )
        if request.method == 'POST':
            if request.POST['next'] == 'confirm':
                rel = get_object_or_404( RelationModel, snippet_id = instance.id )
                messages.success( request, "The {} »{}« was deleted.".format(kwargs['object_type'], kwargs['object_title']) )
                rel.delete()
                instance.delete()

            return redirect( self.full_url )

    @route(r'^prolong/$', name="prolong")
    def prolong( self, request ):
        if self.user_passes_test( request.user, self.EDIT):
            if request.method == 'GET':
                return TemplateResponse(
                    request,
                    'userinput/prolong_project.html',
                    { 'page' : self }
                )
            elif request.method == 'POST':
                if request.POST['next'] == 'prolong':
                    if self.can_prolong:
                        self.expire_at = datetime.datetime.now() + relativedelta (years = 1)
                        self.cnt_prolongations += 1
                        self.save_revision_and_publish( user = request.user )
                        messages.info( request, _('The project was extended by one year.' ) )
                    else:
                        messages.error( request, _('The project cannot be extended anymore. Please contact the RUBION team.' ) )
                else:
                    messages.info( request, _( 'Operation was canceled.' ) )
                return redirect(self.full_url)
        raise PermissionDenied

    @route(r'^close/$', name="close")
    def close( self, request ):
        if self.user_passes_test( request.user, self.EDIT):            
            if request.method == 'GET':
                return TemplateResponse(
                    request,
                    'userinput/close_project.html',
                    { 'page' : self }
                )
            elif request.method == 'POST':
                if request.POST['next'] == 'close':
                    self.inactivate(user = request.user)
                    messages.info( request, _('The project was closed.' ) )
                    return redirect(self.get_parent().full_url)
                else:
                    messages.info( request, _( 'Operation was canceled.' ) )
                return redirect(self.full_url)
        raise PermissionDenied



        
    # --- Successful creation of new project

    def serve_success ( self, request, edit = False ):
        if edit:
            return redirect( self.full_url )
        else:
            return redirect( self.full_url + self.reverse_subpage('add_funding') )


    # --- render a project in the list of projects

    def render_as_child ( self ):
        return render_to_string(
            'userinput/project_child.html',
            { 
                'page' : self,
            }
        )

    # --- get workgroup for project
    def get_workgroup( self ):
        return self.get_parent().get_parent().specific

    # --- get info about workgroup
    def get_workgroup_info( self ):
        wg = self.get_workgroup()
        return "{}, {}, {}".format(
            wg.title_trans,
            wg.institute,
            wg.university
        )
            
    def get_methods( self ):
            
        methods = []

        for p2m in Project2MethodRelation.objects.filter(project_page = self):
            if p2m not in methods:
                methods.append(p2m.page) 

        return methods


    def get_context(self, request):

        context = super(Project, self).get_context( request )
        context['user_may_change_project'] = self.user_passes_test( request.user, self.EDIT, test_for_lock = False )
        UserModel = get_user_model()
        
        if self.expire_at:
            if (datetime.datetime.now() + relativedelta(months=1)) > self.expire_at:
                context['will_expire_soon'] = True                

        # @TODO the owner_id is not set on pages? It seems to be available 
        # through the revisions
        #context['owner'] = UserModel.objects.get(pk = self.owner_id)
        return context

class Project2MethodRelation( AbstractRelatedMethods ):
    project_page = ParentalKey( Project, related_name = 'related_methods')

    panels = [
        PageChooserPanel('page', 'instruments.MethodPage'),
    ]

class Project2FundingRelation( AbstractFundingRelation ):
    project_page = ParentalKey( Project, related_name = 'related_fundings')
    panels = AbstractFundingRelation.panels

class Project2PublicationRelation( AbstractPublicationRelation ):
    project_page = ParentalKey( Project, related_name = 'related_publications')
    panels = AbstractPublicationRelation.panels

class Project2ThesisRelation( AbstractThesisRelation ):
    project_page = ParentalKey( Project, related_name = 'related_theses')
    panels = AbstractThesisRelation.panels

class Project2NuclideRelation( AbstractNuclideRelation ):
   project_page = ParentalKey( Project, related_name = 'related_nuclides')
   max_order = models.CharField (
       max_length = 8,
       blank = True,
       null = True,
       verbose_name = _('max amount per order (in MBq)')
   )
   amount_per_experiment = models.CharField (
       blank = True,
       null = True,
       max_length = 8,
       verbose_name = _('estimated amount per experiment (in MBq)')
   )
   room = models.CharField(
       max_length = 8,
       null = True,
       blank = True,
       verbose_name = _('room')
   )

   panels = AbstractNuclideRelation.panels + [ 
       FieldPanel('max_order'), 
       FieldPanel('amount_per_experiment'),
       FieldPanel('room'),

   ]
