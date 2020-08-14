from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from rai.edit_handlers import (
    RAIDecorationPanel, RAIMultiFieldPanel, RAIFieldPanel
)

from .models import RAIComment

import inspect

class CommentDisplayPanel(RAIMultiFieldPanel):
    object_template = 'rai/comments/edit_handlers/comment-display-panel_as-object.html'
    field_template = 'rai/comments/edit_handlers/comment-display-panel_as-field.html'

    def __init__(self, children, *args, **kwargs):
        super().__init__(children = children, *args, **kwargs)

    def on_form_bound(self):
        self.children = [
            child.bind_to(form = self.form) for child in self.children
        ]
        
    def render_as_object(self):
        return self._render(self.object_template)
    
    def render_as_field(self):
        return self._render(self.field_template)

    def render(self):
        # default is to render as object
        return self.render_as_object()
    
    def _render(self, template):
        content = None
        for child in self.children:
            if issubclass(child.__class__, CommentContentPanel):
                content = child

        # It might happen that the panel was not bound to a request.
        # Maybe this should not happen?

        if not hasattr(self, 'request') or not self.request:
            user = None
        else:
            user = self.request.user
                
        context = {
            'self': self,
            'content' : content,
            'has_instance' : False,
            'request_user' : user
        }
        if self.instance:
            if user:
                may_edit = self.instance.owner == self.request.user or self.request.user.is_superuser
            else:
                may_edit = False
            context.update({
                'owner' : self.instance.owner,
                'timestamp' : self.instance.created_at,
                'id' : self.instance.pk,
                'has_instance' : True,
                'may_edit' : may_edit
            })

        return mark_safe(render_to_string(template, context))

class CommentContentPanel(RAIFieldPanel):
    def on_request_bound(self):
        if self.instance:
            self.form.fields['comment'].widget.is_editable = False
        else:
            pass

    def get_comparison(self):
        return []

class CommentPanel(RAIDecorationPanel):
    template = 'rai/comments/edit_handlers/comment-panel.html'
    def __init__(self, *args, **kwargs):
        opts = RAIComment._meta
        rai_model = '{}.{}'.format(opts.app_label, opts.model_name)
        self.panels = [
            CommentContentPanel('comment'),
        ]
        super().__init__(rai_model, panels = self.panels, *args, **kwargs)

    def get_child_edit_handler(self):
        return CommentDisplayPanel(self.panels)
        
    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        del(kwargs['rai_model_id'])
        del(kwargs['panels'])
        return kwargs
    
    def required_fields(self):
        return []

    def required_internal_fields(self):
        return ['comment']

    def on_request_bound(self):
        super().on_request_bound()
        child_edit_handler = self.get_child_edit_handler()
        child_edit_handler = child_edit_handler.bind_to(
            model = self.rai_model,
            form = self.form_class(),
            request = self.request
        )
        self.children.append(
            child_edit_handler
        )
