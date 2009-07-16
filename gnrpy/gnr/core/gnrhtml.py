#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#


from gnr.core.gnrbag import Bag,BagNode
from gnr.core.gnrstring import splitAndStrip
from gnr.core.gnrstructures import GnrStructData
#from gnr.core import gnrstring
from gnr.core.gnrsys import expandpath
from gnr.pdf.wk2pdf import WK2pdf
import sys
#import cStringIO
import os
#from gnr.core.gnrlang import optArgs

class GnrHtmlSrcError(Exception):
    pass

class GnrHtmlElem(object):
    def __init__(self,obj,tag):
        self.obj=obj
        self.tag=tag
    
    def __call__(self,*args,**kwargs):
        if self.tag in GnrHtmlSrc.html_autocontent_NS:
            if args:
                kwargs['content'],args = args[0],args[1:]
        child=self.obj.child(self.tag,*args, **kwargs)
        return child
    

class GnrHtmlSrc(GnrStructData):

    html_base_NS=['a', 'abbr', 'acronym', 'address', 'area',  'base', 'bdo', 'big', 'blockquote',
            'body', 'br', 'button', 'caption', 'cite', 'code', 'col', 'colgroup', 'dd', 'del',
            'dfn', 'dl', 'dt', 'em', 'fieldset', 'form', 'frame', 'frameset', 'head', 'hr', 'html',
            'iframe', 'img', 'input', 'ins', 'kbd', 'label', 'legend',  'link', 'map', 'meta', 'noframes', 
            'noscript', 'object', 'ol', 'optgroup', 'option',  'param',  'samp', 'select',  'style', 
            'sub', 'sup', 'table', 'tbody', 'textarea', 'tfoot', 'th', 'thead', 'title', 'tr', 'tt', 
            'ul', 'var']
                   
    gnrNS=['layout','row','cell']
    
    html_autocontent_NS=['div','h1', 'h2', 'h3','h4','h5', 'h6','span','td','li','b','i','small', 'strong','p','pre', 'q',]
    
    htmlNS = html_base_NS + html_autocontent_NS
    
    genroNameSpace=dict([(name.lower(),name) for name in htmlNS])
    genroNameSpace.update(dict([(name.lower(),name) for name in gnrNS]))
    
    def __getattr__(self,func_name):
        func_namelower=func_name.lower()
        if (func_name != func_namelower) and hasattr(self,func_namelower) :
            return getattr(self,func_namelower)
        elif func_namelower in self.genroNameSpace:
            return GnrHtmlElem(self,'%s' % (self.genroNameSpace[func_namelower]))

        else:
            raise AttributeError, func_name
            
    def style(self,style=''):
        self.root.builder.head.child('style',content=style)
        
    def child(self,tag,*args, **kwargs):
        if('_class' in kwargs):
            kwargs['class']=kwargs.pop('_class')
        if('class_' in kwargs):
            kwargs['class']=kwargs.pop('class_')
        return super(GnrHtmlSrc, self).child(tag,*args,**kwargs)

    def layout(self, name='l1', um='mm',top=0,left=0,bottom=0,right=0,width=0,height=0,
                    border_width=0.3,border_color='grey',border_style='solid', row_border=True, cell_border=True,
                    lbl_height=3, lbl_class='lbl_base',content_class='content_base',
                    **kwargs):
        self.style(".%s_layout{border:%s%s %s %s;position:absolute;}" % (name,border_width,um,border_style,border_color))
                                     
        layout = self.child(tag='layout', **kwargs)
        layout.layout_name = name
        layout.layout_class='%s_layout'% name
        layout.um = um
        layout.top = float(top or 0)
        layout.left = float(left or 0)
        layout.bottom = float(bottom or 0)
        layout.right = float(right or 0)
        layout.width = float(width or 0)
        layout.height = float(height or 0)
        layout.border_width = float(border_width or 0)
        layout.border_color = border_color
        layout.border_style = border_style
        layout.row_border = row_border
        layout.cell_border = cell_border
        layout.lbl_height = float(lbl_height or 0)
        layout.lbl_class = lbl_class
        layout.content_class = content_class
        layout.elastic_rows = []
        layout.nested = self.parentNode.getAttr('tag')=='cell'
        return layout
        
    def row(self, height=0, row_border=None, cell_border=None,lbl_height=None, lbl_class=None,content_class=None, **kwargs):
        assert self.parentNode.getAttr('tag') == 'layout'
        layout = self
        row = self.child(tag='row', **kwargs)
        row.lbl_height = float(lbl_height or 0)
        row.lbl_class = lbl_class
        row.content_class = content_class
        row.height = float(height or 0)
        if row_border is None:
            row.row_border = layout.row_border
        else:
            row.row_border = row_border
        if cell_border is None:
            row.cell_border = layout.cell_border
        else:
            row.cell_border = cell_border
        row.idx = len(layout)-1
        row.layout = layout
        row.elastic_cells = []
        if not row.height:
            layout.elastic_rows.append(row)
        return row

    def cell(self, content=None,width=0, content_class=None, lbl=None,lbl_class=None,lbl_height=None, cell_border=None, **kwargs):
        assert self.parentNode.getAttr('tag') == 'row'
        row=self
        cell = row.child(tag='cell', **kwargs)
        #cell = row.child(tag='cell',content=content, **kwargs)
        if content:
            cell.child(tag='div', content=content, class_=content_class)
        cell.width = float(width or 0)
        cell.row = row
        cell.content_class=content_class
        cell.lbl=lbl
        cell.lbl_class=lbl_class
        cell.lbl_height=float(lbl_height or 0)
        if cell_border is None:
            cell.cell_border = row.cell_border
        else:
            cell.cell_border = cell_border
        if not cell.width:
            row.elastic_cells.append(cell)
        return cell


