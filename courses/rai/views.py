from .forms import ResultsUploadForm, AttendeesMoveChooseCourseForm

from courses.models import CourseAttendee, CourseInformationPage, Course, Course2AttendeeRelation
from courses.pdfhandling import CourseNamePlate, CourseCertificate

from django.db.models import Q
from django.forms import modelform_factory
from django.http import HttpResponseNotFound, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.utils.text import slugify
from django.utils.safestring import mark_safe


import pandas as pd
from rai.default_views.generic import RAIView, RAIAdminView,  SingleObjectMixin, PageMenuMixin
from rai.default_views.multiform_create import MultiFormCreateView


class CourseAttendeeView(RAIAdminView, PageMenuMixin, SingleObjectMixin):
    template_name = 'courses/rai/attendee-view.html'


    def get_actions(self):
        return self.get_group_actions() + self.get_item_actions()

    def dispatch(self, request, *args, **kwargs):
        self.obj = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # ATTENDEE_TYPES contains the classes
        from courses.attendees import ATTENDEE_TYPES
        
        context = super().get_context_data(**kwargs)
        context['object'] = self.obj
        attendees = []
        attendee_type_names = {
            'SskRubMemberAttendee' : 'RUB-Mitarbeiter',
            'SskStudentAttendee' : 'Student der RUB',
            'SskHospitalAttendee' : 'Mitarbeiter des Universitätsklinikums',
            'SskExternalAttendee' : 'Extern',
            'StudentAttendee' : 'Student der RUB',
            'SskExternalStudentUARuhr' : 'Student der UA-Ruhr'

        }
        for attendee in CourseAttendee.objects.filter(related_course = self.obj).order_by('created_at'):
            specific = attendee.specific
            attendees.append({
                'data' : specific,
                'type' : attendee_type_names[specific.__class__.__name__],
                'waitlist' : False
            })

        for attendee in CourseAttendee.objects.filter(waitlist_course = self.obj).order_by('created_at'):
            specific = attendee.specific
            attendees.append({
                'data' : specific,
                'type' : attendee_type_names[specific.__class__.__name__],
                'waitlist' : True
            })
        context['attendees'] = attendees
        context['page_menu'] = render_to_string('courses/rai/attendee-view-actions.html', {})
        return context

class DeleteAttendees(RAIView, PageMenuMixin):
    template_name = 'courses/rai/delete-attendees.html'
    def dispatch(self, request, *args, **kwargs):
        self.pks = []
        self.next = request.GET.get('next', '')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.next
        context['attendees'] = CourseAttendee.objects.filter(pk__in = self.pks)
        return context

    def post(self, request, *args, **kwargs):
        self.pks = request.POST.getlist('pk')
        if request.POST.get('action', None) == 'delete':
            for pk in self.pks:
                at = CourseAttendee.objects.get(pk = pk)
                at.delete()
            if len(self.pks) > 1:
                self.success_message('{} Teilnehmer wurden gelöscht'.format(len(self.pk)))
            else:
                self.success_message('Ein Teilnehmer wurde gelöscht.')
            redirect(self.next)
        else:
            return self.get(request, *args, **kwargs)

class CourseCreateView(MultiFormCreateView):
    def prepare_next_form(self, prefix):
        if prefix == 'settings':
            parent_id = self.session_store['parent']['form']['parent']
            parent = CourseInformationPage.objects.get(pk = parent_id)
            instance = Course()
            for field in self.formclass._meta.fields:
                if hasattr(parent, field):
                    setattr(instance, field, getattr(parent, field))
            for field in self.formclass._meta.formsets:
                if hasattr(parent, field):
                    rels = getattr(parent, field)
                    rels_new = []
                    for rel in rels.all():
                        rels_new.append(Course2AttendeeRelation.from_CourseDefinitionRelation(rel))
                    setattr(instance, field, rels_new)
            self.form = self.formclass(instance = instance)


    def prepare_cleaned_data(self, data, prefix):
        if prefix == 'dates':
            start = data.get('start', None)
            end = data.get('end', None)
            if start:
                data.update({'start': start.isoformat()})
            if end:
                data.update({'end': end.isoformat()})
        return data


    def prepare_formsets(self, data, prefix):
        if prefix == 'settings':
            types = data['attendee_types']
            for t in types:
                t['price'] = float(t['price'])
        return data
    
    def finalize(self, request):
        parent_id = self.session_store['parent']['form']['parent']
        parent = CourseInformationPage.objects.get(pk = parent_id)
        dates = self.session_store['dates']['form']
        title = dates.get('start')
        if dates.get('end', None):
            title += '--'+dates.get('end')
        settings = self.session_store['settings']['form']
        instance = Course(
            start = self.session_store['dates']['form']['start'],
            end = self.session_store['dates']['form']['end'],
            title = title,
            title_de = title,
            slug = slugify(title),
            overrule_parent = True,
            register_via_website = settings.get('register_via_website', False),
            share_data_via_website = settings.get('share_data_via_website', False),
            max_attendees = settings.get('max_attendees', None),
            
        )
        instance = parent.add_child(instance = instance)
        fs = self.session_store['settings']['formsets']
        attendee_types = fs.get('attendee_types', [])
        for at in attendee_types:
            rel = Course2AttendeeRelation(
                attendee = at['attendee'],
                price = at.get('price', 0),
                max_attendees = at.get('max_attendees', None),
                waitlist = at.get('waitlist', False),
                course = instance
            )
            rel.save()
        
        self.success_message('Veranstaltung vom {} angelegt.'.format(title))
        return redirect('rai_courses_course_list')
    
