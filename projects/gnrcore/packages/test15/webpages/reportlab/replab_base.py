# -*- coding: utf-8 -*-
# 
"""replab_base"""

from builtins import object
from reportlab.pdfgen import canvas
from gnr.core.gnrdecorator import public_method
from io import BytesIO


class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"

    @public_method
    def createTempPdf(self, rlab_method = None , **kwargs):
        pdf = BytesIO()
        self.canvas = canvas.Canvas(pdf)
        handler = getattr(self, 'rlab_{rlab_method}'.format(rlab_method=rlab_method))
        handler(**kwargs)
        self.canvas.showPage()
        self.canvas.save()
        pdf.seek(0)
        self.response.add_header("Content-Disposition", str("inline; filename=%s" % 'test_pdf.pdf'))
        self.response.content_type = 'application/pdf'
        return pdf.read()


    def test_1_hello(self, pane):
        bc = pane.borderContainer(height='500px')
        bc.contentPane(region='top', height='100px').textbox('^.text')
        bc.contentPane(region='center').iframe(height='100%', width='100%', rpcCall='createTempPdf', 
                                                rpc_rlab_method='hello', rpc_mytext='^.text')

        
    def rlab_hello(self, mytext=None, **kwargs):
        mytext = mytext or 'Hello world'
        self.canvas.drawString(100,100, mytext)

    
    def test_2_rect(self, pane):
        bc = pane.borderContainer(height='500px')
        bc.contentPane(region='top', height='100px').textbox('^.text')
        bc.contentPane(region='center').iframe(height='100%', width='100%', rpcCall='createTempPdf', 
                                                rpc_rlab_method='rect', rpc_mytext='^.text')

        
    def rlab_rect(self, mytext=None, **kwargs):
        mytext = mytext or 'rectangle!'
        from reportlab.lib.units import inch
        c = self.canvas
        # move the origin up and to the left
        c.translate(inch,inch)
        # define a large font
        c.setFont("Helvetica", 14)
        # choose some colors
        c.setStrokeColorRGB(0.2,0.5,0.3)
        c.setFillColorRGB(1,0,1)
        # draw some lines
        c.line(0,0,0,1.7*inch)
        c.line(0,0,1*inch,0)
        # draw a rectangle
        c.rect(0.2*inch,0.2*inch,1*inch,1.5*inch, fill=1)
        # make text go straight up
        c.rotate(90)
        # change color
        c.setFillColorRGB(0,0,0.77)
        # say hello (note after rotate the y coord needs to be negative!)
        c.drawString(0.3*inch, -inch, mytext)


    

    #@public_method
    #def createTempPdf_file(self, testo=None, **kwargs):
    #    pdfSn = self.site.storageNode('temp:test_rlab.pdf')
    #    c = canvas.Canvas(pdfSn.internal_path)
    #    self.hello(c, testo=testo)
    #    c.showPage()
    #    c.save()
    #    with pdfSn.open() as pdf:
    #        self.response.add_header("Content-Disposition", str("inline; filename=%s" % 'test_rlab.pdf'))
    #        self.response.content_type = 'application/pdf'
    #        return pdf.read()



    

