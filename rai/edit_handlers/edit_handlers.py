from pprint import pprint 
from .generic import (
    RAIEditHandler,
    RAIBaseFormEditHandler,
    RAIBaseCompositeEditHandler,
    RAIFieldPanel
)


#from .utils import extract_panel_definitions_from_model_class

from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.forms.formsets import DELETION_FIELD_NAME, ORDERING_FIELD_NAME
from django.forms.models import fields_for_model
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe

import functools

#from .utils import extract_panel_definitions_from_model_class

import json
import random
from rai.forms import formfield_for_dbfield, RAIAdminModelForm, rai_modelform_factory

import string
import uuid

from wagtail.admin import compare

class RenderObjectFieldMixin:
    def render_as_object(self):
        return self._render(self.object_template)
    def render_as_field(self):
        return self._render(self.field_template)



class RAITabbedInterface(RAIBaseFormEditHandler):
    template = "wagtailadmin/edit_handlers/tabbed_interface.html"

    def __init__(self, *args, **kwargs):
        
        self.base_form_class = kwargs.pop('base_form_class', None)
        super().__init__(*args, **kwargs)


    
    def clone(self):
        new = super().clone()
        new.base_form_class = self.base_form_class
        return new

    
class RAIObjectList(RAIBaseFormEditHandler):
    template = 'rai/edit_handlers/object-list.html'
    def __init__(self, *args, **kwargs):
        self.wrapper_classes = kwargs.pop('wrapper_classes', None)
        self.base_form_class = kwargs.pop('base_form_class', None)
        super().__init__(*args, **kwargs)
    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs.update({'base_form_class': self.base_form_class, 'wrapper_classes' : self.wrapper_classes})
        return kwargs
    
class RAIFieldList(RAIObjectList):
    template = 'rai/edit_handlers/field-list.html'
    
    
class RAIFieldRowPanel(RAIBaseFormEditHandler):
    object_template = "rai/edit_handlers/field-row-panel_as-object.html"
    field_template = "rai/edit_handlers/field-row-panel_as-field.html"

    def check_for_errors(self):
        self.children_have_errors = False
        for child in self.children:
            if child.bound_field.errors:
                self.children_have_errors = True
                break
        
    def render_as_object(self):
        self.check_for_errors()
        return self._render(self.object_template)
    def render_as_field(self):
        self.check_for_errors()
        return self._render(self.field_template)
    
class RAICollapsablePanel(RAIBaseFormEditHandler):
    is_collapsable = True
    template = 'rai/edit_handlers/collapsable-panel.html'
    
    def __init__(self, *args, **kwargs):
        self.is_collapsed = kwargs.pop('is_collapsed', True)
        self.collapse_id = kwargs.pop('collapse_id', uuid.uuid4())
        self.is_expanded = kwargs.pop('is_expanded', False)
        

        heading = kwargs.pop('heading', None)
        if heading is None:
            raise ImproperlyConfigured(
                "The attribute `heading` is required for {0}".format(
                    self.__class__.__name__
                )
            )            
        super().__init__( heading = heading, *args, **kwargs)

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs.update({
            'collapse_id' : self.collapse_id,
            'is_expanded' : self.is_expanded
        })
        return kwargs
        

class RAIUserDataPanel(RAICollapsablePanel):
    """
    A panel that shows information that is entered by external users.
    Issues a visual warning to avoid editing
    """
    template = 'rai/edit_handlers/userdata-panel.html'

    
class RAICollectionPanel(RAIBaseFormEditHandler):
    """
    A collection panel is a panel without any sorrounding HTML introduced by 
    the panel. Children are rendered as fields.

    Exception is if "depends on" is set. Then, a <div> surrounds the content 
    which can be hidden by JS.   
    """

    template = 'rai/edit_handlers/collection-panel.html'
    
    def __init__(self, *args, **kwargs):
        self.depends_on = kwargs.pop('depends_on', None)
        super().__init__(*args, **kwargs)

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs['depends_on'] = self.depends_on
        return kwargs

    
    def render(self):
        return render_to_string(
            self.template,
            {
                'self' : self,
                'depends_on' : json.dumps(self.depends_on) if self.depends_on else None
            }
        )

    
    
    

