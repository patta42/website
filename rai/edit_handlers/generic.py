from pprint import pprint

from django.forms.models import modelformset_factory
from django.template.loader import render_to_string
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe


from rai.forms import (
    RAIAdminModelForm, rai_modelform_factory, FORM_FIELD_OVERRIDES, formfield_for_dbfield
)
from rai.utils import update_if_not_defined, debug

from taggit.managers import TaggableManager

from wagtail.admin import compare
from wagtail.core.utils import camelcase_to_underscore



class RAIEditHandler: 
    """
    Base EditHandler for RAI

    Code as in WT 2.8, but RAI currently uses WT 2.4, so the code is repeated here.

    - adds information about the PanelType, for debugging purposes mostly
    - picks up RAIWidgets if possible
    """
    def __init__(self, heading='', classname='', help_text='', disabled = False):
        self.heading = heading
        self.classname = classname
        self.help_text = help_text
        self.disabled = disabled
        self.model = None
        self.instance = None
        self.request = None
        self.form = None
        self.formsets = None
        
    def clone(self):
        return self.__class__(**self.clone_kwargs())

    def clone_kwargs(self):
        return {
            'heading': self.heading,
            'classname': self.classname,
            'help_text': self.help_text,
            'disabled' : self.disabled,
        }

    def disable(self, disabled_class = 'disabled'):
        """
        add 'disabled' to the classname
        """
        new = self.clone()
        new.disabled = True
        css_classes = new.classname.split(' ')
        if disabled_class not in css_classes:
            css_classes.append(disabled_class)
        new.classname = ' '.join(css_classes)

        new.on_disable(disabled_class)
        return new

    def on_disable(self, disabled_class):
        pass
        
    # return list of widget overrides that this EditHandler wants to be in place
    # on the form it receives
    def widget_overrides(self):
        """
        Use RAI widgets whenever possible
        """
        if hasattr(self, 'widget'):
            # user-defined widget, don't override
            return {self.field_name: self.widget}
#        else:
#            rride = FORM_FIELD_OVERRIDES.get(self.db_field.__class__, None)
#            if override:
#                return { self.field_name: override['widget'] }    #
        return {}


    # return list of fields that this EditHandler expects to find on the form
    def required_fields(self):
        return []

    # return a dict of formsets that this EditHandler requires to be present
    # as children of the ClusterForm; the dict is a mapping from relation name
    # to parameters to be passed as part of get_form_for_model's 'formsets' kwarg
    def required_formsets(self):
        return {}

    # return a dict of additional formsets that this edit handler requires to be
    # present outside(!) the main model form. Add the corresponding model
    # to the dict.
    def required_additional_formsets(self):
        return {}

    # return a dict of fields that are included, but not editable
    def readonly_fields(self):
        return {}
        
    # return any HTML that needs to be output on the edit page once per edit handler definition.
    # Typically this will be used to define snippets of HTML within <script type="text/x-template"></script> blocks
    # for Javascript code to work with.
    def html_declarations(self):
        return ''

    def bind_to(self, model=None, instance=None, request=None, form=None, formsets=None):
        if model is None and instance is not None and self.model is None:
            model = instance._meta.model

        new = self.clone()
        new.model = self.model if model is None else model
        new.instance = self.instance if instance is None else instance
        new.request = self.request if request is None else request
        new.form = self.form if form is None else form
        new.formsets = self.formsets if formsets is None else formsets

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

    def on_model_bound(self):
        pass

    def on_instance_bound(self):
        pass

    def on_request_bound(self):
        pass

    def on_form_bound(self):
        pass

    def on_formsets_bound(self):
        pass
    
    def __repr__(self):
        return '<%s with model=%s instance=%s request=%s form=%s formsets=%s>' % (
            self.__class__.__name__,
            self.model, self.instance, self.request, self.form.__class__.__name__, self.formsets)

    def classes(self):
        """
        Additional CSS classnames to add to whatever kind of object this is at output.
        Subclasses of EditHandler should override this, invoking super().classes() to
        append more classes specific to the situation.
        """
        if self.classname:
            return [self.classname]
        return []

    def field_type(self):
        """
        The kind of field it is e.g boolean_field. Useful for better semantic markup of field display based on type
        """
        return ""

    def id_for_label(self):
        """
        The ID to be used as the 'for' attribute of any <label> elements that refer
        to this object but are rendered outside of it. Leave blank if this object does not render
        as a single input field.
        """
        return ""

    def render_as_object(self):
        """
        Render this object as it should appear within an ObjectList. Should not
        include the <h2> heading or help text - ObjectList will supply those
        """
        # by default, assume that the subclass provides a catch-all render() method
        return self.render()

    def render_as_field(self):
        """
        Render this object as it should appear within a <ul class="fields"> list item
        """
        # by default, assume that the subclass provides a catch-all render() method
        return self.render()

    def render_missing_fields(self):
        """
        Helper function: render all of the fields that are defined on the form but not "claimed" by
        any panels via required_fields. These fields are most likely to be hidden fields introduced
        by the forms framework itself, such as ORDER / DELETE fields on formset members.
        (If they aren't actually hidden fields, then they will appear as ugly unstyled / label-less fields
        outside of the panel furniture. But there's not much we can do about that.)
        """
        rendered_fields = self.required_fields()
        missing_fields_html = [
            str(self.form[field_name])
            for field_name in self.form.fields
            if field_name not in rendered_fields
        ]

        return mark_safe(''.join(missing_fields_html))

    def render_form_content(self):
        """
        Render this as an 'object', ensuring that all fields necessary for a valid form
        submission are included
        """
        return mark_safe(self.render_as_object() + self.render_missing_fields())

    def get_comparison(self):
        return []


    def panel_type(self):
        """
        Possibilty to get the current panel type in templates. Can be helpful for debugging.
        """
        return self.__class__.__name__


