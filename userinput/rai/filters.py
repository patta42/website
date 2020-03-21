import datetime

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _l
from django.utils.text import format_lazy

from instruments.models import InstrumentPage

from rai.filters import RAIFilter, RAIFilterOption



class RUBIONUserStatusFilter(RAIFilter):
    label = _l('User status')
    filter_id = 'user_status'
    is_mutual_exclusive = True
    help_text = _l('Filters users by their active/inactive status.')
    options = [
        RAIFilterOption(_l('all'), 'all', help_text=_l('Show all users (independent from their status).')),
        RAIFilterOption(_l('active'), 'active', help_text=_l('Show only active users.'), default = True),
        RAIFilterOption(_l('inactive'), 'inactive', help_text=_l('Show inactive users only.'))
    ]

    def get_queryset(self):
        td = datetime.datetime.today()
        # value is a list
        self.value = self.value[0]
        if self.value == 'all':
            return self.qs
        if self.value == 'active':
            return self.qs.filter(Q(expire_at__isnull = True) | Q(expire_at__gte = td))
        if self.value == 'inactive':
            return self.qs.filter(expire_at__lt = td)

        return self.qs


class RUBIONUserInstrumentFilterMeta(type):
    def __new__(cls, name, bases, dct):
        Kls = super().__new__(cls, name, bases, dct)
        
        options =  [ RAIFilterOption(
            instrument.title_trans,
            instrument.pk,
            help_text = _l('Include user using {instrument}'.format(instrument = instrument.title_trans))
        ) for instrument in InstrumentPage.objects.all()]
            
        Kls.options = options
        return Kls

class RUBIONUserInstrumentFilter(RAIFilter, metaclass = RUBIONUserInstrumentFilterMeta):
    label = _l('Used instruments')
    filter_id = 'user_instrument'
    is_mutual_exclusive = False
    help_text = _l('Filter users by their usage of instruments')
