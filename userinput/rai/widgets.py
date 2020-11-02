from django.forms import MultiWidget
from django.urls import reverse

from rai.widgets import RAISelectMultipleCheckboxes, RAISelect, RAITextInput

class RUBIONUserSafetyInstructionWidget(RAISelectMultipleCheckboxes):
    def value_from_datadict(self, data, files, name):
        print(data.getlist(name))
        return data.getlist(name)
        #return super().value_from_datadict(data, files, name)

class UserinputPublicationWidget(RAISelect):
    required_css_classes = ['publication-select', 'custom-select']
    
    def __init__(self, attrs = None):
        if not attrs:
            attrs = {}
            
        attrs.update({'data-add-publication-url' : reverse('userinput_add_publication')})
        super().__init__(attrs = attrs)

class UserinputThesisWidget(RAISelect):
    required_css_classes = ['thesis-select', 'custom-select']
    
    def __init__(self, attrs = None):
        if not attrs:
            attrs = {}
            
        attrs.update({'data-add-publication-url' : reverse('userinput_add_thesis')})
        super().__init__(attrs = attrs)



class DOIInput(RAITextInput):
    def __init__(self, attrs = None):
        if not attrs:
            attrs = {'class':''}

        classes = attrs.get('class', '')
        classes = '{} doi-input'.format(classes)
        attrs.update({'class' : classes})
        super().__init__(attrs = attrs)
    
