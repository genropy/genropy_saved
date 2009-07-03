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
from gnr.core.gnrbag import Bag,BagNode
from gnr.core.gnrstructures import GnrStructData
from gnr.core import gnrstring
from gnr.core.gnrsys import expandpath
import cStringIO
import os
from gnr.core.gnrlang import optArgs

class GnrHtmlSrcError(Exception):
    pass

class GnrHtmlElem(object):
    def __init__(self,obj,tag):
        self.obj=obj
        self.tag=tag
    
    def __call__(self,*args,**kwargs):
        child=self.obj.child(self.tag,*args, **kwargs)
        return child
    

class GnrHtmlSrc(GnrStructData):

    htmlNS=['a', 'abbr', 'acronym', 'address', 'area', 'b', 'base', 'bdo', 'big', 'blockquote',
                   'body', 'br', 'button', 'caption', 'cite', 'code', 'col', 'colgroup', 'dd', 'del',
                   'div', 'dfn', 'dl', 'dt', 'em', 'fieldset', 'form', 'frame', 'frameset', 
                   'h1', 'h2', 'h3','h4','h5', 'h6', 'head', 'hr', 'html', 'i', 'iframe', 'img', 'input', 
                   'ins', 'kbd', 'label', 'legend', 'li', 'link', 'map', 'meta', 'noframes', 'noscript',
                   'object', 'ol', 'optgroup', 'option', 'p', 'param', 'pre', 'q', 'samp', 
                   'select', 'small', 'span', 'strong', 'style', 'sub', 'sup', 'table', 'tbody', 'td',
                   'textarea', 'tfoot', 'th', 'thead', 'title', 'tr', 'tt', 'ul', 'var']
                   
    gnrNS=['layotu','row','cell']
         
    genroNameSpace=dict([(name.lower(),name) for name in htmlNS])
    genroNameSpace.update(dict([(name.lower(),name) for name in gnrNS]))
    
    def __getattr__(self,fname):
        fnamelower=fname.lower()
        if (fname != fnamelower) and hasattr(self,fnamelower) :
            return getattr(self,fnamelower)
        elif fnamelower in self.genroNameSpace:
            return GnrHtmlElem(self,'%s' % (self.genroNameSpace[fnamelower]))

        else:
            raise AttributeError, fname 
    def toHtml(self):
        result,hasRows= self._toHtmlInner()
        return result
    
    def _toHtmlInner(self):
        result=Bag()
        hasRows=False
        for node in self.nodes:
            label=node.label
            attr=dict(node.attr)
            tag=attr.pop('tag')
            if tag=='row':
                hasRows=True
            value=node.getValue()
            if isinstance(value,GnrHtmlSrc) :
                if len(value)==0:
                    value=''
                else:
                    value,hasInnerRows=value._toHtmlInner()
                    if tag=='cell' and hasInnerRows:
                        tag='container'
            if hasattr(self,'compile_%s' %tag):
                handler = getattr(self,'compile_%s' %tag)
                tag,attr= handler(tag,attr)
            result.addItem(tag,value,attr)
        return result,hasRows
            
        
    def compile_layout(self,tag,attr):
        tag = 'div'
        xclass = 'layout_table'
        if attr.get('class'):
            attr['class'] = '%s %s' %(attr['class'],xclass)
        else:
            attr['class'] = xclass
        return tag,attr
        
    def compile_cell(self,tag,attr):
        tag = 'div'
        xclass = 'layout_cell'
        if attr.get('class'):
            attr['class'] = '%s %s' %(attr['class'],xclass)
        else:
            attr['class'] = xclass
        return tag,attr
    
    def compile_container(self,tag,attr):
        tag = 'div'
        xclass = 'layout_container'
        if attr.get('class'):
            attr['class'] = '%s %s' %(attr['class'],xclass)
        else:
            attr['class'] = xclass
        return tag,attr
    
    def compile_row(self,tag,attr):
        tag = 'div'
        xclass = 'layout_row'
        if attr.get('class'):
            attr['class'] = '%s %s' %(attr['class'],xclass)
        else:
            attr['class'] = xclass
        return tag,attr
    

    
    def __content(self,content):
        self.child('__flatten__',content=content)
        
    def content(self,content):
        if not (isinstance(content, list) or isinstance(content, tuple) ) :
            content=[content]
        for single_content in content:
            if isinstance (single_content,GnrHtmlSrc):
                childattr=dict(single_content.parentNode.attr)
                tag=childattr.pop('tag')
                self.child(tag, content=single_content, **childattr)
            else:
                self.child('__flatten__',content=single_content)

    def child(self,tag,*args, **kwargs):
        width=kwargs.pop('width',None)
        height=kwargs.pop('height',None)
        style=kwargs.pop('style','') 
        
        if width or height:
            
            style_dict = dict([(x.split(':')) for x in style.split(';') if x])
            if width:
                style_dict['width']=width
            if height:
                style_dict['height']=height
            style = ''.join(['%s:%s;' %(k,v) for k,v in style_dict.items()])
        if style:
            kwargs['style'] = style
        return super(GnrHtmlSrc, self).child(tag,*args,**kwargs)
        
    def _tagType(self):
        return self.parentNode.attr['tag']
    tagType=property(_tagType)
    
    def _getRow(self, rowidx):
        if rowidx is None:
            rowidx = len(self)+1
        while len(self)<rowidx:
            r=self.tr()
            while len(r)<self.cols:
                r.td()
        return r
    
    def layout(self,width=0,height=0,**kwargs):
        child = self.child(tag='layout', width=width, height=height,**kwargs)
        child.height = height
        child.width = width
        return child
        
    def row(self,height=0,**kwargs):
        child = self.child(tag='row',**kwargs)
        child.height = height
        return child
        
    def cell(self,content=None,width=0, **kwargs):
        child = self.child(tag='cell',width=width,content=content,height=self.height,**kwargs)
        return child

    #def cellStyle(self, rowidx, colidx, rowspan=None, colspan=None,):

