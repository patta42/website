import datetime

from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.db.models import Q, Count, Max

from django_cron import CronJobBase, Schedule

import logging

from notifications.models import ProjectExpiredNotifications

from userinput.models import Project, RUBIONUser
from userinput.notifications import ProjectExpiredMailNotification
from userinput.rai.events import (
    ProjectExpiresSoonEvent, ProjectIsExpiredEvent,
    SafetyInstructionExpiresThisYearEvent, SafetyInstructionExpiresSoonEvent,
    SafetyInstructionIsExpiredEvent, SafetyInstructionNeverGivenEvent
)
import userinput.wagtail_hooks
from website.models import EMailText

logger = logging.getLogger('warn_projects')

class WarnProjects( CronJobBase ):
    RUN_EVERY_MINS = 24 * 60 # once a day

    schedule = Schedule(run_every_mins = RUN_EVERY_MINS)

    code = 'userinput.warn_projects'

    def do( self ):

        self.today = datetime.datetime.today()
        self.next_month =  self.today + relativedelta(months = +1)
        self.two_weeks_ago = self.today + relativedelta(weeks=-2)
        self.one_weeks_ago = self.today + relativedelta(weeks=-1)

        recently_send = ProjectExpiredNotifications.objects.filter(mail__sent_at__gt = self.one_weeks_ago)
        ids = []
        for rs in recently_send.all():
            ids.append(rs.id)
        projects_soon = Project.objects.filter(
            expire_at__gt = self.today, expire_at__lt = self.next_month, locked = False
        ).exclude(id__in = ids)
        projects_expired = Project.objects.filter(expire_at__lte = self.today, locked = False).exclude(id__in = ids)
        for project in projects_expired:
            if self.needs_to_be_sent( project ):
                self.send_expired_mail( project )
                
        for project in projects_soon:
            if self.needs_to_be_sent( project ):
                self.send_will_soon_expire_mail( project )


    def needs_to_be_sent( self, project ):
        notifications = ProjectExpiredNotifications.objects.filter(project = project).order_by('-mail__sent_at')
        try:
            last = notifications[0]
        except IndexError:
            return True

        if last.mail.sent_at < self.two_weeks_ago:
            return True

        return False

    def get_contacts(self, wg):
        return RUBIONUser.objects.live().descendant_of(wg).filter(
            Q(is_leader = True) | Q(may_create_projects = True)
        )

    def send_expired_mail( self, project ):
        mail = EMailText.objects.get(identifier = 'warning.project.expired')
        self.send_mail(mail, project)
        
        
    def send_will_soon_expire_mail( self, project ):
        mail = EMailText.objects.get(identifier = 'warning.project.will_expire')
        self.send_mail(mail, project)

    def send_mail( self, mail, project ):
        print ('sending mail')
        contacts = self.get_contacts( project.get_workgroup() )
        to = []
        languages = []
        for contact in contacts:
            to.append(contact.email)
            if contact.preferred_language is not None:
                languages.append(contact.preferred_language)

        languages = list(set(languages)) # removes duplicates
        if len(languages) == 1:
            languages = languages[0]
        else:
            languages = None
            
        sent_mail = mail.send(
            to, {
                'contacts' : contacts,
                'project_de' : project.title_de,
                'project_en' : project.title,
                'expires' : project.expire_at
            },
            lang = languages 
        )
        noti = ProjectExpiredNotifications(
            project=project, mail = sent_mail
        ).save()

        ProjectExpiredMailNotification( project, contacts ).notify()
        
        logger.info('Sent mail for project {} to {}'.format(project.title_de, ", ".join(to))) 
        
def _active_projects():
    return Project.objects.filter(Project.active_filter())
        
