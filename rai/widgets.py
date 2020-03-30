from pprint import pprint

from django.forms import Widget, Select

from rai.utils import update_if_not_defined


def add_css_class(css_string, css_class):
    css_classes = css_string.split(' ')
    try:
        for cls in css_class:
            if not cls in css_classes:
                css_classes.append(cls)
    except TypeError:
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


class RenderDisabledMixin:
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


class RAIWidget (Widget, RenderDisabledMixin):
    additional_classes = ['form-control']
    requires_label = False
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

    def render_with_errors(self, name, value, attrs = None, renderer = None, errors = []):
        print('render with errors!')
        context = super().get_context(name, value, attrs)
        attrs = context['widget'].pop('attrs', {})
        css_classes = attrs.pop('class', '')
        css_classes = add_css_class(css_classes, ['is-invalid'])
        attrs.update({'class': css_classes})
        context['widget'].update({'errors': errors, 'attrs':attrs})
        template = getattr(self, 'error_template_name', self.template_name)
        pprint(context)
        return self._render(template, context, renderer)


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

class RequiredClassesField(RAIInputField):
    def __init__(self, attrs = None):
        if attrs is None:
            new_attrs = {
                'class':  add_css_class('', self.required_css_classes)
            }
        else:
            new_attrs = attrs.copy()
            css_class_string = add_css_class(attrs.pop('class', ''), self.required_css_classes)
            new_attrs.update({'class' : css_class_string})

        super().__init__(attrs = new_attrs)

def boolean_check(v):
    return not (v is False or v is None or v == '')
        
class RAICheckboxInput(RequiredClassesField):
    required_css_classes = ['custom-control-input']
    input_type = 'checkbox'
    template_name = 'rai/forms/widgets/checkbox.html'
    requires_label = True

    def __init__(self, attrs = None, check_test = None):
        super().__init__(attrs)
        # check_test is a callable that takes a value and returns True
        # if the checkbox should be checked for that value.
        self.check_test = boolean_check if check_test is None else check_test

    def format_value(self, value):
        """Only return the 'value' attribute if value isn't empty."""
        if value is True or value is False or value is None or value == '':
            return
        return str(value)

    def value_from_datadict(self, data, files, name):
        if name not in data:
            # A missing value means False because HTML form submission does not
            # send results for unselected checkboxes.
            return False
        value = data.get(name)
        # Translate true and false strings to boolean values.
        values = {'true': True, 'false': False}
        if isinstance(value, str):
            value = values.get(value.lower(), value)
        return bool(value)

    def value_omitted_from_data(self, data, files, name):
        # HTML checkboxes don't appear in POST data if not checked, so it's
        # never known if the value is actually omitted.
        return False

    
    def get_context(self, name, value, label, attrs):
        if self.check_test(value):
            if attrs is None:
                attrs = {}
            attrs['checked'] = True
        context = super().get_context(name, value, attrs)            
        context['widget'].update({ 'label' : label})
        return context

    def render(self, name, value, label = None, attrs=None, renderer=None):
        """Render the widget as an HTML string."""
        context = self.get_context(name, value, label, attrs)
        return self._render(self.template_name, context, renderer)

class RAIRadioInput(RAICheckboxInput):
    input_type = 'radio'



# input_type is not added by default to the ChoiceWidget context, but ChoiceWidget
# cannot be imported. Fix this on every widget that derives from ChoiceWidget

class RAISelect(Select, RenderDisabledMixin):
    input_type = 'select'
    template_name = 'rai/forms/widgets/select.html'
    option_template_name = 'django/forms/widgets/select_option.html'
    required_css_classes = ['custom-select']
    required_attributes = {}
    default_attributes = {}
    add_id_index = False
    checked_attribute = {'selected': True}
    option_inherits_attrs = False

    def __init__(self, attrs = None):
        if attrs is None:
            new_attrs = {
                'class':  add_css_class('', self.required_css_classes)
            }
        else:
            new_attrs = attrs.copy()
            css_class_string = add_css_class(attrs.pop('class', ''), self.required_css_classes)
            new_attrs.update('class', css_class_string)
            
        for attribute, value in self.required_attributes.items():
            new_attrs.update({ attribute: value })
        for attribute, default in self.default_attributes.items():
            new_attrs = update_if_not_defined(new_attrs, attribute, default)
            
        super().__init__(attrs = new_attrs)
        
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['type'] = self.input_type
        return context

    # copied from django
        
class RAISelectMultiple(RAISelect):
    allow_multiple_selected = True
    required_attributes = { 'multiple' : True }



# This is the default context set by django's Widget
    
    # context = {}
    #     context['widget'] = {
    #         'name': name,
    #         'is_hidden': self.is_hidden,
    #         'required': self.is_required,
    #         'value': self.format_value(value),
    #         'attrs': self.build_attrs(self.attrs, attrs),
    #         'template_name': self.template_name,
    #     }
    #     return context
