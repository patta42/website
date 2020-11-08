from courses.models import CourseAttendee
import courses.templatetags.attendee_tags as attendee_tags 
from rai.mail.base import MailWithTemplate


class CourseResultMail(MailWithTemplate):
    title = 'Kurse: Klausurergebnis'
    identifier = 'courses.mails.course_results'
    description = 'Vorlage für die E-Mail zum Informieren der Kursteilnehmer über die Kursergebnisse'
    template = 'courses/rai/mail/course-results.txt'
    internal = False
    context_definition = {
        'attendee' : {
            'tags' : attendee_tags,
            'label' : 'Kursteilnehmer',
            'prefix' : 'at',
            'preview_model' : CourseAttendee
        }
    }
class CourseResult2ndExamMail(MailWithTemplate):
    title = 'Kurse: Klausurergebnis der Nachklausur'
    identifier = 'courses.mails.course_results_2ndexam'
    description = 'Vorlage für die E-Mail zum Informieren der Kursteilnehmer über die Klursergebnisse (Nachklausur)'
    template = 'courses/rai/mail/course-results.txt'
    internal = False
    context_definition = {
        'attendee' : {
            'tags' : attendee_tags,
            'label' : 'Kursteilnehmer',
            'prefix' : 'at',
            'preview_model' : CourseAttendee
        }
    }
