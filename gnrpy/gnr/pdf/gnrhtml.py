#-*- coding: UTF-8 -*-

#--------------------------------------------------------------------------
# package       : GenroPy web - see LICENSE for details
# module gnrsqlclass : Genro Web structures implementation
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
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
from gnr.core.gnrbag import Bag, BagNode
from gnr.core.gnrstructures import GnrStructData
from gnr.core import gnrstring
from gnr.core.gnrsys import expandpath
import cStringIO
import os
from gnr.core.gnrlang import optArgs

class GnrHtmlSrcError(Exception):
    pass
    
class GnrHtmlElem(object):
    def __init__(self, obj, tag):
        self.obj = obj
        self.tag = tag
        
    def __call__(self, *args, **kwargs):
        child = self.obj.child(self.tag, *args, **kwargs)
        return child
        
class GnrHtmlSrc(GnrStructData):
    """add???
    """
    htmlNS = ['a', 'abbr', 'acronym', 'address', 'area', 'b', 'base', 'bdo', 'big', 'blockquote',
              'body', 'br', 'button', 'caption', 'cite', 'code', 'col', 'colgroup', 'dd', 'del',
              'div', 'dfn', 'dl', 'dt', 'em', 'fieldset', 'form', 'frame', 'frameset',
              'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'head', 'hr', 'html', 'i', 'iframe', 'img', 'input',
              'ins', 'kbd', 'label', 'legend', 'li', 'link', 'map', 'meta', 'noframes', 'noscript',
              'object', 'ol', 'optgroup', 'option', 'p', 'param', 'pre', 'q', 'samp',
              'select', 'small', 'span', 'strong', 'style', 'sub', 'sup', 'table', 'tbody', 'td',
              'textarea', 'tfoot', 'th', 'thead', 'title', 'tr', 'tt', 'ul', 'var']
              
    gnrNS = ['layout', 'row', 'cell']
    
    genroNameSpace = dict([(name.lower(), name) for name in htmlNS])
    genroNameSpace.update(dict([(name.lower(), name) for name in gnrNS]))
        
    def __getattr__(self, fname):
        fnamelower = fname.lower()
        if (fname != fnamelower) and hasattr(self, fnamelower):
            return getattr(self, fnamelower)
        elif fnamelower in self.genroNameSpace:
            return GnrHtmlElem(self, '%s' % (self.genroNameSpace[fnamelower]))
            
        else:
            raise AttributeError, fname
            
    def toHtml(self):
        """add???
        """
        result = self._toHtmlInner()
        return result
        
    def style(self, style=''):
        """add???
        
        :param style: add???. Default value is ``' '``
        :reutrns: add???
        """
        self.root.head.child('style', content=style)
        
    def _toHtmlInner(self):
        result = Bag()
        hasRows = False
        for node in self.nodes:
            label = node.label
            attr = dict(node.attr)
            tag = attr.pop('tag')
            value = node.getValue()
            if isinstance(value, GnrHtmlSrc):
                if len(value) == 0:
                    newValue = ' '
                else:
                    newValue = value._toHtmlInner()
            else:
                newValue = value
            if hasattr(self, 'compile_%s' % tag):
                handler = getattr(self, 'compile_%s' % tag)
                tag, attr = handler(value, tag, attr)
            result.addItem(tag, newValue, attr)
        return result

    def __content(self, content):
        self.child('__flatten__', content=content)

    def content(self, content):
        """add???
        
        :param content: add???
        """
        if not (isinstance(content, list) or isinstance(content, tuple) ):
            content = [content]
        for single_content in content:
            if isinstance(single_content, GnrHtmlSrc):
                childattr = dict(single_content.parentNode.attr)
                tag = childattr.pop('tag')
                self.child(tag, content=single_content, **childattr)
            else:
                self.child('__flatten__', content=single_content)
                
    def valueAndUm(self, value, um):
        """add???
        
        :param value: add???
        :param um: add???
        :returns: add???
        """
        try:
            value = float(value)
            i_value = int(value)
            if i_value == value:
                value = i_value
            return '%s%s' % (value, um)
        except:
            return value
            
    def child_(self, tag, *args, **kwargs):
        """add???
        
        :param tag: add???
        :returns: add???
        """
        width = kwargs.pop('width', None)
        height = kwargs.pop('height', None)
        position = kwargs.pop('position', None)
        left = kwargs.pop('left', None)
        top = kwargs.pop('top', None)
        _class = kwargs.pop('_class', None)
        style = kwargs.pop('style', '')
        um = kwargs.pop('um', '')
        if width or height:
            style_dict = dict([(x.split(':')) for x in style.split(';') if x])
            if width:
                style_dict['width'] = self.valueAndUm(width, um)
            if height:
                style_dict['height'] = self.valueAndUm(height, um)
                style_dict['width'] = self.valueAndUm(width, um)
            if position:
                style_dict['position'] = position
            if left is not None:
                style_dict['left'] = self.valueAndUm(left, um)
            if top is not None:
                style_dict['top'] = self.valueAndUm(top, um)
                
            style = ''.join(['%s:%s;' % (k, v) for k, v in style_dict.items()])
        if style:
            kwargs['style'] = style
        if _class:
            kwargs['class'] = _class
        return super(GnrHtmlSrc, self).child(tag, *args, **kwargs)
        
    def layout(self, width=0, height=0, top=0, left=0, layout_name='l1', um='mm',
               border_size=0.1, border_color='red', lbl_height=3,
               lbl_class='lbl_base', content_class='content_base',
               border_style='solid', **kwargs):
        """define the layout attributes
        
        :param width: the layout's width. Default value is ``0``
        :param height: the layout's height. Default value is ``0``
        :param top: the layout's top. Default value is ``0``
        :param left: the layout's left. Default value is ``0``
        :param layout_name: the layout's name. Default value is ``l1``
        :param um: the layout's unit of measurement. Default value is ``mm``
        :param border_size: the size of the layout's border. Default value is ``0.1``
        :param border_color: the color of the layout's border. Default value is ``red``
        :param lbl_height: the height of the layout's label. Default value is ``3``
        :param lbl_class: the class of the layout's label. Default value is ``lbl_base``
        :param content_class: the class of the layout's content. Default value is ``content_base``
        :param border_style: the syle of the layout's border. Default value is ``solid``
        :returns: the layout
        """
        parentNode = self.parentNode
        if parentNode.getAttr('tag') == 'cell':
            if not width:
                width = float(parentNode.getAttr('width'))
                
        self.style(self.globalCss(layout_name=layout_name, um=um, border_size=border_size,
                                  border_color=border_color,
                                  border_style=border_style))

        container = self.child(tag='layout', width=width, height=height,
                               top=top, left=left, **kwargs)
        container.height = height
        container.width = width
        container.border_size = float(border_size)
        container.um = um
        container.lbl_height = lbl_height
        container.lbl_class = lbl_class
        container.content_class = content_class
        container.layout_name = layout_name
        container.height_calc = 0
        return container
        
    def row(self, height=0, **kwargs):
        """Build the height
        
        :param height: the row's height. Default value is ``0``
        :returns: the row
        """
        container = self
        row = container.child(tag='row', height=height,
                              width=container.width,
                              **kwargs)
        row.idx = len(container) - 1
        row.container = container
        
        row.um = container.um
        row.layout_name = container.layout_name
        row.border_size = container.border_size
        row.height = height
        row.max_width = float(container.width or '0')
        row.delta_y = '%spx' % ((len(container) - 1) * container.border_size)
        row.curr_x = 0
        return row
        
    def borderWidths(self, b):
        """Define the border's width
        
        :param b: the border
        :returns: the border's width
        """
        b = b.upper()
        borders = ['T' in b, 'R' in b, 'B' in b, 'L' in b]
        if True in borders:
            return 'border-width:%s;' % ' '.join([('%spx') % int(x) for x in borders])
            
    def cell(self, content=None, width=0, lbl=None, lbl_class=None, lbl_height=None, content_class=None, **kwargs):
        """Define a cell
        
        :param content: the cell's content. Default value is ``None``
        :param width: the cell's width. Default value is ``0``
        :param lbl: the cell's lbl. Default value is ``None``
        :param lbl_class: the cell's lbl_class. Default value is ``None``
        :param lbl_height: the cell's lbl_height. Default value is ``None``
        :param content_class: the cell's content_class. Default value is ``None``
        :returns: the cell
        """
        row = self
        width = float(width)
        um = row.container.um
        dbs = row.border_size
        content_class = content_class or row.container.content_class
        if lbl:
            lbl_height = lbl_height or row.container.lbl_height
            lbl_class = lbl_class or row.container.lbl_class
            cell = row.child(tag='cell', width=width, idx=len(row), **kwargs)
            caption_attr = {'class': lbl_class, 'top': dbs, 'height': lbl_height, 'left': dbs, 'right': dbs}
            self.setValueAndUm(caption_attr, um=um, position='absolute')
            cell.child('div', content=lbl, **caption_attr)
            content_attr = {'class': content_class, 'top': dbs + lbl_height}
            self.setValueAndUm(content_attr, um=um, position='absolute')
            cell = cell.child('div', content=content, **content_attr)
        else:
            cell = row.child(tag='cell', content=content, width=width, idx=len(row), **kwargs)
        return cell
        
    def compile_cell(self, cell, tag, attr):
        """Compile a cell
        
        :param cell: the cell
        :param tag: a list of the cell's tag
        :param attr: a dict of the cell's attributes
        :returns: ``tag`` and ``attr`` attributes
        """
        bs = self.border_size
        dbs = min(bs / 2., .2)
        tag = 'div'
        width = float(attr['width'])
        idx = attr.pop('idx')
        if width == 0:
            wl = [float(w) for w in self.digest('#a.width')][idx:]
            width = (self.max_width - (self.curr_x + sum(wl))) / wl.count(0.0)
        if self.height == 0:
            hl = [float(h) for h in self.container.digest('#a.height')][self.idx:]
            self.height = (self.container.height - (self.container.height_calc + sum(hl))) / hl.count(0.0)
        width = width - bs
        attr['width'] = width + dbs
        attr['height'] = self.height - bs + dbs
        attr['class'] = '%s_br' % self.layout_name
        attr['top'] = -dbs
        attr['left'] = self.curr_x - dbs
        self.curr_x = self.curr_x + width + bs
        self.setValueAndUm(attr, self.um)
        return tag, attr
        
    def compile_row(self, row, tag, attr):
        """Compile a row
        
        :param row: the row
        :param tag: a list of the row's tag
        :param attr: a dict of the row's attributes
        :returns: ``tag`` and ``attr`` attributes
        """
        tag = 'div'
        attr['top'] = row.container.height_calc
        self.height_calc = self.height_calc + float(row.height)
        self.setValueAndUm(attr, self.um, position='absolute')
        return tag, attr
        
    def compile_layout(self, layout, tag, attr):
        """Compile the layout
        
        :param layout: the layout
        :param tag: a list of the layout's tag
        :param attr: a dict of the layout's attributes
        :returns: ``tag`` and ``attr`` attributes
        """
        tag = 'div'
        attr['height'] = layout.height_calc - .2
        attr['class'] = '%s_tl' % layout.layout_name
        self.setValueAndUm(attr, layout.um, position='absolute')
        return tag, attr
        
    def setValueAndUm(self, attr, um, **kwargs):
        """add???
        
        :param attr: ???
        :param um: ???
        """
        style = attr.pop('style', '')
        style_dict = dict([(x.split(':')) for x in style.split(';') if x])
        style_dict.update(kwargs)
        for name in ('width', 'height', 'top', 'left', 'right'):
            if name in attr:
                value = attr.pop(name)
                try:
                    value = float(value)
                    i_value = int(value)
                    if i_value == value:
                        value = i_value
                    value = '%s%s' % (value, um)
                except:
                    pass
                style_dict[name] = value
                
        attr['style'] = ''.join(['%s:%s;' % (k, v) for k, v in style_dict.items()])
        
    def globalCss(self, layout_name='', um='mm', border_size=0.1, border_color='gray', border_style='solid'):
        """handle the css attributes
        
        :param layout_name: the layout's name. Default value is ``''``
        :param um: the unit of measurement. Default value is ``mm``
        :param border_size: the border size. Default value is ``0.1``
        :param border_color: the border color. Default value is ``gray``
        :param border_style: the border style. Default value is ``solid``
        :returns: the css attributes
        """
        st = '%s%s %s %s' % (border_size, um, border_style, border_color)
        css = """.%s_tl{border-top:%s;border-left:%s;position:absolute;}
                  .%s_br{border-bottom:%s;border-right:%s;position:absolute;}
               """ % (layout_name, st, st, layout_name, st, st)
        return css
        
