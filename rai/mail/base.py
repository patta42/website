from rai.notifications.base import NotificationTemplateMixin
from wagtail.core import hooks


class RAIMailAddressCollection:
    label = None
    
    def register(self):
        @hooks.register('rai_mail_collection')
        def register_with_rai():
            return self
        
    def get_mail_addresses(self):
        pass

    def get_for_instance(self, instance):
        pass

    def get_objects(self):
        pass

class RAIModelAddressCollection(RAIMailAddressCollection):
    model = None
    mail_field = None
    search_fields = None
    multiple_for_instance = False

    def format_as_mail_string(self, instance):
        return '{} {} <{}>'.format(
            instance.first_name,
            instance.last_name,
            instance.email
        )
    
    def mail_address(self, instance):
        return instance.email
    
    def get_objects(self):
        return self.model.objects.all()

    def get_mail_addresses(self):
        addresses = [] 
        for obj in self.get_objects():
            addresses.append(self.get_for_instance(obj))

        return addresses

    def get_all_for_pk(self, pk):
        pass
    
def register_mail_collection(mail_collection_class):
    mail_collection = mail_collection_class()
    mail_collection.register()

class MailWithTemplate(NotificationTemplateMixin):
    def register(self):
        self.register_template()
        self.register_with_wagtail()
        
    def register_with_wagtail(self):
        @hooks.register('rai_notification')
        def register_notification():
            return self


def register_mail_template(TemplateMailClass):
    mail = TemplateMailClass()
    mail.register()
