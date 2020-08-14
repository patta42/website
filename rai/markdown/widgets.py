from rai.widgets import RAITextarea

class RAIMarkdownWidget(RAITextarea):
    template_name = 'rai/markdown/widgets/markdown.html'
    required_css_classes = ['custom-control-input markdown-editor']

    default_features = {
        'heading': {
            'icon' : {
                'font' : 'fas',
                'icon' : 'heading'
            },
            'command' : {
                'pre' : '# ',
                'post' : '',
                'default' : 'Überschrift',
                'newline': 'both'
            }
        },
        'bold' : {
            'icon' : {
                'font' : 'fas',
                'icon' : 'bold'
            },
            'command' : {
                'pre' : '**',
                'post' : '**',
                'default' : 'fetter Text',
                'newline': 'none'
            }
        },
        'italic' : {
            'icon' : {
                'font' : 'fas',
                'icon' : 'italic'
            },
            'command' : {
                'pre' : '_',
                'post' : '_',
                'default' : 'kursiver Text',
                'newline': 'none'
            }
        },
        'ul' : {
            'icon' : {
                'font' : 'fas',
                'icon' : 'list'
            },
            'command' : {
                'pre' : '-    ',
                'post' : '',
                'default' : 'Listeneintrag',
                'newline': 'pre'
            }
        },
        'ol' : {
            'icon' : {
                'font' : 'fas',
                'icon' : 'list-ol'
            },
            'command' : {
                'pre' : '1.    ',
                'post' : '',
                'default' : 'Listeneintrag',
                'newline': 'pre'
            }
        },
        'tasks' : {
            'icon' : {
                'font' : 'fas',
                'icon' : 'tasks'
            },
            'command' : {
                'pre' : '- [ ] ',
                'post' : '',
                'default' : 'Aufgabe',
                'newline': True
            }
        }
    }
    
    def __init__(self, features, attrs = None):
        self.features = { **self.default_features, **(features or {}) }
        self.is_editable = True
        self.edit_mode = True
        super().__init__(attrs)
    
    def render_as_object(self, name, value, attrs):
        pass

    def render_as_field(self, name, value, attrs):
        pass

    def render(self, name, value, attrs):
        return self._render(
            self.template_name,
            self.get_context(name, value, attrs)
        )

        
    def get_context(self, name, value, attrs):
        context = {}
        context['widget'] = {
            'name': name,
            'is_hidden': self.is_hidden,
            'required': self.is_required,
            'is_editable' : self.is_editable,
            'value': self.format_value(value),
            'attrs': self.build_attrs(self.attrs, attrs),
            'template_name': self.template_name,
            'features' : self.features
        }
        return context
