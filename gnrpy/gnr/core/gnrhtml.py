#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#


from gnr.core.gnrbag import Bag,BagNode
from gnr.core.gnrstructures import GnrStructData
#from gnr.core import gnrstring
from gnr.core.gnrsys import expandpath
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
    
    
    def clean_names(self, kw, names):
        for name in names:
            if name in kw:
                kw[name.replace('_','')]=kw.pop(name)
    
    def __call__(self,*args,**kwargs):
        self.clean_names(kwargs,['class_','_class'])
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
    
    
    def layout(self, name='l1', um='mm',top=0,left=0,width=0,height=0,
                    border_size=0.3,border_color='grey',border_style='solid', row_border=True, cell_border=True,
                    lbl_height=3, lbl_class='lbl_base',content_class='content_base',
                    **kwargs):
        layout = self.child(tag='layout', **kwargs)
        layout.layout_name = name
        layout.um = um
        layout.top = float(top or 0)
        layout.left = float(left or 0)
        layout.width = float(width or 0)
        layout.height = float(height or 0)
        layout.border_size = float(border_size or 0)
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
        
    def row(self, height=0, row_border=None, cell_border=None, **kwargs):
        assert self.parentNode.getAttr('tag') == 'layout'
        layout = self
        row = self.child(tag='row', **kwargs)
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
        cell = self.child(tag='cell', **kwargs)
        if content:
            cell.child(tag='span', content=content, class_=content_class)
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
        
    def cell_():
        um=row.container.um
        dbs=row.border_size
        content_class=content_class or row.container.content_class
        if lbl:
            lbl_height=lbl_height or row.container.lbl_height
            lbl_class=lbl_class or row.container.lbl_class
            cell= row.child(tag='cell', width=width, idx=len(row),**kwargs)
            caption_attr={'class':lbl_class,'top':dbs,'height':lbl_height,'left':dbs, 'right':dbs}
            self.setValueAndUm(caption_attr,um=um,position='absolute')
            cell.child('div',content=lbl,**caption_attr)
            content_attr={'class':content_class,'top':dbs+lbl_height}
            self.setValueAndUm(content_attr,um=um,position='absolute')
            cell=cell.child('div',content=content,**content_attr)
        else:
            cell= row.child(tag='cell', content=content, width=width, idx=len(row),**kwargs)
        return cell


    def row_():
        row.um=layout.um
        row.layout_name=container.layout_name
        row.border_size=container.border_size
        row.height = height
        row.max_width=float(container.width or '0')
        row.delta_y='%spx'%((len(container)-1)*container.border_size)
        row.curr_x=0
        return row
        
    def layout_(self):
        parentNode=self.parentNode
        if parentNode.getAttr('tag')=='cell':
            if not width:
                width=float(parentNode.getAttr('width'))
        self.style(self.globalCss(layout_name=layout_name,um=um,border_size=border_size,
                                     border_color=border_color,
                                     border_style=border_style))

        container.height = height
        container.width = width
        container.border_size=float(border_size)
        container.um=um
        container.lbl_height=lbl_height
        container.lbl_class=lbl_class
        container.content_class=content_class
        container.layout_name=layout_name
        container.height_calc=0
        return container

    def toHtml(self):
        self.finalize()
        result = self._toHtmlInner()
        return result

