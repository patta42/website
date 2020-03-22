import datetime

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _l
from django.utils.text import format_lazy

from instruments.models import InstrumentPage

from rai.filters import RAIFilter, RAIFilterOption, RAIStatusFilter



class RUBIONUserStatusFilter(RAIStatusFilter):
    label = _l('User status')
    filter_id = 'user_status'
    help_text = _l('Filters users by their active/inactive status.')
    options = [
        RAIFilterOption(_l('all'), 'all', help_text=_l('Show all users (independent from their status).')),
        RAIFilterOption(_l('active'), 'active', help_text=_l('Show only active users.'), default = True),
        RAIFilterOption(_l('inactive'), 'inactive', help_text=_l('Show inactive users only.'))
    ]


class RUBIONUserInstrumentFilterMeta(type):
    """ 
    Meta class for RUBIONUserInstrumentFilter

    Defines the options from the DB
    """
    
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

    def get_queryset(self):
        """
        Filters the users by their instrument usage
        """

        # I don't know how to do this on a pure DB level
        #
        # Hopefully this does not take too long
        #
        # Maybe one way would be to
        #
        # get the selected instrument
        # get the corresponding methods
        # get the workgroup
        # get the users
        # compare the two qs
        #
        # Best would be to create a relation 
        # workgroup <-> user on the DB level
        exclude = []

        pks = [int(v) for v in self.value]
        
        for user in self.qs.all():
            do_exclude = True
            for instrument in user.get_instruments():
                
                if instrument.pk in pks:
                    print('Instrument found')
                    do_exclude = False
                    break

            if do_exclude:
                exclude.append(user.pk)
            
        return self.qs.exclude(pk__in = exclude)

class ProjectStatusFilter(RAIStatusFilter):
    label = _l('Project status')
    filter_id = 'project_status'
    help_text = _l('Filters projects by their active/inactive status.')
    options = [
        RAIFilterOption(_l('all'), 'all', help_text=_l('Show all projects (independent from their status).')),
        RAIFilterOption(_l('active'), 'active', help_text=_l('Show only active projects.'), default = True),
        RAIFilterOption(_l('inactive'), 'inactive', help_text=_l('Show only inactive projects.'))
    ]

class WorkgroupStatusFilter(RAIStatusFilter):
    label = _l('Workgroupt status')
    filter_id = 'workgroup_status'
    help_text = _l('Filters work groups by their active/inactive status.')
    options = [
        RAIFilterOption(_l('all'), 'all', help_text=_l('Show all work groups (independent from their status).')),
        RAIFilterOption(_l('active'), 'active', help_text=_l('Show only active work groups.'), default = True),
        RAIFilterOption(_l('inactive'), 'inactive', help_text=_l('Show only inactive work groups.'))
    ]