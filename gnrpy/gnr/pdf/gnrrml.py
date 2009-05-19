#-*- coding: UTF-8 -*-

#--------------------------------------------------------------------------
# package       : GenroPy web - see LICENSE for details
# module gnrsqlclass : Genro Web structures implementation
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Francesco Cavazzana
#                 Saverio Porcari, Francesco Porcari
#--------------------------------------------------------------------------

#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

#import weakref
from gnr.core.gnrbag import Bag
from gnr.core.gnrstructures import GnrStructData
from gnr.core import gnrstring
from lxml import etree
from z3c.rml import document as pdfdoc
import cStringIO
import os

class GnrRmlSrcError(Exception):
    pass

class GnrRmlElem(object):
    def __init__(self,obj,tag):
        self.obj=obj
        self.tag=tag
    
    def __call__(self,*args,**kwargs):
        child=self.obj.child(self.tag,*args, **kwargs)
        return child
    

class GnrRmlSrc(GnrStructData):

    rmlNS = ['addMapping', 'alias', 'bar', 'barChart', 'barChart3D', 'barCode', 'barCodeFlowable', 'bars', 
     'blockAlignment', 'blockBackground', 'blockBottomPadding', 'blockColBackground', 'blockFont', 'blockLeading', 
     'blockLeftPadding', 'blockRightPadding', 'blockRowBackground', 'blockSpan', 'blockTable', 'blockTableStyle', 
     'blockTextColor', 'blockTopPadding', 'blockValign', 'bookmark', 'bulkData', 'buttonField', 'categoryAxis', 
     'circle', 'color', 'condPageBreak', 'curves', 'curvesto', 'curveto', 'document', 'drawAlignedString', 
     'drawCenteredString', 'drawCentredString', 'drawRightString', 'drawString', 'ellipse', 'fill', 'fixedSize', 
     'frame', 'font', 'grid', 'h1', 'h2', 'h3', 'hr', 'illustration', 'image', 'imageAndFlowables', 'initialize', 
     'indent', 'keepInFrame', 'keepTogether', 'label', 'labels', 'line', 'lineLabels', 'lineMode', 'linePlot', 
     'lineStyle', 'lines', 'link', 'moveto', 'name', 'nextFrame', 'option', 'outlineAdd', 'pageGraphics', 
     'pageInfo', 'pageTemplate', 'pageNumber', 'para', 'paraStyle', 'param', 'path', 'pieChart', 'pieChart3D', 
     'place', 'plugInFlowable', 'pointer', 'pre', 'rect', 'registerCidFont', 'registerFont', 'registerTTFont', 
     'registerType1Face', 'rotate', 'scale', 'selectField', 'series', 'setFont', 'setNextFrame', 
     'setNextTemplate', 'skew', 'slice', 'slices', 'spacer', 'spiderChart', 'spoke', 'spokeLabels', 'spokes', 
     'stylesheet','story', 'strand', 'strandLabels', 'strands', 'stroke', 'td', 'template', 'text', 
     'textAnnotation', 'textField', 'title', 'transform', 'translate', 'valueAxis', 'xValueAxis', 'xpre', 
     'yValueAxis']

    gnrNS=['string','_content']
           
    genroNameSpace=dict([(name.lower(),name) for name in rmlNS])
    genroNameSpace.update(dict([(name.lower(),name) for name in gnrNS]))
    
    def __getattr__(self,fname):
        fnamelower=fname.lower()
        if (fname != fnamelower) and hasattr(self,fnamelower) :
            return getattr(self,fnamelower)
        elif fnamelower in self.genroNameSpace:
            return GnrRmlElem(self,'%s' % (self.genroNameSpace[fnamelower]))
        else:
            raise AttributeError("object has no attribute '%s'" % fname)
    
    def string(self,content=None, align='L', **kwargs):
        if align.lower() in ('r','right'):
            self.drawRightString(content=content, **kwargs) 
        elif align.lower() in ('c','center'):
            self.drawCenteredString(content=content, **kwargs) 
        else:
            self.drawString(content=content, **kwargs)
    
    def toRml(self,filename=None,encoding='UTF-8'):
        return self.toXml(filename=filename, encoding=encoding,typeattrs=False, autocreate=True,
                omitUnknownTypes=True, omitRoot=True, forcedTagAttr='tag',addBagTypeAttr=False)

    def _content(self,content):
        self.child('__flatten__',content=content)
    
    def child(self,*args,**kwargs):
        if 'name' in kwargs:
            kwargs['_name'] = kwargs.pop('name')
        return super(GnrRmlSrc, self).child(*args,**kwargs)

class GnrRml(object):

    def __init__(self, filename='', invariant=1, **kwargs):
        self.root = GnrRmlSrc.makeRoot()
        self.document = self.root.document(filename=filename, invariant=invariant, **kwargs)
    

    def toRml(self,filename=None):
        return self.root.toRml(filename=filename)
        
    def toPdf(self,filename=None):
        if filename:
            self.root.setAttr('#0',filename=os.path.basename(filename))
            output = open(filename,'wb')
        else:
            output = cStringIO.StringIO()
        root = etree.fromstring(self.toRml())
        pdf = pdfdoc.Document(root)
        pdf.process(output)
        if not filename:
            output.seek(0)
            return output.read()
        output.close()

if __name__ =='__main__':
    pdf = GnrRml(filename='a.pdf')
    document=pdf.document
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
    print pdf.toPdf('/Users/michele/a.pdf')
    #print pdf.toRml('/Users/michele/a.rml')