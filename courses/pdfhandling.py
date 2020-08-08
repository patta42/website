from .helpers import get_next_invoice_number

import datetime

from decimal import Decimal

from django.conf import settings

from io import BytesIO

import locale

import os

from PyPDF2 import PdfFileWriter, PdfFileReader

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm

from textwrap import wrap

from website.pdfhandling import RUBIONPDF, RUBIONLetter





class RUBIONInvoice( RUBIONLetter ):
    def __init__( self, sender, *args, **kwargs ):
        super().__init__( sender, *args, **kwargs )

        label_de_y = 529.396
        label_en_y = 520.583

        label2_de_y = 445.583
        label2_en_y = 434.683

        content_y = 501.327
        
        last_col_x = 487.078+67.95
        col2_x = 102.55
        col1_x_left = 73.214
        subcol = 247.57
        
        self.POSITIONS.update({
            'invoice_label_de' : (col1_x_left, label_de_y),
            'invoice_label_en' : (col1_x_left, label_en_y),
            'partner_label_de' : (344.95, label_de_y),
            'partner_label_en' : (330.2, label_en_y),
            'delivery_date_label_de' : (417.050, label_de_y),
            'delivery_date_label_en' : (417.50, label_en_y),
            'invoice_date_label_de' : (484.05, label_de_y),
            'invoice_date_label_en' : (496.668, label_en_y),
            'date' : (491.241, content_y),
            'invoice_number': (col1_x_left,content_y),
            'position_label_de' : (77.95, label2_de_y),
            'position_label_en' : (76.914, label2_en_y),
            'description_label_de' : (col2_x, label2_de_y),
            'description_label_en' : (col2_x, label2_en_y),
            'quantity_label_de' : (320.678+(32.706/2), label2_de_y),
            'quantity_label_en' : (320.678+(32.706/2), label2_en_y),
            'unit_label_de' : (366.75 + 26.937/2, label2_de_y),
            'unit_label_en' : (366.75 + 26.937/2, label2_en_y),
            'price_label_de' : (413.65+62.208, label2_de_y),
            'price_label_en' : (413.65+62.208, label2_en_y),
            'total_price_label_de' : ( last_col_x, label2_de_y),
            'total_price_label_en' : (last_col_x, label2_en_y),
            'tax_note_l1' : (col1_x_left, 283.052),
            'tax_note_l2' : (col1_x_left, 273.352),
            'net_amount_label' : (360.1+115.696, 293.152),
            'vat_amount_label' : (360.1+115.696, 278.256),
            'gross_amount_label' :(360.1+115.696, 263.152),
            'net_amount' : (last_col_x, 293.152),
            'vat_amount' : (last_col_x, 278.256),
            'gross_amount' :(last_col_x, 263.152),
            'shipping_method_label': (col1_x_left, 248.213),
            'shipping_method': (subcol, 248.213),
            'terms_of_delivery_label': (col1_x_left, 234.196),
            'terms_of_delivery': (subcol, 234.196),
            'terms_of_payment_label': (col1_x_left, 220.296),
            'terms_of_payment': (subcol, 220.296),
            'provide_information_headline' : (col1_x_left, 206.396),
            'payee_label' :  (col1_x_left, 192.496),
            'payee' :  (subcol, 192.496),
            'bank_account_label' : (col1_x_left, 178.596),
            'bank_account' : (subcol, 178.596),
            'purpose_label' :  (col1_x_left, 164.696),
            'purpose' :  (subcol, 164.696),
            'information_label' : (col1_x_left, 151.013),
            'information_l1' : (col1_x_left, 137.996),
            'information_l2' : (col1_x_left, 126.796),
            'additional1' : (col1_x_left, 108.152),
            'additional2' : (col1_x_left, 82.352+8.65/2),
            'additional3' : (col1_x_left, 65.052+8.65),
        })
        col1_x = 77.95+14.967/2
        col3_x = 341.129+14.85
        col4_x = 366.75+26.937/2
        col5_x = 451.504+24.075

        for y in range(0,9):
            ypos = 418.096-y*0.49*cm
            self.POSITIONS.update(
                {
                    'description_l{}'.format(y+1) : (col2_x, ypos),
                    'item_l{}'.format(y+1) : (col1_x, ypos),
                    'unit_l{}'.format(y+1) : (col4_x, ypos),
                    'quantity_l{}'.format(y+1) : (col3_x, ypos),
                    'total_l{}'.format(y+1) : (last_col_x, ypos),
                    'price_l{}'.format(y+1) : (col5_x, ypos),
                }
            )
        
        self.item_line_counter = 0
        self.n_items = 0
        self.total_amount = Decimal(0)

        self.draw_labels()
        self.draw_table_lines()
        self.font_scala(8, self.WEIGHT_REGULAR, self.BLACK)
        self._draw_multiline(
            'tax_note', 
            [
                'Die Lieferung/Leistung is umsatzsteuerfrei gemäß § 4 UStG. / The deliviery/service', 
                'is not subject to VAT in accordance with section 4 of the Value Added Tax Act'
            ]
        )


        self.font_scala(8.5, self.WEIGHT_REGULAR, self.BLACK)
        self._draw_at_pos('payee', 'Ruhr-Universität Bochum')
        self._draw_at_pos(
            'bank_account', 
            'Sparkasse Bochum | BIC: WELADED1BOC | IBAN: DE18430500010001498807'
        )
        self.additional_lines(1, 
            [
                'Die gelieferte Ware bleibt bis zur vollständigen Bezahlung Eigentum der Ruhr-Universität Bochum. / The goods supplied will remain property',
                'of Ruhr-Universität Bochum pending full payment.'
            ]             
        )
        self.additional_lines(2, 
            [
'Steuer-Nr.: / Tax No.: 350/5708/0018 | UStID-Nr.: / VAT ID No.: DE 127 056 261 | Zoll-Nr.: / Customs No.: 3796868'
            ]
        )
        self.additional_lines(3,
            [
                'Die Ruhr-Universität Bochum ist eine wissenschaftliche Hochschule und vom Land Nordrhein-Westfalen getragene rechtsfähige Körperschaft',
                'des öffentlichen Rechts. Sie wird vertreten durch ihren Rektor, Herrn Prof. Dr. Axel Schölmerich. Gerichtsstand ist Bochum. / Ruhr-',
                'Universität Bochum is a higher education institution and a public body of North Rhine-Westphalia with legal capacity. It is represented by its',
                'Rector,  Prof. Dr. Axel Schölmerich. Place of jurisdiction is Bochum.'
            ]
        )
                
    def draw_information(self, lines):
        self.font_scala(9, self.WEIGHT_REGULAR, self.BLACK)
        self._draw_multiline('information', lines)

    def additional_lines(self, identifier, lines):
        textobj=self.pdf.beginText()
        textobj.setTextOrigin(
            *self.POSITIONS['additional{}'.format(identifier)]
        )
        textobj.setFont('ScalaR', 8)
        for line in lines:
            textobj.textLine(line)
        self.pdf.drawText(textobj)
        
    def _add_two_lang_text(self, identifier, de, en):
        textobj=self.pdf.beginText()
        textobj.setTextOrigin(
            *self.POSITIONS[identifier]
        )
        textobj.setFont("ScalaBd",9)
        textobj.textOut('{} / '.format(de))
        textobj.setFont("ScalaBd",8)
        textobj.textOut(en)
        self.pdf.drawText(textobj)
        


    def add_item( self, description, quantity, price, unit = None):
        self.font_scala(9, self.WEIGHT_REGULAR, self.BLACK)
        self.n_items = self.n_items + 1
        yline = self.item_line_counter+1
        self._draw_at_pos(
            'item_l{}'.format(yline), 
            str(self.n_items),
            align = self.ALIGN_CENTER
        )
        c = 1
        for line in description:
            lines = wrap(line, width=50)
            for wline in lines:
                self._draw_at_pos('description_l{}'.format(c + yline - 1), wline)
                c = c + 1
        self._draw_at_pos('quantity_l{}'.format(yline), "{:1.2f}".format(quantity), align = self.ALIGN_RIGHT)
        if unit:
            self._draw_at_pos('unit_l{}'.format(yline), unit, align = self.ALIGN_CENTER)
        self._draw_at_pos('price_l{}'.format(yline), "{:1.2f}".format(price), align = self.ALIGN_RIGHT)
        self._draw_at_pos('total_l{}'.format(yline), "{:1.2f}".format(quantity*price), align = self.ALIGN_RIGHT)
        self.total_amount = self.total_amount + Decimal(quantity)*Decimal(price)
        self.item_line_counter = self.item_line_counter + len(description)

    def compute_total( self, vat = None ):
        if vat is None:
            vat = Decimal(19)/Decimal(100)
        self.font_scala(9, self.WEIGHT_REGULAR, self.BLACK)
        self._draw_at_pos('net_amount', "{:1.2f}".format(self.total_amount), align = self.ALIGN_RIGHT)
        vat_amount = self.total_amount * Decimal(vat)
        self._draw_at_pos('vat_amount', "{:1.2f}".format(vat_amount), align = self.ALIGN_RIGHT)
        self.font_scala(9, self.WEIGHT_BOLD, self.BLACK)
        self._draw_at_pos('gross_amount', "{:1.2f}".format(self.total_amount - round(vat_amount,2)), align = self.ALIGN_RIGHT)


    def draw_labels(self):
        self.font_scala(9, self.WEIGHT_BOLD, self.BLACK)
        self._draw_at_pos('invoice_label_de','Rechnung')
        self._draw_at_pos('partner_label_de','Partner')
        self._draw_at_pos('delivery_date_label_de','Lieferdatum')
        self._draw_at_pos('invoice_date_label_de','Rechnungsdatum')
        
        self._draw_at_pos('position_label_de','Pos.')
        self._draw_at_pos('description_label_de','Bezeichnung der Lieferung/Leistung')
        self._draw_at_pos('price_label_de','Einzelpreis EUR', align = self.ALIGN_RIGHT)
        self._draw_at_pos('quantity_label_de','Menge', align = self.ALIGN_CENTER)
        self._draw_at_pos('unit_label_de','Einheit', align = self.ALIGN_CENTER)
        self._draw_at_pos('total_price_label_de','Gesamtpreis EUR', align = self.ALIGN_RIGHT)

        self.font_scala(8, self.WEIGHT_BOLD, self.BLACK)
        self._draw_at_pos('invoice_label_en','Invoice')
        self._draw_at_pos('partner_label_en','Buisness Partner')
        self._draw_at_pos('delivery_date_label_en','Delivery Date')
        self._draw_at_pos('invoice_date_label_en','Invoice Date')
        
        self._draw_at_pos('position_label_en','Item')
        self._draw_at_pos('description_label_en','Description of goods/services')
        self._draw_at_pos('price_label_en','Unit price EUR', align = self.ALIGN_RIGHT)
        self._draw_at_pos('quantity_label_en','Quantity', align = self.ALIGN_CENTER)
        self._draw_at_pos('unit_label_en','Unit', align = self.ALIGN_CENTER)
        self._draw_at_pos('total_price_label_en','Total price EUR', align = self.ALIGN_RIGHT)
        self._draw_at_pos('gross_amount_label','Bruttobetrag / Gross amount EUR', align = self.ALIGN_RIGHT)

        self.font_scala(8, self.WEIGHT_REGULAR, self.BLACK)
        self._draw_at_pos('net_amount_label','Nettobetrag / Net amount EUR', align = self.ALIGN_RIGHT)
        self._draw_at_pos('vat_amount_label','Umsatzsteuer / VAT EUR', align = self.ALIGN_RIGHT)

        self._add_two_lang_text(
            'shipping_method_label', 'Versandart', 'Shipping method')
        self._add_two_lang_text(
            'terms_of_delivery_label', 'Lieferbedingung', 'Terms of delivery')
        self._add_two_lang_text(
            'terms_of_payment_label', 'Zahlbedingung','Terms of payment')
        self._add_two_lang_text(
            'provide_information_headline', 
            'Bei Zahlung bitte unbedingt folgende Angaben verwenden:',
            'Please provide the following information upon payment:')
        self._add_two_lang_text(
            'payee_label', 'Zahlungsempfänger', 'Payee')
        self._add_two_lang_text(
            'bank_account_label','Bankverbindung','Bank account')
        self._add_two_lang_text(
            'purpose_label', 'Verwendungszweck', 'Purpose of use')
        self._add_two_lang_text(
            'information_label','Hinweise und Vermerke', 'Information and notes')

    def draw_table_lines(self):
        # it's just a faked table...
        self.pdf.setLineWidth(.8)
        self.pdf.setStrokeColor(self.RUBGRAY)
        
        # long h-lines
        width = 487
        left_pos = 70.4
        ypos = [541.826, 498.726, 455.926, 430.026, 305.026, 260.026, 218.326, 162.826, 121.126]
        self.hlines([
            [left_pos, y, width] for y in ypos
        ])
        
        # long v-lines
        
        height = 421.4
        bottom = 121.1
        xpos = [70.426, 557.226]
        self.vlines([
            [x, bottom, height] for x in xpos
        ])
        
        # short v-lines top row
        height = 43.8
        bottom = 498.7
        xpos = [244.626, 315.126, 401.426, 477.462]
        
        self.vlines([
            [x, bottom, height] for x in xpos
        ])
        
        # short v-lines, next row
        # most  xpos are still valid
        bottom = 305.0
        height = 151.7
        xpos[0] = 99.726
        del xpos[3]
        
        self.vlines([
            [x, bottom, height] for x in xpos
        ])
        # longer v-lines, same row
        height = 196.7
        xpos = [357.826, 477.426]
        bottom = 260.0
        self.vlines([
            [x, bottom, height] for x in xpos
        ])
        # one single hline....
        self.hline(357.8, 275.026, 199.6)
        
    def hline( self, x, y, w ):
        self.pdf.line( x, y, x+w, y)     

    def vline( self, x, y, h ):
        self.pdf.line( x, y, x, y+h)     

    def hlines( self, lines ):
        for line in lines:
            self.hline(*line)

    def vlines( self, lines ):
        for line in lines:
            self.vline(*line)
             

    def _draw_description_line(self, line, no):
        self.font_scala(9, self.WEIGHT_REGULAR, self.BLACK)
        self._draw_at_pos('description_l{}'.format(no), line)

    def draw_date(self, date = None):

        if not date:
            date = datetime.date.today()

        self.font_scala(11, self.WEIGHT_BOLD, self.BLACK)
        self._draw_at_pos('date', date.strftime('%d/%m/%Y'))

    def draw_invoice_number(self, number):
        self.font_scala(11, self.WEIGHT_BOLD, self.BLACK)
        self._draw_at_pos('invoice_number', number)
        self.font_scala(8.5, self.WEIGHT_REGULAR, self.BLACK)
        self._draw_at_pos('purpose', number)



