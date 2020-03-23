from django.template.loader import render_to_string
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe


from rai.forms import (
    RAIAdminModelForm, rai_modelform_factory, FORM_FIELD_OVERRIDES
)


from wagtail.admin import compare
from wagtail.admin.edit_handlers import EditHandler
from wagtail.core.utils import camelcase_to_underscore

class RAIEditHandler(EditHandler):
    """
    Base EditHandler for RAI

    Adds information about the PanelType, for debugging purposes mostly
    """

    def panel_type(self):
        return self.__class__.__name__
    
    def widget_overrides(self):
        """
        Use RAI widgets whenever possible
        """
        if hasattr(self, 'widget'):
            # user-defined widget, don't override
            return {self.field_name: self.widget}
        else:
            override = FORM_FIELD_OVERRIDES.get(self.db_field.__class__, None)
            if override:
                return { self.field_name: override['widget'] }    #
        return {}


class RAIBaseCompositeEditHandler(RAIEditHandler):
    """
    Abstract class for EditHandlers that manage a set of sub-EditHandlers.
    Concrete subclasses must attach a 'children' property
    """

    def __init__(self, children=(), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = children

    def clone(self):
        return self.__class__(
            children=self.children,
            heading=self.heading,
            classname=self.classname,
            help_text=self.help_text,
        )

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

    def html_declarations(self):
        return mark_safe(''.join([c.html_declarations() for c in self.children]))

    def on_model_bound(self):
        self.children = [child.bind_to_model(self.model)
                         for child in self.children]

    def on_instance_bound(self):
        children = []
        for child in self.children:
            
            if isinstance(child, RAIFieldPanel):
                if self.form._meta.exclude:
                    if child.field_name in self.form._meta.exclude:
                        continue
                if self.form._meta.fields:
                    if child.field_name not in self.form._meta.fields:

                        continue

            children.append(child.bind_to_instance(instance=self.instance,
                                                   form=self.form,
                                                   request=self.request))
        self.children = children

    def render(self):
        return mark_safe(render_to_string(self.template, {
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
                '%s is not bound to a model yet. Use `.bind_to_model(model)` '
                'before using this method.' % self.__class__.__name__)
        # If a custom form class was passed to the EditHandler, use it.
        # Otherwise, use the base_form_class from the model.
        # If that is not defined, use WagtailAdminModelForm.
        model_form_class = getattr(self.model, 'base_form_class',
                                   RAIAdminModelForm)
        base_form_class = self.base_form_class or model_form_class

        # For reasons I don't understand, the form_class generated above does
        # not automatically pick up the RAI widgets.

        form_class = rai_modelform_factory(
            self.model,
            form_class=base_form_class,
            fields=self.required_fields(),
            formsets=self.required_formsets(),
            widgets=self.widget_overrides())

        return form_class

class RAIFieldPanel(RAIEditHandler):
    TEMPLATE_VAR = 'field_panel'

    def __init__(self, field_name, *args, **kwargs):
        widget = kwargs.pop('widget', None)
        if widget is not None:
            self.widget = widget
        super().__init__(*args, **kwargs)
        self.field_name = field_name

    def clone(self):
        return self.__class__(
            field_name=self.field_name,
            widget=self.widget if hasattr(self, 'widget') else None,
            heading=self.heading,
            classname=self.classname,
            help_text=self.help_text
        )

#    def widget_overrides(self):
#        """check if a specific widget has been defined for this field"""
#        if hasattr(self, 'widget'):
#            return {self.field_name: self.widget}
#        return {}

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

    def on_instance_bound(self):
        self.bound_field = self.form[self.field_name]
        self.heading = self.bound_field.label
        self.help_text = self.bound_field.help_text

    def __repr__(self):
        class_name = self.__class__.__name__
        try:
            bound_to = force_text(getattr(self, 'instance',
                                          getattr(self, 'model')))
        except AttributeError:
            return "<%s '%s'>" % (class_name, self.field_name)
        return "<%s '%s' bound to %s>" % (class_name, self.field_name, bound_to)



    
def convert_from_wagtail(eh):
    return eh
