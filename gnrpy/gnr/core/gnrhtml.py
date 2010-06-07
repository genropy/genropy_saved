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
            
    def style(self,style='',**kwargs):
        self.root.builder.head.child('style',content=style,**kwargs)
    
    def comment(self,content=None):
        self.child(tag='__flatten__',content='<!--%s-->' %content)
                
    def script(self,script='',_type="text/javascript",**kwargs):
        self.root.builder.head.child('script',content=script, _type=_type,**kwargs)
        
    def link(self,href='',**kwargs ):
        self.root.builder.head.child('link',href=href,**kwargs)
        
    def csslink(self,href='',media='screen',**kwargs ):
        self.root.builder.head.child('link',href=href,rel="stylesheet",_type="text/css",media=media,**kwargs)
        
    def meta(self,name=None,content=None,http_equiv=None,**kwargs):   
        _attributes = dict()
        if http_equiv:
            _attributes['http-equiv'] = http_equiv
        self.root.builder.head.child('meta',_name=name,_content=content,_attributes=_attributes,**kwargs)
        
            
    def child(self,tag,*args, **kwargs):
        for lbl in ['_class','class_','_type','type_','_for','for_']:
            if lbl in kwargs:
                kwargs[lbl.replace('_','')]=kwargs.pop(lbl)

        if 'name' in kwargs:
            kwargs['_name']=kwargs.pop('name')
        return super(GnrHtmlSrc, self).child(tag,*args,**kwargs)

    def layout(self, name='l1', um='mm',top=0,left=0,bottom=0,right=0,width=0,height=0,
                    border_width=0.3,border_color='grey',border_style='solid', row_border=True, cell_border=True,
                    lbl_height=3, lbl_class='lbl_base',content_class='content_base',
                    hasBorderTop=None,hasBorderLeft=None,hasBorderRight=None,hasBorderBottom=None,
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
        layout.hasBorderTop=hasBorderTop
        layout.hasBorderLeft=hasBorderLeft
        layout.hasBorderRight=hasBorderRight
        layout.hasBorderBottom=hasBorderBottom
        layout.nested = self.parentNode.getAttr('tag')=='cell'
        return layout
        
    def row(self, height=0, row_border=None, cell_border=None,lbl_height=None, lbl_class=None,content_class=None, **kwargs):
        assert self.parentNode.getAttr('tag') == 'layout'
        layout = self
        row = self.child(tag='row', **kwargs)
        row.lbl_height = float(lbl_height or 0)
        row.lbl_class = lbl_class
        row.content_class = content_class
        if height:
            height = height - layout.border_width
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
    
    styleAttrNames=['height', 'width','top','left', 'right', 'bottom',
                              'visibility', 'overflow', 'float', 'clear', 'display',
                              'z_index', 'border','position','padding','margin',
                              'color','white_space','vertical_align','background', 'text'];
                              
                              
    def __init__(self,page_height=None,page_width=None,page_margin_top=None,
                    page_margin_left=None,page_margin_right=None,page_margin_bottom=None,
                    showTemplateContent = None,
                    htmlTemplate=None,page_debug=False,srcfactory=None,
                    print_button=None,bodyAttributes=None):
        self.srcfactory=srcfactory or GnrHtmlSrc
        self.htmlTemplate = htmlTemplate or Bag()
        self.page_height = page_height or self.htmlTemplate['main.page.height'] or 280
        self.page_width = page_width or self.htmlTemplate['main.page.width'] or 200
        self.page_margin_top = page_margin_top or self.htmlTemplate['main.page.top'] or 0
        self.page_margin_left = page_margin_left or self.htmlTemplate['main.page.left'] or 0
        self.page_margin_right = page_margin_right or self.htmlTemplate['main.page.right'] or 0
        self.page_margin_bottom = page_margin_bottom or self.htmlTemplate['main.page.bottom'] or 0
        self.page_debug = page_debug 
        self.print_button = print_button
        self.showTemplateContent = showTemplateContent
        
    def initializeSrc(self, **bodyAttributes):
        bodyAttributes=bodyAttributes or {}
        self.root = self.srcfactory.makeRoot()
        self.root.builder = self
        self.htmlBag = self.root.html()
        self.head = self.htmlBag.head()
        self.body = self.htmlBag.body(**bodyAttributes)
        self.body.style("""
                        .no_print{
                            display:none;
                        }
                        """,media='print')
        self.body.style("""
                        #printButton{
                            position:fixed;right:30px;top:5px;z-index:100;
                            cursor:pointer;',onclick='window.print();
                            background:#3F5A8D; color:white; -moz-border-radius:8px;
                            -webkit-border-radius:8px;font-size:9pt;
                            padding:3px;padding-left:8px;
                            padding-right:8px;border:1px solid white;
                            -moz-box-shadow:4px 4px 5px gray;
                            -webkit-box-shadow:4px 4px 5px gray;
                            font-family:courier;
                        }
                        """)

        
    def prepareTplLayout(self,tpl):
        layout = tpl.layout(top=0,height=self.page_height-self.page_margin_top-self.page_margin_bottom,
                            left=0,width=self.page_width-self.page_margin_left-self.page_margin_right,
                            border=0)
        regions = dict(center_center=layout)
        if self.htmlTemplate['main.design'] == 'headline':
            for region in ('top','center','bottom'):
                height = self.htmlTemplate['layout.%s?height' %region] or 0
                if region=='center' or height:
                    row = layout.row(height=height)
                    for subregion in ('left','center','right'):
                        width = self.htmlTemplate['layout.%s.%s?width' %(region,subregion)] or 0
                        if subregion=='center' or width:
                            innerHTML = self.htmlTemplate['layout.%s.%s.html' %(region,subregion)] or None
                            if innerHTML:
                                if self.showTemplateContent:
                                    print 'aaa'
                                    innerHTML = "%s::HTML" %innerHTML
                                else:
                                    innerHTML = ''
                            regions['%s_%s' %(region,subregion)] = row.cell(content=innerHTML,width=width,border=0)
        elif self.htmlTemplate['main.design'] == 'sidebar':
            mainrow = layout.row(height=0)
            for region in ('left','center','right'):
                width = self.htmlTemplate['layout.%s?width' %region] or 0
                if region=='center' or width:
                    col = mainrow.cell(width=width,border=0).layout()
                    for subregion in ('top','center','bottom'):
                        height = self.htmlTemplate['layout.%s.%s?height' %(region,subregion)] or 0
                        if subregion=='center' or height:
                            row = col.row(height=height)
                            innerHTML = self.htmlTemplate['layout.%s.%s.html' %(region,subregion)] or None
                            if innerHTML:
                                innerHTML = "%s::HTML" %innerHTML
                            regions['%s_%s' %(region,subregion)] = row.cell(content=innerHTML,border=0)
                
        return regions['center_center']
                            
            
    def newPage(self):
        firstpage = (len(self.body)==0)
        border_color = 'red' if self.page_debug else 'white'
        page_break = '' if firstpage else 'page-break-before:always;'
        page = self.body.div(style="""position:relative;
                                   width:%smm;
                                   height:%smm;
                                   border:.3mm solid %s; /* do not remove */
                                   top:0mm;
                                   left:0mm;
                                   %s""" %(self.page_width,self.page_height,border_color,page_break))
        tplpage = page.div(style="""position:absolute;
                                   top:%imm;
                                   left:%imm;
                                   right:%imm;
                                   bottom:%imm;""" %(
                                   self.page_margin_top,self.page_margin_left,
                                   self.page_margin_right,self.page_margin_bottom))
        if self.htmlTemplate:
            tplpage = self.prepareTplLayout(tplpage)                           
        if firstpage and self.print_button:
            tplpage.div(self.print_button,_class='no_print',id='printButton',onclick='window.print();')
        return tplpage
    
    def styleForLayout(self):
        self.head.style(""".x_br{border-top:none!important;border-left:none!important;}
                           .x_r{border-top:none!important;border-left:none!important;border-bottom:none!important;}
                           .x_b{border-top:none!important;border-left:none!important;border-right:none!important;}
                           .x_{border:none!important;}
                        """)



    def toHtml_(self,filepath=None):
        if filepath:
            filepath=expandpath(filepath)
        self.finalize(self.body)
        self.html = self.root.toXml(filename=filepath,
                                    omitRoot=True,
                                    autocreate=True,
                                    forcedTagAttr='tag',
                                    addBagTypeAttr=False, typeattrs=False, self_closed_tags=['meta','br','img'])
        return self.html
                                    
                                    
    def toHtml(self,filepath=None):
        if filepath:
            filepath=expandpath(filepath)
        self.finalize(self.body)
        self.html = self.root.toXml(filename=filepath,
                                    omitRoot=True,
                                    autocreate=True,
                                    forcedTagAttr='tag',
                                    addBagTypeAttr=False, typeattrs=False,self_closed_tags=['meta','br','img'],
                                    docHeader='<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"> \n')
        return self.html
        
    def toPdf(self, filename):
        from subprocess import call
        if sys.platform.startswith('linux'):
            res = call(['wkhtmltopdf','-q','%s.%s'%(filename,'html'),filename])
        else:
            res = call(['wkhtmltopdf','-q','%s.%s'%(filename,'html'),filename])
        
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
        
    def styleMaker(self,attr):
        style=attr.pop('style','')
        style = style.replace('\n','')
        style_dict = dict([(splitAndStrip(x,':')) for x in style.split(';') if ':' in x])
        for oneattr in attr.keys():
            if oneattr in self.styleAttrNames or ('_' in oneattr and oneattr.split('_')[0] in self.styleAttrNames) :
                style_dict[oneattr.replace('_','-')]=attr.pop(oneattr)
        attr['style']=''.join(['%s:%s;' %(k,v) for k,v in style_dict.items()])
        
    def finalize(self, src):
        for node in src:
            node_tag = node.getAttr('tag')
            node_value = node.value
            getattr(self,'finalize_%s'%node_tag, self.finalize_pass)(src, node.attr, node.value)
            
            if node_value and isinstance(node_value, GnrHtmlSrc):
                self.finalize(node_value)
            getattr(self,'finalize_%s_after'%node_tag, self.finalize_pass)(src, node.attr, node.value)
            self.styleMaker(node.attr)
    
    def finalize_layout(self, parent, attr, layout):

        borders='%s%s'% (layout.border_width,layout.um)
        if layout.nested:

            layout.has_topBorder = layout.hasBorderTop if layout.hasBorderTop is not None else bool(layout.top or parent.lbl)
            layout.has_leftBorder = layout.hasBorderLeft if layout.hasBorderLeft is not None else bool(layout.left)
            layout.has_rightBorder = layout.hasBorderRight if layout.hasBorderRight is not None else bool(layout.right)
            layout.has_bottomBorder = layout.hasBorderBottom if layout.hasBorderBottom is not None else bool(layout.bottom)
            
            layout.width=layout.width or parent.width-layout.left-layout.right -  int(layout.has_leftBorder)*layout.border_width - int(layout.has_rightBorder)*layout.border_width
            layout.height=layout.height or parent.height-layout.top-layout.bottom - int(layout.has_topBorder)*layout.border_width - int(layout.has_bottomBorder)*layout.border_width
            borders=' '.join(['%s%s'% (int(getattr(layout,'has_%sBorder'%side)) * layout.border_width,layout.um) for side in ('top','right','bottom','left') ])
      
        if layout.elastic_rows:
            if layout.height:
                height = (layout.height - sum([(row.height) for row in layout.values() if row.height]) - layout.border_width*(len(layout)-1))/len(layout.elastic_rows)
                for row in layout.elastic_rows:
                    row.height = height
            else:
                raise GnrHtmlSrcError('No total height with elastic rows')
                ## Possibile ricerca in profondità
        layout.height = sum([row.height for row in layout.values()])+layout.border_width*(len(layout)-1)
        layout.values()[-1].row_border=False
        
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
        if row.elastic_cells:
            if layout.width:
                elastic_width = (layout.width - sum([cell.width for cell in row.values() if cell.width]) - layout.border_width*(len(row)-1))/len(row.elastic_cells)
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
        layout.curr_y += row.height+layout.border_width
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
        attr['width'] = width
        attr['height'] = cell.height
        attr['tag'] = 'div'
        attr['top']=0
        attr['left']=row.curr_x
        cell_class='x_br'
        if not bottom_border_width:
            cell_class=cell_class.replace('b','')
        if not right_border_width:
            cell_class=cell_class.replace('r','')
        attr['class'] = ' '.join(x for x in [attr.get('class'),row.layout.layout_class,cell_class] if x)   
        row.curr_x += width+right_border_width
        self.calculate_style(attr, row.layout.um)
        
    def setLabel(self, cell, attr):
        row=cell.row
        layout=row.layout
        um=row.layout.um
        lbl=cell.lbl 
        lbl_height=cell.lbl_height or row.lbl_height or layout.lbl_height
        lbl_class=cell.lbl_class or row.lbl_class or layout.lbl_class
        content_class=cell.content_class or row.content_class or layout.content_class
        if len(cell) >0:
            cur_content_node=cell.popNode('#0')
            cur_content_attr= cur_content_node.attr
            cur_content_value= cur_content_node.value
        else:
            cur_content_value = ''
        # set the label
        lbl_attr={'class':lbl_class,'top':0,'height':lbl_height,'left':0, 'right':0}
        self.calculate_style(lbl_attr, um,position='absolute')
        cell.child('div',content=lbl,**lbl_attr)
        if isinstance (cur_content_value, GnrHtmlSrc):
            tag=cur_content_attr.pop('tag')
            cur_content_value.top=cur_content_value.top+lbl_height
            cell.child(tag,content=cur_content_value, **cur_content_attr)
        else:
            content_attr={'class':content_class,'top':lbl_height,'left':0, 'right':0}
            self.calculate_style(content_attr, um,position='absolute')
            cell.child('div',content=cur_content_value, **content_attr)

    def finalize_pass(self, src, attr, value):
        pass

def test0(pane):
    
    d=180
    layout = pane.layout(width=d,height=d,um='mm',top=10,left=10,border_width=3,
                        lbl_height=4,lbl_class='z1',content_class='content',_class='mmm')

    layout.style(".z1{font-size:7pt;background-color:silver;text-align:center}")
    layout.style(".z2{font-size:9pt;background-color:pink;text-align:right;}")
    layout.style(".content{font-size:12pt;text-align:center;}")
    layout.style(".myclass{font-size:18pt;text-align:center;background-color:green;}")
    layout.style(".uuu{color:red;}")
    layout.style(".mmm{font-family:courier;}")
    layout.script("aaaaaaaaaaa")
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
    layout=subtable.layout(name='inner',um='mm',border_width=1,top=0,left=0,right=0,bottom=0,
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

def testRowsInner(cell):
    innerLayout=cell.layout(name='inner',um='mm',top=0,left=0,bottom=3,right=0,border_width=1.2,border_color='navy',lbl_height=4,
                         lbl_class='z1',hasBorderLeft=True)
    row=innerLayout.row()
    row.cell('aaa', width =30, lbl='bb', background_color='lime')
    row.cell('bbb', width =0, lbl='aa')
    
    
def testRows(pane):
    layout = pane.layout(name='outer',width=180,height=130,um='mm',
                         top=1,left=1,
                         border_width=3,border_color='red',
                         lbl_height=4,
                         lbl_class='z1')

    layout.style(".z1{font-size:7pt;background-color:silver;text-align:center}")
    
    for h in [20,0,0,20]:
        row=layout.row(height=h)
        #row.cell('hhh',lbl='foo', width=60)
        row.cell(lbl='bar')
        testRowsInner(row.cell(lbl='foo', width=60))
        #testRowsInner(row.cell(lbl='bar'))
    
    
    
if __name__ =='__main__':
    builder = GnrHtmlBuilder() 
    builder.initializeSrc()
    builder.styleForLayout()
    testRows(builder.body)
    builder.toHtml('testhtml/test0.html')