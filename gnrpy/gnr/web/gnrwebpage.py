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
from gnr.core.gnrlang import GnrObject

class GnrWebPage(object):
    pass


class GnrIndexWebPage(object):
    def main(self, root, **kwargs):
        #root=self.rootLayoutContainer(root,_class='index_browserPane',menues='')
        directory=Bag()
        back=self.utils.relativePageFolder().lstrip('/').split('/')
        directory=self.utils.dirbag(include='*.py',exclude='_*,.*,*.wsgi,indexwsgi.py')
        directory=directory['#0']
        self.walkDirectory(directory,root,back)

    def windowTitle(self):
        return 'IndexPage:'+self.utils.relativePageFolder().lstrip('/')

    def walkDirectory(self, bag, where, back=None):
        cmax=10
        c=cmax
        if back:
            table=where.table(border="0",cellspacing="0", cellpadding="0",id='folderIndexTable').tbody()
            main=back.pop()
            href=['..' for x in back]
            for label in back:
                label = '!!' + label.replace('_',' ').capitalize() 
                row=table.tr()
                row.td(_class='index_td index_back',content=label,connect_onclick='genro.gotoURL("%s")'% '/'.join(href))
                href.pop()
            row=table.tr()
            row.td(_class='index_header',content=main.replace('_',' ').capitalize())
            table=table.tr().td(_class='index_back_client').table(border="0",cellspacing="1", cellpadding="0" ).tbody()
        else:
            table=where.table(border="0",cellspacing="1", cellpadding="0", border_spacing='2px').tbody()

        for n in bag.nodes: 
            k=n.label   
            label = '!!' + k.replace('_',' ').capitalize()   
            v=n.value
            href=self.utils.diskPathToUri(n.getAttr('abs_path'))
            if hasattr(v,'items'):
                row=table.tr()
                row.td(_class='index_td index_folder',connect_onclick='genro.gotoURL("%s")'% href,content=label)
                self.walkDirectory( v,row.td(_class='index_tdfolder_right'))
                c=cmax
            elif k != 'index':
                c=c+1
                if(c>cmax):
                    c=1
                    row=table.tr()
                row.td(_class='index_td index_file',connect_onclick='genro.gotoURL("%s")'% href,content=label)
                
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
    def __on_class_mixin__(cls, _mixintarget, site=None):
        js_requires = [x for x in splitAndStrip(getattr(cls, 'js_requires', ''),',') if x]
        css_requires = [x for x in splitAndStrip(getattr(cls, 'css_requires', ''),',') if x]
        py_requires = [x for x in splitAndStrip(getattr(cls, 'py_requires', '') ,',') if x]
        for css in css_requires:
            if css and not css in _mixintarget.css_requires:
                _mixintarget.css_requires.append(css)
        for js in js_requires:
            if js and not js in _mixintarget.js_requires:
                _mixintarget.js_requires.append(js)
                
        #_mixintarget.css_requires.extend(css_requires)
        #_mixintarget.js_requires.extend(js_requires)
        if py_requires:
            if site:
                site.page_pyrequires_mixin(_mixintarget, py_requires)

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