class GnrHtmlBuilder(object):
    def __init__(self,bodyAttributes=None):
        pass

                        
    def initializeSrc(self, bodyAttributes=None):
        bodyAttributes=bodyAttributes or {}
        self.root = GnrHtmlSrc.makeRoot()
        self.root.builder = self
        self.htmlBag = self.root.html()
        self.head = self.htmlBag.head()
        self.body = self.htmlBag.body(**bodyAttributes)
        self.head.style(""".x_br{border-top:none!important;border-left:none!important;}
                           .x_r{border-top:none!important;border-left:none!important;border-bottom:none!important;}
                           .x_b{border-top:none!important;border-left:none!important;border-right:none!important;}
                           .x_{border:none!important;}
                        """)

    def toHtml(self,filename=None):
        if filename:
            filename=expandpath(filename)
        self.finalize(self.body)
        self.html = self.root.toXml(filename=filename,
                                    omitRoot=True,
                                    autocreate=True,
                                    forcedTagAttr='tag',
                                    addBagTypeAttr=False, typeattrs=False)
        return self.html
        
    def toPdf(self, filename):
        self.toHtml('%s.%s'%(filename,'html'))
        wkprinter = WK2pdf('%s.%s'%(filename,'html'),filename)
        wkprinter.run()
        wkprinter.exec_()
        
    def calculate_style(self,attr,um,**kwargs):
        style=attr.pop('style','')
        style = style.replace('\n','')
        style_dict = dict([(splitAndStrip(x,':')) for x in style.split(';') if ':' in x])
        style_dict.update(kwargs)
        for name in ('width', 'height', 'top', 'left', 'right','bottom'):
            if name in attr:
                value=attr.pop(name)
                try:
                    value=float(value)
                    i_value=int(value)
                    if i_value==value:
                        value=i_value
                    value='%s%s' % (value,um)
                except:
                    pass
                style_dict[name]=value
        attr['style']=''.join(['%s:%s;' %(k,v) for k,v in style_dict.items()])
        
    def finalize(self, src):
        for node in src:
            node_tag = node.getAttr('tag')
            node_value = node.value
            getattr(self,'finalize_%s'%node_tag, self.finalize_pass)(src, node.attr, node.value)
            if node_value and isinstance(node_value, GnrHtmlSrc):
                self.finalize(node_value)
            getattr(self,'finalize_%s_after'%node_tag, self.finalize_pass)(src, node.attr, node.value)
            
                
    def finalize_layout(self, parent, attr, layout):
        if layout.nested:
            layout.width=layout.width or parent.width-layout.left-layout.right-layout.border_width
            layout.height=layout.height or parent.height-layout.top-layout.bottom-layout.border_width
      
        if layout.elastic_rows:
            if layout.height:
                height = (layout.height - sum([row.height for row in layout.values() if row.height]))/len(layout.elastic_rows)
                for row in layout.elastic_rows:
                    row.height = height
            else:
                raise GnrHtmlSrcError('No total height with elastic rows')
                ## Possibile ricerca in profondità
        layout.height = sum([row.height for row in layout.values()])
        layout.values()[-1].row_border=False
        if layout.nested:
            borders=' '.join(['%s%s'% (int(getattr(layout,side)!=0) * layout.border_width,layout.um) for side in ('top','right','bottom','left')])
        else:
            borders='%s%s'% (layout.border_width,layout.um)
        attr['top'] = layout.top
        attr['left'] = layout.left
        attr['bottom'] = layout.bottom
        attr['right'] = layout.right
        attr['height'] = layout.height
        attr['width'] = layout.width
        attr['class'] = ' '.join(x for x in [attr.get('class'),row.layout.layout_class] if x) 
        kw={'border-width':borders}
       
        self.calculate_style(attr, layout.um,**kw)
        layout.curr_y = 0
        attr['tag'] = 'div'
        
    def finalize_row(self, layout, attr, row):
        width = layout.width
        if row.elastic_cells:
            if width:
                elastic_width = (width - sum([cell.width for cell in row.values() if cell.width]))/len(row.elastic_cells)
                for cell in row.elastic_cells:
                    cell.width = elastic_width
            else:
                raise GnrHtmlSrcError('No total width with elastic cells')
                ## Possibile ricerca in profondità
        cells=row.values()
        if cells:
            cells[-1].cell_border=False
        attr['height'] = row.height
        attr['top'] = layout.curr_y
        attr['tag'] = 'div'
        layout.curr_y += row.height
        self.calculate_style(attr, layout.um,position='absolute')
        row.curr_x = 0
        
        
    def finalize_cell(self, row, attr, cell):
        cell.height = row.height
        width = cell.width
        um = row.layout.um
        if cell.lbl:
            self.setLabel(cell, attr)
        bottom_border_width = row.layout.border_width if row.row_border else 0
        right_border_width = row.layout.border_width if cell.cell_border else 0
        net_width = width - right_border_width
        net_height = cell.height - bottom_border_width
        attr['width'] = net_width
        attr['height'] = net_height
        attr['tag'] = 'div'
        attr['top']=0
        attr['left']=row.curr_x
        cell_class='x_br'
        if not bottom_border_width:
            cell_class=cell_class.replace('b','')
        if not right_border_width:
            cell_class=cell_class.replace('r','')
        attr['class'] = ' '.join(x for x in [attr.get('class'),row.layout.layout_class,cell_class] if x)   
        row.curr_x += width
        self.calculate_style(attr, row.layout.um)
        
    def setLabel(self, cell, attr):
        row=cell.row
        layout=row.layout
        um=row.layout.um
        lbl=cell.lbl 
        lbl_height=cell.lbl_height or row.lbl_height or layout.lbl_height
        lbl_class=cell.lbl_class or row.lbl_class or layout.lbl_class
        content_class=cell.content_class or row.content_class or layout.content_class
        cur_content=cell.popNode('#0')
        lbl_attr={'class':lbl_class,'top':0,'height':lbl_height,'left':0, 'right':0}
        self.calculate_style(lbl_attr, um,position='absolute')
        cell.child('div',content=lbl,**lbl_attr)
        content_attr={'class':content_class,'top':lbl_height,'left':0, 'right':0}
        self.calculate_style(content_attr, um,position='absolute')
        x=cell.child('div',**content_attr)
        x.setItem('div_0',cur_content)
        x.width=cell.width
        x.height=cell.height-lbl_height

    def finalize_pass(self, src, attr, value):
        pass