def edit_attendee(request, pk = None, field = None):
    if not request.is_ajax():
        return HttpResponseNotFound()
    if request.method == 'POST':
        if not pk:
            pk = request.POST.get('pk', None)
        if not field:
            field = request.POST.get('field', None)
        if not( pk and field ):
            return HttpResponseNotFound()
        attendee = get_object_or_404(CourseAttendee, pk = pk)
        attendee = attendee.specific
        Form = modelform_factory(attendee.__class__, fields = [field])
        form = Form(request.POST, instance = attendee)
        errors = {}
        if form.is_valid():
            attendee = form.save()
            has_errors = False
        else:
            has_errors = True
            
        json_attendee = {}
        for key, val in attendee.__dict__.items():
            if not key.startswith('_'):
                json_attendee[key] = val
            
        return JsonResponse({
            'status' : 200,
            'object' : json_attendee,
            'has_errors' : has_errors,
            'errors' : form.errors
        })

class AttendeeMoveView(RAIView):
    def nxt(self):
        nxt = self.request.GET.get('next', None)
        if not nxt:
            nxt = self.request.POST.get('next', None)
        return nxt
    def selection_form(self):
        context = self.get_context_data()
        context.update({
            'attendees' : self.attendees,
            'form' : self.form,
            'origin' : self.origin,
            'next' : self.nxt()
        })
        return TemplateResponse(
                self.request,
                'courses/rai/move-attendees_select.html',
                context,
                
            )
    def post(self, request):
        print(request.POST)
        self.request = request
        action = self.request.POST.get('action', 'select')
        self.origin = get_object_or_404(Course, pk = request.POST.get('origin'))
        attendee_pks = request.POST.getlist('pk', [])
        
        self.attendees = (
            CourseAttendee.objects
            .filter(pk__in = attendee_pks)
            .filter(Q(related_course = self.origin)|Q(waitlist_course = self.origin))
        )
        if len(self.attendees) != len(attendee_pks):
            return HttpResponseNotFound()
        course_type = self.origin.get_parent()
        if action == 'select':
            self.form = AttendeesMoveChooseCourseForm(course_type = course_type)
            return self.selection_form()
        
        if action == 'move':
            self.form = AttendeesMoveChooseCourseForm(request.POST, course_type = course_type)
            if self.form.is_valid():
                new_course = Course.objects.get(pk=self.form.cleaned_data['course'])
                for attendee in self.attendees:
                    attendee.related_course = new_course
                    attendee.waitlist_course = None
                    attendee.save()
                self.success_message('{} Teilnehmer verschoben'.format(len(self.attendees)))
                self.info_message(mark_safe(
                    'Die Teilnehmer wurden <strong>nicht</strong> automatisch informiert.'
                ))
                return redirect(self.nxt())
            else:
                return self.selection_form()

        
    def get(self, request):
        return HttpResponseNotFound()

def import_results(request):
    if not request.is_ajax():
        return HttpResponseNotFound()
    
    if request.method == 'GET':
        form = ResultsUploadForm()
        return JsonResponse({
            'status' : 200,
            'html' : form.as_p()
        })
    if request.method == 'POST':
        form = ResultsUploadForm(request.POST, request.FILES)
        df = pd.read_excel(request.FILES['file_'])
        pd.set_option('display.float_format',lambda x: '%.12g' % x)
        return JsonResponse({
            'status' : 200,
            'html' : df.to_html(na_rep  ='')
        })
    

def pdf_certificate(request):
    if request.method == 'POST':
        attendee_pks = request.POST.getlist('attendee_pks')
        pdf = CourseCertificate(attendee_pks)
        resp = HttpResponse(
            pdf.for_content_file(endpage = False),
            content_type='application/pdf'
        )
        resp['Content-Disposition'] = "attachment; filename=Zertifikate.pdf"
        return resp
        
def pdf_nameplate(request):
    if request.method == 'POST':
        attendee_pks = request.POST.getlist('attendee_pks')
        pdf = CourseNamePlate(attendee_pks)
        resp = HttpResponse(
            pdf.for_content_file(endpage = False),
            content_type='application/pdf'
        )
        resp['Content-Disposition'] = "attachment; filename=Tischschilder.pdf"
        return resp