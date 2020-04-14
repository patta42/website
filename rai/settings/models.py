from django.conf import settings
from django.db import models


class ListFilterSettings(models.Model):
    view_name = models.CharField(max_length = 128)
    filter_spec = models.CharField(max_length = 512)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)

class AdminMenuSettings(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    group_order = models.TextField(
        blank = True
    )
    item_labels = models.TextField(
        blank = True
    )
    group_item_labels = models.TextField(
        blank = True
    )
