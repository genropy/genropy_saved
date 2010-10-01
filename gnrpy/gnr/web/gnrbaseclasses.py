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
    batch_steps = None #'foo,bar'

    def __init__(self,page=None,resource_table=None):
        self.page = page
        self.resource_table = resource_table
        self.btc = self.page.btc
    
    def __call__(self,batch_note=None,**kwargs):
        self.batch_parameters = kwargs
        self.batch_note = batch_note
        try:
            self.run()
        except self.btc.exception_stopped:
           self.btc.batch_aborted()
        except Exception, e:
           self.btc.batch_error(error=str(e))
        self.btc.batch_complete(self.result_handler())
    
    def run(self):
        self.btc.batch_create(batch_id='%s_%s' %(self.batch_prefix,self.page.getUuid()),
                            title=self.batch_title,
                            cancellable=self.batch_cancellable,delay=self.batch_delay,note=self.batch_note) 
        if self.batch_steps:
            for step in self.btc.thermo_wrapper(self.batch_steps,'btc_steps',message=self.get_step_caption,keep=True):
                step_handler = getattr(self,'step_%s' %step)
                step_handler()
        else:
            self.do()
    
    def result_handler(self):
        return 'Execution completed',dict()
        
    def get_step_caption(self,item,progress,maximum,**kwargs):
        step_handler = getattr(self,'step_%s' %item)
        return step_handler.__doc__
        
    def get_record_caption(self,item,progress,maximum,iterable=None,**kwargs):
        caption = iterable.dbtable.recordCaption(item)
        return '%s (%i/%i)' %(caption,progress,maximum)

    def do(self,**kwargs):
        """override me"""
        pass
    
    def defineSelection(self,selectionName=None,selectedRowidx=None):
        self.selectionName = selectionName
        self.selectedRowidx = selectedRowidx
    
    def get_selection(self):
        selection = self.page.getUserSelection(selectionName=self.selectionName,
                                         selectedRowidx=self.selectedRowidx)
        return selection
        
    def rpc_selectionFilterCb(self,row):
        """override me"""
        return True
        
    def parameters_pane(self,pane,**kwargs):
        """Pass a ContentPane for adding forms to allow you to ask parameters to the clients"""
        pass
    
class BaseResourceAction(BaseResourceBatch):
    pass
    
class BaseResourceMail(BaseResourceBatch):
    def __init__(self,*args,**kwargs):
        super(BaseResourceMail,self).__init__(**kwargs)
        self.mail_handler = self.page.getService('mail')
        self.mail_pars = dict()
        
        
    def send_one_mail(self, chunk, **kwargs):
        mp = self.mail_pars
        self.mail_handler.sendmail_template(chunk, to_address=mp['to_address'] or chunk[self.doctemplate['meta.to_address']],
                         body=self.doctemplate['content'],subject=self.doctemplate['meta.subject'],
                         cc_address=mp['cc_address'], bcc_address=mp['bcc_address'], from_address=mp['from_address'], 
                         attachments=mp['attachments'], account=mp['account'],
                         host=mp['host'], port=mp['port'], user=mp['user'], password=mp['password'],
                         ssl=mp['ssl'], tls=mp['tls'], html=True,  async=True)
    
class BaseResourcePrint(BaseResourceBatch):
    pass
    
    