from .signals import pre_page_move, post_page_move

import datetime
import logging

from django import forms
from django.db import transaction
from django.db.models import Q

from wagtail.core.models import Page



class StyledModelForm( forms.ModelForm ):
    required_css_class = 'required'
    error_css_class = 'error'

    fieldset_trans = {}

    def get_legend_trans( self, legend ):
        try:
            return self.fieldset_trans[legend]
        except KeyError:
            return legend

    class Meta:
        abstract = True

class StyledForm( forms.Form ):
    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        abstract = True

class ActiveInactiveMixin:
    @property
    def is_active(self):
        return not self.locked

    def activate(self, user = None, save = True):
        self.locked = False
        self.expire_at = None
        if save:
            self.save_revision_and_publish(user = user)

    def inactivate(self, user = None, save = True):
        self.locked = True
        self.expire_at = datetime.datetime.now()
        if save:
            self.save_revision_and_publish(user = user)
            
    @classmethod
    def active_filter(self):
        return Q(expire_at__isnull = True) | Q(expire_at__gte = datetime.datetime.now())
    

logger = logging.getLogger('wagtail.core')

class MoveMixin:
    '''Taken from WT2.10 to emit pre_page_move and post_page_move signals'''
    
    def move(self, target, pos=None, user=None):
        """
        Extension to the treebeard 'move' method to ensure that url_path is updated,
        and to emit a 'pre_page_move' and 'post_page_move' signals.
        """
        # Determine old and new parents
        parent_before = self.get_parent()
        if pos in ('first-child', 'last-child', 'sorted-child'):
            parent_after = target
        else:
            parent_after = target.get_parent()

        # Determine old and new url_paths
        # Fetching new object to avoid affecting `self`
        old_self = Page.objects.get(id=self.id)
        old_url_path = old_self.url_path
        new_url_path = old_self.set_url_path(parent=parent_after)

        # Emit pre_page_move signal
        pre_page_move.send(
            sender=self.specific_class or self.__class__,
            instance=self,
            parent_page_before=parent_before,
            parent_page_after=parent_after,
            url_path_before=old_url_path,
            url_path_after=new_url_path,
        )

        # Only commit when all descendants are properly updated
        with transaction.atomic():
            # Allow treebeard to update `path` values
            super().move(target, pos=pos)

            # Treebeard's move method doesn't actually update the in-memory instance,
            # so we need to work with a freshly loaded one now
            new_self = Page.objects.get(id=self.id)
            new_self.url_path = new_url_path
            new_self.save()

            # Update descendant paths if url_path has changed
            if old_url_path != new_url_path:
                new_self._update_descendant_url_paths(old_url_path, new_url_path)

        # Emit post_page_move signal
        post_page_move.send(
            sender=self.specific_class or self.__class__,
            instance=new_self,
            parent_page_before=parent_before,
            parent_page_after=parent_after,
            url_path_before=old_url_path,
            url_path_after=new_url_path,
        )

        logger.info("Page moved: \"%s\" id=%d path=%s", self.title, self.id, new_url_path)
