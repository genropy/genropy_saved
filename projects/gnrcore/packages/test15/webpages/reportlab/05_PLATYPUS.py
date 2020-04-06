# -*- coding: utf-8 -*-

"""Chapter 5 - PLATYPUS - Page Layout and Typography Using Scripts"""

"""Platypus stands for "Page Layout and Typography Using Scripts". It is a high level page layout library which
lets you programmatically create complex documents with a minimum of effort.

The design of Platypus seeks to separate "high level" layout decisions from the document content as much as
possible. Thus, for example, paragraphs are constructed using paragraph styles and pages are constructed using
page templates with the intention that hundreds of documents with thousands of pages can be reformatted
to different style specifications with the modifications of a few lines in a single shared file which contains the
paragraph styles and page layout specifications.
"""

# First we import some constructors, some paragraph styles and other conveniences from other modules.
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch

from gnr.core.gnrdecorator import public_method
from io import BytesIO

PAGE_HEIGHT=defaultPageSize[1]
PAGE_WIDTH=defaultPageSize[0]
styles = getSampleStyleSheet()

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull, gnrcomponents/source_viewer/source_viewer:SourceViewer"


    def test_1_Table(self, pane):
        bc = pane.borderContainer(height='700px')
        bc.contentPane(region='top', height='100px').simpleTextArea(value='^.mydata', height='98%', width='98%', editor=False)  # textbox('^.text')
        bc.contentPane(region='center').iframe(height='98%', width='98%', rpcCall='createPlatypusPdf', 
                                                rpc_rlab_method='platypus')  # , rpc_mydata='^.mydata')


    def myFirstPage(self, canvas, doc):
        """We define the fixed features of the first page of the document with the function below."""
        Title = "Hello world"
        pageinfo = "platypus example"

        canvas.saveState()
        canvas.setFont('Times-Bold', 16)
        canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-108, Title)
        canvas.setFont('Times-Roman',9)
        canvas.drawString(inch, 0.75 * inch, "First Page / %s" % pageinfo)
        canvas.restoreState()


    def myLaterPages(self, canvas, doc):
        """Since we want pages after the first to look different from the first we define an alternate layout for the fixed
           features of the other pages. Note that the two functions use the pdfgen level canvas operations to
           paint the annotations for the pages.
        """
        pageinfo = "platypus example"
        canvas.saveState()
        canvas.setFont('Times-Roman',9)
        canvas.drawString(inch, 0.75 * inch, "Page %d %s" % (doc.page, pageinfo))
        canvas.restoreState()

    def rlab_platypus(self, **kwargs):
        self.Story = [Spacer(1,2*inch)]
        style = styles["Normal"]
        for i in range(10):
            bogustext = ("This is Paragraph number %s. " % i) *20
            p = Paragraph(bogustext, style)
            self.Story.append(p)
            self.Story.append(Spacer(1,0.2*inch))


    @public_method
    def createPlatypusPdf(self, rlab_method = None , **kwargs):
        pdf = BytesIO()
        self.mydoc = SimpleDocTemplate(pdf)

        handler = getattr(self, 'rlab_{rlab_method}'.format(rlab_method=rlab_method))
        handler(**kwargs)

        self.mydoc.build(self.Story, onFirstPage=self.myFirstPage, onLaterPages=self.myLaterPages)
        pdf.seek(0)
        self.response.add_header("Content-Disposition", str("inline; filename=%s" % 'test_pdf.pdf'))
        self.response.content_type = 'application/pdf'
        return pdf.read()
