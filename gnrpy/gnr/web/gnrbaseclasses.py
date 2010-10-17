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
import tempfile
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
    html_folder = '*connections/html'
    pdf_folder = '*connections/pdf'
    
    def __init__(self,page=None,resource_table=None,**kwargs):
        super(TableScriptToHtml, self).__init__(**kwargs)
        self.page = page
        self.db = page.db
        self.tblobj = resource_table
        self.maintable = resource_table.fullname
        self.templateLoader = self.db.table('adm.htmltemplate').getTemplate
        self.thermo_wrapper = self.page.btc.thermo_wrapper
    
    def __call__(self,record=None,folder=None,pdf=None,**kwargs):
        record = self.tblobj.recordAs(record, mode='bag') 
        folder = folder or self.hmtlFolderPath()
        self.thermo_kwargs = dictExtract(kwargs,'thermo_',pop=True)
        result = super(TableScriptToHtml, self).__call__(record=record,folder=folder,**kwargs)
        if pdf:
            temp = tempfile.NamedTemporaryFile(suffix='.pdf')
            self.page.getService('print').htmlToPdf(self.filepath, temp.name)
            with open(temp.name,'rb') as f:
                result=f.read()
        return result
    
    def hmtlFolderPath(self):
        return self.getFolderPath(*self.html_folder.split('/'))
        
    def getFolderPath(self, *folders):
        folders=folders or []
        if folders and folders[0] == '*connections':
            folders = [self.page.connectionDocument(*list(folders[1:]+('',)))] 
        elif folders and folders[0] == '*users':
            folders = [self.page.userDocument(*list(folders[1:]+('',)))] 
        result = os.path.join(*folders)
        return result
        
        
    def outputDocName(self, ext=''):
        if ext and not ext[0]=='.':
            ext = '.%s' % ext
        caption = ''
        if self.record is not None:
            caption= slugify(self.tblobj.recordCaption(self.getData('record')))
        doc_name = '%s_%s%s' % (self.tblobj.name, caption, ext)
        return doc_name
    