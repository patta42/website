import datetime
from dateutil.relativedelta import relativedelta

from django.db.models import Q

from rai.default_views.paginated import PaginatedView
from website.models import SentMail

class SentMailView(PaginatedView):
    model = SentMail
    template_name = 'website/rai/sent-mail/list.html'

    def get_pagination(self, **kwargs):
        kwargs = {}
        search = self.request.GET.get('search', None)
        if search:
            kwargs['search'] = search
        if self.action == 'simple':
            kwargs['qs'] = self.request.GET.get('qs', None)
        
            
        return super().get_pagination(**kwargs)

    def advanced_search(self, qs):
        to = self.request.GET.get('to', None)
        if to:
            qs = qs.filter(to__icontains = to)
        subject = self.request.GET.get('subject', None)
        if subject:
            qs = qs.filter(subject__icontains = subject)
        start = self.request.GET.get('startDate', None)
        if start:
            start_date = datetime.datetime.strptime(start, '%Y-%m-%d')
            qs = qs.filter(sent_at__gte = start_date)
        end = self.request.GET.get('endDate', None)
        if end:
            end_date = datetime.datetime.strptime(end, '%Y-%m-%d')
            qs = qs.filter(sent_at__lte = end_date)
            
        return qs
    
    def get_all_objects(self):
        qs = super().get_all_objects()

        if self.action == 'simple':
            term = self.request.GET.get('qs', None)
            if term:
                qs = qs.filter(Q(to__icontains = term) | Q(subject__icontains = term))
        if self.action == 'advanced':
            qs = self.advanced_search(qs)
        return qs.order_by('-sent_at')
            
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = {}
        for k in ['search', 'qs', 'to', 'subject', 'startDate', 'endDate']:
            d[k] = self.request.GET.get(k, None)
        
        context.update(d)
        return context

    def get(self, request):
        self.action = request.GET.get('search', None)
        return super().get(request)
