#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
import time

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer 
from reportlab.platypus.tables import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet 
from reportlab.lib.units import cm 
from reportlab.pdfgen import canvas 
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4


class GnrCustomWebPage(object):
    py_requires = 'public:Public'
    
    def main(self, root, **kwargs):
        fb = root.formbuilder(cols=1)
        fb.simpletextarea(value="^pdf.text", width='60em', height='20ex', default_value='Pippo')
        fb.checkbox(label='download', value='^pdf.down')
        fb.button('PDF Canvas', fire_testCanvas='^pdf.do')
        fb.button('PDF Platypus', fire_testPlatypus='^pdf.do')
        fb.button('test thermo', fire_testPlatypus='^test.do')

        fb.dataRpc('dummy', 'testThermo', pdfmode='^test.do')
        
        fb.dataRpc('pdf.filename', 'app.pdfmaker', txt='=pdf.text', pdfmode='^pdf.do', _POST=True)
        fb.dataController("genro.viewPDF(filename, forcedownload);", filename='^pdf.filename', forcedownload='=pdf.down', _if='filename')
        self.thermoDialog(root, thermoId='build_pdf', title='Generazione PDF', thermolines=2, fired='^pdf.do')

    def pdf_testCanvas(self, fpath, txt, **kwargs):
        c = canvas.Canvas(fpath) 
        c.drawString(100,100, txt) 
        c.showPage() 
        c.save() 

    def rpc_testThermo(self, **kwargs):
        self.app.setThermo('build_pdf', 0, 'Preparo elaborazione' , 100, command='init')
        for x in range(100):
            self.app.setThermo('build_pdf', x, str(x))
        self.app.setThermo('build_pdf', command='end')

        
    def pdf_testPlatypus(self, fpath, txt, pkg=None, tbl=None, **kwargs):
        self.app.setThermo('build_pdf', 0, 'Preparo elaborazione' , 10, command='init')
        PAGE_HEIGHT=A4[1]; PAGE_WIDTH=A4[0] 
        styles = getSampleStyleSheet() 
        
        def myLaterPages(canvas, doc): 
            canvas.saveState() 
            canvas.setFont('Times-Roman',9) 
            canvas.drawString(cm, 2 * cm, "Page %d" % (doc.page)) 
            canvas.restoreState() 

        doc = SimpleDocTemplate(fpath) 
        Story = [Spacer(1, 4 * cm)] 
        style = styles["Normal"]
        colWidths = (3*cm, 1*cm, 1*cm, 4*cm, 5*cm)
        tstyle = TableStyle([('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                             ('GRID', (0,0), (-1,-1), 0.25, colors.black),
                             #('FONTSIZE', (0,0), (-1,-1), 7)
                             ])

        packages = [o for p,o in self.db.packages.items() if not pkg or p==pkg]
        self.app.setThermo('build_pdf', maximum_1=len(packages)+1)

        for i, pobj in enumerate(packages):
            tables = [o for t,o in pobj.tables.items() if not tbl or t==tbl]
            self.app.setThermo('build_pdf', i, pobj.name, progress_2=0, message_2='', maximum_2=len(tables))
            for k,tobj in enumerate(tables):
                if self.app.setThermo('build_pdf', progress_2=k, message_2=tobj.fullname) == 'stop':
                    self.app.setThermo('build_pdf', command='stopped')
                    return
                p = Paragraph(tobj.fullname, style)
                Story.append(p) 
                Story.append(Spacer(1, 1 * cm)) 
                data = [['Name', 'Type', 'Size', 'Name Long', 'Relations']]
                for cobj in tobj.columns.values():
                    rel = ''
                    if cobj.relatedColumn():
                        rel = cobj.relatedColumn().fullname
                    elif cobj.name == tobj.pkey and tobj.relatingColumns:
                        rel = Paragraph('<br/>'.join(tobj.relatingColumns), style)
                    data.append([cobj.name, 
                            cobj.attributes.get('dtype',''), 
                            cobj.attributes.get('size',''), 
                            self._(cobj.attributes.get('name_long','')),
                            rel])
                                
                t=Table(data, colWidths=colWidths)
                t.setStyle(tstyle) 
                Story.append(t) 
                Story.append(Spacer(1, 1 * cm)) 
        self.app.setThermo('build_pdf', i+1, "Impaginazione PDF", progress_2=0, message_2='', maximum_2=0)
        doc.build(Story, onFirstPage=myLaterPages, onLaterPages=myLaterPages) 
        self.app.setThermo('build_pdf', command='end')


