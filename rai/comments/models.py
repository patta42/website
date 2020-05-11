from django.contrib.auth import get_user_model
from django.db import models
from rai.markdown.fields import MarkdownField

class RAIComment(models.Model):
    owner = models.ForeignKey(
        get_user_model(),
        on_delete = models.CASCADE,
        null = True
    )
    comment = MarkdownField(
        max_length = 2048
    )
    created_at = models.DateTimeField(
        auto_now_add = True
    )

class RAICommentDecoration(models.Model):
    class Meta:
        abstract = True

    rai_model = models.ForeignKey(RAIComment, on_delete = models.CASCADE)
    decorated_model = None
    