def test0(pane):
    
    d=180
    layout = pane.layout(width=d,height=d,um='mm',top=10,left=10,border_width=.3,
                        lbl_height=4,lbl_class='z1',content_class='content',_class='mmm')

    layout.style(".z1{font-size:7pt;background-color:silver;text-align:center}")
    layout.style(".z2{font-size:9pt;background-color:pink;text-align:right;}")
    layout.style(".content{font-size:12pt;text-align:center;}")
    layout.style(".myclass{font-size:18pt;text-align:center;background-color:green;}")
    layout.style(".uuu{color:red;}")
    layout.style(".mmm{font-family:courier;}")

    x=d/3.
    r = layout.row(_class='uuu')
    r.cell('foo',lbl='name',_class='myclass')
    r.cell('bar',width=x,lbl='weight')
    r.cell('<b>spam</b>::HTML',lbl='time')
    r = layout.row(height=x)
    r.cell('foo',lbl='cc')
    subtable=r.cell(width=x)
    r.cell('baz',lbl='dd')
    r = layout.row()
    r.cell('foo',lbl='alfa')
    r.cell('bar',width=x,lbl='beta')
    r.cell('baz',lbl='gamma')
    layout=subtable.layout(name='inner',um='mm',border_width=.3,top=0,left=0,right=0,bottom=0,
                        border_color='green',
                        lbl_height=4,lbl_class='z1',content_class='content')
    x=x/2.
    r = layout.row()
    r.cell('foo')
    r.cell('bar',width=x)
    r.cell('baz')
    r = layout.row(height=x)
    r.cell('foo')
    r.cell('bar',width=x)
    r.cell('baz')
    r = layout.row()
    r.cell('foo')
    r.cell('bar',width=x)
    r.cell('baz')
    
    
    
