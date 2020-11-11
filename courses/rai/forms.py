from courses.models import CourseInformationPage, Course

import datetime

from django import forms
from django.forms.widgets import SelectDateWidget
from rai.widgets import (
    RAIFileInput, RAIRadioSelect, RAIDateInput, RAIHiddenInput,
    RAINumberInput, RAITextInput, RAISelectDateWidget
)

class ResultsUploadForm(forms.Form):
    file_ = forms.FileField(
        widget = RAIFileInput(attrs = {'accept' : '.xls, .xlsx, .csv, .ods'}),
        label = 'Bitte eine Excel-Datei (*.xls, *.xlsx), ein OpenOffice Spreadsheet (*.ods) oder eine Datei mit komma-separierten Werten (*.csv) auswählen' 
    )
    
class CourseChooseParentForm(forms.Form):
    parent = forms.ChoiceField(
        label = "Aus Kursangebot auswählen",
        widget = RAIRadioSelect
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].choices = [
            (p.pk, p.title_de) for p in CourseInformationPage.objects.all().order_by('title_de')
        ]

class AttendeesMoveChooseCourseForm(forms.Form):
    course = forms.ChoiceField(
        label = 'In welchen Kurs sollen die Teilnehmer verschoben werden?',
        widget = RAIRadioSelect
    )

    def __init__(self, *args, **kwargs):
        course_type = kwargs.pop('course_type')
        super().__init__(*args, **kwargs)

        today = datetime.date.today()
        
        self.fields['course'].choices = [(c.pk, c.title) for c in Course.objects.filter(start__gt = today).child_of(course_type).order_by('start')]


        
class CreditPointsForm(forms.Form):
    exam_type = forms.ChoiceField(
        label = 'Klausur',
        choices = [
            ('r', 'reguläre Klausur'),
            ('n1', 'erste Nachklausur')
        ],
        widget = RAIRadioSelect
    )

    datum = forms.DateField(
        label = 'Datum der Klausur',
        widget = RAISelectDateWidget
    )
    credit_points = forms.IntegerField(
        label = 'Anzahl der vergebenen Credit-Points',
        initial = 5,
        widget = RAINumberInput
    )
    sws = forms.IntegerField(
        label = 'Anzahl der Semester-Wochenstunden',
        initial = 2,
        widget = RAINumberInput
    )
    action = forms.CharField(
        widget = RAIHiddenInput,
        initial = 'check'
    )
    attendee_pks = forms.CharField(
        widget = RAIHiddenInput
    )
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        td = datetime.date.today()
        r = range(td.year-20, td.year+2)
        self.fields['datum'].widget.years = r
        self.fields['datum'].initial = td
    #     if date:
    #         self.fields['date'].initial = date
    #         self.fields['exam_type'].initial = 'r'
