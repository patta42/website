from rai.notifications.base import PageContentChangedEvent, RAIEvent
from userdata.models import StaffUser
from userinput.models import RUBIONUser, Project, WorkGroup

class RUBIONUserChangedEvent(PageContentChangedEvent):
    model = RUBIONUser

class ProjectChangedEvent(PageContentChangedEvent):
    model = Project

class WorkGroupChangedEvent(PageContentChangedEvent):
    model = WorkGroup

class FieldChangedMixin:
    fields = []
    cache_emit_kwargs = True
    
    def check(self, **kwargs):
        if super().check(**kwargs):
            emit_kwargs = self.get_emit_kwargs(**kwargs)
            for field in self.fields:
                if field in emit_kwargs['changed_fields']:
                    return True
                
        return False

class InactivatedMixin(FieldChangedMixin):
    fields = ['locked']
    def check(self, **kwargs):
        if super().check(**kwargs):
            emit_kwargs = self.get_emit_kwargs(**kwargs)
            return emit_kwargs['new_instance'].locked
        
class ActivatedMixin(FieldChangedMixin):
    fields = ['locked']
    def check(self, **kwargs):
        if super().check(**kwargs):
            emit_kwargs = self.get_emit_kwargs(**kwargs)
            return emit_kwargs['new_instance'].locked == False

        
class NewOfficialDosemeter(FieldChangedMixin, RUBIONUserChangedEvent):
    fields = ['dosemeter']
    identifier = 'rubionuser.new_official_dosemeter'

    def check(self, **kwargs):
        if super().check(**kwargs):
            emit_kwargs = self.get_emit_kwargs(**kwargs)
            return emit_kwargs['new_instance'].dosemeter == RUBIONUser.OFFICIAL_DOSEMETER
        
class NoMoreOfficialDosemeter(FieldChangedMixin, RUBIONUserChangedEvent):
    fields = ['dosemeter']
    identifier = 'rubionuser.no_more_official_dosemeter'
    def check(self, **kwargs):
        if super().check(**kwargs):
            emit_kwargs = self.get_emit_kwargs(**kwargs)
            return emit_kwargs['old_instance'].dosemeter == RUBIONUser.OFFICIAL_DOSEMETER

class NewKey(FieldChangedMixin, RUBIONUserChangedEvent):
    fields = ['key_number']
    identifier = 'rubionuser.new_key'
    def check(self, **kwargs):
        if super().check(**kwargs):
            emit_kwargs = self.get_emit_kwargs(**kwargs)
            if not emit_kwargs['old_instance'].key_number:
                return True
            else:
                return str(emit_kwargs['old_instance'].key_number).strip() == ''
        
    
class RUBIONUserActivated(ActivatedMixin, RUBIONUserChangedEvent):
    identifier = 'rubionuser.activated'
    pass


class RUBIONUserInactivated(InactivatedMixin, RUBIONUserChangedEvent):
    identifier = 'rubionuser.inactivated'
    pass

class RUBIONUserInactivatedByColleague(RUBIONUserInactivated):
    identifier = RUBIONUserInactivated.identifier + '.by_colleague'
    def check(self, **kwargs):
        if super().check(**kwargs):
            emit_kwargs = self.get_emit_kwargs(**kwargs)
            ruser = RUBIONUser.get_from_user(emit_kwargs['user'])
            if not ruser:
                return False
            staff = StaffUser.get_from_user(emit_kwargs['user'])
            if staff:
                # if a staff user is connected, emit the corresponding `by_RUBION` event
                # below
                return False
            return ruser.get_workgroup() == emit_kwargs['new_instance'].get_workgroup()
        
        return False

    
class RUBIONUserInactivatedByRUBION(RUBIONUserInactivated):
    identifier = RUBIONUserInactivated.identifier + '.by_RUBION'
    def check(self, **kwargs):
        if super().check(**kwargs):
            emit_kwargs = self.get_emit_kwargs(**kwargs)
            staff = StaffUser.get_from_user(emit_kwargs['user'])
            if not staff:
                return False
            return True

# As for manually triggered events, the question is
# where the check should occur if the event it triggered.
# For example, for expiring SafetyInstructions, should the cron job
# check the expire_date and call Event.emit() or should Event.signal_received
# should be called and then check tests the event occurs.
# I guess the first solution might be better since it may allow to reduce
# the number of checks by, for example, selecting only the RUBIONUsers from the DB
# that have an expired SI. this makes the definition of the event quite easy.

class SafetyInstructionExpiresThisYearEvent(RAIEvent):
    model = RUBIONUser
    identifier = 'safetyinstruction.expire.this_year'

class SafetyInstructionExpiresSoonEvent(RAIEvent):
    identifier = 'safetyinstruction.expire.soon'
    model = RUBIONUser

class SafetyInstructionIsExpiredEvent(RAIEvent):
    identifier = 'safetyinstruction.expire.is_expired'    
    model = RUBIONUser

class SafetyInstructionNeverGivenEvent(RAIEvent):
    identifier = 'safetyinstruction.expire.never_given'
    model = RUBIONUser

class ProjectExpiresSoonEvent(RAIEvent):
    model = Project
    identifier = 'project.expire.soon'

    

class ProjectIsExpiredEvent(RAIEvent):
    identifier = 'project.expire.is_expired'
    model = Project

    
NewOfficialDosemeter.register()
NoMoreOfficialDosemeter.register()
NewKey.register()
RUBIONUserInactivated.register()
RUBIONUserActivated.register()
RUBIONUserInactivatedByColleague.register()
RUBIONUserInactivatedByRUBION.register()
ProjectExpiresSoonEvent.register()
ProjectIsExpiredEvent.register()
SafetyInstructionNeverGivenEvent.register()
