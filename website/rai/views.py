import caldav, datetime, pytz

from collections import OrderedDict

#from dateutil.relativedelta import relativedelta
from dateutil import rrule
from dateutils import relativedelta

from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string

from rai.default_views.paginated import PaginatedView
from website.cdav import client
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

def _is_on_date(d1,d2):
    return d1.year == d2.year and d1.month == d2.month and d1.day == d2.day

    
def _percent_for_display(t1, t2 = None):
    starttime = 8
    endtime = 22

    if t1 and t1.hour < starttime  : 
        t1 = datetime.datetime(t1.year, t1.month, t1.day, starttime, tzinfo = t1.tzinfo)
    if t2 and (t2.hour > endtime or (t2.hour == endtime and t2.minute > 0)):
        t2 = datetime.datetime(t2.year, t2.month, t2.day, endtime, tzinfo = t2.tzinfo)
        
    displ_diff = (endtime - starttime) * 60
    start = (t1.hour - starttime) * 60 + t1.minute
    if t2:
        end = (t2.hour - starttime) * 60 + t2.minute
        time = end - start
        m = endtime * 60 - (t2.hour - starttime) * 60
    else:
        time = start
        m = 100
    
    return str(float(100*time/displ_diff)).replace(',','.')


def _get_beamtimes(date = None):
    _CATEGORIES = [
        '4 - 4 MV (NT 06)',
        '3 - 500 kV (NT 06)',
        '2 - 100 kV (NT 07)',
        '1 - 100 kV (NI 05)'
    ]
    _APPLICATION_CATEGORIES = [
        'Analyse-Research',
        'Implantation-Research',
        'Modifikation-Research',
        '1 - Implantation-Industry',
        '2 - Service-Engineering'
    ]
    _CATNAMES = {
        '4 - 4 MV (NT 06)' : 'Tandem',
        '3 - 500 kV (NT 06)' : '500 kV',
        '2 - 100 kV (NT 07)' : '100 kV',
        '1 - 100 kV (NI 05)' : 'Med-Implanter'
    }
    _CAT_COLORS = {
        'Tandem' : '#FF3300',
        '500 kV' : '#666600',
        '100 kV' : '#ff6600',
        'Med-Implanter' : '#FF9900',
        'Analyse-Research' : '#CC3333',
        'Implantation-Research' : '#00FFFF',
        'Modifikation-Research' : '#0066ff',
        '1 - Implantation-Industry' : '#00ff00',
        '2 - Service-Engineering' : '#990000'
    }


    cal = caldav.Calendar(client = client, url = settings.EGROUPWARE_CAL_URLS['beamtime'])
    tz = pytz.timezone('Europe/Berlin')
    td = date or datetime.datetime.today(tzinfo = tz)
    tm = td + relativedelta(days=1)

    heute = datetime.datetime(2020,11,16,0,0, tzinfo = tz)
    morgen = datetime.datetime(2020,11,17,0,0, tzinfo = tz)
    evts = cal.date_search(td, tm)
    beamtimes = OrderedDict()
    for c in _CATEGORIES:
        beamtimes[_CATNAMES[c]] = []
    for evt in evts:
        evt = evt.vobject_instance
        n=0
        for event in evt.vevent_list:
            n=n+1
            try:
                categories = event.categories.value
            except AttributeError:
                continue
            cat = None
            ccat = None
            for c in categories:
                if c in _CATEGORIES:
                    cat = _CATNAMES[c]
                if c in _APPLICATION_CATEGORIES:
                    ccat = c
                if cat and ccat:
                    break
            if not ccat:
                ccat = cat
            rr = []
            if cat:
                try:
                    rr = rrule.rrulestr(event.rrule.value, dtstart = event.dtstart.value)
                except AttributeError:
                    # check if event is today. might be an exception for a rrule...
                    if _is_on_date(event.dtstart.value, td):
                        try:
                            desc = event.description.value
                        except AttributeError:
                            desc = None

                        beamtimes[cat].append({
                            'summary' : event.summary.value,
                            'start' : event.dtstart.value,
                            'end' : event.dtend.value,
                            'desc' : desc, 
                            'startPercent' : _percent_for_display(event.dtstart.value),
                            'durationPercent' : _percent_for_display(event.dtstart.value, event.dtend.value),
                            'bgcolor' : _CAT_COLORS[ccat] 
                        })
                if rr:
                    try:
                        excl = event.exdate.value
                    except AttributeError:
                        excl = None

                    rs = rrule.rruleset()
                    rs.rrule(rr)

                    if excl and rs:
                        if not isinstance(excl, list):
                            excl = [excl]
                        for e in excl:
                            rs.exdate(e)
                    if rs:
                        for dt in rs.between(td,tm):
                            try:
                                desc = event.description.value
                            except AttributeError:
                                desc = None

                            beamtimes[cat].append({
                                'summary' : event.summary.value,
                                'start' : event.dtstart.value,
                                'end' : event.dtend.value,
                                'desc' : desc,
                                'startPercent' : _percent_for_display(event.dtstart.value),
                                'durationPercent' : _percent_for_display(event.dtstart.value, event.dtend.value),
                                'bgcolor' : _CAT_COLORS[ccat] 
                            })    
    return beamtimes
                        

    
def beamtimes(request):
    if request.is_ajax() and request.method == 'GET':
        
        date = datetime.datetime(
            int(request.GET.get('year')),
            int(request.GET.get('month')),
            int(request.GET.get('day')),
            tzinfo = pytz.timezone('Europe/Berlin')
        )
        return JsonResponse({
            'html' : render_to_string(
                'website/rai/panels/beamtime.html',
                {
                    'beamtimes' : _get_beamtimes(date = date),
                    
                }        
            ),
            'status' : 200
        })
    else:
        return HttpResponse(status = 405)