class RUBIONCourseInvoice( RUBIONInvoice ):

    def __init__( 
            self,
            attendee,
            sender,
            *args, **kwargs
    ):
        super().__init__(sender, *args, **kwargs)

        self.draw_date()
        self.attendee = attendee
        self.draw_address()

        # find price for attendee
        course = attendee.related_course
        price = None
        for a2c_rel in course.get_attendee_types().all():
            if attendee.__class__.identifier == a2c_rel.attendee:
                price = a2c_rel.price
        self.add_item(
            [
                'Kursgebühr für "{}"'.format(course.get_parent().specific.title_de),
                'vom {} bis zum {}'.format(course.start.strftime('%d.%m.%Y'), course.end.strftime('%d.%m.%Y')),
                'Teilnehmer: {} {}'.format(attendee.first_name, attendee.last_name)
            ],
            Decimal(1),
            Decimal(price)
        )

        self.draw_invoice_number('{}{}'.format(
            get_next_invoice_number(),
            '4752140006'
        ))


    def draw_address(self):
        address = []
        address.append(self.attendee.invoice_company)
#        address.append(self.attendee.full_name)
        for field in [
                self.attendee.invoice_additional_line_1,
                self.attendee.invoice_additional_line_2,
                self.attendee.invoice_additional_line_3
        ]:
            if field:
                address.append(field)
        address.append("{} {}".format(
            self.attendee.invoice_street, 
            self.attendee.invoice_street_number
        ))
        address.append("{} {}".format(
            self.attendee.invoice_town_zip, 
            self.attendee.invoice_street_number
        ))
        if self.attendee.invoice_country:
            address.append(self.attendee.invoice_country)
        
        super().draw_address(address)

        
    def write2file(self):
        self.compute_total( vat = Decimal(0))
        self.filename = os.path.join(
            settings.INVOICE_ROOT,
            "{}__{}-{}.pdf".format(
                datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S:%f'),
                self.attendee.last_name,
                self.attendee.first_name
            )
        )
        
        super().write2file(self.filename)

        return self.filename