class RAIBaseCompositeEditHandler(RAIEditHandler):
    """
    Abstract class for EditHandlers that manage a set of sub-EditHandlers.
    Concrete subclasses must attach a 'children' property
    """

    def __init__(self, children=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = children

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs['children'] = self.children
        return kwargs

    def widget_overrides(self):
        # build a collated version of all its children's widget lists
        widgets = {}
        for handler_class in self.children:
            widgets.update(handler_class.widget_overrides())
        widget_overrides = widgets

        return widget_overrides

    def required_fields(self):
        fields = []
        for handler in self.children:
            fields.extend(handler.required_fields())
        return fields

    def required_formsets(self):
        formsets = {}
        for handler_class in self.children:
            formsets.update(handler_class.required_formsets())
        return formsets
    def readonly_fields(self):
        readonly = {}
        for handler_class in self.children:
            readonly.update(handler_class.readonly_fields())
        return readonly
    def required_additional_formsets(self):
        formsets = {}
        for handler_class in self.children:
            formsets.update(handler_class.required_additional_formsets())
        return formsets

    
    def html_declarations(self):
        return mark_safe(''.join([c.html_declarations() for c in self.children]))

    def on_model_bound(self):
        
        try:
            model = self.model
        except AttributeError:
            model = None
        
        if model:
            self.children = [
                child.bind_to(model=self.model) for child in self.children
            ]
        else:
            self.children = []
            
            
    def on_instance_bound(self):
        self.children = [child.bind_to(instance=self.instance)
                         for child in self.children]
        
    def on_request_bound(self):
        self.children = [child.bind_to(request=self.request)
                         for child in self.children]

    def _bind_children_to(self, attr):
        children = []
        for child in self.children:
            readonly = self.readonly_fields().keys()
            
            if hasattr(child, 'field_name') and child.field_name not in readonly:
                if isinstance(child, RAIFieldPanel):
                    obj = getattr(self, attr)
                    meta = getattr(obj, '_meta', None)
                    if meta and hasattr(meta, 'exclude') and meta.exclude:
                        if child.field_name in meta.exclude:
                            continue
                    if meta and hasattr(meta, 'fields'):
                        if child.field_name not in meta.fields:
                            continue
            children.append(child.bind_to(**{attr:getattr(self, attr)}))
        return children
        
    def on_form_bound(self):
        self.children = self._bind_children_to('form')

    def on_formset_bound(self):
        self.children = self._bind_children_to('formset')

    def on_disable(self, disabled_class):
        self.children = [child.disable(disabled_class)
                         for child in self.children]
    def render(self):
        return self._render(self.template)
    
    def _render(self, template):
        return mark_safe(render_to_string(template, {
            'self': self
        }))
    
    def get_comparison(self):
        comparators = []

        for child in self.children:
            comparators.extend(child.get_comparison())

        return comparators

        

class RAIBaseFormEditHandler(RAIBaseCompositeEditHandler):

    base_form_class = None
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
            self.model,
            form_class=base_form_class,
            fields=self.required_fields(),
            formsets=formsets,
            widgets=self.widget_overrides())
        form_class.readonly_fields = self.readonly_fields()
        return form_class

    def get_additional_formset_classes(self):
        formsets = self.required_additional_formsets()
        formset_classes = {}
        for key, formset_spec in formsets.items():
            model = formset_spec['model']
            model_form_class = getattr(
                model, 'rai_base_form_class',
                RAIAdminModelForm
            )
            base_form_class = self.base_form_class or model_form_class
            formset_kwargs = formset_spec.get('formset_kwargs', {})
            formset_kwargs = update_if_not_defined(formset_kwargs, 'form', model_form_class)
            formset_class = modelformset_factory(formset_spec['model'], **formset_kwargs)
            formset_classes.update( { key: formset_class } )
        return formset_classes
    

