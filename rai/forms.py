from pprint import pprint

"""
This is heavily copied from wagtail.admin.forms.models
"""
import copy

import rai.widgets as widgets

from django import forms
from django.db import models

from django.forms import formset_factory
from django.forms.forms import Form, DeclarativeFieldsMetaclass
from django.forms.models import (
    modelform_factory, modelformset_factory, BaseModelFormSet, ModelForm, ModelFormMetaclass
)
from django.forms.formsets import BaseFormSet
from django.forms.utils import ErrorList
from django.template.loader import render_to_string


from modelcluster.forms import ClusterForm, ClusterFormMetaclass

from wagtail.core.models import Page

FORM_FIELD_OVERRIDES = {
    # this has a widget for every known django database field
    #
    # TODO: Check the DB Fields from Wagtail
    models.BigIntegerField: {'widget': widgets.RAINumberInput},
    models.BinaryField: {'widget': widgets.RAITextInput},
    models.BooleanField: {'widget' : widgets.RAICheckboxInput},
#
    models.DateField: {'widget': widgets.RAIDateInput},
    models.DateTimeField: {'widget': widgets.RAIDateTimeInput},
    models.DecimalField: {'widget': widgets.RAINumberInput},
    models.DurationField: {'widget': widgets.RAITextInput},
    models.EmailField: {'widget': widgets.RAIEMailInput},
#    models.FileField:  {'widget': widgets.RAIFileInput},
    models.FilePathField: {'widget': widgets.RAISelect},
    models.FloatField: {'widget': widgets.RAINumberInput},
#    models.ImageField: {'widget': widgets.RAIImageInput},
    models.IntegerField: {'widget': widgets.RAINumberInput},
    models.GenericIPAddressField: {'widget': widgets.RAITextInput},
#    models.NullBooleanField: {'widget': widgets.RAICheckboxInput},
    models.PositiveIntegerField: {'widget': widgets.RAINumberInput},
    models.PositiveSmallIntegerField: {'widget': widgets.RAINumberInput},
    models.SlugField: {'widget': widgets.RAITextInput},
    models.SmallIntegerField: {'widget': widgets.RAINumberInput},
    models.TextField: {'widget': widgets.RAITextarea},
#    models.TimeField: {'widget': wigets.RAITimeInput},
    models.URLField: {'widget': widgets.RAIUrlInput},
    models.UUIDField: {'widget': widgets.RAITextInput},
    models.ForeignKey: {'widget': widgets.RAISelect},
    models.ManyToManyField: {'widget': widgets.RAISelectMultiple},
}
    

# Form field properties to override whenever we encounter a model field
# that matches one of these types exactly, ignoring subclasses.
# (This allows us to override the widget for models.TextField, but leave
# the RichTextField widget alone)
DIRECT_FORM_FIELD_OVERRIDES = {
#    models.TextField: {'widget': widgets.RAITextarea },
    models.CharField: {'widget': widgets.RAITextInput},
}


# Callback to allow us to override the default form fields provided for each model field.
def formfield_for_dbfield(db_field, **kwargs):
    # adapted from django/contrib/admin/options.py

    overrides = None

    # If we've got overrides for the formfield defined, use 'em. **kwargs
    # passed to formfield_for_dbfield override the defaults.
    if db_field.__class__ in DIRECT_FORM_FIELD_OVERRIDES:
        overrides = DIRECT_FORM_FIELD_OVERRIDES[db_field.__class__]
    else:
        for klass in db_field.__class__.mro():
            if klass in FORM_FIELD_OVERRIDES:
                overrides = FORM_FIELD_OVERRIDES[klass]
                break

    if overrides:
        if callable(overrides):
            overrides = overrides(db_field)

        kwargs = dict(copy.deepcopy(overrides), **kwargs)

    return db_field.formfield(**kwargs)


