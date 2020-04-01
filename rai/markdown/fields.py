from django.db import models

class MarkdownField(models.TextField):
    def __init__(self, *args, **kwargs):
#        self.editor = kwargs.pop('editor', 'default')
        self.features = kwargs.pop('features', None)
        # TODO: preserve 'editor' and 'features' when deconstructing for migrations
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        from rai.markdown.widgets import RAIMarkdownWidget
        defaults = {'widget': RAIMarkdownWidget(features=self.features)}

        return super().formfield(**defaults)
