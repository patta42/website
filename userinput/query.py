import datetime

from django.db import Q

from wagtail.core.query import PageQuerySet
from wagtail.core.models import BasePageManager



class ActiveInactivePageQuerySet(PageQuerySet):
    def active(self):
        td = datetime.datetime.today()
        return self.filter(Q(expire_at__isnull = True) | Q(expire_at__gt = td))

    def inactive(self):
        td = datetime.datetime.today()
        return self.filter(expire_at__lte = td)

ActiveInactivePageManager = BasePageManager.from_queryset(ActiveInactivePageQuerySet)
    