class RAIPillsPanel(RAIBaseFormEditHandler):
    """
    A pills panel shows its children in pills. Children are rendered as objects.
    if rendered as field, it is shown in a fieldset.
    """
    object_template = 'rai/edit_handlers/pills-panel.html'
    field_template = 'rai/edit_handlers/pills-panel_as-field.html'
    
    def __init__(self, *args, **kwargs):
        self.unique_id = kwargs.pop(
            'unique_id',
            ''.join(
                random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(10) 
            )
        )
        self.nav_label = kwargs.pop('nav_label', None)
        super().__init__(*args, **kwargs)

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs.update({
            'unique_id' : self.unique_id,
            'nav_label' : self.nav_label
        })
        return kwargs

    def render(self):
        # default is to render as field
        return self.render_as_field()
    
    def render_as_object(self):
        return self._render(self.object_template)
    def render_as_field(self):
        return self._render(self.field_template)

    def _render(self, template):
        return mark_safe(
            render_to_string(template, {
                'self' : self
            })
        )

    
class RAITranslatedContentPanel(RAIPillsPanel):
    """
    A Panel which automatically builds a RAIPillsPanel for translated content.

    It simply uses RAIFieldPanels for the fields. For more complex layout, built a 
    RAIPillsPanel manually.
    """

    # It would be easier if I'd know a way to read the field_en and field_de properties
    # of website.models.TranslatedField. However, I don't know how to access them.
    #
    # Thus, I use a (reasonable) guess:
    #
    # If field is title, field_en = title and field_de = title_de
    # ion any other case, field_en = <foo>_en and field_de = <foo>_de

    def __init__(self, languages, fieldnames, *args, **kwargs):
        """
        languages should be a dict like {'de':'german', 'en':'english'}, that is, 
        suffix -> name

        fieldnames is a list of fieldnames without suffix.
        """
        nav_label = kwargs.pop('nav_label', 'Select language')
        kwargs.update({'nav_label':nav_label})

        
        children = []
        for suffix, lang in languages.items():
            grandchildren = []
            for field in fieldnames:
                if not(suffix == 'en' and field == 'title'):
                    field_name = "{field}_{suffix}".format(field = field, suffix = suffix)
                else:
                    field_name = field                    
                grandchildren.append(RAIFieldPanel(field_name))
            children.append(RAICollectionPanel(grandchildren, heading = lang))
        super().__init__(children, *args, **kwargs)        

    def clone(self):
        return RAIPillsPanel(**self.clone_kwargs())


class RAIMultiFieldPanel(RAIBaseCompositeEditHandler):
    template = 'rai/edit_handlers/multi-field-panel.html'

    def classes(self):
        classes = super().classes()
        classes.append('multi-field')
        return classes


