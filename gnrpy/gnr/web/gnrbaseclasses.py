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

#Created by Giovanni Porcari on 2007-03-24.
#Copyright (c) 2007 Softwell. All rights reserved.

import os,sys
from gnr.core.gnrbaghtml import BagToHtml
from gnr.core.gnrdecorator import extract_kwargs
from gnr.core.gnrstring import  splitAndStrip, slugify,templateReplace
from gnr.core.gnrlang import GnrObject
from gnr.core.gnrbag import Bag

def page_mixin(func):
    """TODO
    
    :param func: TODO"""
    def decore(self, obj, *args, **kwargs):
        setattr(func, '_mixin_type', 'page')
        result = func(self, obj, *args, **kwargs)
        return result
        
    return decore

def zzzcomponent_hook(func_or_name):
    """A decorator. Allow to register a new method (in a page or in a component)
    that will be available in the web structs::
        
        @struct_method
        def includedViewBox(self, bc, ...):
            pass
            
        def somewhereElse(self, bc):
            bc.includedViewBox(...)
            
    If the method name includes an underscore, only the part that follows the first
    underscore will be the struct method's name::
        
        @struct_method
        def iv_foo(self, bc, ...):
            pass
            
        def somewhereElse(self, bc):
            bc.foo(...)
            
    You can also pass a name explicitly::
        
        @struct_method('bar')
        def foo(self, bc, ...):
            pass
            
        def somewhereElse(self, bc):
            bc.bar(...)"""
            
    def register(name, func):
        """TODO
        
        :param func:"""
        func_name = func.__name__
        existing_name = GnrDomSrc._external_methods.get(name, None)
        if existing_name and (existing_name != func_name):
            # If you want to override a struct_method, be sure to call its implementation method in the same way as the original.
            # (Otherwise, the result would NOT  be well defined due to uncertainty in the mixin process at runtime plus the fact that the GnrDomSrc is global)
            raise StructMethodError(
                    "struct_method %s is already tied to implementation method %s" % (repr(name), repr(existing_name)))
        GnrDomSrc._external_methods[name] = func_name
        
    if isinstance(func_or_name, basestring):
        name = func_or_name
        
        def decorate(func):
            register(name, func)
            return func
            
        return decorate
    else:
        name = func_or_name.__name__
        if '_' in name:
            name = name.split('_', 1)[1]
        register(name, func_or_name)
        return func_or_name
        
class BaseComponent(object):
    """The base class for the :ref:`components`"""
    def __onmixin__(self, _mixinsource, site=None):
        js_requires = splitAndStrip(getattr(_mixinsource, 'js_requires', ''), ',')
        css_requires = splitAndStrip(getattr(_mixinsource, 'css_requires', ''), ',')
        py_requires = splitAndStrip(getattr(_mixinsource, 'py_requires', ''), ',')
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
            elif hasattr(self, '_pyrequiresMixin'):
                self._pyrequiresMixin(py_requires)
                
    @classmethod
    def __on_class_mixin__(cls, _mixintarget, **kwargs):
        js_requires = [x for x in splitAndStrip(getattr(cls, 'js_requires', ''), ',') if x]
        css_requires = [x for x in splitAndStrip(getattr(cls, 'css_requires', ''), ',') if x]
        namespace = getattr(cls, 'namespace', None)
        if namespace:
            if not hasattr(_mixintarget, 'struct_namespaces'):
                _mixintarget.struct_namespaces = set()
            _mixintarget.struct_namespaces.add(namespace)
        if css_requires and not hasattr(_mixintarget, 'css_requires'):
            _mixintarget.css_requires=[] 
        for css in css_requires:
            if css and not css in _mixintarget.css_requires:
                _mixintarget.css_requires.append(css)
        if js_requires and not hasattr(_mixintarget, 'js_requires'):
            _mixintarget.js_requires=[]
        for js in js_requires:
            if js and not js in _mixintarget.js_requires:
                _mixintarget.js_requires.append(js)
                
    @classmethod
    def __py_requires__(cls, target_class, **kwargs):
        from gnr.web.gnrwsgisite import currentSite
        
        loader = currentSite().resource_loader
        return loader.py_requires_iterator(cls, target_class)
        
class BaseResource(GnrObject):
    """Base class for a webpage resource"""
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if v:
                setattr(self, k, v)
                
class BaseProxy(object):
    """Base class for a webpage proxy"""
        
    def __init__(self, **kwargs):
        for argname, argvalue in kwargs.items():
            setattr(self, argname, argvalue)
            
class BaseWebtool(object):
    """TODO"""
    pass
        

