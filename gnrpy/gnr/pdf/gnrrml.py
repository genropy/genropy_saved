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
from lxml import etree
from z3c.rml import document as pdfdoc
import cStringIO
import os
from gnr.core.gnrlang import optArgs

class GnrRmlSrcError(Exception):
    pass

class GnrRmlElem(object):
    def __init__(self, obj, tag):
        self.obj = obj
        self.tag = tag

    def __call__(self, *args, **kwargs):
        child = self.obj.child(self.tag, *args, **kwargs)
        return child


class GnrRmlSrc(GnrStructData):
    rmlNS = ['addMapping', 'alias', 'bar', 'barChart', 'barChart3D', 'barCode', 'barCodeFlowable', 'bars',
             'blockAlignment', 'blockBackground', 'blockBottomPadding', 'blockColBackground', 'blockFont',
             'blockLeading',
             'blockLeftPadding', 'blockRightPadding', 'blockRowBackground', 'blockSpan', 'blockTable', 'blockTableStyle'
             ,
             'blockTextColor', 'blockTopPadding', 'blockValign', 'bookmark', 'bulkData', 'buttonField', 'categoryAxis',
             'circle', 'color', 'condPageBreak', 'curves', 'curvesto', 'curveto', 'document', 'drawAlignedString',
             'drawCenteredString', 'drawCentredString', 'drawRightString', 'drawString', 'ellipse', 'fill', 'fixedSize',
             'frame', 'font', 'grid', 'h1', 'h2', 'h3', 'hr', 'illustration', 'image', 'imageAndFlowables', 'initialize'
             ,
             'indent', 'keepInFrame', 'keepTogether', 'label', 'labels', 'line', 'lineLabels', 'lineMode', 'linePlot',
             'lineStyle', 'lines', 'link', 'moveto', 'name', 'nextFrame', 'option', 'outlineAdd', 'pageGraphics',
             'pageInfo', 'pageTemplate', 'pageNumber', 'para', 'paraStyle', 'param', 'path', 'pieChart', 'pieChart3D',
             'place', 'plugInFlowable', 'pointer', 'pre', 'rect', 'registerCidFont', 'registerFont', 'registerTTFont',
             'registerType1Face', 'rotate', 'scale', 'selectField', 'series', 'setFont', 'setNextFrame',
             'setNextTemplate', 'skew', 'slice', 'slices', 'spacer', 'spiderChart', 'spoke', 'spokeLabels', 'spokes',
             'stylesheet', 'story', 'strand', 'strandLabels', 'strands', 'stroke', 'td', 'tr', 'template', 'text',
             'textAnnotation', 'textField', 'title', 'transform', 'translate', 'valueAxis', 'xValueAxis', 'xpre',
             'yValueAxis']

    gnrNS = ['string', 'content']

    genroNameSpace = dict([(name.lower(), name) for name in rmlNS])
    genroNameSpace.update(dict([(name.lower(), name) for name in gnrNS]))

    def __getattr__(self, fname):
        fnamelower = fname.lower()
        if (fname != fnamelower) and hasattr(self, fnamelower):
            return getattr(self, fnamelower)
        elif fnamelower in self.genroNameSpace:
            return GnrRmlElem(self, '%s' % (self.genroNameSpace[fnamelower]))
        else:
            raise AttributeError("object has no attribute '%s'" % fname)

    def string(self, content=None, align='L', **kwargs):
        if align.lower() in ('r', 'right'):
            self.drawRightString(content=content, **kwargs)
        elif align.lower() in ('c', 'center'):
            self.drawCenteredString(content=content, **kwargs)
        else:
            self.drawString(content=content, **kwargs)

    def toRml(self, filename=None, encoding='UTF-8'):
        return self.toXml(filename=filename, encoding=encoding, typeattrs=False, autocreate=True,
                          omitUnknownTypes=True, omitRoot=True, forcedTagAttr='tag', addBagTypeAttr=False)

    def __content(self, content):
        self.child('__flatten__', content=content)

    def content(self, content):
        if not (isinstance(content, list) or isinstance(content, tuple) ):
            content = [content]
        for single_content in content:
            if isinstance(single_content, GnrRmlSrc):
                childattr = dict(single_content.parentNode.attr)
                tag = childattr.pop('tag')
                self.child(tag, content=single_content, **childattr)
            else:
                self.child('__flatten__', content=single_content)

    def _get_um(self):
        if self._um:
            return um
        if self.parent:
            return self.parent.um
        return 'pt'

    def child(self, tag, *args, **kwargs):
        um = kwargs.pop('um', None)
        if um:
            self._um = um
        if 'name' in kwargs:
            kwargs['_name'] = kwargs.pop('name')
        kwargs = optArgs(**kwargs)
        return super(GnrRmlSrc, self).child(tag, *args, **kwargs)


    def paraStyle(self, name='', fontName=None, fontSize=None, leading=None, leftIndent=None,
                  rightIndent=None, firstLineIndent=None, spaceBefore=None, spaceAfter=None,
                  alignment=None, bulletFontName=None, bulletFontSize=None, bulletIndent=None,
                  textColor=None, backColor=None, keepWithNext=None, wordWrap=None, alias=None, parent=None):
        return self.child('paraStyle', name=name, fontName=fontName, fontSize=fontSize, leading=leading,
                          leftIndent=leftIndent, rightIndent=rightIndent, firstLineIndent=firstLineIndent,
                          spaceBefore=spaceBefore, spaceAfter=spaceAfter, alignment=alignment,
                          bulletFontName=bulletFontName, bulletFontSize=bulletFontSize, bulletIndent=bulletIndent,
                          textColor=textColor, backColor=backColor, keepWithNext=keepWithNext,
                          wordWrap=wordWrap, alias=alias, parent=parent)

    def _tagType(self):
        return self.parentNode.attr['tag']

    tagType = property(_tagType)

    def _getRow(self, rowidx):
        if rowidx is None:
            rowidx = len(self) + 1
        while len(self) < rowidx:
            r = self.tr()
            while len(r) < self.cols:
                r.td()
        return r


    def row(self, cell_list=None, height=None, startcol=0, rowidx=None, **kwargs):
        def fill_cell(cellidx, cell):
            destcell = row.cell(cellidx)
            if isinstance(cell, tuple) and isinstance(cell[-1], dict):
                destcell.parentNode.attr = cell[-1]
                cell = cell[0]
            destcell.content(cell)

        row = self._getRow(rowidx)
        if isinstance(cell_list, list):
            for i, cell in enumerate(cell_list):
                fill_cell(startcol + i, cell)
        else:
            for cellname, cellidx in self.columns.items():
                fill_cell(cellidx, kwargs.get(cellname))

        return row

    def cell(self, rowidx, colidx=None):
        if self.tagType == 'tr':
            cellidx = rowidx
            row = self
        else:
            cellidx = colidx
            while len(self) < rowidx:
                self.row()
            row = self['#%i' % rowidx]
        if cellidx < 0:
            cellidx = len(row) + cellidx
        return row['#%i' % int(cellidx)]

    #def cellStyle(self, rowidx, colidx, rowspan=None, colspan=None,):

    def blockTableStyle(self, id='', keepWithNext=None):
        return self.child('blockTableStyle', id=id, keepWithNext=keepWithNext)

    def document(self, filename=None, debug=None, compression=None, invariant=None, **kwargs):
        return self.child('document', filename=filename, debug=debug, compression=compression, invariant=invariant,
                          **kwargs)

    def registerType1Face(self, afmFile=None, pfbFile=None, **kwargs):
        return self.child('registerType1Face', afmFile=afmFile, pfbFile=pfbFile, **kwargs)

    def registerFont(self, name=None, faceName=None, encName=None, **kwargs):
        return self.child('registerFont', name=name, faceName=faceName, encName=encName, **kwargs)

    def registerTTFont(self, faceName=None, fileName=None, **kwargs):
        return self.child('registerTTFont', faceName=faceName, fileName=fileName, **kwargs)

    def registerCidFont(self, faceName=None, **kwargs):
        return self.child('registerCidFont', faceName=faceName, **kwargs)

    def color(self, id=None, value=None, **kwargs):
        return self.child('color', id=id, value=value, **kwargs)

    def addMapping(self, faceName=None, bold=None, italic=None, psName=None, **kwargs):
        return self.child('addMapping', faceName=faceName, bold=bold, italic=italic, psName=psName, **kwargs)

    def name(self, id=None, value=None, text=None, **kwargs):
        return self.child('name', id=id, value=value, text=text, **kwargs)

    def alias(self, id=None, value=None, **kwargs):
        return self.child('alias', id=id, value=value, **kwargs)

    def paraStyle(self, fontName=None, fontSize=None, leading=None, leftIndent=None, rightIndent=None,
                  firstLineIndent=None, spaceBefore=None, spaceAfter=None, alignment=None, bulletFontName=None,
                  bulletFontSize=None, bulletIndent=None, textColor=None, backColor=None, keepWithNext=None,
                  wordWrap=None, name=None, alias=None, parent=None, **kwargs):
        return self.child('paraStyle', fontName=fontName, fontSize=fontSize, leading=leading, leftIndent=leftIndent,
                          rightIndent=rightIndent, firstLineIndent=firstLineIndent, spaceBefore=spaceBefore,
                          spaceAfter=spaceAfter, alignment=alignment, bulletFontName=bulletFontName,
                          bulletFontSize=bulletFontSize, bulletIndent=bulletIndent, textColor=textColor,
                          backColor=backColor, keepWithNext=keepWithNext, wordWrap=wordWrap, name=name, alias=alias,
                          parent=parent, **kwargs)

    def blockTableStyle(self, id=None, keepWithNext=None, **kwargs):
        return self.child('blockTableStyle', id=id, keepWithNext=keepWithNext, **kwargs)

    def blockFont(self, start=None, stop=None, name=None, size=None, leading=None, **kwargs):
        return self.child('blockFont', start=start, stop=stop, name=name, size=size, leading=leading, **kwargs)

    def blockLeading(self, start=None, stop=None, length=None, **kwargs):
        return self.child('blockLeading', start=start, stop=stop, length=length, **kwargs)

    def blockTextColor(self, start=None, stop=None, colorName=None, **kwargs):
        return self.child('blockTextColor', start=start, stop=stop, colorName=colorName, **kwargs)

    def blockAlignment(self, start=None, stop=None, value=None, **kwargs):
        return self.child('blockAlignment', start=start, stop=stop, value=value, **kwargs)

    def blockLeftPadding(self, start=None, stop=None, length=None, **kwargs):
        return self.child('blockLeftPadding', start=start, stop=stop, length=length, **kwargs)

    def blockRightPadding(self, start=None, stop=None, length=None, **kwargs):
        return self.child('blockRightPadding', start=start, stop=stop, length=length, **kwargs)

    def blockBottomPadding(self, start=None, stop=None, length=None, **kwargs):
        return self.child('blockBottomPadding', start=start, stop=stop, length=length, **kwargs)

    def blockTopPadding(self, start=None, stop=None, length=None, **kwargs):
        return self.child('blockTopPadding', start=start, stop=stop, length=length, **kwargs)

    def blockBackground(self, start=None, stop=None, colorName=None, colorsByRow=None, colorsByCol=None, **kwargs):
        return self.child('blockBackground', start=start, stop=stop, colorName=colorName, colorsByRow=colorsByRow,
                          colorsByCol=colorsByCol, **kwargs)

    def blockRowBackground(self, start=None, stop=None, colorNames=None, **kwargs):
        return self.child('blockRowBackground', start=start, stop=stop, colorNames=colorNames, **kwargs)

    def blockColBackground(self, start=None, stop=None, colorNames=None, **kwargs):
        return self.child('blockColBackground', start=start, stop=stop, colorNames=colorNames, **kwargs)

    def blockValign(self, start=None, stop=None, value=None, **kwargs):
        return self.child('blockValign', start=start, stop=stop, value=value, **kwargs)

    def blockSpan(self, block_list=None, start=None, stop=None, **kwargs):
        if block_list:
            for start, stop in block_list:
                self.child('blockSpan', start=start, stop=stop, **kwargs)
        else:
            self.child('blockSpan', start=start, stop=stop, **kwargs)

    def lineStyle(self, start=None, stop=None, kind=None, thickness=None, colorName=None, cap=None, dash=None, join=None
                  , count=None, **kwargs):
        return self.child('lineStyle', start=start, stop=stop, kind=kind, thickness=thickness, colorName=colorName,
                          cap=cap, dash=dash, join=join, count=count, **kwargs)

    def template(self, pagesize=None, rotation=None, leftMargin=None, rightMargin=None, topMargin=None,
                 bottomMargin=None, showBoundary=None, allowSplitting=None, title=None, author=None, **kwargs):
        return self.child('template', pagesize=pagesize, rotation=rotation, leftMargin=leftMargin,
                          rightMargin=rightMargin, topMargin=topMargin, bottomMargin=bottomMargin,
                          showBoundary=showBoundary, allowSplitting=allowSplitting, title=title, author=author,
                          **kwargs)

    def pageTemplate(self, id=None, pagesize=None, rotation=None, **kwargs):
        return self.child('pageTemplate', id=id, pagesize=pagesize, rotation=rotation, **kwargs)

    def frame(self, x1=None, y1=None, width=None, height=None, id=None, leftPadding=None, rightPadding=None,
              topPadding=None, bottomPadding=None, showBoundary=None, **kwargs):
        return self.child('frame', x1=x1, y1=y1, width=width, height=height, id=id, leftPadding=leftPadding,
                          rightPadding=rightPadding, topPadding=topPadding, bottomPadding=bottomPadding,
                          showBoundary=showBoundary, **kwargs)

    def story(self, firstPageTemplate=None, **kwargs):
        return self.child('story', firstPageTemplate=firstPageTemplate, **kwargs)

    def spacer(self, width=None, length=None, **kwargs):
        return self.child('spacer', width=width, length=length, **kwargs)

    def illustration(self, width=None, height=None, **kwargs):
        return self.child('illustration', width=width, height=height, **kwargs)

    def pre(self, style=None, bulletText=None, dedent=None, text=None, **kwargs):
        return self.child('pre', style=style, bulletText=bulletText, dedent=dedent, text=text, **kwargs)

    def xpre(self, style=None, bulletText=None, dedent=None, text=None, **kwargs):
        return self.child('xpre', style=style, bulletText=bulletText, dedent=dedent, text=text, **kwargs)

    def plugInFlowable(self, module=None, function=None, params=None, **kwargs):
        return self.child('plugInFlowable', module=module, function=function, params=params, **kwargs)

    def barCodeFlowable(self, code=None, width=None, height=None, strokeColor=None, strokeWidth=None, fillColor=None,
                        barStrokeColor=None, barStrokeWidth=None, barFillColor=None, gap=None, barWidth=None,
                        barHeight=None, ratio=None, checksum=None, bearers=None, quiet=None, lquiet=None, rquiet=None,
                        fontName=None, fontSize=None, humanReadable=None, stop=None, spaceWidth=None, shortHeight=None,
                        textColor=None, value=None, **kwargs):
        return self.child('barCodeFlowable', code=code, width=width, height=height, strokeColor=strokeColor,
                          strokeWidth=strokeWidth, fillColor=fillColor, barStrokeColor=barStrokeColor,
                          barStrokeWidth=barStrokeWidth, barFillColor=barFillColor, gap=gap, barWidth=barWidth,
                          barHeight=barHeight, ratio=ratio, checksum=checksum, bearers=bearers, quiet=quiet,
                          lquiet=lquiet, rquiet=rquiet, fontName=fontName, fontSize=fontSize,
                          humanReadable=humanReadable, stop=stop, spaceWidth=spaceWidth, shortHeight=shortHeight,
                          textColor=textColor, value=value, **kwargs)

    def outlineAdd(self, title=None, key=None, level=None, closed=None, **kwargs):
        return self.child('outlineAdd', title=title, key=key, level=level, closed=closed, **kwargs)

    def title(self, fontName=None, fontSize=None, leading=None, leftIndent=None, rightIndent=None, firstLineIndent=None,
              spaceBefore=None, spaceAfter=None, alignment=None, bulletFontName=None, bulletFontSize=None,
              bulletIndent=None, textColor=None, backColor=None, keepWithNext=None, wordWrap=None, bulletText=None,
              dedent=None, text=None, style=None, **kwargs):
        return self.child('title', fontName=fontName, fontSize=fontSize, leading=leading, leftIndent=leftIndent,
                          rightIndent=rightIndent, firstLineIndent=firstLineIndent, spaceBefore=spaceBefore,
                          spaceAfter=spaceAfter, alignment=alignment, bulletFontName=bulletFontName,
                          bulletFontSize=bulletFontSize, bulletIndent=bulletIndent, textColor=textColor,
                          backColor=backColor, keepWithNext=keepWithNext, wordWrap=wordWrap, bulletText=bulletText,
                          dedent=dedent, text=text, style=style, **kwargs)

    def h1(self, fontName=None, fontSize=None, leading=None, leftIndent=None, rightIndent=None, firstLineIndent=None,
           spaceBefore=None, spaceAfter=None, alignment=None, bulletFontName=None, bulletFontSize=None,
           bulletIndent=None, textColor=None, backColor=None, keepWithNext=None, wordWrap=None, bulletText=None,
           dedent=None, text=None, style=None, **kwargs):
        return self.child('h1', fontName=fontName, fontSize=fontSize, leading=leading, leftIndent=leftIndent,
                          rightIndent=rightIndent, firstLineIndent=firstLineIndent, spaceBefore=spaceBefore,
                          spaceAfter=spaceAfter, alignment=alignment, bulletFontName=bulletFontName,
                          bulletFontSize=bulletFontSize, bulletIndent=bulletIndent, textColor=textColor,
                          backColor=backColor, keepWithNext=keepWithNext, wordWrap=wordWrap, bulletText=bulletText,
                          dedent=dedent, text=text, style=style, **kwargs)

    def h2(self, fontName=None, fontSize=None, leading=None, leftIndent=None, rightIndent=None, firstLineIndent=None,
           spaceBefore=None, spaceAfter=None, alignment=None, bulletFontName=None, bulletFontSize=None,
           bulletIndent=None, textColor=None, backColor=None, keepWithNext=None, wordWrap=None, bulletText=None,
           dedent=None, text=None, style=None, **kwargs):
        return self.child('h2', fontName=fontName, fontSize=fontSize, leading=leading, leftIndent=leftIndent,
                          rightIndent=rightIndent, firstLineIndent=firstLineIndent, spaceBefore=spaceBefore,
                          spaceAfter=spaceAfter, alignment=alignment, bulletFontName=bulletFontName,
                          bulletFontSize=bulletFontSize, bulletIndent=bulletIndent, textColor=textColor,
                          backColor=backColor, keepWithNext=keepWithNext, wordWrap=wordWrap, bulletText=bulletText,
                          dedent=dedent, text=text, style=style, **kwargs)

    def h3(self, fontName=None, fontSize=None, leading=None, leftIndent=None, rightIndent=None, firstLineIndent=None,
           spaceBefore=None, spaceAfter=None, alignment=None, bulletFontName=None, bulletFontSize=None,
           bulletIndent=None, textColor=None, backColor=None, keepWithNext=None, wordWrap=None, bulletText=None,
           dedent=None, text=None, style=None, **kwargs):
        return self.child('h3', fontName=fontName, fontSize=fontSize, leading=leading, leftIndent=leftIndent,
                          rightIndent=rightIndent, firstLineIndent=firstLineIndent, spaceBefore=spaceBefore,
                          spaceAfter=spaceAfter, alignment=alignment, bulletFontName=bulletFontName,
                          bulletFontSize=bulletFontSize, bulletIndent=bulletIndent, textColor=textColor,
                          backColor=backColor, keepWithNext=keepWithNext, wordWrap=wordWrap, bulletText=bulletText,
                          dedent=dedent, text=text, style=style, **kwargs)

    def para(self, content=None, fontName=None, fontSize=None, leading=None, leftIndent=None, rightIndent=None,
             firstLineIndent=None, spaceBefore=None, spaceAfter=None, alignment=None, bulletFontName=None,
             bulletFontSize=None, bulletIndent=None, textColor=None, backColor=None, keepWithNext=None, wordWrap=None,
             style=None, bulletText=None, dedent=None, text=None, **kwargs):
        para = self.child('para', fontName=fontName, fontSize=fontSize, leading=leading, leftIndent=leftIndent,
                          rightIndent=rightIndent, firstLineIndent=firstLineIndent, spaceBefore=spaceBefore,
                          spaceAfter=spaceAfter, alignment=alignment, bulletFontName=bulletFontName,
                          bulletFontSize=bulletFontSize, bulletIndent=bulletIndent, textColor=textColor,
                          backColor=backColor, keepWithNext=keepWithNext, wordWrap=wordWrap, style=style,
                          bulletText=bulletText, dedent=dedent, text=text, **kwargs)
        if content:
            para.content(content)
        return para

    def blockTable(self, style=None, rowHeights=None, colWidths=None, repeatRows=None, alignment=None, **kwargs):
        colIndex_dict = {}
        col_list = colWidths.split(',')
        colWidths_list = []
        for idx, col in enumerate(col_list):
            if ':' in col:
                name, width = col.split(':')
            else:
                name = 'c%i' % idx
                width = col
            colWidths_list.append(width)
            colIndex_dict[name] = idx
        colWidths = ','.join(colWidths_list)
        child = self.child('blockTable', style=style, rowHeights=rowHeights, colWidths=colWidths, repeatRows=repeatRows,
                           alignment=alignment, **kwargs)
        child.cols = len(col_list)
        child.columns = colIndex_dict
        return child

    def td(self, content=None, fontName=None, fontSize=None, leading=None, fontColor=None, leftPadding=None,
           rightPadding=None, topPadding=None, bottomPadding=None, background=None, align=None, vAlign=None,
           lineBelowThickness=None, lineBelowColor=None, lineBelowCap=None, lineBelowCount=None, lineBelowSpace=None,
           lineAboveThickness=None, lineAboveColor=None, lineAboveCap=None, lineAboveCount=None, lineAboveSpace=None,
           lineLeftThickness=None, lineLeftColor=None, lineLeftCap=None, lineLeftCount=None, lineLeftSpace=None,
           lineRightThickness=None, lineRightColor=None, lineRightCap=None, lineRightCount=None, lineRightSpace=None,
           **kwargs):
        return self.child('td', content=content, fontName=fontName, fontSize=fontSize, leading=leading,
                          fontColor=fontColor, leftPadding=leftPadding, rightPadding=rightPadding, topPadding=topPadding
                          , bottomPadding=bottomPadding, background=background, align=align, vAlign=vAlign,
                          lineBelowThickness=lineBelowThickness, lineBelowColor=lineBelowColor,
                          lineBelowCap=lineBelowCap, lineBelowCount=lineBelowCount, lineBelowSpace=lineBelowSpace,
                          lineAboveThickness=lineAboveThickness, lineAboveColor=lineAboveColor,
                          lineAboveCap=lineAboveCap, lineAboveCount=lineAboveCount, lineAboveSpace=lineAboveSpace,
                          lineLeftThickness=lineLeftThickness, lineLeftColor=lineLeftColor, lineLeftCap=lineLeftCap,
                          lineLeftCount=lineLeftCount, lineLeftSpace=lineLeftSpace,
                          lineRightThickness=lineRightThickness, lineRightColor=lineRightColor,
                          lineRightCap=lineRightCap, lineRightCount=lineRightCount, lineRightSpace=lineRightSpace,
                          **kwargs)

    def bulkData(self, content=None, **kwargs):
        return self.child('bulkData', content=content, **kwargs)

    def nextFrame(self, name=None, **kwargs):
        return self.child('nextFrame', name=name, **kwargs)

    def setNextFrame(self, name=None, **kwargs):
        return self.child('setNextFrame', name=name, **kwargs)

    def setNextTemplate(self, name=None, **kwargs):
        return self.child('setNextTemplate', name=name, **kwargs)

    def condPageBreak(self, height=None, **kwargs):
        return self.child('condPageBreak', height=height, **kwargs)

    def keepInFrame(self, maxWidth=None, maxHeight=None, mergeSpace=None, onOverflow=None, id=None, frame=None,
                    **kwargs):
        return self.child('keepInFrame', maxWidth=maxWidth, maxHeight=maxHeight, mergeSpace=mergeSpace,
                          onOverflow=onOverflow, id=id, frame=frame, **kwargs)

    def keepTogether(self, maxHeight=None, **kwargs):
        return self.child('keepTogether', maxHeight=maxHeight, **kwargs)

    def imageAndFlowables(self, imageName=None, imageWidth=None, imageHeight=None, imageMask=None, imageLeftPadding=None
                          , imageRightPadding=None, imageTopPadding=None, imageBottomPadding=None, imageSide=None,
                          **kwargs):
        return self.child('imageAndFlowables', imageName=imageName, imageWidth=imageWidth, imageHeight=imageHeight,
                          imageMask=imageMask, imageLeftPadding=imageLeftPadding, imageRightPadding=imageRightPadding,
                          imageTopPadding=imageTopPadding, imageBottomPadding=imageBottomPadding, imageSide=imageSide,
                          **kwargs)

    def indent(self, left=None, right=None, **kwargs):
        return self.child('indent', left=left, right=right, **kwargs)

    def fixedSize(self, width=None, height=None, **kwargs):
        return self.child('fixedSize', width=width, height=height, **kwargs)

    def bookmark(self, name=None, fitType=None, left=None, top=None, right=None, zoom=None, **kwargs):
        return self.child('bookmark', name=name, fitType=fitType, left=left, top=top, right=right, zoom=zoom, **kwargs)

    def link(self, destination=None, url=None, boxStrokeWidth=None, boxStrokeDashArray=None, boxStrokeColor=None,
             **kwargs):
        return self.child('link', destination=destination, url=url, boxStrokeWidth=boxStrokeWidth,
                          boxStrokeDashArray=boxStrokeDashArray, boxStrokeColor=boxStrokeColor, **kwargs)

    def hr(self, width=None, thickness=None, color=None, lineCap=None, spaceBefore=None, spaceAfter=None, align=None,
           valign=None, dash=None, **kwargs):
        return self.child('hr', width=width, thickness=thickness, color=color, lineCap=lineCap, spaceBefore=spaceBefore,
                          spaceAfter=spaceAfter, align=align, valign=valign, dash=dash, **kwargs)

    def pageInfo(self, pageSize=None, **kwargs):
        return self.child('pageInfo', pageSize=pageSize, **kwargs)

    def drawString(self, x=None, y=None, text=None, **kwargs):
        return self.child('drawString', x=x, y=y, text=text, **kwargs)

    def drawRightString(self, x=None, y=None, text=None, **kwargs):
        return self.child('drawRightString', x=x, y=y, text=text, **kwargs)

    def drawCenteredString(self, x=None, y=None, text=None, **kwargs):
        return self.child('drawCenteredString', x=x, y=y, text=text, **kwargs)

    def drawCentredString(self, x=None, y=None, text=None, **kwargs):
        return self.child('drawCentredString', x=x, y=y, text=text, **kwargs)

    def drawAlignedString(self, x=None, y=None, text=None, pivotChar=None, **kwargs):
        return self.child('drawAlignedString', x=x, y=y, text=text, pivotChar=pivotChar, **kwargs)

    def ellipse(self, x=None, y=None, fill=None, stroke=None, width=None, height=None, **kwargs):
        return self.child('ellipse', x=x, y=y, fill=fill, stroke=stroke, width=width, height=height, **kwargs)

    def circle(self, x=None, y=None, fill=None, stroke=None, radius=None, **kwargs):
        return self.child('circle', x=x, y=y, fill=fill, stroke=stroke, radius=radius, **kwargs)

    def rect(self, x=None, y=None, fill=None, stroke=None, width=None, height=None, round=None, **kwargs):
        return self.child('rect', x=x, y=y, fill=fill, stroke=stroke, width=width, height=height, round=round, **kwargs)

    def grid(self, xs=None, ys=None, **kwargs):
        return self.child('grid', xs=xs, ys=ys, **kwargs)

    def lines(self, linelist=None, strokeWidth=None, strokeColor=None, strokeDashArray=None, symbol=None, **kwargs):
        return self.child('lines', linelist=linelist, strokeWidth=strokeWidth, strokeColor=strokeColor,
                          strokeDashArray=strokeDashArray, symbol=symbol, **kwargs)

    def curves(self, curvelist=None, **kwargs):
        return self.child('curves', curvelist=curvelist, **kwargs)

    def image(self, file=None, x=None, y=None, width=None, height=None, showBoundary=None, preserveAspectRatio=None,
              **kwargs):
        return self.child('image', file=file, x=x, y=y, width=width, height=height, showBoundary=showBoundary,
                          preserveAspectRatio=preserveAspectRatio, **kwargs)

    def place(self, x=None, y=None, width=None, height=None, **kwargs):
        return self.child('place', x=x, y=y, width=width, height=height, **kwargs)

    def textAnnotation(self, contents=None, **kwargs):
        return self.child('textAnnotation', contents=contents, **kwargs)

    def param(self, name=None, value=None, **kwargs):
        return self.child('param', name=name, value=value, **kwargs)

    def path(self, x=None, y=None, fill=None, stroke=None, points=None, close=None, **kwargs):
        return self.child('path', x=x, y=y, fill=fill, stroke=stroke, points=points, close=close, **kwargs)

    def moveto(self, position=None, **kwargs):
        return self.child('moveto', position=position, **kwargs)

    def curveto(self, curvelist=None, **kwargs):
        return self.child('curveto', curvelist=curvelist, **kwargs)

    def curvesto(self, curvelist=None, **kwargs):
        return self.child('curvesto', curvelist=curvelist, **kwargs)

    def fill(self, color=None, **kwargs):
        return self.child('fill', color=color, **kwargs)

    def stroke(self, color=None, **kwargs):
        return self.child('stroke', color=color, **kwargs)

    def setFont(self, name=None, size=None, leading=None, **kwargs):
        return self.child('setFont', name=name, size=size, leading=leading, **kwargs)

    def scale(self, sx=None, sy=None, **kwargs):
        return self.child('scale', sx=sx, sy=sy, **kwargs)

    def translate(self, dx=None, dy=None, **kwargs):
        return self.child('translate', dx=dx, dy=dy, **kwargs)

    def rotate(self, degrees=None, **kwargs):
        return self.child('rotate', degrees=degrees, **kwargs)

    def skew(self, alpha=None, beta=None, **kwargs):
        return self.child('skew', alpha=alpha, beta=beta, **kwargs)

    def transform(self, matrix=None, **kwargs):
        return self.child('transform', matrix=matrix, **kwargs)

    def lineMode(self, width=None, dash=None, miterLimit=None, join=None, cap=None, **kwargs):
        return self.child('lineMode', width=width, dash=dash, miterLimit=miterLimit, join=join, cap=cap, **kwargs)

    def barCode(self, code=None, value=None, width=None, height=None, strokeColor=None, strokeWidth=None, fillColor=None
                , barStrokeColor=None, barStrokeWidth=None, barFillColor=None, gap=None, barWidth=None, barHeight=None,
                ratio=None, checksum=None, bearers=None, quiet=None, lquiet=None, rquiet=None, fontName=None,
                fontSize=None, humanReadable=None, stop=None, spaceWidth=None, shortHeight=None, textColor=None, x=None,
                y=None, **kwargs):
        return self.child('barCode', code=code, value=value, width=width, height=height, strokeColor=strokeColor,
                          strokeWidth=strokeWidth, fillColor=fillColor, barStrokeColor=barStrokeColor,
                          barStrokeWidth=barStrokeWidth, barFillColor=barFillColor, gap=gap, barWidth=barWidth,
                          barHeight=barHeight, ratio=ratio, checksum=checksum, bearers=bearers, quiet=quiet,
                          lquiet=lquiet, rquiet=rquiet, fontName=fontName, fontSize=fontSize,
                          humanReadable=humanReadable, stop=stop, spaceWidth=spaceWidth, shortHeight=shortHeight,
                          textColor=textColor, x=x, y=y, **kwargs)

    def textField(self, title=None, x=None, y=None, width=None, height=None, value=None, maxLength=None, multiline=None,
                  **kwargs):
        return self.child('textField', title=title, x=x, y=y, width=width, height=height, value=value,
                          maxLength=maxLength, multiline=multiline, **kwargs)

    def buttonField(self, title=None, x=None, y=None, value=None, **kwargs):
        return self.child('buttonField', title=title, x=x, y=y, value=value, **kwargs)

    def selectField(self, title=None, x=None, y=None, width=None, height=None, value=None, **kwargs):
        return self.child('selectField', title=title, x=x, y=y, width=width, height=height, value=value, **kwargs)

    def option(self, value=None, **kwargs):
        return self.child('option', value=value, **kwargs)

    def barChart(self, dx=None, dy=None, dwidth=None, dheight=None, angle=None, x=None, y=None, width=None, height=None,
                 strokeColor=None, strokeWidth=None, fillColor=None, debug=None, direction=None, useAbsolute=None,
                 barWidth=None, groupSpacing=None, barSpacing=None, **kwargs):
        return self.child('barChart', dx=dx, dy=dy, dwidth=dwidth, dheight=dheight, angle=angle, x=x, y=y, width=width,
                          height=height, strokeColor=strokeColor, strokeWidth=strokeWidth, fillColor=fillColor,
                          debug=debug, direction=direction, useAbsolute=useAbsolute, barWidth=barWidth,
                          groupSpacing=groupSpacing, barSpacing=barSpacing, **kwargs)

    def series(self, values=None, **kwargs):
        return self.child('series', values=values, **kwargs)

    def bars(self, strokeColor=None, strokeWidth=None, fillColor=None, **kwargs):
        return self.child('bars', strokeColor=strokeColor, strokeWidth=strokeWidth, fillColor=fillColor, **kwargs)

    def bar(self, strokeColor=None, strokeWidth=None, fillColor=None, **kwargs):
        return self.child('bar', strokeColor=strokeColor, strokeWidth=strokeWidth, fillColor=fillColor, **kwargs)

    def categoryAxis(self, visible=None, visibleAxis=None, visibleTicks=None, visibleLabels=None, visibleGrid=None,
                     strokeWidth=None, strokeColor=None, strokeDashArray=None, gridStrokeWidth=None,
                     gridStrokeColor=None, gridStrokeDashArray=None, gridStart=None, gridEnd=None, style=None,
                     categoryNames=None, joinAxis=None, joinAxisPos=None, reverseDirection=None, labelAxisMode=None,
                     tickShift=None, **kwargs):
        return self.child('categoryAxis', visible=visible, visibleAxis=visibleAxis, visibleTicks=visibleTicks,
                          visibleLabels=visibleLabels, visibleGrid=visibleGrid, strokeWidth=strokeWidth,
                          strokeColor=strokeColor, strokeDashArray=strokeDashArray, gridStrokeWidth=gridStrokeWidth,
                          gridStrokeColor=gridStrokeColor, gridStrokeDashArray=gridStrokeDashArray, gridStart=gridStart,
                          gridEnd=gridEnd, style=style, categoryNames=categoryNames, joinAxis=joinAxis,
                          joinAxisPos=joinAxisPos, reverseDirection=reverseDirection, labelAxisMode=labelAxisMode,
                          tickShift=tickShift, **kwargs)

    def labels(self, dx=None, dy=None, angle=None, boxAnchor=None, boxStrokeColor=None, boxStrokeWidth=None,
               boxFillColor=None, boxTarget=None, fillColor=None, strokeColor=None, strokeWidth=None, frontName=None,
               frontSize=None, leading=None, width=None, maxWidth=None, height=None, textAnchor=None, visible=None,
               leftPadding=None, rightPadding=None, topPadding=None, bottomPadding=None, x=None, y=None, **kwargs):
        return self.child('labels', dx=dx, dy=dy, angle=angle, boxAnchor=boxAnchor, boxStrokeColor=boxStrokeColor,
                          boxStrokeWidth=boxStrokeWidth, boxFillColor=boxFillColor, boxTarget=boxTarget,
                          fillColor=fillColor, strokeColor=strokeColor, strokeWidth=strokeWidth, frontName=frontName,
                          frontSize=frontSize, leading=leading, width=width, maxWidth=maxWidth, height=height,
                          textAnchor=textAnchor, visible=visible, leftPadding=leftPadding, rightPadding=rightPadding,
                          topPadding=topPadding, bottomPadding=bottomPadding, x=x, y=y, **kwargs)

    def label(self, dx=None, dy=None, angle=None, boxAnchor=None, boxStrokeColor=None, boxStrokeWidth=None,
              boxFillColor=None, boxTarget=None, fillColor=None, strokeColor=None, strokeWidth=None, frontName=None,
              frontSize=None, leading=None, width=None, maxWidth=None, height=None, textAnchor=None, visible=None,
              leftPadding=None, rightPadding=None, topPadding=None, bottomPadding=None, x=None, y=None, text=None,
              _text=None, row=None, col=None, format=None, dR=None, **kwargs):
        return self.child('label', dx=dx, dy=dy, angle=angle, boxAnchor=boxAnchor, boxStrokeColor=boxStrokeColor,
                          boxStrokeWidth=boxStrokeWidth, boxFillColor=boxFillColor, boxTarget=boxTarget,
                          fillColor=fillColor, strokeColor=strokeColor, strokeWidth=strokeWidth, frontName=frontName,
                          frontSize=frontSize, leading=leading, width=width, maxWidth=maxWidth, height=height,
                          textAnchor=textAnchor, visible=visible, leftPadding=leftPadding, rightPadding=rightPadding,
                          topPadding=topPadding, bottomPadding=bottomPadding, x=x, y=y, text=text, _text=_text, row=row,
                          col=col, format=format, dR=dR, **kwargs)

    def valueAxis(self, visible=None, visibleAxis=None, visibleTicks=None, visibleLabels=None, visibleGrid=None,
                  strokeWidth=None, strokeColor=None, strokeDashArray=None, gridStrokeWidth=None, gridStrokeColor=None,
                  gridStrokeDashArray=None, gridStart=None, gridEnd=None, style=None, forceZero=None,
                  minimumTickSpacing=None, maximumTicks=None, labelTextFormat=None, labelTextPostFormat=None,
                  labelTextScale=None, valueMin=None, valueMax=None, valueStep=None, valueSteps=None, rangeRound=None,
                  zrangePref=None, **kwargs):
        return self.child('valueAxis', visible=visible, visibleAxis=visibleAxis, visibleTicks=visibleTicks,
                          visibleLabels=visibleLabels, visibleGrid=visibleGrid, strokeWidth=strokeWidth,
                          strokeColor=strokeColor, strokeDashArray=strokeDashArray, gridStrokeWidth=gridStrokeWidth,
                          gridStrokeColor=gridStrokeColor, gridStrokeDashArray=gridStrokeDashArray, gridStart=gridStart,
                          gridEnd=gridEnd, style=style, forceZero=forceZero, minimumTickSpacing=minimumTickSpacing,
                          maximumTicks=maximumTicks, labelTextFormat=labelTextFormat,
                          labelTextPostFormat=labelTextPostFormat, labelTextScale=labelTextScale, valueMin=valueMin,
                          valueMax=valueMax, valueStep=valueStep, valueSteps=valueSteps, rangeRound=rangeRound,
                          zrangePref=zrangePref, **kwargs)

    def text(self, x=None, y=None, angle=None, text=None, fontName=None, fontSize=None, fillColor=None, textAnchor=None,
             **kwargs):
        return self.child('text', x=x, y=y, angle=angle, text=text, fontName=fontName, fontSize=fontSize,
                          fillColor=fillColor, textAnchor=textAnchor, **kwargs)

    def barChart3D(self, dx=None, dy=None, dwidth=None, dheight=None, angle=None, x=None, y=None, width=None,
                   height=None, strokeColor=None, strokeWidth=None, fillColor=None, debug=None, direction=None,
                   useAbsolute=None, barWidth=None, groupSpacing=None, barSpacing=None, thetaX=None, thetaY=None,
                   zDepth=None, zSpace=None, **kwargs):
        return self.child('barChart3D', dx=dx, dy=dy, dwidth=dwidth, dheight=dheight, angle=angle, x=x, y=y, width=width
                          , height=height, strokeColor=strokeColor, strokeWidth=strokeWidth, fillColor=fillColor,
                          debug=debug, direction=direction, useAbsolute=useAbsolute, barWidth=barWidth,
                          groupSpacing=groupSpacing, barSpacing=barSpacing, thetaX=thetaX, thetaY=thetaY, zDepth=zDepth,
                          zSpace=zSpace, **kwargs)

    def linePlot(self, dx=None, dy=None, dwidth=None, dheight=None, angle=None, x=None, y=None, width=None, height=None,
                 strokeColor=None, strokeWidth=None, fillColor=None, debug=None, reversePlotOrder=None,
                 lineLabelNudge=None, lineLabelFormat=None, joinedLines=None, **kwargs):
        return self.child('linePlot', dx=dx, dy=dy, dwidth=dwidth, dheight=dheight, angle=angle, x=x, y=y, width=width,
                          height=height, strokeColor=strokeColor, strokeWidth=strokeWidth, fillColor=fillColor,
                          debug=debug, reversePlotOrder=reversePlotOrder, lineLabelNudge=lineLabelNudge,
                          lineLabelFormat=lineLabelFormat, joinedLines=joinedLines, **kwargs)

    def line(self, strokeWidth=None, strokeColor=None, strokeDashArray=None, symbol=None, name=None, **kwargs):
        return self.child('line', strokeWidth=strokeWidth, strokeColor=strokeColor, strokeDashArray=strokeDashArray,
                          symbol=symbol, name=name, **kwargs)

    def xValueAxis(self, visible=None, visibleAxis=None, visibleTicks=None, visibleLabels=None, visibleGrid=None,
                   strokeWidth=None, strokeColor=None, strokeDashArray=None, gridStrokeWidth=None, gridStrokeColor=None,
                   gridStrokeDashArray=None, gridStart=None, gridEnd=None, style=None, forceZero=None,
                   minimumTickSpacing=None, maximumTicks=None, labelTextFormat=None, labelTextPostFormat=None,
                   labelTextScale=None, valueMin=None, valueMax=None, valueStep=None, valueSteps=None, rangeRound=None,
                   zrangePref=None, tickUp=None, tickDown=None, joinAxis=None, joinAxisMode=None, joinAxisPos=None,
                   **kwargs):
        return self.child('xValueAxis', visible=visible, visibleAxis=visibleAxis, visibleTicks=visibleTicks,
                          visibleLabels=visibleLabels, visibleGrid=visibleGrid, strokeWidth=strokeWidth,
                          strokeColor=strokeColor, strokeDashArray=strokeDashArray, gridStrokeWidth=gridStrokeWidth,
                          gridStrokeColor=gridStrokeColor, gridStrokeDashArray=gridStrokeDashArray, gridStart=gridStart,
                          gridEnd=gridEnd, style=style, forceZero=forceZero, minimumTickSpacing=minimumTickSpacing,
                          maximumTicks=maximumTicks, labelTextFormat=labelTextFormat,
                          labelTextPostFormat=labelTextPostFormat, labelTextScale=labelTextScale, valueMin=valueMin,
                          valueMax=valueMax, valueStep=valueStep, valueSteps=valueSteps, rangeRound=rangeRound,
                          zrangePref=zrangePref, tickUp=tickUp, tickDown=tickDown, joinAxis=joinAxis,
                          joinAxisMode=joinAxisMode, joinAxisPos=joinAxisPos, **kwargs)

    def yValueAxis(self, visible=None, visibleAxis=None, visibleTicks=None, visibleLabels=None, visibleGrid=None,
                   strokeWidth=None, strokeColor=None, strokeDashArray=None, gridStrokeWidth=None, gridStrokeColor=None,
                   gridStrokeDashArray=None, gridStart=None, gridEnd=None, style=None, forceZero=None,
                   minimumTickSpacing=None, maximumTicks=None, labelTextFormat=None, labelTextPostFormat=None,
                   labelTextScale=None, valueMin=None, valueMax=None, valueStep=None, valueSteps=None, rangeRound=None,
                   zrangePref=None, tickLeft=None, tickRight=None, joinAxis=None, joinAxisMode=None, joinAxisPos=None,
                   **kwargs):
        return self.child('yValueAxis', visible=visible, visibleAxis=visibleAxis, visibleTicks=visibleTicks,
                          visibleLabels=visibleLabels, visibleGrid=visibleGrid, strokeWidth=strokeWidth,
                          strokeColor=strokeColor, strokeDashArray=strokeDashArray, gridStrokeWidth=gridStrokeWidth,
                          gridStrokeColor=gridStrokeColor, gridStrokeDashArray=gridStrokeDashArray, gridStart=gridStart,
                          gridEnd=gridEnd, style=style, forceZero=forceZero, minimumTickSpacing=minimumTickSpacing,
                          maximumTicks=maximumTicks, labelTextFormat=labelTextFormat,
                          labelTextPostFormat=labelTextPostFormat, labelTextScale=labelTextScale, valueMin=valueMin,
                          valueMax=valueMax, valueStep=valueStep, valueSteps=valueSteps, rangeRound=rangeRound,
                          zrangePref=zrangePref, tickLeft=tickLeft, tickRight=tickRight, joinAxis=joinAxis,
                          joinAxisMode=joinAxisMode, joinAxisPos=joinAxisPos, **kwargs)

    def lineLabels(self, dx=None, dy=None, angle=None, boxAnchor=None, boxStrokeColor=None, boxStrokeWidth=None,
                   boxFillColor=None, boxTarget=None, fillColor=None, strokeColor=None, strokeWidth=None, frontName=None
                   , frontSize=None, leading=None, width=None, maxWidth=None, height=None, textAnchor=None, visible=None
                   , leftPadding=None, rightPadding=None, topPadding=None, bottomPadding=None, x=None, y=None,
                   **kwargs):
        return self.child('lineLabels', dx=dx, dy=dy, angle=angle, boxAnchor=boxAnchor, boxStrokeColor=boxStrokeColor,
                          boxStrokeWidth=boxStrokeWidth, boxFillColor=boxFillColor, boxTarget=boxTarget,
                          fillColor=fillColor, strokeColor=strokeColor, strokeWidth=strokeWidth, frontName=frontName,
                          frontSize=frontSize, leading=leading, width=width, maxWidth=maxWidth, height=height,
                          textAnchor=textAnchor, visible=visible, leftPadding=leftPadding, rightPadding=rightPadding,
                          topPadding=topPadding, bottomPadding=bottomPadding, x=x, y=y, **kwargs)

    def pieChart(self, dx=None, dy=None, dwidth=None, dheight=None, angle=None, x=None, y=None, width=None, height=None,
                 strokeColor=None, strokeWidth=None, fillColor=None, debug=None, startAngle=None, direction=None,
                 checkLabelOverlap=None, pointerLabelMode=None, sameRadii=None, orderMode=None, xradius=None,
                 yradius=None, **kwargs):
        return self.child('pieChart', dx=dx, dy=dy, dwidth=dwidth, dheight=dheight, angle=angle, x=x, y=y, width=width,
                          height=height, strokeColor=strokeColor, strokeWidth=strokeWidth, fillColor=fillColor,
                          debug=debug, startAngle=startAngle, direction=direction, checkLabelOverlap=checkLabelOverlap,
                          pointerLabelMode=pointerLabelMode, sameRadii=sameRadii, orderMode=orderMode, xradius=xradius,
                          yradius=yradius, **kwargs)

    def slices(self, strokeWidth=None, fillColor=None, strokeColor=None, strokeDashArray=None, popout=None,
               fontName=None, fontSize=None, labelRadius=None, fillColorShaded=None, **kwargs):
        return self.child('slices', strokeWidth=strokeWidth, fillColor=fillColor, strokeColor=strokeColor,
                          strokeDashArray=strokeDashArray, popout=popout, fontName=fontName, fontSize=fontSize,
                          labelRadius=labelRadius, fillColorShaded=fillColorShaded, **kwargs)

    def slice(self, strokeWidth=None, fillColor=None, strokeColor=None, strokeDashArray=None, popout=None, fontName=None
              , fontSize=None, labelRadius=None, swatchMarker=None, fillColorShaded=None, **kwargs):
        return self.child('slice', strokeWidth=strokeWidth, fillColor=fillColor, strokeColor=strokeColor,
                          strokeDashArray=strokeDashArray, popout=popout, fontName=fontName, fontSize=fontSize,
                          labelRadius=labelRadius, swatchMarker=swatchMarker, fillColorShaded=fillColorShaded, **kwargs)

    def pointer(self, strokeColor=None, strokeWidth=None, elbowLength=None, edgePad=None, piePad=None, **kwargs):
        return self.child('pointer', strokeColor=strokeColor, strokeWidth=strokeWidth, elbowLength=elbowLength,
                          edgePad=edgePad, piePad=piePad, **kwargs)

    def pieChart3D(self, dx=None, dy=None, dwidth=None, dheight=None, angle=None, x=None, y=None, width=None,
                   height=None, strokeColor=None, strokeWidth=None, fillColor=None, debug=None, startAngle=None,
                   direction=None, checkLabelOverlap=None, pointerLabelMode=None, sameRadii=None, orderMode=None,
                   xradius=None, yradius=None, perspective=None, depth_3d=None, angle_3d=None, **kwargs):
        return self.child('pieChart3D', dx=dx, dy=dy, dwidth=dwidth, dheight=dheight, angle=angle, x=x, y=y, width=width
                          , height=height, strokeColor=strokeColor, strokeWidth=strokeWidth, fillColor=fillColor,
                          debug=debug, startAngle=startAngle, direction=direction, checkLabelOverlap=checkLabelOverlap,
                          pointerLabelMode=pointerLabelMode, sameRadii=sameRadii, orderMode=orderMode, xradius=xradius,
                          yradius=yradius, perspective=perspective, depth_3d=depth_3d, angle_3d=angle_3d, **kwargs)

    def spiderChart(self, dx=None, dy=None, dwidth=None, dheight=None, angle=None, x=None, y=None, width=None,
                    height=None, strokeColor=None, strokeWidth=None, fillColor=None, debug=None, startAngle=None,
                    direction=None, **kwargs):
        return self.child('spiderChart', dx=dx, dy=dy, dwidth=dwidth, dheight=dheight, angle=angle, x=x, y=y,
                          width=width, height=height, strokeColor=strokeColor, strokeWidth=strokeWidth,
                          fillColor=fillColor, debug=debug, startAngle=startAngle, direction=direction, **kwargs)

    def strands(self, strokeWidth=None, fillColor=None, strokeColor=None, strokeDashArray=None, symbol=None,
                symbolSize=None, name=None, **kwargs):
        return self.child('strands', strokeWidth=strokeWidth, fillColor=fillColor, strokeColor=strokeColor,
                          strokeDashArray=strokeDashArray, symbol=symbol, symbolSize=symbolSize, name=name, **kwargs)

    def strand(self, strokeWidth=None, fillColor=None, strokeColor=None, strokeDashArray=None, symbol=None,
               symbolSize=None, name=None, **kwargs):
        return self.child('strand', strokeWidth=strokeWidth, fillColor=fillColor, strokeColor=strokeColor,
                          strokeDashArray=strokeDashArray, symbol=symbol, symbolSize=symbolSize, name=name, **kwargs)

    def strandLabels(self, dx=None, dy=None, angle=None, boxAnchor=None, boxStrokeColor=None, boxStrokeWidth=None,
                     boxFillColor=None, boxTarget=None, fillColor=None, strokeColor=None, strokeWidth=None,
                     frontName=None, frontSize=None, leading=None, width=None, maxWidth=None, height=None,
                     textAnchor=None, visible=None, leftPadding=None, rightPadding=None, topPadding=None,
                     bottomPadding=None, _text=None, row=None, col=None, format=None, **kwargs):
        return self.child('strandLabels', dx=dx, dy=dy, angle=angle, boxAnchor=boxAnchor, boxStrokeColor=boxStrokeColor,
                          boxStrokeWidth=boxStrokeWidth, boxFillColor=boxFillColor, boxTarget=boxTarget,
                          fillColor=fillColor, strokeColor=strokeColor, strokeWidth=strokeWidth, frontName=frontName,
                          frontSize=frontSize, leading=leading, width=width, maxWidth=maxWidth, height=height,
                          textAnchor=textAnchor, visible=visible, leftPadding=leftPadding, rightPadding=rightPadding,
                          topPadding=topPadding, bottomPadding=bottomPadding, _text=_text, row=row, col=col,
                          format=format, **kwargs)

    def spokes(self, strokeWidth=None, fillColor=None, strokeColor=None, strokeDashArray=None, labelRadius=None,
               visible=None, **kwargs):
        return self.child('spokes', strokeWidth=strokeWidth, fillColor=fillColor, strokeColor=strokeColor,
                          strokeDashArray=strokeDashArray, labelRadius=labelRadius, visible=visible, **kwargs)

    def spoke(self, strokeWidth=None, fillColor=None, strokeColor=None, strokeDashArray=None, labelRadius=None,
              visible=None, **kwargs):
        return self.child('spoke', strokeWidth=strokeWidth, fillColor=fillColor, strokeColor=strokeColor,
                          strokeDashArray=strokeDashArray, labelRadius=labelRadius, visible=visible, **kwargs)

    def spokeLabels(self, dx=None, dy=None, angle=None, boxAnchor=None, boxStrokeColor=None, boxStrokeWidth=None,
                    boxFillColor=None, boxTarget=None, fillColor=None, strokeColor=None, strokeWidth=None,
                    frontName=None, frontSize=None, leading=None, width=None, maxWidth=None, height=None,
                    textAnchor=None, visible=None, leftPadding=None, rightPadding=None, topPadding=None,
                    bottomPadding=None, **kwargs):
        return self.child('spokeLabels', dx=dx, dy=dy, angle=angle, boxAnchor=boxAnchor, boxStrokeColor=boxStrokeColor,
                          boxStrokeWidth=boxStrokeWidth, boxFillColor=boxFillColor, boxTarget=boxTarget,
                          fillColor=fillColor, strokeColor=strokeColor, strokeWidth=strokeWidth, frontName=frontName,
                          frontSize=frontSize, leading=leading, width=width, maxWidth=maxWidth, height=height,
                          textAnchor=textAnchor, visible=visible, leftPadding=leftPadding, rightPadding=rightPadding,
                          topPadding=topPadding, bottomPadding=bottomPadding, **kwargs)


