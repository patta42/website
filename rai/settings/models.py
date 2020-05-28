from .fields import JsonField
from django.conf import settings as dj_settings
from django.db import models

import json

class ListFilterSettings(models.Model):
    view_name = models.CharField(max_length = 128)
    filter_spec = models.CharField(max_length = 512)
    user = models.ForeignKey(dj_settings.AUTH_USER_MODEL, on_delete = models.CASCADE)


class ModelWithJsonField(models.Model):
    class Meta:
        abstract = True
        
    def save(self, *args, **kwargs):
        # this jsonifies every JsonField
        for field in self._meta.fields:
            if isinstance(field, JsonField):
                attr = getattr(self, field.name)
                if attr and not isinstance(attr, str):
                    setattr(self, field.name, json.dumps(attr))
                    
        super().save(*args, **kwargs)

class ListViewSettings(ModelWithJsonField):
    view_name = models.CharField(max_length = 128)
    settings =   JsonField(
        blank = True
    )
    user = models.ForeignKey(dj_settings.AUTH_USER_MODEL, on_delete = models.CASCADE)

    
class AdminMenuSettings(ModelWithJsonField):
    user = models.ForeignKey(dj_settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    group_order = JsonField(
        blank = True
    )
    item_labels = JsonField(
        blank = True
    )
    group_item_labels = JsonField(
        blank = True
    )

    # def save(self, *args, **kwargs):
    #     # this jsonifies every JsonField
    #     for field in self._meta.fields:
    #         if isinstance(field, JsonField):
    #             attr = getattr(self, field.name)
    #             if attr and not isinstance(attr, str):
    #                 setattr(self, field.name, json.dumps(attr))
                    
    #     super().save(*args, **kwargs)

    def as_dict(self):
        dct = {
            'group_order' : [],
            'item_labels' : {},
            'group_item_labels' : {}
        }
        if self.group_order:
            dct.update({'group_order' : json.loads(self.group_order)})
        if self.item_labels:
            dct.update({'item_labels' : json.loads(self.item_labels)})
        if self.group_item_labels:
            dct.update({'group_item_labels' : json.loads(self.group_item_labels)})

        return dct
    def update(self, dct):
        for k,v in dct.items():
            if v and hasattr(self, k):
                setattr(self, k , v)