class RAIFieldPanel(RAIEditHandler):
    TEMPLATE_VAR = 'field_panel'

    def __init__(self, field_name, *args, **kwargs):
        widget = kwargs.pop('widget', None)
        if widget is not None:
            self.widget = widget
        super().__init__(*args, **kwargs)
        self.field_name = field_name
    def clone_kwargs(self):    
        kwargs = super().clone_kwargs()
        kwargs.update(
            field_name=self.field_name,
            widget=self.widget if hasattr(self, 'widget') else None,
        )
        
    
        return kwargs
    
    def classes(self):
        classes = super().classes()
        if self.bound_field.field.required:
            classes.append("required")
        if self.bound_field.errors:
            classes.append("error")
        classes.append(self.field_type())

        return classes

    def field_type(self):
        return camelcase_to_underscore(self.bound_field.field.__class__.__name__)

    def id_for_label(self):
        return self.bound_field.id_for_label

    object_template = "rai/edit_handlers/field-panel-as_object.html"

    def render_as_object(self):
        return mark_safe(render_to_string(self.object_template, {
            'self': self,
            self.TEMPLATE_VAR: self,
            'field': self.bound_field,
        }))

    field_template = "rai/edit_handlers/field-panel-as_field.html"

    def render_as_field(self):
        return mark_safe(render_to_string(self.field_template, {
            'field': self.bound_field,
            'field_type': self.field_type(),
            'classes' : self.classes()
        }))

    def required_fields(self):
        return [self.field_name]

    def get_comparison_class(self):
        # Hide fields with hidden widget
        widget_override = self.widget_overrides().get(self.field_name, None)
        if widget_override and widget_override.is_hidden:
            return

        try:
            field = self.db_field

            if field.choices:
                return compare.ChoiceFieldComparison

            if field.is_relation:
                if isinstance(field, TaggableManager):
                    return compare.TagsFieldComparison
                elif field.many_to_many:
                    return compare.M2MFieldComparison

                return compare.ForeignObjectComparison

            if isinstance(field, RichTextField):
                return compare.RichTextFieldComparison

            if isinstance(field, (CharField, TextField)):
                return compare.TextFieldComparison

        except FieldDoesNotExist:
            pass

        return compare.FieldComparison

    def get_comparison(self):
        comparator_class = self.get_comparison_class()

        if comparator_class:
            try:
                return [functools.partial(comparator_class, self.db_field)]
            except FieldDoesNotExist:
                return []
        return []

    @cached_property
    def db_field(self):
        try:
            model = self.model
        except AttributeError:
            raise ImproperlyConfigured("%r must be bound to a model before calling db_field" % self)

        
        return model._meta.get_field(self.field_name)

    def on_form_bound(self):
        self.bound_field = self.form[self.field_name]
        self.heading = self.bound_field.label
        self.help_text = self.bound_field.help_text
        
        
    def __repr__(self):
        return "<%s '%s' with model=%s instance=%s request=%s form=%s>" % (
            self.__class__.__name__, self.field_name,
            self.model, self.instance, self.request, self.form.__class__.__name__)
    
    
