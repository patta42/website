
from .forms import rai_form_factory
from .generic import RAIFieldPanel

from rai.edit_handlers.multiform import RAISubFormEditHandler
from rai.widgets import RAIRadioSelect

from django.forms import ChoiceField
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


from wagtail.core.models import Page

class RAINonModelFieldPanel(RAIFieldPanel):
    pass

class RAIChooseParentHandler(RAISubFormEditHandler):
    """
    implements a choose parent form

    """

    template = 'rai/edit_handlers/pages/choose-parent-handler.html'
    label = 'Unterhalb welcher Seite soll die neue Seite erzeugt werden?'
    def __init__(self, *args, **kwargs):
        self.label = kwargs.pop('label', None)
        
        super().__init__(children = [
            RAIParentChooserPanel('parent_page', label = self.label)
        ],*args, **kwargs)
        

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs['label'] = self.label
        del(kwargs['children'])
        return kwargs
        
    def compute_choices(self):
        allowed_parent_page_models = self.model.allowed_parent_page_models()
        content_types = ContentType.objects.get_for_models(*allowed_parent_page_models).values()
        self.page_choices = Page.objects.filter(content_type__in = content_types)

    def get_form_class(self):
        if not self.model:
            raise ImproperlyConfigured(
                'RAIChooseParentHandler needs to be bound to a model before '
                'the form class can be provided'
            )
        self.compute_choices()
        opts = self.model._meta
        name = '{}{}ParentChooser'.format(opts.app_label, opts.model_name)
        page_choices = list(self.page_choices)
        page_choices.sort(key=lambda x: x.specific.title_de)
        print(page_choices)
        choices = (
            (choice.pk, choice.specific.title_de)
            for choice in page_choices
        )

        return rai_form_factory(
            name,
            {
                'parent_page' : ChoiceField(
                    required = True,
                    label = self.label,
                    choices = choices,
                    widget = RAIRadioSelect 
                )
            }
        )

        
class RAIParentChooserPanel(RAINonModelFieldPanel):
#    def field_template = 'rai/edit_handlers/pages/parent-chooser-panel.html'
    def __init__(self, field_name, label = None, *args, **kwargs):
        self.label = label
        super().__init__(field_name, *args, **kwargs)


    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs['label'] = self.label
        return kwargs
    
    def render_as_field(self):
        if self.label:
            self.bound_field.label = self.label
        return mark_safe(render_to_string(self.field_template, {
            'field': self.bound_field,
            'field_type': self.field_type(),
            'classes' : self.classes()
        }))


