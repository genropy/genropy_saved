# -*- coding: utf-8 -*-

"""Chapter 7 - Tables and TableStyles"""

"""The Table and LongTable classes derive from the Flowable class and are intended as a simple textual
gridding mechanisms. The longTable class uses a greedy algorithm when calculating column widths and is
intended for long tables where speed counts. Table cells can hold anything which can be converted to a Python
string or Flowables (or lists of Flowables).
"""


from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Image, Paragraph, PageBreak , Flowable
# from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import mm, cm
# from reportlab.lib.styles import getSampleStyleSheet

from gnr.core.gnrdecorator import public_method
from io import BytesIO


PAGE_HEIGHT = defaultPageSize[1]
PAGE_WIDTH = defaultPageSize[0]
Title0 = "Chapter 7 - Tables and TableStyles"


class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull, gnrcomponents/source_viewer/source_viewer:SourceViewer"


    def test_1_Table(self, pane):
        bc = pane.borderContainer(height='700px')
        bc.contentPane(region='top', height='100px').simpleTextArea(value='^.mydata', height='98%', width='98%', editor=False)  # textbox('^.text')
        bc.contentPane(region='center').iframe(height='98%', width='98%', rpcCall='createTablePdfSimpleDoc', 
                                                rpc_rlab_method='table')  # , rpc_mydata='^.mydata')


    def myFirstPage(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Bold', 12)
        canvas.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT-1.25*cm, Title0)
        canvas.setFont('Times-Roman', 10)
        canvas.drawCentredString(PAGE_WIDTH/2, 1*cm, "Pag. %d" % (doc.page))
        canvas.restoreState()


    def myLaterPages(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 10)
        canvas.drawCentredString(PAGE_WIDTH/2, 1*cm, "Pag. %d" % (doc.page))
        canvas.restoreState()


    def rlab_table(self, mydata=None, **kwargs):
        self.elements = []  # gli elementi componenti la pagina

        # inserisco tabella di regioni, con uno stile
        mydata = []  # i dati da mostrare in tabella
        regioni = self.db.table('glbl.regione').query(columns='$sigla,$nome,$zona,$codice_istat', order_by='$sigla').fetch()
        mydata.append(['sigla','nome','zona','codice istat'])
        for regione in regioni:
            mydata.append(list(regione)[:-1])

        t=Table(mydata, spaceAfter=2*cm, spaceBefore=None)
        t.setStyle(TableStyle([
                        ('LINEABOVE', (0,0), (-1,0), 2, colors.green),
                        ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
                        ('LINEBELOW', (0,-1), (-1,-1), 2, colors.green),
                        ('ALIGN', (0,0), (-1,0), 'CENTER'),
                        ('TEXTCOLOR',(0,0),(-1,0), colors.red)
                    ]))

        self.elements.append(t)

        # inserisco tabella di province, più lunga e con stile diverso
        mydata = []  # i dati da mostrare in tabella
        province = self.db.table('glbl.provincia').query(columns='$sigla,$nome,$codice_istat,@regione.nome', order_by='$sigla').fetch()
        mydata.append(['sigla','nome','regione','codice istat'])
        for provincia in province:
            mydata.append(list(provincia)[:-1])

        t=Table(mydata, spaceAfter=2*cm, spaceBefore=None, repeatRows=1)
        t.setStyle(TableStyle([
                        ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                        ('BOX',(0,0),(-1,-1),2,colors.black),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.orange)
                        # ('FONT', (0,0), (-1,-1), 'Helvetica'),
                        # ('FONTSIZE', (0,0), (-1,-1), 10),
                    ]))

        self.elements.append(t)


    @public_method
    def createTablePdfSimpleDoc(self, rlab_method = None , **kwargs):
        pdf = BytesIO()
        self.mydoc = SimpleDocTemplate(pdf, pagesize=A4, topMargin=2*cm) # canvas.Canvas(pdf)
        handler = getattr(self, 'rlab_{rlab_method}'.format(rlab_method=rlab_method))
        handler(**kwargs)
        self.mydoc.build(self.elements, onFirstPage=self.myFirstPage, onLaterPages=self.myLaterPages)
        pdf.seek(0)
        self.response.add_header("Content-Disposition", str("inline; filename=%s" % 'test_pdf.pdf'))
        self.response.content_type = 'application/pdf'
        return pdf.read()