class TableScriptToHtml(BagToHtml):
    """TODO"""
    rows_table = None
    virtual_columns = None
    html_folder = 'temp:html'
    pdf_folder = 'page:pdf'
    cached = None
    css_requires = 'print_stylesheet'
    client_locale = False


    def __init__(self, page=None, resource_table=None, **kwargs):
        super(TableScriptToHtml, self).__init__(**kwargs)
        self.page = page
        self.site = page.site
        self.db = page.db
        self.locale = self.page.locale if self.client_locale else self.site.server_locale
        self.tblobj = resource_table
        self.maintable = resource_table.fullname
        self.templateLoader = self.db.table('adm.htmltemplate').getTemplate
        self.thermo_wrapper = self.page.btc.thermo_wrapper
        self.print_handler = self.page.getService('print')
        self.record = None
        
    def __call__(self, record=None, pdf=None, downloadAs=None, thermo=None,record_idx=None,serveAsLocalhost=None, **kwargs):
        if not record:
            return
        self.thermo_kwargs = thermo
        self.record_idx = record_idx
        if record=='*':
            record = None
        else:
            record = self.tblobj.recordAs(record, virtual_columns=self.virtual_columns)
        self.serveAsLocalhost = serveAsLocalhost or pdf
        html_folder = self.getHtmlPath(autocreate=True)
        html = super(TableScriptToHtml, self).__call__(record=record, folder=html_folder, **kwargs)
        
        if not html:
            return False
        if not pdf:
            return html
        
        self.writePdf(docname=self.getDocName())
        if downloadAs:
            with open(self.pdfpath, 'rb') as f:
                result = f.read()
            return result
        else:
            return self.pdfpath
            #with open(temp.name,'rb') as f:
            #    result=f.read()

    def getDocName(self):
        return os.path.splitext(os.path.basename(self.filepath))[0]

    @extract_kwargs(pdf=True)
    def writePdf(self,filepath=None, pdfpath=None,docname=None,pdf_kwargs=None,**kwargs):
        self.pdfpath = pdfpath or self.getPdfPath('%s.pdf' % docname, autocreate=-1)
        self.print_handler.htmlToPdf(filepath or self.filepath, self.pdfpath, orientation=self.orientation(),pdf_kwargs=pdf_kwargs)

    def get_css_requires(self):
        """TODO"""
        css_requires = []
        for css_require in self.css_requires.split(','):
            if not css_require.startswith('http'):
                css_requires.extend(self.page.getResourceExternalUriList(css_require,'css',serveAsLocalhost=self.serveAsLocalhost))
            else:
                css_requires.append(css_require)
        return css_requires
        
    def get_record_caption(self, item, progress, maximum, **kwargs):
        """TODO
        
        :param item: TODO
        :param progress: TODO
        :param maximum: TODO"""
        if self.rows_table:
            tblobj = self.db.table(self.rows_table)
            caption = '%s (%i/%i)' % (tblobj.recordCaption(item.value), progress, maximum)
        else:
            caption = '%i/%i' % (progress, maximum)
        return caption
        
    def getHtmlPath(self, *args, **kwargs):
        """TODO"""
        return self.site.getStaticPath(self.html_folder, *args, **kwargs)
        
    def getPdfPath(self, *args, **kwargs):
        """TODO"""
        return self.site.getStaticPath(self.pdf_folder, *args, **kwargs)
        
    def getHtmlUrl(self, *args, **kwargs):
        """TODO"""
        return self.site.getStaticUrl(self.html_folder, *args, **kwargs)
        
    def getPdfUrl(self, *args, **kwargs):
        """TODO"""
        return self.site.getStaticUrl(self.pdf_folder, *args, **kwargs)
        
    def outputDocName(self, ext=''):
        """TODO
        :param ext: TODO"""
        if ext and not ext[0] == '.':
            ext = '.%s' % ext
        caption = ''
        if self.record is not None:
            caption = slugify(self.tblobj.recordCaption(self.getData('record')))
            idx = self.record_idx
            if idx is not None:
                caption = '%s_%i' %(caption,idx)
        doc_name = '%s_%s%s' % (self.tblobj.name, caption, ext)
        return doc_name

class TableTemplateToHtml(BagToHtml):
    def __init__(self, table=None, **kwargs):
        super(TableTemplateToHtml, self).__init__(**kwargs)
        self.db = table.db
        self.site = self.db.application.site
        self.tblobj = table
        self.maintable = table.fullname
        self.templateLoader = self.db.table('adm.htmltemplate').getTemplate
        self.print_handler = self.site.getService('print')
        self.record = None

    def __call__(self,record=None,template=None, htmlContent=None, locale=None,**kwargs):
        if not htmlContent:
            htmlContent = self.contentFromTemplate(record,template,locale=locale)
            record = self.record
        return super(TableTemplateToHtml, self).__call__(record=record,htmlContent=htmlContent,**kwargs)

    def contentFromTemplate(self,record,template,locale=None,**kwargs):
        virtual_columns=None
        if isinstance(template,Bag):
            kwargs['locale'] = locale or template.getItem('main?locale')
            kwargs['masks'] = template.getItem('main?masks')
            kwargs['formats'] = template.getItem('main?formats')
            kwargs['df_templates'] = template.getItem('main?df_templates')
            kwargs['dtypes'] = template.getItem('main?dtypes')
            virtual_columns = template.getItem('main?virtual_columns')
        self.record = self.tblobj.recordAs(record,virtual_columns=virtual_columns)
        return templateReplace(template,self.record, safeMode=True,noneIsBlank=False,
                    localizer=self.db.application.localizeText,urlformatter=self.site.externalUrl,
                    **kwargs)

    @extract_kwargs(pdf=True)
    def writePdf(self,pdfpath=None,docname=None,pdf_kwargs=None,**kwargs):
        pdfpath = pdfpath or self.filepath.replace('.html','.pdf')
        self.print_handler.htmlToPdf(self.filepath,pdfpath, orientation=self.orientation(),pdf_kwargs=pdf_kwargs)
        return pdfpath

        

