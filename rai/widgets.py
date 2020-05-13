from pprint import pprint

from django.forms import Widget, Select, CheckboxSelectMultiple, RadioSelect

from rai.utils import update_if_not_defined, add_css_class, remove_css_class


import random



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
        context = super().get_context(name, value, attrs)
        attrs = context['widget'].pop('attrs', {})
        css_classes = attrs.pop('class', '')
        css_classes = add_css_class(css_classes, ['is-invalid'])
        attrs.update({'class': css_classes})
        context['widget'].update({'errors': errors, 'attrs':attrs})
        template = getattr(self, 'error_template_name', self.template_name)
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
        # if we have not label in the args, try to fetch it from widget.attrs
        if not label:
            label = context['widget']['attrs'].get('label', None)
        # and update the context only if it does not already have a label-key (should not happen)
        context['widget'] = update_if_not_defined(context['widget'], 'label', label)
        
        return context

    def render(self, name, value, label = None, attrs=None, renderer=None):
        """Render the widget as an HTML string."""
        context = self.get_context(name, value, label, attrs)
        return self._render(self.template_name, context, renderer)

class RAISwitchInput(RAICheckboxInput):
    
    template_name = 'rai/forms/widgets/switch.html'
    
    def __init__(self, *args, **kwargs):
        self.checked_label = kwargs.pop('checked_label', 'ja')
        self.unchecked_label = kwargs.pop('unchecked_label', 'nein')
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, label, attrs):
        context = super().get_context(name, value, label, attrs)
        context['checked_label'] = self.checked_label
        context['unchecked_label'] = self.unchecked_label
        return context
        
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

    def __init__(self, attrs = None, choices = ()):
        if attrs is None:
            new_attrs = {
                'class':  add_css_class('', self.required_css_classes)
            }
        else:
            new_attrs = attrs.copy()
            css_class_string = add_css_class(attrs.pop('class', ''), self.required_css_classes)
            new_attrs.update({'class': css_class_string})
            
        for attribute, value in self.required_attributes.items():
            new_attrs.update({ attribute: value })
        for attribute, default in self.default_attributes.items():
            new_attrs = update_if_not_defined(new_attrs, attribute, default)
            
        super().__init__(attrs = new_attrs, choices = choices)
        
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['type'] = self.input_type
        return context

    # copied from django


class RAISelectMultiple(RAISelect):

    allow_multiple_selected = True
    required_attributes = { 'multiple' : True }

    
    
class RAIRadioSelect(RadioSelect):
    input_type = 'radio'
    template_name = 'rai/forms/widgets/multiple-input.html'
    option_template_name = 'rai/forms/widgets/checkbox.html'
    #option_template_name = 'django/forms/widgets/radio_option.html'
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        # add class to attrs
        if attrs:
            new_attrs = attrs.copy()
        else:
            new_attrs = {}
        css_classes = add_css_class(new_attrs.get('class', ''), ['custom-control-input'])
#        random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(10)    
        new_attrs.update({'class' : css_classes})
        return super().create_option(
            name, value, label, selected,
            index, subindex=subindex, attrs=new_attrs
        )

class RAIRadioSelectTable(RAIRadioSelect):
    template_name = 'rai/forms/widgets/multiple-input-table.html'
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        # remove label from attrs
        
        return super().create_option(
            name, value, "", selected,
            index, subindex=subindex, attrs=attrs
        )
    
class RAISelectMultipleSelectionLists(CheckboxSelectMultiple):
    class Meta:
        js = ('/js/admin/third-party/mark.js-8.11.1/jquery.mark.min.js',)
    template_name = 'rai/forms/widgets/select-multiple-selection-lists.html'
    option_template_name = 'rai/forms/widgets/checkbox-option-select-multiple-lists.html'
    option_content_template = 'rai/forms/widgets/checkoption-option-select-multiple-item.html'

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        option['content_template'] = self.option_content_template
        return option

class RAISelectMultipleCheckboxes(CheckboxSelectMultiple):
    option_template_name = 'rai/forms/widgets/checkbox-option-multiple.html'
    template_name = 'rai/forms/widgets/select-multiple-checkboxes.html'
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        attrs = option.pop('attrs', {})
        classname = attrs.pop('class', '')
        classname = add_css_class(classname, ['custom-control-input'])
        attrs.update({'class' : classname})
        option.update({'attrs' : attrs})
        return option

class RAITypeAndSelect(RAISelect):
    # the differences to a SELECT will be introduced by javascript
    required_css_classes = ['type-and-select'] + RAISelect.required_css_classes


class RAISelectRAIItems(RAISelect):
    """
    A select with pre-defined options
    """
    required_css_classes = ['select-rai-items'] + RAISelect.required_css_classes
    def optgroups(self, name, value, attrs = None):
        from rai.internals import registered_rai_items_as_choices
        self.choices = registered_rai_items_as_choices()
        return super().optgroups(name, value, attrs = None)

class RAIFileInput(RequiredClassesField):
    required_css_classes = ['custom-file-input']
    input_type = "file"
    template_name = 'rai/forms/widgets/file-input.html'


class RAIExtendedFileInput(RAIInputField):
    input_type = "file"
    template_name = 'rai/forms/widgets/x-file-input.html'

class RUBLoginIdInput(RAIInputField):
    input_type = "text"
    template_name = 'rai/forms/widgets/rub-login-input.html'
    
    # def __init__(self, attrs = None):
    #     super().__init__(attrs = attrs)
    #     pprint(self.attrs)

class RAIDateInput(RequiredClassesField):
    required_css_classes = ['datetimepicker-input', 'form-control']
    template_name = 'rai/forms/widgets/date.html'
    input_type = 'text'

class RAITimeInput(RAIDateInput):
    template_name = 'rai/forms/widgets/time.html'

class RAIDateTimeInput(RAIDateInput):
    template_name = 'rai/forms/widgets/datetime.html'

    
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
