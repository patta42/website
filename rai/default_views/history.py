from pprint import pprint

from .generic import RAIAdminView, SingleObjectMixin, PageMenuMixin

from rai.actions import EditAction

from wagtail.core.models import PageRevision 

class HistoryView(SingleObjectMixin, PageMenuMixin, RAIAdminView):
    template_name = 'rai/views/default/history.html'
    edit_handler = None
    
    def get_comparison(self, revision_a, revision_b):
        page_a = revision_a.as_page_object().specific
        page_b = revision_b.as_page_object().specific
        comparison = self.edit_handler.get_comparison()
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
        return context

