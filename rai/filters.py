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