def test1(pane):
    layout = pane.layout(width='150',height=150,um='mm',top=10,left=10,border_width=.3,
                        lbl_height=4,lbl_class='z1',content_class='content')
    layout.style(".z1{font-size:7pt;background-color:silver;text-align:center}")
    layout.style(".z2{font-size:9pt;background-color:pink;text-align:right;}")
    layout.style(".content{font-size:12pt;text-align:center;}")

    r = layout.row(height=20)
    r.cell('foo',width=40,lbl='name')
    r.cell()
    r.cell('bar',width=22)
    r.cell('<b>spam</b>',width=18)
    r.cell()
    r.cell('eggs',width=30)
    sublayout = layout.row().cell()
    r = layout.row(height=40)
    r.cell('maa',width=60,lbl='name')
    r.cell()
    r.cell('dooo',width=60)
    sl=sublayout.layout(width='150',height=70,um='mm',top=0,left=0,border_width=.3,
                        lbl_height=4,lbl_class='z1',content_class='content')
    r=sl.row(height=10)
    r.cell('xx',width=10)
    r.cell()
    r.cell('yy',width=20)
    sl.row().cell()
    r=sl.row(height=30)
    r.cell('tt',width=40)
    r.cell('kkkkk')
    r.cell('mmm',width=40)
    
    


if __name__ =='__main__':
    builder = GnrHtmlBuilder() 
    #test1(body)
    test0(builder.body)
    #pdf.root.toXml('testhtml/test0.xml',autocreate=True)
    builder.toHtml('testhtml/test0.html')
    from gnr.pdf.wk2pdf import WK2pdf
    wkprinter = WK2pdf('testhtml/test0.html','testhtml/test0.pdf')
    wkprinter.run()
    wkprinter.exec_()
    #print builder.html