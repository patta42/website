from .forms import RAIEMailForm
from .collections import RAIMailFileCollection

from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.forms.models import modelform_factory
from django.http import JsonResponse
from django.template.response import TemplateResponse

from rai.default_views.generic import RAIView, PageMenuMixin
from rai.files.models import RAIDocument

from website.models import SentMail

class EMailView(RAIView, PageMenuMixin):
    template_name = 'rai/mail/email-view.html'
    save_button = True
    save_button_label = 'E-Mail versenden'
    save_button_icon = 'paper-plane'


    def get_actions(self):
        return []
    
    def get_context_data(self):
        context = super().get_context_data()
        context['icon'] = 'envelope'
        context['icon_font'] = 'fas'
        context['form'] = self.form
        context['page_menu'] = self.get_page_menu()
        
        return context

    def send_mails(self, receivers):
        connection = get_connection()
        messages = []
        from_ = self.request.POST['from_']
        reply_to = '"{} {}" <{}>'.format(
                self.request.user.first_name,
                self.request.user.last_name,
                self.request.user.email
        )
        if from_ == "auto":
            sender = settings.RUBION_MAIL_FROM
        else:
            sender = reply_to
            
        for receiver in list(set(receivers)):
            msg = EmailMessage(
                self.request.POST['subject'],
                self.request.POST['body'],
                sender,
                [receiver],
                reply_to = [reply_to],
                connection = connection
            )
            for att in self.attachements:
                msg.attach(att.title, att.file.read())
            msg.send()
            copy = SentMail.from_email_message(msg)
            #copy.save()

    def handle_files(self, request):
        self.attachements = []
        form_class = modelform_factory(
            RAIDocument,
            fields = ['file', 'title']
        )
        collection = RAIMailFileCollection().get_obj()
        
        for file in request.FILES.getlist('attachements'):
            form = form_class({'title' : file.name},{'file' : file})
            if form.is_valid():
                instance = form.save(commit = False)
                instance.uploaded_by_user = request.user
                instance.collection = collection
                instance.save()
                self.attachements.append(instance)
                
            else:
                print(form.errors)
            
    def get(self, request, *args, **kwargs):
        self.form = RAIEMailForm(user = request.user)
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        post = request.POST.copy()
        to_list = post.getlist('to', [])
        post.update({'to': ', '.join(to_list)})
        self.form = RAIEMailForm(post, request.FILES, user = request.user)
        if self.form.is_valid():

            self.handle_files(request)
            
            # The values in to might look like "Foo Bar <foo@bar.com>__<somegroup>" to allow
            # for re-building the groups in the widget. We have to cut the __<somegroup> part here
            # Furthermore, the name-part (Foo Bar) should be enclosed in quotation marks 
            receivers = ['"{}" <{}'.format(*receiver.split('__')[0].split(' <')) for receiver in to_list]
            self.send_mails(receivers)
            context = self.get_context_data()
            del(context['page_menu'])
            choices = dict(self.form.fields['from_'].choices)
            context['from_display'] = choices[post['from_']]
            context['receivers'] = receivers
            context['attachements'] = self.attachements
            return TemplateResponse(request, 'rai/mail/email-success.html', context)

        else:
            self.warning_message('Die Angaben sind unvollständig oder enthalten Fehler.')
            return super().get(request, *args, **kwargs)
    
def fetch_mail_list(request):
    from .internals import REGISTERED_MAIL_COLLECTIONS

    if request.is_ajax() and request.method=='POST':
        pk = request.POST.get('pk', None)
        cid = request.POST.get('id', None)

        if pk and cid:
            collection = REGISTERED_MAIL_COLLECTIONS[cid]
            return JsonResponse({
                'mails' : collection.get_all_for_pk(pk)
            })
        else:
            return JsonResponse(status = 404)
