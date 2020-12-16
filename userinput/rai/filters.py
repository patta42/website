import datetime

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _l
from django.utils.text import format_lazy

from instruments.models import InstrumentPage

from rai.filters import RAIFilter, RAIFilterOption, RAIStatusFilter

from userdata.models import SafetyInstructionsSnippet

class RUBIONUserStatusFilter(RAIStatusFilter):
    label = _l('User status')
    filter_id = 'user_status'
    help_text = _l('Filters users by their active/inactive status.')
    options = [
        RAIFilterOption(_l('all'), 'all', help_text=_l('Show all users (independent from their status).')),
        RAIFilterOption(_l('active'), 'active', help_text=_l('Show only active users.'), default = True),
        RAIFilterOption(_l('inactive'), 'inactive', help_text=_l('Show inactive users only.'))
    ]

class SafetyInstructionFilterMeta(type):
    """
    Meta class for filters using safety instructions
    """
    def __new__(cls, name, bases, dct):
        Kls = super().__new__(cls, name, bases, dct)
        
        options = [ RAIFilterOption(
            si.title_de_short,
            si.pk,
            help_text = ''#Zeige Nutzer, die {si} benötigen'.format(
            #    si = si.title_de
            #)
        ) for si in SafetyInstructionsSnippet.objects.order_by('title_de_short')]
            
        Kls.options = options
        return Kls
    

    

class RUBIONUserSafetyInstructionfilter(RAIFilter, metaclass=SafetyInstructionFilterMeta):
    """
    Filters the users by the SafetyInstructions they need.
    """
    label = 'Benötigte Sicherheitsunterweisungen'
    filter_id = 'user_safety_instructions'
    is_mutual_exclusive = False
    help_text = 'Zeigt nur Nutzer, die die entsprechende Unterweisung benötigen.'

    def __init__(self, qs, value):
        super().__init__(qs, value = value)

        # convert string values to integers 
        if self.value is not None:
            values = [int(val) for val in self.value]
            self.value = values

    def get_queryset(self):
        return self.qs.filter(safety_instructions__instruction__pk__in = self.values)
                    
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

    def __init__(self, qs, value = None):
        super().__init__(qs, value)
        if self.value is not None:
            values = [int(val) for val in self.value]
            self.value = values
    
    
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

        
        
        for user in self.qs.all():
            do_exclude = True
            for instrument in user.get_instruments():
                
                if instrument.pk in self.value:
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
        RAIFilterOption('alle', 'all', help_text='Alle Projekte.'),
        RAIFilterOption('aktiv', 'active', help_text='Aktive Projekte', default = True),
        RAIFilterOption('abgelaufen', 'expired', 'Abgelaufene aber nicht abgeschlossene Projekte.'),
        RAIFilterOption('aktive und abgelaufen', 'active+expired', help_text='Aktive und abgelaufene Projekte.', default = True),
        RAIFilterOption('abgeschlossen', 'closed', help_text='Abgeschlossene Projekte')
    ]
    
    def get_queryset(self):
        # value is a list
        self.value = self.value[0]
        if self.value == 'all':
            return self.qs
        if self.value == 'active':
            return self.qs.active().filter(locked = False)
        if self.value == 'expired':
            return self.qs.inactive().filter(locked = False)
        if self.value == 'active+expired':
            return self.qs.filter(locked=False)
        if self.value == 'closed':
            return self.qs.filter(locked=True)


class WorkgroupStatusFilter(RAIStatusFilter):
    label = _l('Workgroup status')
    filter_id = 'workgroup_status'
    help_text = _l('Filters work groups by their active/inactive status.')
    options = [
        RAIFilterOption(_l('all'), 'all', help_text=_l('Show all work groups (independent from their status).')),
        RAIFilterOption(_l('active'), 'active', help_text=_l('Show only active work groups.'), default = True),
        RAIFilterOption(_l('inactive'), 'inactive', help_text=_l('Show only inactive work groups.'))
    ]

class ScientificOutputDuplicateFilter(RAIFilter):
    label = 'Duplikate auflisten'
    filter_id = 'duplicates'
    help_text = 'Sollen Duplikate angezeigt werden?'
    is_mutual_exclusive = True
    options = [
        RAIFilterOption('alle', 'all', help_text='Alle anzeigen'),
        RAIFilterOption('keine Duplikate', 'origs', help_text='Keine Duplikate anzeigen', default = True),
        RAIFilterOption('nur Duplikate', 'duplicates', help_text='Nur Duplikate anzeigen'),
    ]

    def get_queryset(self):
        self.value = self.value[0]
        if self.value == 'all':
            return self.qs
        if self.value == 'origs':
            return self.qs.filter(is_duplicate = False)
        if self.value == 'duplicates':
            return self.qs.filter(is_duplicate = True)
        return self.qs
    