class GnrHtmlBuilder(object):
    def __init__(self):
        self.root = GnrHtmlSrc.makeRoot()
        self.root.builder = self
        self.html = self.root.html()
        self.head = self.html.head()
        self.body = self.html.body()

    #def toXml(self,filename=None,encoding='UTF-8'):
    #    return self.root.toXml(filename=filename, encoding=encoding,typeattrs=False, autocreate=True,
    #            omitUnknownTypes=True, omitRoot=True, forcedTagAttr='tag',addBagTypeAttr=False)
    #
    def toHtml(self,filename=None):
        if filename:
            filename=expandpath(filename)
        self.finalize(self.body)
        return self.root.toXml(filename=filename,omitRoot=True,autocreate=True,forcedTagAttr='tag',addBagTypeAttr=False, typeattrs=False)
        
    def calculate_style(self,attr,um,**kwargs):
        style=attr.pop('style','')
        style_dict = dict([(x.split(':')) for x in style.split(';') if x])
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
            getattr(self,'finalize_%s_before'%node_tag, self.finalize_pass)(src, node.attr, node.value)
            if isinstance(node_value, GnrHtmlSrc):
                self.finalize(node_value)
            getattr(self,'finalize_%s_after'%node_tag, self.finalize_pass)(src, node.attr, node.value)
            
                
    def finalize_layout_before(self, parent, attr, layout):
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
        bs = '%s%s'%(layout.border_size,layout.um) if not layout.nested else 0
        attr['top'] = layout.top
        attr['left'] = layout.left
        #attr['bottom'] = layout.bottom
        attr['height'] = layout.height
        attr['width'] = layout.width
        self.calculate_style(attr, layout.um, **{'border-width':bs,'border-color': layout.border_color,'border-style':layout.border_style,'position':'absolute'})
        layout.curr_y = 0
        attr['tag'] = 'div'
        
    def finalize_row_before(self, layout, attr, row):
        width = layout.width
        if row.elastic_cells:
            if width:
                elastic_width = (width - sum([cell.width for cell in row.values() if cell.width]))/len(row.elastic_cells)
                for cell in row.elastic_cells:
                    cell.width = elastic_width
            else:
                raise GnrHtmlSrcError('No total width with elastic cells')
                ## Possibile ricerca in profondità
        row.values()[-1].cell_border=False
        attr['height'] = row.height
        attr['top'] = layout.curr_y
        attr['tag'] = 'div'
        layout.curr_y += row.height
        self.calculate_style(attr, layout.um,position='absolute')
        row.curr_x = 0
        
        
    def finalize_cell_before(self, row, attr, cell):
        height = row.height
        width = cell.width
        um = row.layout.um
        bottom_border_size = row.layout.border_size if row.row_border else 0
        right_border_size = row.layout.border_size if cell.cell_border else 0
        net_width = width - right_border_size
        net_height = height - bottom_border_size
        attr['width'] = net_width
        attr['height'] = net_height
        attr['tag'] = 'div'
        #attr['class']='%s_br' % self.layout_name
        attr['top']=0
        
        attr['left']=row.curr_x
        row.curr_x += width
        bs = '0 %s%s %s%s 0'%(right_border_size,um,bottom_border_size,um)
        self.calculate_style(attr, row.layout.um, **{'border-width':bs,'position':'absolute','border-style':row.layout.border_style,'border-color':row.layout.border_color})
        
        
    def finalize_pass(self, src, attr, value):
        pass
    #
    #
    #def toPdf(self,filename=None):
    #    """call the pdf webkit generator"""
    #    pass

def test0(pane):
    layout = pane.layout(width='100',height=20,um='mm',top=10,left=10,border_size=.3,
                        lbl_height=4,lbl_class='z1',content_class='content')
    layout.style(".z1{font-size:7pt;background-color:silver;text-align:center}")
    layout.style(".z2{font-size:9pt;background-color:pink;text-align:right;}")
    layout.style(".content{font-size:12pt;text-align:center;}")

    r1 = layout.row(height=20)
    r1.cell('foo',width=40,lbl='name')
    #r1.cell()
    r1.cell('bar',width=22)
    #r1.cell('spam',width=18)
    #r1.cell()
    #r1.cell('eggs',width=30)
    


if __name__ =='__main__':
    builder = GnrHtmlBuilder() 
    #test1(body)
    test0(builder.body)
    #pdf.root.toXml('testhtml/test0.xml',autocreate=True)
    builder.toHtml('testhtml/test0.html')
    #from gnr.pdf.wk2pdf import WK2pdf
    #wkprinter = WK2pdf('testhtml/test0.html','testhtml/test0.pdf')
    #wkprinter.run()
    #wkprinter.exec_()
    print builder.html