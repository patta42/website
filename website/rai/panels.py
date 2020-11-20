import caldav, datetime, pytz

from collections import OrderedDict
from dateutil import rrule
from dateutils import relativedelta
from django.conf import settings


from rai.panels.base import FrontPanel


class BeamtimePanel(FrontPanel):
    template = 'website/rai/panels/beamtime-panel.html'
    title = 'Strahlzeitplan'
    desc = 'Zeigt den Strahlzeitplan'
    identifier = 'website.beamtime.cal'
    max_cols = 3
    max_rows = 1
    min_rows = 1
    min_cols = 1

    def get_context(self, date = None):
        context = super().get_context()
        context['title'] = self.title
        dt = date or datetime.date.today()
#
        context['date'] = dt
        return context

    
