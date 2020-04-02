# -*- coding: utf-8 -*-

"""Esempio"""

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

from gnr.pdf.gnrrml import GnrPdf


PAGE_HEIGHT = defaultPageSize[1]
PAGE_WIDTH = defaultPageSize[0]
Title0 = "Esempio"


class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull, gnrcomponents/source_viewer/source_viewer:SourceViewer"


    def test_1_Table(self, pane):
        bc = pane.borderContainer(height='700px')
        bc.contentPane(region='top', height='100px').simpleTextArea(value='^.mydata', height='98%', width='98%', editor=False)  # textbox('^.text')
        bc.contentPane(region='center').iframe(height='98%', width='98%', rpcCall='createRmlPdf', 
                                                rpc_rml_method='test1')  # , rpc_mydata='^.mydata')


    def rml_test1(self, document=None, **kwargs):

        template=document.template(pageSize='letter', leftMargin=72, showBoundary=1)
        pt=template.pageTemplate(id='main', pageSize='letter portrait')
        pg =pt.pageGraphics()
        pg.setFont(name='Helvetica-BoldOblique', size=18)
        pg.string('RML2PDF Test Suite',x=523, y=800,align='r') 
        ta=pg.textAnnotation()
        ta.param(name='Rect',content='0,0,1,1')
        ta.param(name='F',content='3')
        ta.param(name='escape',content='6')
        ta._content(content='X::PDF PX(S) MT(PINK)')
        pt.frame(id='first',x1='1in',y1='1in',width='6.26in',height='9.69in')
        ss = document.stylesheet()

        ss.initialize().alias(id='style.normal',value='style.Normal')
        ss.paraStyle(name='h1', fontName="Helvetica-BoldOblique", fontSize="32", leading="36")
        ss.paraStyle(name="normal", fontName="Helvetica", fontSize="10", leading="12")
        ss.paraStyle(name="spaced", fontName="Helvetica", fontSize="10", leading="12",
            spaceBefore="12", spaceAfter="12")
        story=document.story()
        para1=story.para(style='normal')
        para1._content(content='Hello World.  This is a normal paragraph. Blah')
        para1.font(color="red")._content(content='IPO') 
        para1._content(content="""blah blah blah blah growth forecast blah
    blah blah forecast blah.Blah blah blah blah blah blah blah blah blah blah blah profit blah blah blah blah blah
    blah blah blah blah blah IPO.Blah blah blah blah blah blah blah reengineering blah growth blah blah blah
    proactive direction strategic blah blah blah forward-thinking blah.Blah blah doubletalk blah blah blah blah
    blah profit blah blah growth blah blah blah blah blah profit.Blah blah blah blah venture capital blah blah blah
    blah blah forward-thinking blah. Here are some common characters
            """)
        story.para(style='spaced', content=u"""This is spaced.  There should be 12 points before and after.""")
        # return pdf # pdf.toPdf(filename)        

    
    @public_method
    def createRmlPdf(self, rml_method = None , **kwargs):

        pdf = GnrPdf()
        document=pdf.document()

        handler = getattr(self, 'rml_{rml_method}'.format(rml_method=rml_method))
        handler(document=pdf.document, **kwargs)
        self.response.add_header("Content-Disposition", str("inline; filename=%s" % 'test_pdf.pdf'))
        self.response.content_type = 'application/pdf'
        pdf.toRml('c:\\sviluppo\\temp.rml')
        return pdf.toPdf()