class GnrHtmlPdf(object):
    """add???
    """
    def __init__(self, filename=None, **kwargs):
        self.root = GnrHtmlSrc.makeRoot()
        html = self.root.html()
        self.root.head = html.head()
        self.body = html.body()
        
    def toXml(self, filename=None, encoding='UTF-8'):
        """Transform the HTML into a XML, using the ``toXml`` method of the ``gnr.core.gnrbag``
        
        :param filename: the name of the output file. Default value is ``None``
        :param encoding: The multibyte character encoding you choose. Default value is ``UTF-8``
        :returns: the XML file
        """
        return self.root.toXml(filename=filename, encoding=encoding, typeattrs=False, autocreate=True,
                               omitUnknownTypes=True, omitRoot=True, forcedTagAttr='tag', addBagTypeAttr=False)
                               
    def toHtml(self, filename=None):
        """add???
        
        :param filename: add???. Default value is ``None``
        """
        if filename:
            filename = expandpath(filename)
        result = self.root.toHtml()
        return result.toXml(filename=filename, omitRoot=True, autocreate=True)
        
    def toPdf(self, filename=None):
        """Call the PDF webkit generator
        
        :param filename: add???. Default value is ``None``
        """
        pass
        
def test0(body):
    layout = body.layout(width='180', height=100, um='mm', top=10, left=10, border_size=.3,
                         lbl_height=4, lbl_class='z1', content_class='content')
    layout.style(".z1{font-size:7pt;background-color:silver;text-align:center}")
    layout.style(".z2{font-size:9pt;background-color:pink;text-align:right;}")
    layout.style(".content{font-size:12pt;text-align:center;}")
        
    r1 = layout.row(height=20)
    r1.cell('foo', width=40, lbl='name')
    r1.cell()
    r1.cell('bar', width=22)
    r1.cell('spam', width=18)
    r1.cell()
    r1.cell('eggs', width=30)
        
    r2 = layout.row()
    r2.cell(lbl='name', lbl_class='z1')
    subtable = r2.cell(width='80', lbl='name')
    r2.cell('gina', width=30, lbl='name')
        
    r3 = layout.row(height=20)
    r3.cell('a', width='30', lbl='name')
    r3.cell('b', width=20, lbl='name')
    r3.cell('c', width=20, lbl='name', lbl_class='z2')
    r3.cell('', lbl='name')
        
    l2 = subtable.layout(layout_name='inner', um='mm', top=0, left=0, width='80', border_size=.3)
    r = l2.row(height=10)
    r.cell('xx', width=12)
    r.cell('yy', width=22)
    r.cell('zz', width=8)
    r.cell()
    r.cell('tt', width=8)
    r = l2.row()
    r.cell('gg', width=9)
    r.cell('nn', width=12)
    r.cell()
    r.cell('mm', width=6)
        
