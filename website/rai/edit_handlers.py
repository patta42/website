from rai.edit_handlers import (
    RAIObjectList, RAIReadOnlyPanel, RAIQueryInlinePanel,
    RAIReadOnlyPanel, RAIMultiFieldPanel
)
from website.models import SentMail

class SentMailMultiFieldPanel(RAIMultiFieldPanel):
    template =  'website/sent_mail/rai/edit_handlers/multi-field.html'

class SentMailSubjectField(RAIReadOnlyPanel):
    field_template = 'website/sent_mail/rai/edit_handlers/subject-field.html'

class SentMailSentAtField(RAIReadOnlyPanel):
    field_template = 'website/sent_mail/rai/edit_handlers/sent_at-field.html'
    
    
class SentMailSenderField(RAIReadOnlyPanel):
    field_template = 'website/sent_mail/rai/edit_handlers/sender-field.html'

class SentMailFetchMailField(RAIReadOnlyPanel):
    field_template = 'website/sent_mail/rai/edit_handlers/fetch-mail-field.html'
class SentMailBodyField(RAIReadOnlyPanel):
    field_template = 'website/sent_mail/rai/edit_handlers/body-field.html'

class SentMailPanel(RAIObjectList):
    """
    An edit handler for showing SentMails
    """

    def __init__(self, field_name, get_sent_mail, *args, **kwargs):
        self.field_name = field_name
        self.get_sent_mail_callback = get_sent_mail
        super().__init__(*args, **kwargs)
        self.children = [
            RAIQueryInlinePanel(
                field_name, SentMail, self.get_sent_mail_callback,
                [
                    SentMailMultiFieldPanel([
                        SentMailSubjectField('subject'),
                        SentMailSenderField('sender'),
                        SentMailSentAtField('sent_at'),
                        SentMailBodyField('body'),
                    ])
                ], heading='E-Mails', allow_add = False
            )
        ]


    def clone(self):
        return self.__class__(
            self.field_name, self.get_sent_mail_callback,
            **self.clone_kwargs()
        )


    
