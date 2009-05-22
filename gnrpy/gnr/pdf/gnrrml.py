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
from gnr.core.gnrsys import expandpath
from lxml import etree
from z3c.rml import document as pdfdoc
import cStringIO
import os
from gnr.core.gnrlang import optArgs

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
     'stylesheet','story', 'strand', 'strandLabels', 'strands', 'stroke', 'td', 'tr', 'template', 'text', 
     'textAnnotation', 'textField', 'title', 'transform', 'translate', 'valueAxis', 'xValueAxis', 'xpre', 
     'yValueAxis']

    gnrNS=['string','content']
           
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

    def content(self,content):
        if not isinstance(content, list):
            content=[content]
        for single_content in content:
            self.child('__flatten__',content=single_content)

    
    def child(self,*args,**kwargs):
        if 'name' in kwargs:
            kwargs['_name'] = kwargs.pop('name')
        kwargs = optArgs(**kwargs)
        return super(GnrRmlSrc, self).child(*args,**kwargs)
    
    def document(self, filename, debug=0, compression=1, invariant=1):
        return self.child('document', filename = filename, debug=0, compression=1, invariant=1)
        
    def story(self, firstPageTemplate=None):
        return self.child('story', firstPageTemplate=firstPageTemplate)
    
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
    tagType=property(_tagType)
    
    def _getRow(self, rowidx):
        if rowidx is None:
            rowidx = len(self)+1
        while len(self)<rowidx:
            r=self.tr()
            while len(r)<self.cols:
                r.td()
        return r
    
    def row(self,cell_list=None,height=None,startcol=0,rowidx=None,**kwargs):
        row = self._getRow(rowidx)
        cell_list = cell_list or []
        for i,cell in enumerate(cell_list):
            cellidx = i + startcol
            destcell = row.cell(cellidx)
            print destcell
            if isinstance(cell, tuple):
                content, attributes = cell
                destcell.parentNode.attr = attributes
            else:
                content = cell
            if content:
                destcell.content(content)
        return row

    def cell(self, rowidx, colidx=None):
        if self.tagType=='tr':
            cellidx = rowidx
            row = self
        else:
            cellidx = colidx
            while len(self)<rowidx:
                self.row()
            row = self['#%i'%rowidx]
        if cellidx<0:
            cellidx = len(row)+cellidx
        return row['#%i'%cellidx]

    def blockTableStyle(self, id='', keepWithNext=None):
        return self.child('blockTableStyle', id=id, keepWithNext=keepWithNext)

    def document(self,filename=None,debug=None,compression=None,invariant=None):
        return self.child('document',filename=filename,debug=debug,compression=compression,invariant=invariant)

    def registerType1Face(self,afmFile=None,pfbFile=None):
        return self.child('registerType1Face',afmFile=afmFile,pfbFile=pfbFile)

    def registerFont(self,name=None,faceName=None,encName=None):
        return self.child('registerFont',name=name,faceName=faceName,encName=encName)

    def registerTTFont(self,faceName=None,fileName=None):
        return self.child('registerTTFont',faceName=faceName,fileName=fileName)

    def registerCidFont(self,faceName=None):
        return self.child('registerCidFont',faceName=faceName)

    def color(self,id=None,value=None):
        return self.child('color',id=id,value=value)

    def addMapping(self,faceName=None,bold=None,italic=None,psName=None):
        return self.child('addMapping',faceName=faceName,bold=bold,italic=italic,psName=psName)

    def name(self,id=None,value=None,text=None):
        return self.child('name',id=id,value=value,text=text)

    def alias(self,id=None,value=None):
        return self.child('alias',id=id,value=value)

    def paraStyle(self,fontName=None,fontSize=None,leading=None,leftIndent=None,rightIndent=None,firstLineIndent=None,spaceBefore=None,spaceAfter=None,alignment=None,bulletFontName=None,bulletFontSize=None,bulletIndent=None,textColor=None,backColor=None,keepWithNext=None,wordWrap=None,name=None,alias=None,parent=None):
        return self.child('paraStyle',fontName=fontName,fontSize=fontSize,leading=leading,leftIndent=leftIndent,rightIndent=rightIndent,firstLineIndent=firstLineIndent,spaceBefore=spaceBefore,spaceAfter=spaceAfter,alignment=alignment,bulletFontName=bulletFontName,bulletFontSize=bulletFontSize,bulletIndent=bulletIndent,textColor=textColor,backColor=backColor,keepWithNext=keepWithNext,wordWrap=wordWrap,name=name,alias=alias,parent=parent)

    def blockTableStyle(self,id=None,keepWithNext=None):
        return self.child('blockTableStyle',id=id,keepWithNext=keepWithNext)

    def blockFont(self,start=None,stop=None,name=None,size=None,leading=None):
        return self.child('blockFont',start=start,stop=stop,name=name,size=size,leading=leading)

    def blockLeading(self,start=None,stop=None,length=None):
        return self.child('blockLeading',start=start,stop=stop,length=length)

    def blockTextColor(self,start=None,stop=None,colorName=None):
        return self.child('blockTextColor',start=start,stop=stop,colorName=colorName)

    def blockAlignment(self,start=None,stop=None,value=None):
        return self.child('blockAlignment',start=start,stop=stop,value=value)

    def blockLeftPadding(self,start=None,stop=None,length=None):
        return self.child('blockLeftPadding',start=start,stop=stop,length=length)

    def blockRightPadding(self,start=None,stop=None,length=None):
        return self.child('blockRightPadding',start=start,stop=stop,length=length)

    def blockBottomPadding(self,start=None,stop=None,length=None):
        return self.child('blockBottomPadding',start=start,stop=stop,length=length)

    def blockTopPadding(self,start=None,stop=None,length=None):
        return self.child('blockTopPadding',start=start,stop=stop,length=length)

    def blockBackground(self,start=None,stop=None,colorName=None,colorsByRow=None,colorsByCol=None):
        return self.child('blockBackground',start=start,stop=stop,colorName=colorName,colorsByRow=colorsByRow,colorsByCol=colorsByCol)

    def blockRowBackground(self,start=None,stop=None,colorNames=None):
        return self.child('blockRowBackground',start=start,stop=stop,colorNames=colorNames)

    def blockColBackground(self,start=None,stop=None,colorNames=None):
        return self.child('blockColBackground',start=start,stop=stop,colorNames=colorNames)

    def blockValign(self,start=None,stop=None,value=None):
        return self.child('blockValign',start=start,stop=stop,value=value)

    def blockSpan(self,start=None,stop=None):
        return self.child('blockSpan',start=start,stop=stop)

    def lineStyle(self,start=None,stop=None,kind=None,thickness=None,colorName=None,cap=None,dash=None,join=None,count=None):
        return self.child('lineStyle',start=start,stop=stop,kind=kind,thickness=thickness,colorName=colorName,cap=cap,dash=dash,join=join,count=count)

    def template(self,pageSize=None,rotation=None,leftMargin=None,rightMargin=None,topMargin=None,bottomMargin=None,showBoundary=None,allowSplitting=None,title=None,author=None):
        return self.child('template',pageSize=pageSize,rotation=rotation,leftMargin=leftMargin,rightMargin=rightMargin,topMargin=topMargin,bottomMargin=bottomMargin,showBoundary=showBoundary,allowSplitting=allowSplitting,title=title,author=author)

    def pageTemplate(self,id=None,pagesize=None,rotation=None):
        return self.child('pageTemplate',id=id,pagesize=pagesize,rotation=rotation)

    def frame(self,x1=None,y1=None,width=None,height=None,id=None,leftPadding=None,rightPadding=None,topPadding=None,bottomPadding=None,showBoundary=None):
        return self.child('frame',x1=x1,y1=y1,width=width,height=height,id=id,leftPadding=leftPadding,rightPadding=rightPadding,topPadding=topPadding,bottomPadding=bottomPadding,showBoundary=showBoundary)

    def story(self,firstPageTemplate=None):
        return self.child('story',firstPageTemplate=firstPageTemplate)

    def spacer(self,width=None,length=None):
        return self.child('spacer',width=width,length=length)

    def illustration(self,width=None,height=None):
        return self.child('illustration',width=width,height=height)

    def pre(self,style=None,bulletText=None,dedent=None,text=None):
        return self.child('pre',style=style,bulletText=bulletText,dedent=dedent,text=text)

    def xpre(self,style=None,bulletText=None,dedent=None,text=None):
        return self.child('xpre',style=style,bulletText=bulletText,dedent=dedent,text=text)

    def plugInFlowable(self,module=None,function=None,params=None):
        return self.child('plugInFlowable',module=module,function=function,params=params)

    def barCodeFlowable(self,code=None,width=None,height=None,strokeColor=None,strokeWidth=None,fillColor=None,barStrokeColor=None,barStrokeWidth=None,barFillColor=None,gap=None,barWidth=None,barHeight=None,ratio=None,checksum=None,bearers=None,quiet=None,lquiet=None,rquiet=None,fontName=None,fontSize=None,humanReadable=None,stop=None,spaceWidth=None,shortHeight=None,textColor=None,value=None):
        return self.child('barCodeFlowable',code=code,width=width,height=height,strokeColor=strokeColor,strokeWidth=strokeWidth,fillColor=fillColor,barStrokeColor=barStrokeColor,barStrokeWidth=barStrokeWidth,barFillColor=barFillColor,gap=gap,barWidth=barWidth,barHeight=barHeight,ratio=ratio,checksum=checksum,bearers=bearers,quiet=quiet,lquiet=lquiet,rquiet=rquiet,fontName=fontName,fontSize=fontSize,humanReadable=humanReadable,stop=stop,spaceWidth=spaceWidth,shortHeight=shortHeight,textColor=textColor,value=value)

    def outlineAdd(self,title=None,key=None,level=None,closed=None):
        return self.child('outlineAdd',title=title,key=key,level=level,closed=closed)

    def title(self,fontName=None,fontSize=None,leading=None,leftIndent=None,rightIndent=None,firstLineIndent=None,spaceBefore=None,spaceAfter=None,alignment=None,bulletFontName=None,bulletFontSize=None,bulletIndent=None,textColor=None,backColor=None,keepWithNext=None,wordWrap=None,bulletText=None,dedent=None,text=None,style=None):
        return self.child('title',fontName=fontName,fontSize=fontSize,leading=leading,leftIndent=leftIndent,rightIndent=rightIndent,firstLineIndent=firstLineIndent,spaceBefore=spaceBefore,spaceAfter=spaceAfter,alignment=alignment,bulletFontName=bulletFontName,bulletFontSize=bulletFontSize,bulletIndent=bulletIndent,textColor=textColor,backColor=backColor,keepWithNext=keepWithNext,wordWrap=wordWrap,bulletText=bulletText,dedent=dedent,text=text,style=style)

    def h1(self,fontName=None,fontSize=None,leading=None,leftIndent=None,rightIndent=None,firstLineIndent=None,spaceBefore=None,spaceAfter=None,alignment=None,bulletFontName=None,bulletFontSize=None,bulletIndent=None,textColor=None,backColor=None,keepWithNext=None,wordWrap=None,bulletText=None,dedent=None,text=None,style=None):
        return self.child('h1',fontName=fontName,fontSize=fontSize,leading=leading,leftIndent=leftIndent,rightIndent=rightIndent,firstLineIndent=firstLineIndent,spaceBefore=spaceBefore,spaceAfter=spaceAfter,alignment=alignment,bulletFontName=bulletFontName,bulletFontSize=bulletFontSize,bulletIndent=bulletIndent,textColor=textColor,backColor=backColor,keepWithNext=keepWithNext,wordWrap=wordWrap,bulletText=bulletText,dedent=dedent,text=text,style=style)

    def h2(self,fontName=None,fontSize=None,leading=None,leftIndent=None,rightIndent=None,firstLineIndent=None,spaceBefore=None,spaceAfter=None,alignment=None,bulletFontName=None,bulletFontSize=None,bulletIndent=None,textColor=None,backColor=None,keepWithNext=None,wordWrap=None,bulletText=None,dedent=None,text=None,style=None):
        return self.child('h2',fontName=fontName,fontSize=fontSize,leading=leading,leftIndent=leftIndent,rightIndent=rightIndent,firstLineIndent=firstLineIndent,spaceBefore=spaceBefore,spaceAfter=spaceAfter,alignment=alignment,bulletFontName=bulletFontName,bulletFontSize=bulletFontSize,bulletIndent=bulletIndent,textColor=textColor,backColor=backColor,keepWithNext=keepWithNext,wordWrap=wordWrap,bulletText=bulletText,dedent=dedent,text=text,style=style)

    def h3(self,fontName=None,fontSize=None,leading=None,leftIndent=None,rightIndent=None,firstLineIndent=None,spaceBefore=None,spaceAfter=None,alignment=None,bulletFontName=None,bulletFontSize=None,bulletIndent=None,textColor=None,backColor=None,keepWithNext=None,wordWrap=None,bulletText=None,dedent=None,text=None,style=None):
        return self.child('h3',fontName=fontName,fontSize=fontSize,leading=leading,leftIndent=leftIndent,rightIndent=rightIndent,firstLineIndent=firstLineIndent,spaceBefore=spaceBefore,spaceAfter=spaceAfter,alignment=alignment,bulletFontName=bulletFontName,bulletFontSize=bulletFontSize,bulletIndent=bulletIndent,textColor=textColor,backColor=backColor,keepWithNext=keepWithNext,wordWrap=wordWrap,bulletText=bulletText,dedent=dedent,text=text,style=style)

    def para(self,fontName=None,fontSize=None,leading=None,leftIndent=None,rightIndent=None,firstLineIndent=None,spaceBefore=None,spaceAfter=None,alignment=None,bulletFontName=None,bulletFontSize=None,bulletIndent=None,textColor=None,backColor=None,keepWithNext=None,wordWrap=None,style=None,bulletText=None,dedent=None,text=None):
        return self.child('para',fontName=fontName,fontSize=fontSize,leading=leading,leftIndent=leftIndent,rightIndent=rightIndent,firstLineIndent=firstLineIndent,spaceBefore=spaceBefore,spaceAfter=spaceAfter,alignment=alignment,bulletFontName=bulletFontName,bulletFontSize=bulletFontSize,bulletIndent=bulletIndent,textColor=textColor,backColor=backColor,keepWithNext=keepWithNext,wordWrap=wordWrap,style=style,bulletText=bulletText,dedent=dedent,text=text)

    def blockTable(self,style=None,rowHeights=None,colWidths=None,repeatRows=None,alignment=None):
        child=self.child('blockTable',style=style,rowHeights=rowHeights,colWidths=colWidths,repeatRows=repeatRows,alignment=alignment)
        child.cols=len(colWidths.split(','))
        return child
        
    def td(self,content=None,fontName=None,fontSize=None,leading=None,fontColor=None,leftPadding=None,rightPadding=None,topPadding=None,bottomPadding=None,background=None,align=None,vAlign=None,lineBelowThickness=None,lineBelowColor=None,lineBelowCap=None,lineBelowCount=None,lineBelowSpace=None,lineAboveThickness=None,lineAboveColor=None,lineAboveCap=None,lineAboveCount=None,lineAboveSpace=None,lineLeftThickness=None,lineLeftColor=None,lineLeftCap=None,lineLeftCount=None,lineLeftSpace=None,lineRightThickness=None,lineRightColor=None,lineRightCap=None,lineRightCount=None,lineRightSpace=None):
        return self.child('td',content=content,fontName=fontName,fontSize=fontSize,leading=leading,fontColor=fontColor,leftPadding=leftPadding,rightPadding=rightPadding,topPadding=topPadding,bottomPadding=bottomPadding,background=background,align=align,vAlign=vAlign,lineBelowThickness=lineBelowThickness,lineBelowColor=lineBelowColor,lineBelowCap=lineBelowCap,lineBelowCount=lineBelowCount,lineBelowSpace=lineBelowSpace,lineAboveThickness=lineAboveThickness,lineAboveColor=lineAboveColor,lineAboveCap=lineAboveCap,lineAboveCount=lineAboveCount,lineAboveSpace=lineAboveSpace,lineLeftThickness=lineLeftThickness,lineLeftColor=lineLeftColor,lineLeftCap=lineLeftCap,lineLeftCount=lineLeftCount,lineLeftSpace=lineLeftSpace,lineRightThickness=lineRightThickness,lineRightColor=lineRightColor,lineRightCap=lineRightCap,lineRightCount=lineRightCount,lineRightSpace=lineRightSpace)

    def tr(self):
        return self.child('tr')

    def bulkData(self,content=None):
        return self.child('bulkData',content=content)

    def nextFrame(self,name=None):
        return self.child('nextFrame',name=name)

    def setNextFrame(self,name=None):
        return self.child('setNextFrame',name=name)

    def setNextTemplate(self,name=None):
        return self.child('setNextTemplate',name=name)

    def condPageBreak(self,height=None):
        return self.child('condPageBreak',height=height)

    def keepInFrame(self,maxWidth=None,maxHeight=None,mergeSpace=None,onOverflow=None,id=None,frame=None):
        return self.child('keepInFrame',maxWidth=maxWidth,maxHeight=maxHeight,mergeSpace=mergeSpace,onOverflow=onOverflow,id=id,frame=frame)

    def keepTogether(self,maxHeight=None):
        return self.child('keepTogether',maxHeight=maxHeight)

    def imageAndFlowables(self,imageName=None,imageWidth=None,imageHeight=None,imageMask=None,imageLeftPadding=None,imageRightPadding=None,imageTopPadding=None,imageBottomPadding=None,imageSide=None):
        return self.child('imageAndFlowables',imageName=imageName,imageWidth=imageWidth,imageHeight=imageHeight,imageMask=imageMask,imageLeftPadding=imageLeftPadding,imageRightPadding=imageRightPadding,imageTopPadding=imageTopPadding,imageBottomPadding=imageBottomPadding,imageSide=imageSide)

    def indent(self,left=None,right=None):
        return self.child('indent',left=left,right=right)

    def fixedSize(self,width=None,height=None):
        return self.child('fixedSize',width=width,height=height)

    def bookmark(self,name=None,fitType=None,left=None,top=None,right=None,zoom=None):
        return self.child('bookmark',name=name,fitType=fitType,left=left,top=top,right=right,zoom=zoom)

    def link(self,destination=None,url=None,boxStrokeWidth=None,boxStrokeDashArray=None,boxStrokeColor=None):
        return self.child('link',destination=destination,url=url,boxStrokeWidth=boxStrokeWidth,boxStrokeDashArray=boxStrokeDashArray,boxStrokeColor=boxStrokeColor)

    def hr(self,width=None,thickness=None,color=None,lineCap=None,spaceBefore=None,spaceAfter=None,align=None,valign=None,dash=None):
        return self.child('hr',width=width,thickness=thickness,color=color,lineCap=lineCap,spaceBefore=spaceBefore,spaceAfter=spaceAfter,align=align,valign=valign,dash=dash)

    def pageInfo(self,pageSize=None):
        return self.child('pageInfo',pageSize=pageSize)

    def drawString(self,x=None,y=None,text=None):
        return self.child('drawString',x=x,y=y,text=text)

    def drawRightString(self,x=None,y=None,text=None):
        return self.child('drawRightString',x=x,y=y,text=text)

    def drawCenteredString(self,x=None,y=None,text=None):
        return self.child('drawCenteredString',x=x,y=y,text=text)

    def drawCentredString(self,x=None,y=None,text=None):
        return self.child('drawCentredString',x=x,y=y,text=text)

    def drawAlignedString(self,x=None,y=None,text=None,pivotChar=None):
        return self.child('drawAlignedString',x=x,y=y,text=text,pivotChar=pivotChar)

    def ellipse(self,x=None,y=None,fill=None,stroke=None,width=None,height=None):
        return self.child('ellipse',x=x,y=y,fill=fill,stroke=stroke,width=width,height=height)

    def circle(self,x=None,y=None,fill=None,stroke=None,radius=None):
        return self.child('circle',x=x,y=y,fill=fill,stroke=stroke,radius=radius)

    def rect(self,x=None,y=None,fill=None,stroke=None,width=None,height=None,round=None):
        return self.child('rect',x=x,y=y,fill=fill,stroke=stroke,width=width,height=height,round=round)

    def grid(self,xs=None,ys=None):
        return self.child('grid',xs=xs,ys=ys)

    def lines(self,linelist=None,strokeWidth=None,strokeColor=None,strokeDashArray=None,symbol=None):
        return self.child('lines',linelist=linelist,strokeWidth=strokeWidth,strokeColor=strokeColor,strokeDashArray=strokeDashArray,symbol=symbol)

    def curves(self,curvelist=None):
        return self.child('curves',curvelist=curvelist)

    def image(self,file=None,x=None,y=None,width=None,height=None,showBoundary=None,preserveAspectRatio=None):
        return self.child('image',file=file,x=x,y=y,width=width,height=height,showBoundary=showBoundary,preserveAspectRatio=preserveAspectRatio)

    def place(self,x=None,y=None,width=None,height=None):
        return self.child('place',x=x,y=y,width=width,height=height)

    def textAnnotation(self,contents=None):
        return self.child('textAnnotation',contents=contents)

    def param(self,name=None,value=None):
        return self.child('param',name=name,value=value)

    def path(self,x=None,y=None,fill=None,stroke=None,points=None,close=None):
        return self.child('path',x=x,y=y,fill=fill,stroke=stroke,points=points,close=close)

    def moveto(self,position=None):
        return self.child('moveto',position=position)

    def curveto(self,curvelist=None):
        return self.child('curveto',curvelist=curvelist)

    def curvesto(self,curvelist=None):
        return self.child('curvesto',curvelist=curvelist)

    def fill(self,color=None):
        return self.child('fill',color=color)

    def stroke(self,color=None):
        return self.child('stroke',color=color)

    def setFont(self,name=None,size=None,leading=None):
        return self.child('setFont',name=name,size=size,leading=leading)

    def scale(self,sx=None,sy=None):
        return self.child('scale',sx=sx,sy=sy)

    def translate(self,dx=None,dy=None):
        return self.child('translate',dx=dx,dy=dy)

    def rotate(self,degrees=None):
        return self.child('rotate',degrees=degrees)

    def skew(self,alpha=None,beta=None):
        return self.child('skew',alpha=alpha,beta=beta)

    def transform(self,matrix=None):
        return self.child('transform',matrix=matrix)

    def lineMode(self,width=None,dash=None,miterLimit=None,join=None,cap=None):
        return self.child('lineMode',width=width,dash=dash,miterLimit=miterLimit,join=join,cap=cap)

    def barCode(self,code=None,value=None,width=None,height=None,strokeColor=None,strokeWidth=None,fillColor=None,barStrokeColor=None,barStrokeWidth=None,barFillColor=None,gap=None,barWidth=None,barHeight=None,ratio=None,checksum=None,bearers=None,quiet=None,lquiet=None,rquiet=None,fontName=None,fontSize=None,humanReadable=None,stop=None,spaceWidth=None,shortHeight=None,textColor=None,x=None,y=None):
        return self.child('barCode',code=code,value=value,width=width,height=height,strokeColor=strokeColor,strokeWidth=strokeWidth,fillColor=fillColor,barStrokeColor=barStrokeColor,barStrokeWidth=barStrokeWidth,barFillColor=barFillColor,gap=gap,barWidth=barWidth,barHeight=barHeight,ratio=ratio,checksum=checksum,bearers=bearers,quiet=quiet,lquiet=lquiet,rquiet=rquiet,fontName=fontName,fontSize=fontSize,humanReadable=humanReadable,stop=stop,spaceWidth=spaceWidth,shortHeight=shortHeight,textColor=textColor,x=x,y=y)

    def textField(self,title=None,x=None,y=None,width=None,height=None,value=None,maxLength=None,multiline=None):
        return self.child('textField',title=title,x=x,y=y,width=width,height=height,value=value,maxLength=maxLength,multiline=multiline)

    def buttonField(self,title=None,x=None,y=None,value=None):
        return self.child('buttonField',title=title,x=x,y=y,value=value)

    def selectField(self,title=None,x=None,y=None,width=None,height=None,value=None):
        return self.child('selectField',title=title,x=x,y=y,width=width,height=height,value=value)

    def option(self,value=None):
        return self.child('option',value=value)

    def barChart(self,dx=None,dy=None,dwidth=None,dheight=None,angle=None,x=None,y=None,width=None,height=None,strokeColor=None,strokeWidth=None,fillColor=None,debug=None,direction=None,useAbsolute=None,barWidth=None,groupSpacing=None,barSpacing=None):
        return self.child('barChart',dx=dx,dy=dy,dwidth=dwidth,dheight=dheight,angle=angle,x=x,y=y,width=width,height=height,strokeColor=strokeColor,strokeWidth=strokeWidth,fillColor=fillColor,debug=debug,direction=direction,useAbsolute=useAbsolute,barWidth=barWidth,groupSpacing=groupSpacing,barSpacing=barSpacing)

    def series(self,values=None):
        return self.child('series',values=values)

    def bars(self,strokeColor=None,strokeWidth=None,fillColor=None):
        return self.child('bars',strokeColor=strokeColor,strokeWidth=strokeWidth,fillColor=fillColor)

    def bar(self,strokeColor=None,strokeWidth=None,fillColor=None):
        return self.child('bar',strokeColor=strokeColor,strokeWidth=strokeWidth,fillColor=fillColor)

    def categoryAxis(self,visible=None,visibleAxis=None,visibleTicks=None,visibleLabels=None,visibleGrid=None,strokeWidth=None,strokeColor=None,strokeDashArray=None,gridStrokeWidth=None,gridStrokeColor=None,gridStrokeDashArray=None,gridStart=None,gridEnd=None,style=None,categoryNames=None,joinAxis=None,joinAxisPos=None,reverseDirection=None,labelAxisMode=None,tickShift=None):
        return self.child('categoryAxis',visible=visible,visibleAxis=visibleAxis,visibleTicks=visibleTicks,visibleLabels=visibleLabels,visibleGrid=visibleGrid,strokeWidth=strokeWidth,strokeColor=strokeColor,strokeDashArray=strokeDashArray,gridStrokeWidth=gridStrokeWidth,gridStrokeColor=gridStrokeColor,gridStrokeDashArray=gridStrokeDashArray,gridStart=gridStart,gridEnd=gridEnd,style=style,categoryNames=categoryNames,joinAxis=joinAxis,joinAxisPos=joinAxisPos,reverseDirection=reverseDirection,labelAxisMode=labelAxisMode,tickShift=tickShift)

    def labels(self,dx=None,dy=None,angle=None,boxAnchor=None,boxStrokeColor=None,boxStrokeWidth=None,boxFillColor=None,boxTarget=None,fillColor=None,strokeColor=None,strokeWidth=None,frontName=None,frontSize=None,leading=None,width=None,maxWidth=None,height=None,textAnchor=None,visible=None,leftPadding=None,rightPadding=None,topPadding=None,bottomPadding=None,x=None,y=None):
        return self.child('labels',dx=dx,dy=dy,angle=angle,boxAnchor=boxAnchor,boxStrokeColor=boxStrokeColor,boxStrokeWidth=boxStrokeWidth,boxFillColor=boxFillColor,boxTarget=boxTarget,fillColor=fillColor,strokeColor=strokeColor,strokeWidth=strokeWidth,frontName=frontName,frontSize=frontSize,leading=leading,width=width,maxWidth=maxWidth,height=height,textAnchor=textAnchor,visible=visible,leftPadding=leftPadding,rightPadding=rightPadding,topPadding=topPadding,bottomPadding=bottomPadding,x=x,y=y)

    def label(self,dx=None,dy=None,angle=None,boxAnchor=None,boxStrokeColor=None,boxStrokeWidth=None,boxFillColor=None,boxTarget=None,fillColor=None,strokeColor=None,strokeWidth=None,frontName=None,frontSize=None,leading=None,width=None,maxWidth=None,height=None,textAnchor=None,visible=None,leftPadding=None,rightPadding=None,topPadding=None,bottomPadding=None,x=None,y=None,text=None,_text=None,row=None,col=None,format=None,dR=None):
        return self.child('label',dx=dx,dy=dy,angle=angle,boxAnchor=boxAnchor,boxStrokeColor=boxStrokeColor,boxStrokeWidth=boxStrokeWidth,boxFillColor=boxFillColor,boxTarget=boxTarget,fillColor=fillColor,strokeColor=strokeColor,strokeWidth=strokeWidth,frontName=frontName,frontSize=frontSize,leading=leading,width=width,maxWidth=maxWidth,height=height,textAnchor=textAnchor,visible=visible,leftPadding=leftPadding,rightPadding=rightPadding,topPadding=topPadding,bottomPadding=bottomPadding,x=x,y=y,text=text,_text=_text,row=row,col=col,format=format,dR=dR)

    def valueAxis(self,visible=None,visibleAxis=None,visibleTicks=None,visibleLabels=None,visibleGrid=None,strokeWidth=None,strokeColor=None,strokeDashArray=None,gridStrokeWidth=None,gridStrokeColor=None,gridStrokeDashArray=None,gridStart=None,gridEnd=None,style=None,forceZero=None,minimumTickSpacing=None,maximumTicks=None,labelTextFormat=None,labelTextPostFormat=None,labelTextScale=None,valueMin=None,valueMax=None,valueStep=None,valueSteps=None,rangeRound=None,zrangePref=None):
        return self.child('valueAxis',visible=visible,visibleAxis=visibleAxis,visibleTicks=visibleTicks,visibleLabels=visibleLabels,visibleGrid=visibleGrid,strokeWidth=strokeWidth,strokeColor=strokeColor,strokeDashArray=strokeDashArray,gridStrokeWidth=gridStrokeWidth,gridStrokeColor=gridStrokeColor,gridStrokeDashArray=gridStrokeDashArray,gridStart=gridStart,gridEnd=gridEnd,style=style,forceZero=forceZero,minimumTickSpacing=minimumTickSpacing,maximumTicks=maximumTicks,labelTextFormat=labelTextFormat,labelTextPostFormat=labelTextPostFormat,labelTextScale=labelTextScale,valueMin=valueMin,valueMax=valueMax,valueStep=valueStep,valueSteps=valueSteps,rangeRound=rangeRound,zrangePref=zrangePref)

    def text(self,x=None,y=None,angle=None,text=None,fontName=None,fontSize=None,fillColor=None,textAnchor=None):
        return self.child('text',x=x,y=y,angle=angle,text=text,fontName=fontName,fontSize=fontSize,fillColor=fillColor,textAnchor=textAnchor)

    def barChart3D(self,dx=None,dy=None,dwidth=None,dheight=None,angle=None,x=None,y=None,width=None,height=None,strokeColor=None,strokeWidth=None,fillColor=None,debug=None,direction=None,useAbsolute=None,barWidth=None,groupSpacing=None,barSpacing=None,thetaX=None,thetaY=None,zDepth=None,zSpace=None):
        return self.child('barChart3D',dx=dx,dy=dy,dwidth=dwidth,dheight=dheight,angle=angle,x=x,y=y,width=width,height=height,strokeColor=strokeColor,strokeWidth=strokeWidth,fillColor=fillColor,debug=debug,direction=direction,useAbsolute=useAbsolute,barWidth=barWidth,groupSpacing=groupSpacing,barSpacing=barSpacing,thetaX=thetaX,thetaY=thetaY,zDepth=zDepth,zSpace=zSpace)

    def linePlot(self,dx=None,dy=None,dwidth=None,dheight=None,angle=None,x=None,y=None,width=None,height=None,strokeColor=None,strokeWidth=None,fillColor=None,debug=None,reversePlotOrder=None,lineLabelNudge=None,lineLabelFormat=None,joinedLines=None):
        return self.child('linePlot',dx=dx,dy=dy,dwidth=dwidth,dheight=dheight,angle=angle,x=x,y=y,width=width,height=height,strokeColor=strokeColor,strokeWidth=strokeWidth,fillColor=fillColor,debug=debug,reversePlotOrder=reversePlotOrder,lineLabelNudge=lineLabelNudge,lineLabelFormat=lineLabelFormat,joinedLines=joinedLines)

    def line(self,strokeWidth=None,strokeColor=None,strokeDashArray=None,symbol=None,name=None):
        return self.child('line',strokeWidth=strokeWidth,strokeColor=strokeColor,strokeDashArray=strokeDashArray,symbol=symbol,name=name)

    def xValueAxis(self,visible=None,visibleAxis=None,visibleTicks=None,visibleLabels=None,visibleGrid=None,strokeWidth=None,strokeColor=None,strokeDashArray=None,gridStrokeWidth=None,gridStrokeColor=None,gridStrokeDashArray=None,gridStart=None,gridEnd=None,style=None,forceZero=None,minimumTickSpacing=None,maximumTicks=None,labelTextFormat=None,labelTextPostFormat=None,labelTextScale=None,valueMin=None,valueMax=None,valueStep=None,valueSteps=None,rangeRound=None,zrangePref=None,tickUp=None,tickDown=None,joinAxis=None,joinAxisMode=None,joinAxisPos=None):
        return self.child('xValueAxis',visible=visible,visibleAxis=visibleAxis,visibleTicks=visibleTicks,visibleLabels=visibleLabels,visibleGrid=visibleGrid,strokeWidth=strokeWidth,strokeColor=strokeColor,strokeDashArray=strokeDashArray,gridStrokeWidth=gridStrokeWidth,gridStrokeColor=gridStrokeColor,gridStrokeDashArray=gridStrokeDashArray,gridStart=gridStart,gridEnd=gridEnd,style=style,forceZero=forceZero,minimumTickSpacing=minimumTickSpacing,maximumTicks=maximumTicks,labelTextFormat=labelTextFormat,labelTextPostFormat=labelTextPostFormat,labelTextScale=labelTextScale,valueMin=valueMin,valueMax=valueMax,valueStep=valueStep,valueSteps=valueSteps,rangeRound=rangeRound,zrangePref=zrangePref,tickUp=tickUp,tickDown=tickDown,joinAxis=joinAxis,joinAxisMode=joinAxisMode,joinAxisPos=joinAxisPos)

    def yValueAxis(self,visible=None,visibleAxis=None,visibleTicks=None,visibleLabels=None,visibleGrid=None,strokeWidth=None,strokeColor=None,strokeDashArray=None,gridStrokeWidth=None,gridStrokeColor=None,gridStrokeDashArray=None,gridStart=None,gridEnd=None,style=None,forceZero=None,minimumTickSpacing=None,maximumTicks=None,labelTextFormat=None,labelTextPostFormat=None,labelTextScale=None,valueMin=None,valueMax=None,valueStep=None,valueSteps=None,rangeRound=None,zrangePref=None,tickLeft=None,tickRight=None,joinAxis=None,joinAxisMode=None,joinAxisPos=None):
        return self.child('yValueAxis',visible=visible,visibleAxis=visibleAxis,visibleTicks=visibleTicks,visibleLabels=visibleLabels,visibleGrid=visibleGrid,strokeWidth=strokeWidth,strokeColor=strokeColor,strokeDashArray=strokeDashArray,gridStrokeWidth=gridStrokeWidth,gridStrokeColor=gridStrokeColor,gridStrokeDashArray=gridStrokeDashArray,gridStart=gridStart,gridEnd=gridEnd,style=style,forceZero=forceZero,minimumTickSpacing=minimumTickSpacing,maximumTicks=maximumTicks,labelTextFormat=labelTextFormat,labelTextPostFormat=labelTextPostFormat,labelTextScale=labelTextScale,valueMin=valueMin,valueMax=valueMax,valueStep=valueStep,valueSteps=valueSteps,rangeRound=rangeRound,zrangePref=zrangePref,tickLeft=tickLeft,tickRight=tickRight,joinAxis=joinAxis,joinAxisMode=joinAxisMode,joinAxisPos=joinAxisPos)

    def lineLabels(self,dx=None,dy=None,angle=None,boxAnchor=None,boxStrokeColor=None,boxStrokeWidth=None,boxFillColor=None,boxTarget=None,fillColor=None,strokeColor=None,strokeWidth=None,frontName=None,frontSize=None,leading=None,width=None,maxWidth=None,height=None,textAnchor=None,visible=None,leftPadding=None,rightPadding=None,topPadding=None,bottomPadding=None,x=None,y=None):
        return self.child('lineLabels',dx=dx,dy=dy,angle=angle,boxAnchor=boxAnchor,boxStrokeColor=boxStrokeColor,boxStrokeWidth=boxStrokeWidth,boxFillColor=boxFillColor,boxTarget=boxTarget,fillColor=fillColor,strokeColor=strokeColor,strokeWidth=strokeWidth,frontName=frontName,frontSize=frontSize,leading=leading,width=width,maxWidth=maxWidth,height=height,textAnchor=textAnchor,visible=visible,leftPadding=leftPadding,rightPadding=rightPadding,topPadding=topPadding,bottomPadding=bottomPadding,x=x,y=y)

    def pieChart(self,dx=None,dy=None,dwidth=None,dheight=None,angle=None,x=None,y=None,width=None,height=None,strokeColor=None,strokeWidth=None,fillColor=None,debug=None,startAngle=None,direction=None,checkLabelOverlap=None,pointerLabelMode=None,sameRadii=None,orderMode=None,xradius=None,yradius=None):
        return self.child('pieChart',dx=dx,dy=dy,dwidth=dwidth,dheight=dheight,angle=angle,x=x,y=y,width=width,height=height,strokeColor=strokeColor,strokeWidth=strokeWidth,fillColor=fillColor,debug=debug,startAngle=startAngle,direction=direction,checkLabelOverlap=checkLabelOverlap,pointerLabelMode=pointerLabelMode,sameRadii=sameRadii,orderMode=orderMode,xradius=xradius,yradius=yradius)

    def slices(self,strokeWidth=None,fillColor=None,strokeColor=None,strokeDashArray=None,popout=None,fontName=None,fontSize=None,labelRadius=None,fillColorShaded=None):
        return self.child('slices',strokeWidth=strokeWidth,fillColor=fillColor,strokeColor=strokeColor,strokeDashArray=strokeDashArray,popout=popout,fontName=fontName,fontSize=fontSize,labelRadius=labelRadius,fillColorShaded=fillColorShaded)

    def slice(self,strokeWidth=None,fillColor=None,strokeColor=None,strokeDashArray=None,popout=None,fontName=None,fontSize=None,labelRadius=None,swatchMarker=None,fillColorShaded=None):
        return self.child('slice',strokeWidth=strokeWidth,fillColor=fillColor,strokeColor=strokeColor,strokeDashArray=strokeDashArray,popout=popout,fontName=fontName,fontSize=fontSize,labelRadius=labelRadius,swatchMarker=swatchMarker,fillColorShaded=fillColorShaded)

    def pointer(self,strokeColor=None,strokeWidth=None,elbowLength=None,edgePad=None,piePad=None):
        return self.child('pointer',strokeColor=strokeColor,strokeWidth=strokeWidth,elbowLength=elbowLength,edgePad=edgePad,piePad=piePad)

    def pieChart3D(self,dx=None,dy=None,dwidth=None,dheight=None,angle=None,x=None,y=None,width=None,height=None,strokeColor=None,strokeWidth=None,fillColor=None,debug=None,startAngle=None,direction=None,checkLabelOverlap=None,pointerLabelMode=None,sameRadii=None,orderMode=None,xradius=None,yradius=None,perspective=None,depth_3d=None,angle_3d=None):
        return self.child('pieChart3D',dx=dx,dy=dy,dwidth=dwidth,dheight=dheight,angle=angle,x=x,y=y,width=width,height=height,strokeColor=strokeColor,strokeWidth=strokeWidth,fillColor=fillColor,debug=debug,startAngle=startAngle,direction=direction,checkLabelOverlap=checkLabelOverlap,pointerLabelMode=pointerLabelMode,sameRadii=sameRadii,orderMode=orderMode,xradius=xradius,yradius=yradius,perspective=perspective,depth_3d=depth_3d,angle_3d=angle_3d)

    def spiderChart(self,dx=None,dy=None,dwidth=None,dheight=None,angle=None,x=None,y=None,width=None,height=None,strokeColor=None,strokeWidth=None,fillColor=None,debug=None,startAngle=None,direction=None):
        return self.child('spiderChart',dx=dx,dy=dy,dwidth=dwidth,dheight=dheight,angle=angle,x=x,y=y,width=width,height=height,strokeColor=strokeColor,strokeWidth=strokeWidth,fillColor=fillColor,debug=debug,startAngle=startAngle,direction=direction)

    def strands(self,strokeWidth=None,fillColor=None,strokeColor=None,strokeDashArray=None,symbol=None,symbolSize=None,name=None):
        return self.child('strands',strokeWidth=strokeWidth,fillColor=fillColor,strokeColor=strokeColor,strokeDashArray=strokeDashArray,symbol=symbol,symbolSize=symbolSize,name=name)

    def strand(self,strokeWidth=None,fillColor=None,strokeColor=None,strokeDashArray=None,symbol=None,symbolSize=None,name=None):
        return self.child('strand',strokeWidth=strokeWidth,fillColor=fillColor,strokeColor=strokeColor,strokeDashArray=strokeDashArray,symbol=symbol,symbolSize=symbolSize,name=name)

    def strandLabels(self,dx=None,dy=None,angle=None,boxAnchor=None,boxStrokeColor=None,boxStrokeWidth=None,boxFillColor=None,boxTarget=None,fillColor=None,strokeColor=None,strokeWidth=None,frontName=None,frontSize=None,leading=None,width=None,maxWidth=None,height=None,textAnchor=None,visible=None,leftPadding=None,rightPadding=None,topPadding=None,bottomPadding=None,_text=None,row=None,col=None,format=None):
        return self.child('strandLabels',dx=dx,dy=dy,angle=angle,boxAnchor=boxAnchor,boxStrokeColor=boxStrokeColor,boxStrokeWidth=boxStrokeWidth,boxFillColor=boxFillColor,boxTarget=boxTarget,fillColor=fillColor,strokeColor=strokeColor,strokeWidth=strokeWidth,frontName=frontName,frontSize=frontSize,leading=leading,width=width,maxWidth=maxWidth,height=height,textAnchor=textAnchor,visible=visible,leftPadding=leftPadding,rightPadding=rightPadding,topPadding=topPadding,bottomPadding=bottomPadding,_text=_text,row=row,col=col,format=format)

    def spokes(self,strokeWidth=None,fillColor=None,strokeColor=None,strokeDashArray=None,labelRadius=None,visible=None):
        return self.child('spokes',strokeWidth=strokeWidth,fillColor=fillColor,strokeColor=strokeColor,strokeDashArray=strokeDashArray,labelRadius=labelRadius,visible=visible)

    def spoke(self,strokeWidth=None,fillColor=None,strokeColor=None,strokeDashArray=None,labelRadius=None,visible=None):
        return self.child('spoke',strokeWidth=strokeWidth,fillColor=fillColor,strokeColor=strokeColor,strokeDashArray=strokeDashArray,labelRadius=labelRadius,visible=visible)

    def spokeLabels(self,dx=None,dy=None,angle=None,boxAnchor=None,boxStrokeColor=None,boxStrokeWidth=None,boxFillColor=None,boxTarget=None,fillColor=None,strokeColor=None,strokeWidth=None,frontName=None,frontSize=None,leading=None,width=None,maxWidth=None,height=None,textAnchor=None,visible=None,leftPadding=None,rightPadding=None,topPadding=None,bottomPadding=None):
        return self.child('spokeLabels',dx=dx,dy=dy,angle=angle,boxAnchor=boxAnchor,boxStrokeColor=boxStrokeColor,boxStrokeWidth=boxStrokeWidth,boxFillColor=boxFillColor,boxTarget=boxTarget,fillColor=fillColor,strokeColor=strokeColor,strokeWidth=strokeWidth,frontName=frontName,frontSize=frontSize,leading=leading,width=width,maxWidth=maxWidth,height=height,textAnchor=textAnchor,visible=visible,leftPadding=leftPadding,rightPadding=rightPadding,topPadding=topPadding,bottomPadding=bottomPadding)



class GnrRml(object):

    def __init__(self, filename='', invariant=1, **kwargs):
        self.root = GnrRmlSrc.makeRoot()
        self.document = self.root.document(filename=filename, invariant=invariant, **kwargs)
        self.stylesheets=self.document.stylesheet()
        
    def template(self,**kwargs):
        self.templates=self.document.template(**kwargs)
        
    def toRml(self,filename=None):
        if filename:
            filename=expandpath(filename)
        return self.root.toRml(filename=filename)
        
    def toPdf(self,filename=None):
        if filename:
            self.root.setAttr('#0',filename=os.path.basename(filename))
            output = open(expandpath(filename),'wb')
        else:
            output = cStringIO.StringIO()
        root = etree.fromstring(self.toRml())
        pdf = pdfdoc.Document(root)
        pdf.process(output)
        if not filename:
            output.seek(0)
            return output.read()
        output.close()