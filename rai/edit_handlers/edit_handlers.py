from .generic import (
    RAIEditHandler,
    RAIBaseFormEditHandler,
    RAIBaseCompositeEditHandler,
    RAIFieldPanel
)

from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.forms.formsets import DELETION_FIELD_NAME, ORDERING_FIELD_NAME
from django.forms.models import fields_for_model
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

import functools

#from .utils import extract_panel_definitions_from_model_class

import random
import string
import uuid





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
        self.base_form_class = kwargs.pop('base_form_class', None)
        super().__init__(*args, **kwargs)
    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs.update({'base_form_class': self.base_form_class})
        return kwargs
    
    
class RAIFieldRowPanel(RAIBaseFormEditHandler):
    template = "rai/edit_handlers/field-row-panel.html"

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
    template = 'rai/edit_handlers/collection-panel.html'
    
class RAIPillsPanel(RAIBaseFormEditHandler):
    template = 'rai/edit_handlers/pills-panel.html'

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
    def __init__(self, relation_name, panels=None, heading='', label='',
                 min_num=None, max_num=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.relation_name = relation_name
        self.panels = panels
        self.heading = heading or label
        self.label = label
        self.min_num = min_num
        self.max_num = max_num

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs.update(
            relation_name=self.relation_name,
            panels=self.panels,
            label=self.label,
            min_num=self.min_num,
            max_num=self.max_num,
        )
        return kwargs

    def get_panel_definitions(self):
        # Look for a panels definition in the InlinePanel declaration
        if self.panels is not None:
            return self.panels
        # Failing that, get it from the model
        return rai.edit_handlers.utils.extract_panel_definitions_from_model_class(
            self.db_field.related_model,
            exclude=[self.db_field.field.name]
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
            self.children.sort(
                key=lambda child: child.form.cleaned_data[ORDERING_FIELD_NAME] or 1)

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
        })
        js = self.render_js_init()
        return formset#widget_with_script(formset, js)

    js_template = "wagtailadmin/edit_handlers/inline_panel.js"

    def render_js_init(self):
        return mark_safe(render_to_string(self.js_template, {
            'self': self,
            'can_order': self.formset.can_order,
        }))


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
