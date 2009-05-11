from gnr.pdf.gnrpdf import GnrPdf
from reportlab.lib.units import inch 


def testPage(root):
    for x in range(2):
        page = root.page(x=1*inch, y=1*inch)
    
        page.setFont("Helvetica", 9) 

    
        pane1 = page.pane(x_=1, y_=15)
        pane2 = page.pane(x_=9, y_=9)
        pane2.setFont("Helvetica", 12) 
    
        pane1.rect(x=0, y=0, width_='10', height_='5')
    
        pane3 = pane1.pane(x_=2, y_=2)
        pane3.rect(x=0, y=0, width_='7', height_='2')
    
        pane1.setFillGray(gray=0.4) 

        pane1.drawString(x_=1, y_=4, text="Hello World") 



        pane2.drawString(x_=1, y_=4, text="Hello World") 
    
    #
    #textobject = pane2.textObject(x_=1, y_=3) 
    ##textobject = canvas.beginText() 
    ##textobject.setTextOrigin(inch, 2.5*inch)
    #textobject.setFont("Helvetica-Oblique", 14) 
    #for line in lyrics: 
    #    textobject.textLine(line) 
    #textobject.setFillGray(0.4) 
    #textobject.textLines(''' 
    #With many apologies to the Beach Boys 
    #and anyone else who finds this objectionable 
    #''') 
    ##canvas.drawText(textobject) 
    #
    
    
    
if __name__ == '__main__':
    pdf = GnrPdf('/testsuite.pdf', unit='cm') 
    root = pdf.root
    testPage(root)
    pdf.draw()
    pdf.save()
    pdf.toXml('/testsuite.xml')
    f = open('/testsuite.txt', 'w')
    f.write('\n'.join(pdf._log))
    f.close()