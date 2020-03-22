from django.utils.translation import ugettext_lazy as _l

class RAIFilter:
    label = None
    qs = None
    help_text = None
    filter_id = None
    is_mutual_exclusive = True
    options = []
    
    def __init__(self, qs, value = None):
        self.qs = qs
        self.value = value
        if self.value is None:
            pass
        
    def get_queryset(self):
        return self.qs

class RAIFilterOption:
    def __init__ ( self, label, value, help_text = None, default = False ):
        self.label = label
        self.value = value
        self.help_text = help_text
        self.default = default

class RAIStatusFilter(RAIFilter):
    """ 
    A filter for page based models that checks the active inactive state of the model.
    Active means: expire_at is null or in the future
    Inactive means: expire_at is in the past.

    Should implement options with values 'active', 'inactive' and 'all'
    """
    is_mutual_exclusive = True

    def get_queryset(self):
        # value is a list
        self.value = self.value[0]
        if self.value == 'all':
            return self.qs
        if self.value == 'active':
            return self.qs.active()
        if self.value == 'inactive':
            return self.qs.inactive()

        return self.qs
