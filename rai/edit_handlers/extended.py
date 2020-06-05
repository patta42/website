from .generic import RAIFieldPanel
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
import json

class RAIDependingFieldPanel(RAIFieldPanel):
    object_template = 'rai/edit_handlers/x/depending-field-panel_as-object.html'
    field_template = 'rai/edit_handlers/x/depending-field-panel_as-field.html'
    def __init__(self, field_name, depends_on = {}, *args, **kwargs):
        self.depends_on = depends_on
        super().__init__(field_name, *args, **kwargs)

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs['depends_on'] = self.depends_on
        return kwargs

    

    def render_as_object(self):
        return mark_safe(render_to_string(self.object_template, {
            'depends_on' : json.dumps(self.depends_on),
            'self': self,
            self.TEMPLATE_VAR: self,
            'field': self.bound_field,
        }))


    def render_as_field(self):
        return mark_safe(render_to_string(self.field_template, {
            'depends_on' : json.dumps(self.depends_on),
            'field': self.bound_field,
            'field_type': self.field_type(),
            'classes' : self.classes()
        }))
