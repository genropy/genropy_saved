from gnr.pdf.gnrrml import GnrRml

class Abba(object):
    def pdfa(self,filename):
        pdf = GnrRml(filename=filename)
        document=pdf.document()
        template=document.template(pageSize='letter', leftMargin=72, showBoundary=1)
        pt=template.pageTemplate(id='main', pageSize='letter portrait')
        pg =pt.pageGraphics()
        pg.setFont(_name='Helvetica-BoldOblique', size=18)
        pg.string('RML2PDF Test Suite',x=523, y=800,align='r') 
        ta=pg.textAnnotation()
        ta.param(_name='Rect',content='0,0,1,1')
        ta.param(_name='F',content='3')
        ta.param(_name='escape',content='6')
        ta._content(content='X::PDF PX(S) MT(PINK)')
        pt.frame(id='first',x1='1in',y1='1in',width='6.26in',height='9.69in')
        ss = document.stylesheet()

        ss.initialize().alias(id='style.normal',value='style.Normal')
        ss.paraStyle(_name='h1', fontName="Helvetica-BoldOblique", fontSize="32", leading="36")
        ss.paraStyle(_name="normal", fontName="Helvetica", fontSize="10", leading="12")
        ss.paraStyle(_name="spaced", fontName="Helvetica", fontSize="10", leading="12",
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
        pdf.toPdf(filename)