class GnrPdf(object):
    def __init__(self, filename=None, debug=None, compression=None, invariant=None, **kwargs):
        self.root = GnrRmlSrc.makeRoot()
        self.document = self.root.document(filename=filename, debug=debug, compression=compression, invariant=invariant)
        self.stylesheet = self.document.stylesheet()
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.auxroot = GnrRmlSrc.makeRoot()

    def template(self, **kwargs):
        self.template = self.document.template(**kwargs)

    def story(self, firstPageTemplate=None, **kwargs):
        self.document.popNode('story')
        return self.document.story(firstPageTemplate=firstPageTemplate, **kwargs)

    def _get_stylesheet(self):
        if not hasattr(self, 'stylesheet'):
            self._stylesheet = self.document.stylesheet()
        return self._stylesheet

    def toRml(self, filename=None):
        if filename:
            filename = expandpath(filename)
        return self.root.toRml(filename=filename)

    def pageTemplate(self, id=None, **kwargs):
        template = self.template.pageTemplate(id=id, **kwargs)
        getattr(self, 'pageTemplate_%s' % id)(template)

    def tableStyle(self, id=None, **kwargs):
        sheet = self.stylesheet.blockTableStyle(id=id, **kwargs)
        getattr(self, 'tableStyle_%s' % id)(sheet)

    def paraStyle(self, **kwargs):
        self.stylesheet.paraStyle(**kwargs)

    def boxStyle(self, **kwargs):
        self.stylesheet.boxStyle(**kwargs)

    def para(self, content=None, **kwargs):
        self.auxroot.para(content=content, **kwargs)
        return self.auxroot.popNode('#0').value

    def child(self, tag, **kwargs):
        handler = getattr(self.auxroot, tag)
        handler(**kwargs)
        return self.auxroot.popNode('#0').value

    def toPdf(self, filename=None):
        if filename:
            self.root.setAttr('#0', filename=os.path.basename(filename))
            output = open(expandpath(filename), 'wb')
        else:
            output = cStringIO.StringIO()
        root = etree.fromstring(self.toRml())
        pdf = pdfdoc.Document(root)
        pdf.process(output)
        if not filename:
            output.seek(0)
            return output.read()
        output.close()