class RAIAdminModelFormMetaclass(ClusterFormMetaclass):#ModelFormMetaclass):
    # Override the behaviour of the regular ModelForm metaclass -
    # which handles the translation of model fields to form fields -
    # to use our own formfield_for_dbfield function to do that translation.
    # This is done by sneaking a formfield_callback property into the class
    # being defined (unless the class already provides a formfield_callback
    # of its own).

    # while we're at it, we'll also set extra_form_count to 0, as we're creating
    # extra forms in JS
    extra_form_count = 0

    def __new__(cls, name, bases, attrs):

        if 'formfield_callback' not in attrs or attrs['formfield_callback'] is None:
            attrs.update({'formfield_callback': formfield_for_dbfield})

        if 'readonly_fields' not in attrs or attrs['readonly_fields'] is None:
            attrs.update({'readonly_fields': {}})

        new_class = super().__new__(cls, name, bases, attrs)        
        return new_class

    @classmethod
    def child_form(cls):
        return RAIAdminModelForm

class RAIAdminFormMetaClass(DeclarativeFieldsMetaclass):
    def __new__(cls, name, bases, attrs):

        if 'formfield_callback' not in attrs or attrs['formfield_callback'] is None:
            attrs['formfield_callback'] = formfield_for_dbfield
        new_class = super().__new__(cls, name, bases, attrs)

        return new_class

class RAIAdminForm(Form, metaclass = RAIAdminFormMetaClass):
    pass

    
class RAIAdminModelForm(ClusterForm, metaclass=RAIAdminModelFormMetaclass):
    readonly_fields = {}
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


       
    @property
    def media(self):
        # Include media from formsets forms. This allow StreamField in InlinePanel for example.
        media = super().media
        for formset in self.formsets.values():
            media += formset.media
        return media


    def save(self, commit = True):
        if commit:
            if issubclass(self._meta.model, Page):
                instance = super().save(commit = False)
                revision = instance.save_revision(user = self.user)
                revision.publish()
            else:
                super().save(commit = True)
        else:
            return super().save(commit = False)
        
        
        
    
def rai_modelform_factory(
        model,
        form_class=RAIAdminModelForm,
        fields = None, exclude = None, formsets = None,
        exclude_formsets = None, widgets = None, treat_as_page = False,
        dont_exclude = []
):
    """
    A modified version of modelform_factory that checks if model is derived from
    Page and then adds some fields to exclude. If treat_as_page is False, will
    remove more fields 
    """

    attrs = {'model' : model}
    
    if issubclass(model, Page):
        if exclude is None:
            exclude = []
        auto_exclude = ['pk', 'path', 'depth', 'numchild', 'content_type', 'owner']
        if not treat_as_page:
            auto_exclude = auto_exclude + [
                'expire_at', 'seo_title', 'show_in_menus', 'go_live_at',
                'first_published_at', 'search_description', 'slug' ]
            
        for excl in auto_exclude:
            if hasattr(model, excl) and excl not in exclude and excl not in fields:
                exclude.append(excl)
    if exclude is not None:
        attrs['exclude'] = exclude
    if fields is not None:
        attrs['fields'] = fields
    if widgets is not None:
        attrs['widgets'] = widgets
    if formsets is not None:
        attrs['formsets'] = formsets
    if exclude_formsets is not None:
        attrs['exclude_formsets'] = exclude_formsets

    class_name = model.__name__ + str('RAIForm')
    bases = (object,)
    
    if hasattr(form_class, 'Meta'):
        bases = (form_class.Meta,) + bases

    form_class_attrs = {
        'Meta': type(str('Meta'), bases, attrs) 
    }

    metaclass = type(form_class)
    new_class = metaclass(class_name, (form_class,), form_class_attrs)

    return new_class



class RAIForm(Form):
    sub_forms = []
    fieldsets = []
    fieldset_template = 'rai/forms/form-as-fieldsets.html'

    edit_handler = None
    
    def set_fieldset_context(self, id, context):
        for fieldset in self.fieldsets:
            if id == fieldset['id']:
                fieldset.update(context)

                
    def as_fieldsets(self):
        fieldsets = []
        defaults = {
            'intro_context' : {},
            'legend_context': {}
        }
        for fieldset in self.fieldsets:
            fieldsets.append({**defaults, **fieldset})
            return render_to_string(
            self.fieldset_template,
            {
                'form':self,
                'fieldsets' : fieldsets
            }
        )

