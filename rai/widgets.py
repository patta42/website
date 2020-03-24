from django.forms import Widget

def add_css_class(css_string, css_class):
    css_classes = css_string.split(' ')
    if not css_class in css_classes:
        css_classes.append(css_class)

    return ' '.join(css_classes)
def remove_css_class(css_string, css_class):
    css_classes = css_string.split(' ')
    try:
        css_classes.remove(css_class)
    except ValueError:
        pass
    return ' '.join(css_classes)

class RAIWidget (Widget):
    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {'class' : 'form-control'}
        else:
            attrs = attrs.copy()
            css_class_str = attrs.pop('class', '')
            css_classes = css_class_str.split(' ')
            if 'form-control' not in css_classes and 'form-control-plaintext' not in css_classes:
                css_classes.append('form-control')
            attrs.update({'class' : " ".join(css_classes)})

        super().__init__(attrs)


        
        
    def render_disabled(self, *args, **kwargs):
        attrs = kwargs.pop('attrs', {})
        
        attrs.update({ 'disabled':'disabled' })
        kwargs['attrs'] = attrs
        if hasattr(self.attrs, 'class'):
            css_string = self.attrs['class']
        else:
            css_string = ''

        css_string = remove_css_class(css_string, 'form-control')
        css_string = add_css_class(css_string, 'form-control-plaintext')
        self.attrs['class'] = css_string
        
        return self.render(*args, **kwargs)
    
class RAIInputField(RAIWidget):
    template_name = 'rai/forms/widgets/input.html'

    input_type = None  # Subclasses must define this.

    def __init__(self, attrs = None):
        if attrs is not None:
            attrs = attrs.copy()
            self.input_type = attrs.pop('type', self.input_type)
            
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['type'] = self.input_type
        print (context)

        return context


class RAITextInput(RAIInputField):
    input_type = 'text'
    template_name = 'rai/forms/widgets/text.html'

class RAINumberInput(RAIInputField):
    input_type = 'number'
    template_name = 'rai/forms/widgets/number.html'

class RAIEMailInput(RAIInputField):
    input_type = 'email'
    template_name = 'rai/forms/widgets/email.html'

class RAIUrlInput(RAIInputField):
    input_type = 'url'
    template_name = 'rai/forms/widgets/url.html'

class RAIPasswordInput(RAIInputField):
    input_type = 'password'
    template_name = 'rai/forms/widgets/password.html'

    def __init__(self, attrs=None, render_value=False):
        super().__init__(attrs)
        self.render_value = render_value

    def get_context(self, name, value, attrs):
        if not self.render_value:
            value = None
        return super().get_context(name, value, attrs)


class RAIHiddenInput(RAIInputField):
    input_type = 'hidden'
    template_name = 'rai/forms/widgets/hidden.html'


class RAIMultiHiddenInput(RAIHiddenInput):
    template_name = 'rai/forms/widgets/multiple_hidden.html'

    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        final_attrs = context['widget']['attrs']
        id_ = context['widget']['attrs'].get('id')

        subwidgets = []
        for index, value_ in enumerate(context['widget']['value']):
            widget_attrs = final_attrs.copy()
            if id_:
                # An ID attribute was given. Add a numeric index as a suffix
                # so that the inputs don't all have the same ID attribute.
                widget_attrs['id'] = '%s_%s' % (id_, index)
            widget = RAIHiddenInput()
            widget.is_required = self.is_required
            subwidgets.append(widget.get_context(name, value_, widget_attrs)['widget'])

        context['widget']['subwidgets'] = subwidgets
        return context

    def value_from_datadict(self, data, files, name):
        try:
            getter = data.getlist
        except AttributeError:
            getter = data.get
        return getter(name)

    def format_value(self, value):
        return [] if value is None else value

class RAITextarea(RAIWidget):
    template_name = 'rai/forms/widgets/textarea.html'

    def __init__(self, attrs=None):
        # Use slightly better defaults than HTML's 20x2 box
        default_attrs = {'cols': '40', 'rows': '10'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
