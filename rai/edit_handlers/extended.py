from .generic import RAIFieldPanel
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from wagtail.admin.edit_handlers import StreamFieldPanel

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
    
class RAIStreamFieldPanel(RAIFieldPanel):
    def classes(self):
        classes = super().classes()
        classes.append("stream-field")

        # In case of a validation error, BlockWidget will take care of outputting the error on the
        # relevant sub-block, so we don't want the stream block as a whole to be wrapped in an 'error' class.
        if 'error' in classes:
            classes.remove("error")

        return classes

    def html_declarations(self):
        self.block_def.all_html_declarations()

    def get_comparison_class(self):
        return compare.StreamFieldComparison

    def id_for_label(self):
        # a StreamField may consist of many input fields, so it's not meaningful to
        # attach the label to any specific one
        return ""

    def on_model_bound(self):
        super().on_model_bound()
        self.block_def = self.db_field.stream_block
