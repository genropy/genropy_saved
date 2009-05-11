from gnr.core.gnrstructures import GnrStructData
from reportlab.pdfgen import canvas 
from reportlab import lib as pdflib
from reportlab.lib.units import inch 
from reportlab.lib.colors import pink, black, red, blue, green 


class GnrPdfElem(object):
    def __init__(self,obj,tag,tagType):
        self.obj=obj
        self.tag=tag
        self.tagType=tagType
        
    def __call__(self,*args,**kwargs):
        if not 'tagType' in kwargs:
            kwargs['tagType']=self.tagType
        child=self.obj.child(self.tag,*args, **kwargs)
        return child

class GnrPdfSrc(GnrStructData):
                   
    pdfDrawNS=['line','grid','bezier','arc','rect','ellipse','wedge','circle','roundRect',
               'drawString','drawRightString','drawCentredString']
    pdfStatusNS=['setFillColorCMYK','setStrokeColorCMYK',
                 'setFillColorRGB','setStrokeColorRGB',
                 'setFillGray','setStrokeGray',
                 'setFillColor','setStrokeColor',
                 'setFont','setLineWidth','setLineCap','setLineJoin',
                 'setMiterLimit','setDash']
    gnrDrawNS=['string']
    gnrStatusNS=['closePage','page']
    pdfNameSpace=dict([(name.lower(),(name,'RD')) for name in pdfDrawNS])
    pdfNameSpace.update(dict([(name.lower(),(name,'RS')) for name in pdfStatusNS]))
    pdfNameSpace.update(dict([(name.lower(),(name,'GD')) for name in gnrDrawNS]))
    pdfNameSpace.update(dict([(name.lower(),(name,'GS')) for name in gnrStatusNS]))

    def __getattr__(self,fname):
        fnamelower=fname.lower()
        if fnamelower in self.pdfNameSpace:
            return GnrPdfElem(self,*self.pdfNameSpace[fnamelower])
        elif hasattr(self,fname) :
            return getattr(self,fname)
        else:
            raise AttributeError("object has no attribute '%s'" % fname)
            
class GnrPdf(object):
    def __init__(self,filename='test.pdf',pagesize='A4',unit='inch'):
        if isinstance(pagesize,basestring):
            pagesize=getattr(pdflib.pagesizes, pagesize,pdflib.pagesizes.A4)
        if isinstance(unit,basestring):
            unit=getattr(pdflib.units, unit, pdflib.units.inch)
        self.canvas=canvas.Canvas(filename,pagesize) 
        self.root=GnrPdfSrc.makeRoot()
        self.unit=unit
        self._pendingDraw=False
        
    def draw(self):
        self.page()
        self.root.walk(self._drawNode)
        
    def _drawNode(self,node):
        self._pageInProgress=True
        attr=dict(node.attr)
        tag=attr.pop('tag')
        tagType=attr.pop('tagType','RS')
        h=getattr(self,tag,None)
        if not h:
            h=getattr(self.canvas,tag,None)
        if h:
            h(**attr)
            if tagType.endswith('D') :
                self._pendingDraw=True

    def page(self,x=0,y=0):
        if self._pendingDraw:
            self.canvas.showPage()
            self._pendingDraw=False
        self.canvas.translate(x*self.unit,y*self.unit)

    def save(self):
        self.canvas.save()
        
if __name__ =='__main__':
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer 
    from reportlab.lib.styles import getSampleStyleSheet 
    from reportlab.rl_config import defaultPageSize 
    from reportlab.lib.units import inch 
    PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0] 
    styles = getSampleStyleSheet() 
    Title = "Hello world" 
    pageinfo = "platypus example" 
    
    def myFirstPage(canvas, doc): 
        canvas.saveState() 
        canvas.setFont('Times-Bold',16) 
        canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-108, Title) 
        canvas.setFont('Times-Roman',9) 
        canvas.drawString(inch, 0.75 * inch, "First Page / %s" % pageinfo) 
        canvas.restoreState() 
        
    def myLaterPages(canvas, doc): 
        canvas.saveState() 
        canvas.setFont('Times-Roman',9) 
        canvas.drawString(inch, 0.75 * inch, "Page %d %s" % (doc.page, pageinfo)) 
        canvas.restoreState()
         
    def go(): 
        doc = SimpleDocTemplate("phello.pdf") 
        Story = [Spacer(1,2*inch)] 
        style = styles["Normal"] 
        for i in range(100): 
            bogustext = ("This is Paragraph number %s.  " % i) *20 
            p = Paragraph(bogustext, style) 
            Story.append(p) 
            Story.append(Spacer(1,0.2*inch)) 
        doc.build(Story, onFirstPage=myFirstPage, onLaterPages=myLaterPages) 

    go()