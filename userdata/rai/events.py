from userinput.rai.events import RUBIONUserInactivated

class RUBIONUserWithDosemeterInactivated(RUBIONUserInactivated):
    identifier = RUBIONUserInactivated.identifier + '._user_has_official_dosemeter'
    def check(self, **kwargs):
        if super().check(**kwargs):
            emit_kwargs = self.get_emit_kwargs(**kwargs)
            return emit_kwargs['old_instance'].dosemeter == emit_kwargs['old_instance'].__class__.OFFICIAL_DOSEMETER
        return False



RUBIONUserWithDosemeterInactivated.register()
