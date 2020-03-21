from rai.filters import RAIFilter, RAIFilterOption

class RUBIONUserStatusFilter(RAIFilter):
    label = _l('User status')
    filter_id = 'user_status'
    is_mutual_exclusive = True
    help_text = _l('Filters users by their active/inactive status.')
    options = [
        RAIFilterOption(_l('all'), 'all', help_text=_l('Show all users (independent from their status).')),
        RAIFilterOption(_l('active'), 'active', help_text=_l('Show only active users.'), default = True),
        RAIFilterOption(_l('inactive'), 'inactive', help_text=_l('Show inactive users only.'))
    ]

    def get_queryset(self):
        td = datetime.datetime.today()
        if self.value == 'all':
            return self.qs
        if self.value == 'active':
            return self.qs.filter(Q(exclude_at__isnull = True) | Q(exclude_at__gte = td))
        if self.value == 'inactive':
            return self.qs.filter(exclude_at__lt = td)

        return self.qs




class RUBIONUserInstrumentFilter(RAIFilter):
    label = _l('Used instruments')
    filter_id = 'user_instrument'
    is_mutual_exclusive = False
    help_text = _l('Filter users by their usage of instruments')
    options = [
        RAIFilterOption(_l('i1'), 'i1', help_text=_l('Show users using i1')),
        RAIFilterOption(_l('i2'), 'i2', help_text=_l('Show users using i2')),
        RAIFilterOption(_l('i3'), 'i3', help_text=_l('Show users using i3')),
        RAIFilterOption(_l('i4'), 'i4', help_text=_l('Show users using i4'))
    ]