class RAIWarnProjects( CronJobBase ):
    # CronJob that triggers Events for expiring projects

    RUN_EVERY_MINS = 24 * 60 # once a day

    schedule = Schedule(run_every_mins = RUN_EVERY_MINS)

    code = 'userinput.warn_projects'

    def do(self):
            
        self.today = datetime.date.today()
        self.in_one_month = self.today + relativedelta(months = +1)
        # get projects that expire within the next month:
        projects = _active_projects()
        expiring_projects = projects.filter(expire_at__lt = self.in_one_month, expire_at__gt = self.today)
        expired_projects = projects.filter(expire_at__lte = self.today)
        

        for project in expiring_projects:
            event = ProjectExpiresSoonEvent()
            event.emit(
                project = project,
                date = self.today
            )
        for project in expired_projects:
            event = ProjectIsExpiredEvent()
            event.emit(
                project = project,
                date = self.today
            )
        
class RAIWarnSafetyInstructions(CronJobBase):
    # run once a day
    RUN_EVERY_MINS = 24 * 60 # once a day
    schedule = Schedule(run_every_mins = RUN_EVERY_MINS)
    code = 'userinput.warn_safety_instructions'
    ALLOW_PARALLEL_RUNS = True
    # SOME NOTES ON THE QUERYSETS
    # get the last safety instruction dates from a single rubionuser `ru`:
    # ru.rubion_user_si.filter(instruction__in = ru.safety_instructions.filter(as_required = False).values_list('instruction', flat = True)).values('instruction').annotate(last = Max('date'))
    
    def do(self):
        # active rubion users which are not staff members
        active_users = RUBIONUser.objects.annotate(
            staffcount = Count('linked_user__staffuser')
        ).filter(staffcount = 0, locked = False)
        logger = logging.getLogger('warn_safety_instructions')

        count = 0
        for user in active_users.prefetch_related('safety_instructions'):
            count += 1
            # get last safety instructions
            inner_q = user.safety_instructions.filter(
                as_required = False
            ).values_list('instruction', flat = True)

            # get and re-arrange last instructions
            last_instructions = {}
            validities = {}
            last_instructions_q = user.rubion_user_si.filter(
                instruction__in = inner_q
            ).values('instruction', 'instruction__is_valid_for').annotate(last = Max('date'))
            
            for li in last_instructions_q:
                last_instructions[li['instruction']] = li['last']
                validities[li['instruction']] = li['instruction__is_valid_for']
                
            
            # The following "deadlines" trigger the events:
            # For instructions which are valid for more than one year:
            #
            # - if the instruction expires within the next year
            # SafetyInstructionExpiresThisYear
            thisyear = []

            # - if the instruction expires within the next two months:
            # SafetyInstructionExpiresSoon
            soon = []

            # - if it is expired:
            # SafetyInstructionIsExpired
            expired = []

            # - if a SI was never given yet:
            # SafetyInstructionNeverGiven
            never = []
            
            today = datetime.date.today()
            two_months = today + relativedelta(months = 2)
            next_year = today + relativedelta(years = 1)

            # loop through the instructions required for the user
            for rel in user.safety_instructions.filter(as_required = False):
                last_date = last_instructions.get(rel.instruction.pk, None)
                if not last_date:
                    never.append(rel.instruction)
                    continue
                # add validity 
                last_date += relativedelta(years = validities[rel.instruction.pk])
                
                if last_date < today:
                    expired.append({
                        'instruction' : rel.instruction,
                        'valid_until' : last_date
                    })
                    continue
                if last_date < two_months:
                    soon.append({
                        'instruction' : rel.instruction,
                        'valid_until' : last_date
                    })

                    continue
                if last_date < next_year and validities[rel.instruction.pk] > 1:
                    thisyear.append({
                        'instruction' : rel.instruction,
                        'valid_until' : last_date
                    })
            # emit the events:
            if never:
                event = SafetyInstructionNeverGivenEvent()
                event.emit(user = user, instructions = never)
                
            if expired:
                event = SafetyInstructionIsExpiredEvent()
                event.emit(user = user, instructions = expired)
                
            if soon:
                event = SafetyInstructionExpiresSoonEvent()
                event.emit(user = user, instructions = soon)

            if thisyear:
                event = SafetyInstructionExpiresThisYearEvent()
                event.emit(user = user, instructions = thisyear)
                