class RAIInlinePanel(RAIEditHandler):
    is_collapsable = True
    def __init__(
            self, relation_name, panels=None, heading='', label='',
            min_num=None, max_num=None, show_all_options = False,
            add_button_label = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.relation_name = relation_name
        self.panels = panels
        self.heading = heading or label
        self.label = label
        self.min_num = min_num
        self.max_num = max_num
        self.show_all_options = show_all_options
        self.add_button_label = add_button_label
    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs.update(
            relation_name=self.relation_name,
            panels=self.panels,
            label=self.label,
            min_num=self.min_num,
            max_num=self.max_num,
            show_all_options = self.show_all_options,
            add_button_label = self.add_button_label 
        )
        return kwargs

    def get_panel_definitions(self):
        # Look for a panels definition in the InlinePanel declaration
        if self.panels is not None:
            return self.panels
        # otehrwise, raise an error
        raise ImproperlyConfigured(
            'RAIInlinePanels needs a panel definition.'
        )

    def get_child_edit_handler(self):
        panels = self.get_panel_definitions()
        child_edit_handler = RAICollectionPanel(panels, heading=self.heading)
        return child_edit_handler.bind_to(model=self.db_field.related_model)

    def required_formsets(self):
        child_edit_handler = self.get_child_edit_handler()
        return {
            self.relation_name: {
                'fields': child_edit_handler.required_fields(),
                'widgets': child_edit_handler.widget_overrides(),
                'min_num': self.min_num,
                'validate_min': self.min_num is not None,
                'max_num': self.max_num,
                'validate_max': self.max_num is not None
            }
        }

    def html_declarations(self):
        return self.get_child_edit_handler().html_declarations()

    def get_comparison(self):
        field_comparisons = []

        for panel in self.get_panel_definitions():
            field_comparisons.extend(
                panel.bind_to(model=self.db_field.related_model)
                .get_comparison())

        return [functools.partial(compare.ChildRelationComparison, self.db_field, field_comparisons)]

    def on_model_bound(self):
        manager = getattr(self.model, self.relation_name)
        self.db_field = manager.rel

    def on_form_bound(self):
        self.formset = self.form.formsets[self.relation_name]

        self.children = []
        for subform in self.formset.forms:
            # override the DELETE field to have a hidden input
            subform.fields[DELETION_FIELD_NAME].widget = forms.HiddenInput()

            # ditto for the ORDER field, if present
            if self.formset.can_order:
                subform.fields[ORDERING_FIELD_NAME].widget = forms.HiddenInput()

            child_edit_handler = self.get_child_edit_handler()
            self.children.append(child_edit_handler.bind_to(
                instance=subform.instance, request=self.request, form=subform))

        # if this formset is valid, it may have been re-ordered; respect that
        # in case the parent form errored and we need to re-render
        if self.formset.can_order and self.formset.is_valid():
            for child in self.children:
                pprint(child.form.fields)
                for field in child.form.fields:
                    print(field)
                    #print ('{}: {}'.format(field, 'foo'))
                
                pprint(child.form.cleaned_data)
            #self.children.sort(
            #    key=lambda child: child.form.cleaned_data[ORDERING_FIELD_NAME] or 1)

        empty_form = self.formset.empty_form
        empty_form.fields[DELETION_FIELD_NAME].widget = forms.HiddenInput()
        if self.formset.can_order:
            empty_form.fields[ORDERING_FIELD_NAME].widget = forms.HiddenInput()

        self.empty_child = self.get_child_edit_handler()
        self.empty_child = self.empty_child.bind_to(
            instance=empty_form.instance, request=self.request, form=empty_form)


        
    template = "rai/edit_handlers/inline-panel.html"
    
        
    def render(self):
        formset = render_to_string(self.template, {
            'self': self,
            'can_order': self.formset.can_order,
            'can_delete' : True
        })
        return formset


class RAIQueryInlinePanel(RAIBaseFormEditHandler):
    """
    An InlinePanel-like panel that allows showing the result of a different query.
    Thus, the model used for this Panel does not need to be attached to the model
    of the parent's edit_handler
    """

    is_collapsable = True
    template = 'rai/edit_handlers/query-inline-panel.html'
    child_template = 'rai/edit_handlers/inline-panel-child.html'

    formset = None
    formset_formclass = None
    
    def __init__(self, name, model, query_callback, panels, *args, **kwargs):
        self.name = name
        self.query_callback = query_callback
        self.panels = panels
        self.long_heading = kwargs.pop('long_heading', None)
        self.can_order = kwargs.pop('can_order', False)
        self.allow_add = kwargs.pop('allow_add', None)
        self.can_delete = kwargs.pop('can_delete', False)
        self.extra = kwargs.pop('extra', 0)
        self.max_num = kwargs.pop('max_num', None)
        self.validate_max = kwargs.pop('validate_max', self.max_num is not None)
        self.min_num = kwargs.pop('min_num',None)
        self.validate_min = kwargs.pop('validate_min', self.min_num is not None)
        super().__init__(*args, **kwargs)

        # Note that here a model is bound!
        
        self.model = model        
        self.on_model_bound()

        

    # this function return the kwargs used for the call to a formset class,
    # including the ones that are not used for cloning (see get_formset_kwargs below)

    def get_full_formset_kwargs(self):
        formset_kwargs = self.get_formset_kwargs()
        
        #update with fields and widgets
        formset_kwargs.update({
            'fields' : self.get_child_edit_handler().required_fields(),
            'widgets' : self.widget_overrides(),
        })
        return formset_kwargs

    

    # the binding stuff is hard to understand.
    #
    # if bind_to(model=...) is called, it will be from a parent edit_handler.
    # This one has its own model, so just self.model. A model should be sufficient to
    # build the formset. Do this in on_model_bound()

    def on_model_bound(self):
        # If adding is allowed, we show (at least) one additional form
        kwargs = self.get_full_formset_kwargs()
        if self.allow_add:
            extra = kwargs.pop('extra', 1)
            if extra is None or extra == 0:
                extra = 1
            kwargs.update({'extra': extra})

        # set self.Formset_Class
        self.Formset_Class = forms.modelformset_factory(
            self.model,
            formfield_callback = formfield_for_dbfield,
            form = self.formset_formclass or RAIAdminModelForm,
            **kwargs
        )
        # since this might be the only call to a bind_to method (most likely
        # if we want to show an empty form) set self.formset to an initiated
        # version of this formset. use self.name as a prefix
        #
        self.formset = self.Formset_Class(prefix = self.name, queryset = self.model.objects.none())

        # bind the children 
        self.bind_formset_forms()

    def get_form_class(self):
        form = super().get_formclass()
        
        form.formsets[self.name] = self.FormsetClass
        form.formsets[self.name].readonly_fields = self.readonly_fields()
        return form

    def on_form_bound(self):
        # what shall we do with a form? We use formsets here
        
        # self.formset = self.Formset_Class(queryset = self.model.objects.none())
        # self.form.formsets.update({
        #     self.name : self.formset
        # })
        
        # # bind children to formset_forms:
        # self.bind_formset_forms()
        pass


    # shorthand to bind the children to the forms of  the formset

    def bind_formset_forms(self):
        
        children = []
        for subform in self.formset.forms:
            children.append(
                self.get_child_edit_handler().bind_to(
                    model = self.model, form = subform, instance = subform.instance
                )
            )
        self.children = children



        
    # If an instance is bound, we assume we have a Formset_Class already. 
    # Rebuild the formset, this time with a query.
    
    def on_instance_bound(self):
        # without an instance and adding allowed, the extras parameter was ignored if it was 0 or None
        # Now, it is fine to show just an add-button but no empty form. For this, we have to re-buid
        # the class
        
        self.Formset_Class = forms.modelformset_factory(
            self.model,
            formfield_callback = formfield_for_dbfield,
            form = self.formset_formclass or RAIAdminModelForm,
            **self.get_full_formset_kwargs()
        )
        qs = self.query_callback(self.instance)
        self.formset = self.Formset_Class( queryset = qs, prefix = self.name )
        for subform in self.formset.forms:
            # override the DELETE field to have a hidden input
            if self.formset.can_delete:
                try: 
                    subform.fields[DELETION_FIELD_NAME].widget = forms.HiddenInput()
                except KeyError:
                    pass
            
            # ditto for the ORDER field, if present
            if self.formset.can_order:
                subform.fields[ORDERING_FIELD_NAME].widget = forms.HiddenInput()

        self.bind_formset_forms()
        empty_form = self.formset.empty_form
        try:
            empty_form.fields[DELETION_FIELD_NAME].widget = forms.HiddenInput()
        except KeyError:
            pass
        if self.formset.can_order:
            empty_form.fields[ORDERING_FIELD_NAME].widget = forms.HiddenInput()

        self.empty_child = self.get_child_edit_handler()
        self.empty_child = self.empty_child.bind_to(
            instance=empty_form.instance, request=self.request, form=empty_form)



        
    def bind_to(self, model=None, form=None, instance=None, request=None, formsets = None):

        new = self.clone()
        
        # don't use the parent's model 
        new.model = self.model 
        # don't use the parent's form
        new.form = self.form 
        # don't use parent formsets
        new.formsets = self.formsets
        
        new.instance = self.instance if instance is None else instance
        new.request = self.request if request is None else request

        if new.model is not None:
            new.on_model_bound()

        if new.form is not None:
            new.on_form_bound()

        if new.formsets is not None:
            new.on_formsets_bound()
            
        if new.instance is not None:
            new.on_instance_bound()

        if new.request is not None:
            new.on_request_bound()


        return new

    def classes(self):
        classes = super().classes()
        classes.append('inline-panel')
        return classes
    
    def clone(self):
        return self.__class__(
            self.name, self.model, self.query_callback, self.panels,
            **self.clone_kwargs()
        )
    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs.update(self.get_formset_kwargs())
        kwargs.update({
            'allow_add' : self.allow_add,
            'long_heading' : self.long_heading
        })
        
        return kwargs

    def get_formset_kwargs(self):
        """
        returns the kwargs accepted by the panel for the call to formset_factory
        """
        return {
            'can_order':self.can_order,
            'can_delete':self.can_delete,
            'extra':self.extra,
            'max_num' : self.max_num,
            'validate_max' : self.validate_max,
            'min_num' : self.min_num,
            'validate_min' : self.validate_min,
        }

    def required_fields(self):
        # We don't need any fields in the parent form
        return []
        
    
    def get_child_edit_handler(self):
        panels = self.get_panel_definitions()
        child_edit_handler = RAICollectionPanel(panels, heading=self.heading)
        return child_edit_handler.bind_to(model=self.model)

    def required_formsets(self):
        # We don't need any formsets in the parent form
        # child_edit_handler = self.get_child_edit_handler()
        # formsets = {
        #     self.name: {
        #         'fields': child_edit_handler.required_fields(),
        #         'widgets': child_edit_handler.widget_overrides(),
        #         'model' : self.model
        #     }
        # }
        # return formsets
        return {}

    def required_additional_formsets(self):
        return { self.name: {
            'model' : self.model,
            'formset_kwargs' : self.get_full_formset_kwargs()
        }}
    
    def html_declarations(self):
        return self.get_child_edit_handler().html_declarations()
    
    def get_panel_definitions(self):
        # Look for a panels definition in the InlinePanel declaration
        if self.panels is not None:
            return self.panels
        # Failing that, get it from the model
        return rai.edit_handlers.utils.extract_panel_definitions_from_model_class(
            self.model,
            exclude=[self.name]
        )

    
    def render(self):
        formset = render_to_string(self.template, {
            'self': self,
            'can_order': self.formset.can_order,
        })
        return formset

    def __repr__(self):
        return "<%s '%s' with model=%s instance=%s request=%s form=%s formset=%s>" % (
            self.__class__.__name__, self.name,
            self.model, self.instance, self.request, self.form.__class__.__name__, self.formset.__class__.__name__)

    
class RAIMissingPanel(RAIEditHandler):
    """
    A panel indicating a missing Panel.
    For conversion from Wagtail edit_handlers
    """
    template = "rai/edit_handlers/missing-panel.html"
    def __init__(self, missing = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.missing = missing
    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs.update({'missing':self.missing})
        return kwargs
    def widget_overrides(self):
        return {}
    def render(self):
        return render_to_string(self.template, {'self':self})


class RAIReadOnlyPanel(RAIFieldPanel):
    field_template = 'rai/edit_handlers/readonly-as_field.html'
    object_template = 'rai/edit_handlers/readonly-as_object.html'
    
    def required_fields(self):
        return []
    def classes(self):
        if self.classname:
            return [self.classname]
        return []

    def readonly_fields(self):
        try:
            db_field = self.db_field
        except ImproperlyConfigured:
            db_field = None
        if db_field:
            label = db_field.verbose_name,
            help_text = db_field.help_text
        else:
            label = ''
            help_text = ''
        return {
            self.field_name: {
                'label' : label,
                'help_text': help_text,
                'value': getattr(self, 'value', None)
            }
        }

    def on_instance_bound(self):
        self.form.readonly_fields.update({
            self.field_name : {
                'label' : self.db_field.verbose_name,
                'help_text' : self.db_field.help_text,
                'value' : getattr(self.instance, self.field_name, None)
            }
        })
        self.value = getattr(self.instance, self.field_name, None)
  

    def render(self):
        return mark_safe('{}: {} ({})'.format('me', self.value, self.field_name))

    def render_as_field(self):
        return mark_safe(
            render_to_string(self.field_template, {
                'field_name' : self.field_name,
                'label' : self.db_field.verbose_name,
                'help_text' : self.db_field.help_text,
                'value' : getattr(self.instance, self.field_name, None)
            })
        )
        
    def render_as_object(self):
        return mark_safe(
            render_to_string(self.object_template, {
                'field_name' : self.field_name,
                'label' : self.db_field.verbose_name,
                'help_text' : self.db_field.help_text,
                'value' : getattr(self.instance, self.field_name, None)
            })
        )
    def on_form_bound(self):
        pass
    
    @cached_property
    def db_field(self):
        try:
            model = self.model
        except AttributeError:
            raise ImproperlyConfigured("%r must be bound to a model before calling db_field" % self)
        if not model:
            raise ImproperlyConfigured("%r must be bound to a model before calling db_field" % self)
        return model._meta.get_field(self.field_name)


class RAIInputGroupCollectionPanel(RenderObjectFieldMixin, RAIBaseCompositeEditHandler):
    object_template = 'rai/edit_handlers/input-group.html'
    field_template = 'rai/edit_handlers/input-group_as-field.html'

    def render(self):
        return self.render_as_field()
    
    def _render(self, template):
        print ('Using template: {}'.format(template))
        return mark_safe(
            render_to_string(template, {
                'self' : self,
                'prepend' : self.children[0],
                'field': self.children[1]
            })
        )
        

class RAIDecorationPanel(RAIObjectList):
    def __init__(self, rai_model_id, panels = [], *args, **kwargs):
        self.rai_model_id = rai_model_id
        self.panels = panels
        super().__init__(*args, **kwargs)

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs['rai_model_id'] = self.rai_model_id
        kwargs['panels'] = self.panels
        
        return kwargs

    def get_child_edit_handler(self):
        return RAIMultiFieldPanel(self.panels)
            
    
    def get_queryset(self):
        field = self.decorator.field_in_decorated_model
        return getattr(self.instance, field).all()

        
    def on_model_bound(self):
        from rai.internals import get_decorator_for
        opts = self.model._meta
        decorated_model_id = '{}.{}'.format(opts.app_label, opts.model_name)
        self.decorator = get_decorator_for(self.rai_model_id, decorated_model_id)
        self.rai_model = self.decorator.get_rai_model()
        child_edit_handler = self.get_child_edit_handler()
        self.form_class = self.get_form_class()
        child_edit_handler = child_edit_handler.bind_to(
            model = self.rai_model,
            form = self.form_class(),
        )
        self.children = [ child_edit_handler ]
    def on_form_bound(self):
        pass

    def on_instance_bound(self):
        from rai.internals import get_decorator_for
        opts = self.model._meta
        decorated_model_id = '{}.{}'.format(opts.app_label, opts.model_name)
        
        qs = self.get_queryset()
        
        children = []
        for obj in qs:
            child_edit_handler = self.get_child_edit_handler()
            child_edit_handler = child_edit_handler.bind_to(
                model = self.decorator.get_rai_model(),
                form = self.form_class(instance = obj.rai_model),
                instance = obj.rai_model
            )
            children.append(child_edit_handler)
        self.children = children

    def on_request_bound(self):
        from rai.internals import get_decorator_for
        opts = self.model._meta
        decorated_model_id = '{}.{}'.format(opts.app_label, opts.model_name)
        

        children = []
        if self.instance:
            qs = self.get_queryset()
            for obj in qs:
                child_edit_handler = self.get_child_edit_handler()
                child_edit_handler = child_edit_handler.bind_to(
                    model = self.decorator.get_rai_model(),
                    form = self.form_class(instance = obj.rai_model),
                    instance = obj.rai_model,
                    request = self.request
                )
                children.append(child_edit_handler)
        else:
            child_edit_handler = self.get_child_edit_handler()
            child_edit_handler = child_edit_handler.bind_to(model = self.decorator.get_rai_model())
            child_edit_handler = child_edit_handler.bind_to(request = self.request)

        self.children = children
        
    def get_form_class(self):
        """
        Adapt to use RAIAdminModelForm instead of WagtailAdminModelForm
        """
        
        """
        Construct a form class that has all the fields and formsets named in
        the children of this edit handler. 
        """
        if not hasattr(self, 'model'):
            raise AttributeError(
                '%s is not bound to a model yet. Use `.bind_to(model=model)` '
                'before using this method.' % self.__class__.__name__)
        # If a custom form class was passed to the EditHandler, use it.
        # Otherwise, use the rai_base_form_class from the model.
        # If that is not defined, use RAIAdminModelForm.
        model_form_class = getattr(self.model, 'rai_base_form_class',
                                   RAIAdminModelForm)
        base_form_class = self.base_form_class or model_form_class

        formsets = self.required_formsets()

        form_class = rai_modelform_factory(
            self.decorator.get_rai_model(),
            form_class=base_form_class,
            fields=self.required_internal_fields(),
            formsets=formsets,
            widgets=self.widget_overrides())
        form_class.readonly_fields = self.readonly_fields()
        return form_class

        

    def required_internal_fields(self):
        return super().required_fields()

    def required_fields(self):
        return []

    def required_formsets(self):
        return {}

    def required_additional_formsets(self):
        return {}

    def html_declarations(self):
        return ''

    