def test_course_invoice( filename = 'test.pdf' ):
    from userdata.models import StaffUser
    from .models import SskExternalAttendee
    
    foo = RUBIONCourseInvoice(
        SskExternalAttendee.objects.first(),
        StaffUser.objects.first()
    )

    foo.write2file(filename)

    

class CourseNamePlate(RUBIONPDF):
    left = 85
    top = 0
    font_size_name = 48
    font_size_affil = 36

    def __init__(self, attendee_pks, *args, **kwargs):
        from .models import CourseAttendee
        super().__init__(pagesize = landscape(A4), *args, **kwargs)
        self.width, self.height = landscape(A4)

        # try to position the name/affil block in the vertical center of the lower part of the page.
        # total height is font size of name + 1.2 font size of affil (1.2 is the line height)
        #
        # Positioning starts from self.height/2
        self.top = (self.height/2 - (self.font_size_name + 1.2*self.font_size_affil))/2+self.font_size_name
        self.left = 1.5*self.font_size_name
        attendees = CourseAttendee.objects.filter(pk__in = attendee_pks)
        for attendee in attendees:
            if attendee.academic_title:
                name = '{} '.format(attendee.get_academic_title_display())
            else:
                name = ''
            name += '{} {}'.format(attendee.first_name, attendee.last_name)
            self.pdf.setStrokeColor(self.RUBGRAY)
            self.font_scala(self.font_size_name, color = self.RUBBLUE)
            self.pdf.drawString(self.left, self.height/2 - self.top, name)
            self.add_affiliation(attendee)
            self.pdf.showPage()

    def add_affiliation(self, attendee):
        attendee = attendee.specific
        self.font_scala(self.font_size_affil)
        
        # use duck-typing for the second line
        
        if hasattr(attendee, 'invoice_company'):
            affil = attendee.invoice_company
        elif hasattr(attendee, 'institute'):
            affil = attendee.institute
        elif hasattr(attendee, 'student_course'):
            affil = 'Student/in '+attendee.student_course
        self.pdf.drawString(self.left, self.height/2 - self.top - 1.2*self.font_size_affil, affil)

        