class GnrHtmlPdf(object):
    def __init__(self, filename=None,**kwargs):
        self.root = GnrHtmlSrc.makeRoot()
        
    def toXml(self,filename=None,encoding='UTF-8'):
        return self.root.toXml(filename=filename, encoding=encoding,typeattrs=False, autocreate=True,
                omitUnknownTypes=True, omitRoot=True, forcedTagAttr='tag',addBagTypeAttr=False)
    
    def toHtml(self,filename=None):
        if filename:
            filename=expandpath(filename)
        result=self.root.toHtml()
        return result.toXml(filename=filename,omitRoot=True)
    
    
    def toPdf(self,filename=None):
        """call the pdf webkit generator"""
        pass
def globalCss():
    return """
    .layout_table{
        display:table;
        border-collapse:collapse;
		border-top:1px solid gray;

    }
    .layout_row{
		border-bottom:1px solid gray;
    }
    .layout_cell{
        display:table-cell;
		border-left:1px solid gray;
	    border-right:1px solid gray;
    }
    .layout_container{
		display:table-cell;
	}
    
    """
def test2(body):
    layout = body.layout(width='190mm')
    r1 = layout.row(height='15mm')
    mycell = r1.cell(width='30mm',lbl='name',lbl_class='z1')
    subrow1 = mycell.row(height='3mm')
    subrow1.cell('nome',width='30mm')
    subrow2 = mycell.row(height='12mm')
    subrow2.cell('pippo',width='30mm')
    r1.cell('pluto',width='90mm')
    r3 = layout.row(height='30mm')
    r3.cell('mario',width='95mm')
    r3.cell('ant',width='95mm')
    r4 = layout.row(height='30mm')
    r4.cell(width='130mm')
    r4.cell(width='60mm')

def test1(body):
    layout = body.layout(width='190mm')
    r1 = layout.row(height='15mm')


    r1.cell('pluto',width='30mm',lbl='name',lbl_class='z1')
    r1.cell('paperino',width='30mm',lbl='name',lbl_class='z1')
    r2 = layout.row(height='90mm')
    leftcol = r2.cell(width='80mm',label='Client info',lbl_class='mainlabel')
    rightcol = r2.cell(lable='Job details',lbl_class='mainlabel')
    lr1 = leftcol.row(height='6mm')
    lr1.cell(width='70mm')
    lr1.cell(width='20mm')
    lr2 = leftcol.row(height='6mm')
    r3 = layout.row(height='30mm')
    r3.cell(width='70mm')
    r3.cell(width='80mm')
    r4 = layout.row(height='30mm')
    r4.cell(width='130mm')
    r4.cell(width='139mm')
    
if __name__ =='__main__':
    pdf = GnrHtmlPdf('testbag.pdf') 
    root=pdf.root
    html = root.html()
    head = html.head()
    head.style(content=globalCss())
    body= html.body()
    #test1(body)
    test2(body)
    
    pdf.toHtml('test3.html')
    print body