def test1(body):
    layout = body.layout(width='190mm')
    r1 = layout.row(height='15mm')
    r1.cell('pluto', width='30mm', lbl='name', lbl_class='z1')
    r1.cell('paperino', width='30mm', lbl='name', lbl_class='z1')
    r2 = layout.row(height='90mm')
    leftcol = r2.cell(width='80mm', label='Client info', lbl_class='mainlabel')
    rightcol = r2.cell(lable='Job details', lbl_class='mainlabel')
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
        
def test2(body):
    layout = body.layout(width='190mm')
    r1 = layout.row(height='15mm')
    mycell = r1.cell(width='30mm', lbl='name', lbl_class='z1')
    subrow1 = mycell.row(height='3mm')
    subrow1.cell('nome', width='30mm')
    subrow2 = mycell.row(height='12mm')
    subrow2.cell('pippo', width='30mm')
    r1.cell('pluto', width='90mm')
    r3 = layout.row(height='30mm')
    r3.cell('mario', width='95mm')
    r3.cell('ant', width='95mm')
    r4 = layout.row(height='30mm')
    r4.cell(width='130mm')
    r4.cell(width='60mm')
        
if __name__ == '__main__':
    pdf = GnrHtmlPdf('testbag.pdf')
    body = pdf.body
    test0(body)
    pdf.root.toXml('testhtml/test0.xml', autocreate=True)
    pdf.toHtml('testhtml/test0.html')
    print body