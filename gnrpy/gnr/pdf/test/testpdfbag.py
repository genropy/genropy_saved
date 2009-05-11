from gnr.core.gnrbag import Bag
from reportlab.pdfgen import canvas 
from reportlab.lib.pagesizes import letter, A4 
from reportlab.lib.units import inch 
from reportlab.lib.colors import pink, black, red, blue, green 

class GnrCanvas(canvas.Canvas):
    def drawFromBag(self,bag):
        bag.walk(self._drawFromBag)
        
    def _drawFromBag(self,node):
        attr=dict(node.attr)
        tag=attr.pop('tag')
        h=getattr(self,tag)
        if h:
            h(**attr)
            
class PdfTester(object):
    def __init__(self,filename='test.pdf',pagesize=A4):
        self.canvas=GnrCanvas(filename,pagesize) 
    
    def save(self):
        self.canvas.save() 
    def showPage(self):
        self.canvas.showPage() 
    def test1(self):
        b=Bag()
        for k in range (10):
            b.child('drawString',x=k*10,y=k*10,text="Hello World from bag _ %s" % str(k))
        self.canvas.drawFromBag(b)
        self.showPage() 

    def test2(self):
        c=self.canvas
        for x in range (10):
            c.drawString(x*10,x*5,"Hello World a _ %s" % str(x)) 
        c.showPage() 
        for x in range (10):
            c.drawString(x*5,x*10,"Hello World b _ %s" % str(x)) 
        c.showPage() 
 
    def test3(self): 
        c=self.canvas
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
        c.drawString(0.3*inch, -inch, "Hello World") 
        c.showPage() 
    def test4(self): 
        
        c = c=self.canvas 
        c.setStrokeColor(pink) 
        c.grid([inch, 2*inch, 3*inch, 4*inch], [0.5*inch, inch, 1.5*inch, 2*inch, 2.5*inch]) 
        c.setStrokeColor(black) 
        c.setFont("Times-Roman", 20) 
        c.drawString(0,0, "(0,0) the Origin") 
        c.drawString(2.5*inch, inch, "(2.5,1) in inches") 
        c.drawString(4*inch, 2.5*inch, "(4, 2.5)") 
        c.setFillColor(red) 
        c.rect(0,2*inch,0.2*inch,0.3*inch, fill=1) 
        c.setFillColor(green) 
        c.circle(4.5*inch, 0.4*inch, 0.2*inch, fill=1) 

if __name__ =='__main__':
    tester = PdfTester('testbag.pdf') 
    tester.test1()
    tester.save() 
    