def test_name_plates(filename = 'test.pdf'):
    foo = CourseNamePlate([2,4,5])
    with open(filename, 'wb') as out:
        out.write(foo.for_content_file()) 

class CourseCertificate(RUBIONPDF):
    template_file = 'templates/courses/pdf/Musterbescheinigung-Fachkunde.pdf'

    xcenter = 308.8225
    name_pos = 449.794
    born_pos = 416.426
    living_pos = 400.826
    coursedate_pos = 296.426
    signdate_pos = 190.683
    
    def __init__(self, attendee_pks, *args, **kwargs):
        from .models import CourseAttendee
        self.width, self.height = A4
        locale.setlocale(locale.LC_ALL, 'de_DE')
        template = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            self.template_file
        )
        super().__init__(templatefile = template, pagesize = A4, *args, **kwargs)
        attendees = CourseAttendee.objects.filter(pk__in = attendee_pks)
        for attendee in attendees:
            attendee = attendee.specific
            self.font_scala(12, weight = self.WEIGHT_BOLD)
            self.pdf.drawCentredString(
                self.xcenter, self.name_pos,
                '{} {}'.format(attendee.first_name, attendee.last_name)
            )
            self.font_scala(12, figures = self.FIGURES_MZ)
            if attendee.country_of_birth != '':
                pob = '{} ({})'.format(attendee.place_of_birth, attendee.country_of_birth)
            else:
                pob = '{}'.format(attendee.place_of_birth)
            self.pdf.drawCentredString(
                self.xcenter, self.born_pos,
                'geboren am {date} in {place}'.format(
                    date = attendee.date_of_birth.strftime('%d. %m. %Y'),
                    place = pob
                )
            )
            if attendee.country:
                place = '{} ({})'.format(attendee.town, attendee.country)
            else:
                place = attendee.town
            self.pdf.drawCentredString(
                self.xcenter, self.living_pos,
                'wohnhaft in {place}'.format(
                    place = place
                )
            )
            if attendee.related_course.end.month == attendee.related_course.start.month:
                start = attendee.related_course.start.strftime('%d.')
            else:
                start = attendee.related_course.start.strftime('%d. %B')
            self.pdf.drawCentredString(
                self.xcenter, self.coursedate_pos,
                'vom {start} – {end}'.format(
                    start = start,
                    end = attendee.related_course.end.strftime('%d. %B %Y')
                )
            )

            today = datetime.date.today()
            self.pdf.drawString(
                71.648, self.signdate_pos,
                'Bochum, {date}'.format(
                    date = today.strftime('%d. %B %Y')
                )
            )
            
            
            self.pdf.showPage()

    def for_content_file(self, endpage = True):
        if endpage:
            self.pdf.showPage()
        self.pdf.save()
        tpl_page = self.template_pdf.getPage(0)
        new_pdf = PdfFileReader(self.buffer)
        new_buf = BytesIO()
        output = PdfFileWriter()
        for n_page in range(new_pdf.getNumPages()-1):
            page = new_pdf.getPage(n_page)
            page.mergePage(tpl_page)
            output.addPage(page)
        output.write(new_buf)
        return new_buf.getvalue()

    
