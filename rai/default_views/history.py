from pprint import pprint



from .generic import RAIAdminView, SingleObjectMixin, PageMenuMixin

import functools
import json


from rai.actions import EditAction

from wagtail.core.models import PageRevision 
from wagtail.admin.compare import FieldComparison, TextFieldComparison

_DEFAULT_COMPARATORS = {
    'CharField' : TextFieldComparison,
    'BooleanField' : FieldComparison,
    
}

class HistoryView(SingleObjectMixin, PageMenuMixin, RAIAdminView):
    template_name = 'rai/views/default/history.html'
    edit_handler = None
    additional_comparisons = ['path', 'locked']
    update_from_json = ['path', 'locked']
    alternative_labels = {}
    comparators = {}
    
    def get_comparison(self, revision_a, revision_b):
        page_a = revision_a.as_page_object().specific
        page_b = revision_b.as_page_object().specific

        a_dict = json.loads(revision_a.content_json)
        b_dict = json.loads(revision_b.content_json)

        comparison = self.edit_handler.get_comparison()
        # undo the changes introduced by as_page_object on the fields `path` and `locked`
        for f in self.additional_comparisons:
            if f in self.update_from_json:
                setattr(page_a, f, a_dict.get(f))
                setattr(page_b, f, b_dict.get(f))
            field = page_a._meta.get_field(f)
            comparator_class = self.comparators.get(
                f,
                _DEFAULT_COMPARATORS.get(
                    field.__class__.__name__,
                    FieldComparison
                )
            )
            comparison.append(
                functools.partial(comparator_class, field)
            )

        comparisons = [comp(page_a, page_b) for comp in comparison]
        changes = [comp for comp in comparisons if comp.has_changed()]

        
        return changes


    def get_revisions(self):
        revisions = self.obj.revisions.all().order_by('created_at')
        ret = []
        prev_rev = None
        for rev in revisions:
            if prev_rev:
                ret.append({
                    'revision' : rev,
                    'changes': self.get_comparison(prev_rev, rev)
                })
            else:
                ret.append({
                    'revision' : rev,
                    'remark' : 'Erster Datensatz'
                })
            prev_rev = rev
        ret.reverse()
        return ret
        
    def get_actions(self):
        return self.get_group_actions() + self.get_item_actions()


    def dispatch(self, request, *args, **kwargs):
        self.obj = self.get_object()
        if not self.edit_handler:
            for action in self.raiadmin.item_actions:
                if issubclass(action, EditAction):
                    self.edit_handler = action.edit_handler.bind_to(model = self.raiadmin.model)
                    break
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.obj
        context['icon'] = self.active_action.icon
        context['action_label'] = 'Liste der Änderungen'
        context['title'] = self.obj.title_trans
        context['revisions'] = self.get_revisions()
        context['page_menu'] = self.get_page_menu()
        context['alternative_lables'] = self.alternative_labels
        return context

