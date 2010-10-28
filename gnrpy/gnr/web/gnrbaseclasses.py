#-*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package           : GenroPy web - see LICENSE for details
# module gnrwebcore : core module for genropy web framework
# Copyright (c)     : 2004 - 2007 Softwell sas - Milano 
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


"""
core.py

Created by Giovanni Porcari on 2007-03-24.
Copyright (c) 2007 Softwell. All rights reserved.
"""
import os
from gnr.core.gnrbag import Bag 
from gnr.core.gnrbaghtml import BagToHtml
from gnr.core.gnrstring import  splitAndStrip,slugify
from gnr.core.gnrdict import dictExtract
from gnr.core.gnrlang import GnrObject, uniquify
from itertools import chain


def page_mixin(func):
    def decore(self,obj,*args,**kwargs):
        setattr(func,'_mixin_type','page')
        result= func(self,obj,*args,**kwargs)
        return result
    return decore

class BaseComponent(object):
    """docstring for BaseComponent"""
    def __onmixin__(self, _mixinsource, site=None):
        js_requires = splitAndStrip(getattr(_mixinsource, 'js_requires', ''),',')
        css_requires = splitAndStrip(getattr(_mixinsource, 'css_requires', ''),',')
        py_requires = splitAndStrip(getattr(_mixinsource, 'py_requires', '') ,',')
        for css in css_requires:
            if css and not css in self.css_requires:
                self.css_requires.append(css)
        for js in js_requires:
            if js and not js in self.js_requires:
                self.js_requires.append(js)
                
        #self.css_requires.extend(css_requires)
        #self.js_requires.extend(js_requires)
        if py_requires:
            if site:
                site.page_pyrequires_mixin(self, py_requires)
            else:
                self._pyrequiresMixin(py_requires)
    
    @classmethod
    def __on_class_mixin__(cls, _mixintarget, **kwargs):
        js_requires = [x for x in splitAndStrip(getattr(cls, 'js_requires', ''),',') if x]
        css_requires = [x for x in splitAndStrip(getattr(cls, 'css_requires', ''),',') if x]
        for css in css_requires:
            if css and not css in _mixintarget.css_requires:
                _mixintarget.css_requires.append(css)
        for js in js_requires:
            if js and not js in _mixintarget.js_requires:
                _mixintarget.js_requires.append(js)
    
    @classmethod
    def __py_requires__(cls, target_class, **kwargs):
        from gnr.web.gnrwsgisite import currentSite
        loader = currentSite().resource_loader
        return loader.py_requires_iterator(cls, target_class)
        

class BaseResource(GnrObject):
    """Base class for a webpage resource."""
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            if v:
                setattr(self,k,v)

class BaseProxy(object):
    """Base class for a webpage proxy."""
    def __init__(self,**kwargs):
        for argname,argvalue in kwargs.items():
            setattr(self,argname,argvalue)

class BaseWebtool(object):
    pass

    
class TableScriptToHtml(BagToHtml):
    rows_table = None
    
    def __init__(self,page=None,resource_table=None,**kwargs):
        super(TableScriptToHtml, self).__init__(**kwargs)
        self.page = page
        self.db = page.db
        self.tblobj = resource_table
        self.maintable = resource_table.fullname
        self.templateLoader = self.db.table('adm.htmltemplate').getTemplate
        self.thermo_wrapper = self.page.btc.thermo_wrapper
        self.print_handler = self.page.getService('print')
        self.record = None
    
    def __call__(self,record=None,pdf=None,downloadAs=None,thermo=None,**kwargs):
        if not record:
            return
        self.thermo_kwargs = thermo
        record = self.tblobj.recordAs(record)
        html_folder = self.getHtmlPath(autocreate=True)
        pdf_folder = self.getPdfPath(autocreate=True)
        html = super(TableScriptToHtml, self).__call__(record=record,folder=html_folder,**kwargs)
        if not html:
            return False
        if not pdf:
            return html
            
            
        docname = os.path.splitext(os.path.basename(self.filepath))[0]
        self.pdfpath = self.getPdfPath('%s.pdf' %docname)
        self.print_handler.htmlToPdf(self.filepath, self.pdfpath)
        if downloadAs:
            with open(self.pdfpath,'rb') as f:
                result=f.read()
            return result
        else:
            return self.pdfpath
           #with open(temp.name,'rb') as f:
           #    result=f.read()
        
    def get_record_caption(self,item,progress,maximum,**kwargs):
        if self.rows_table:
            tblobj = self.db.table(self.rows_table)
            caption = '%s (%i/%i)' % (tblobj.recordCaption(item.value),progress,maximum)
        else:
            caption = '%i/%i' % (progress,maximum)
        return caption

    
    def getHtmlPath(self,*args,**kwargs):
        return self.page.site.getStaticPath('conn:html',*args,**kwargs)

    def getPdfPath(self,*args,**kwargs):
        return self.page.site.getStaticPath('conn:pdf',*args,**kwargs)
        
    def getHtmlUrl(self,*args,**kwargs):
        return self.page.site.getStaticUrl('conn:html',*args,**kwargs)
        
    def getPdfUrl(self,*args,**kwargs):
        return self.page.site.getStaticUrl('conn:pdf',*args,**kwargs)

        
    def outputDocName(self, ext=''):
        if ext and not ext[0]=='.':
            ext = '.%s' % ext
        caption = ''
        if self.record is not None:
            caption= slugify(self.tblobj.recordCaption(self.getData('record')))
        doc_name = '%s_%s%s' % (self.tblobj.name, caption, ext)
        return doc_name
    