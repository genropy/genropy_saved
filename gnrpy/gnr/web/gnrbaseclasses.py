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
from gnr.core.gnrbag import Bag 
from gnr.core.gnrstring import  splitAndStrip
from gnr.core.gnrlang import GnrObject, uniquify
from itertools import chain

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
    
class BaseResourceBatch(object):
    batch_prefix = 'BB'
    batch_thermo_lines = 'batch_steps,batch_main,ts_loop'
    batch_title = 'My Batch Title'
    batch_cancellable = True
    batch_delay = 0.5
    batch_note = None

    def __init__(self,page=None,resource_table=None):
        self.page = page
        self.resource_table = resource_table
    
    def do(self,**kwargs):
        """override me"""
        btc_handler = self.page.btc
        btc_handler.batch_create(batch_id='%s_%s' %(self.batch_prefix,self.page.getUuid()),
                            title=self.batch_title,thermo_lines=self.batch_thermo_lines,
                            cancellable=self.batch_cancellable,delay=self.batch_delay,note=self.batch_note) 
        self.page.btc.thermo_line_start(line='batch_steps',maximum=5,message='')
        self.btc.thermo_line_update(line='batch_steps',maximum=6,progress=1,message='Getting data')
    
    def defineSelection(self,selectionName=None,selectedRowIdx=None):
        self.selectionName = selectionName
        self.selectedRowIdx = selectedRowIdx
    
    @property
    def selection(self):
        self.selection = self.page.getUserSelection(selectionName=self.selectionName,
                                         selectedRowidx=self.selectedRowidx,
                                         filterCb=self.selectionFilterCb)
    
    def selectionFilterCb(self,row):
        """override me"""
        return True
        
    def askParameters(self,pane,**kwargs):
        """Pass a ContentPane for adding forms to allow you to ask parameters to the clients"""
        pass
    
        

class BaseResourceAction(BaseResourceBatch):
    pass
    
class BaseResourceMail(BaseResourceBatch):
    pass
    
    
class BaseResourcePrint(BaseResourceBatch):
    pass
    
    