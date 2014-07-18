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

import os
import sys
import glob
from gnr.core.gnrsys import expandpath
from gnr.core.gnrbag import Bag
from gnr.core.gnrlang import gnrImport
from gnr.core.gnrstring import slugify

from gnr.core.gnrstructures import  GnrStructData

class MenuStruct(GnrStructData):
    def __init__(self,filepath=None,application=None,autoconvert=False):
        super(MenuStruct, self).__init__()
        self.setBackRef()
        if not filepath:
            return
        filename,ext = os.path.splitext(filepath)

        if not ext:
            if os.path.exists('%s.xml' %filepath):
                filepath = '%s.xml' %filepath
                ext = '.xml'
            elif os.path.exists('%s.py' %filepath):
                filepath = '%s.py' %filepath
                ext = '.py'
            else:
                return
        if ext=='.py':
            m = gnrImport(filepath, avoidDup=True)
            m.config(self,application=application)
        elif ext=='.xml':
            self.fillFrom(filepath)
            if len(self) and autoconvert:
                self.toPython(filepath.replace('.xml','.py'))
        else:
            raise Exception('Wrong extension for filepath')


    def branch(self, label, basepath=None ,tags='', **kwargs):
        return self.child('branch',label=label,basepath=basepath,tags=tags,**kwargs)

    def webpage(self, label,filepath=None,tags='',multipage=None, **kwargs):
        return self.child('webpage',label=label,multipage=multipage,tags=tags,file=filepath,_returnStruct=False,**kwargs)

    def thpage(self, label,table=None,tags='',multipage=None, **kwargs):
        return self.child('thpage',label=label,table=table,multipage=multipage,tags=tags,_returnStruct=False,**kwargs)

    def lookups(self,label,lookup_manager=None,tags=None,**kwargs):
        return self.child('lookups',label=label,lookup_manager=lookup_manager,tags=tags,_returnStruct=False,**kwargs)

    def toPython(self,filepath=None):
        filepath = filepath or 'menu.py'
        with open(filepath,'w') as f:
            text = """
#!/usr/bin/env python
# encoding: utf-8
def config(root,application=None):"""         
            f.write(text)
            self._toPythonInner(f,self,'root')


    def _toPythonInner(self,filehandle,b,rootname):
        filehandle.write('\n')
        for n in b:
            kw = dict(n.attr)
            label = kw.pop('label',n.label)
            attrlist = ['u"%s"' %label]
            for k,v in kw.items():
                if k=='file':
                    k = 'filepath'
                attrlist.append('%s="%s"' %(k,v))
            if n.value:
                varname = slugify(label).replace('!!','').replace('-','_')
                filehandle.write('    %s = %s.branch(%s)' %(varname,rootname,', '.join(attrlist)))
                self._toPythonInner(filehandle,n.value,varname) 
            elif 'table' in kw:
                filehandle.write('    %s.thpage(%s)' %(rootname,', '.join(attrlist)))
            elif 'lookup_manager' in kw:
                filehandle.write('    %s.lookups(%s)' %(rootname,', '.join(attrlist)))
            elif 'pkg' in kw:
                filehandle.write('    %s.branch(%s)' %(rootname,', '.join(attrlist)))
            else:
                filehandle.write('    %s.webpage(%s)' %(rootname,', '.join(attrlist)))
            filehandle.write('\n')


def getSiteHandler(site_name, gnr_config=None):
    gnr_config = gnr_config or getGnrConfig()
    path_list = []
    gnrenv = gnr_config['gnr.environment_xml']
    sites = gnrenv['sites']
    projects = gnrenv['projects']
    if sites:
        sites = sites.digest('#a.path,#a.site_template')
        path_list.extend([(expandpath(path), site_template) for path, site_template in sites 
                                                            if os.path.isdir(expandpath(path))])
    if projects:
        projects = projects.digest('#a.path,#a.site_template') 
        projects = [(expandpath(path), template) for path, template in projects
                                                 if os.path.isdir(expandpath(path))]
        for project_path, site_template in projects:
            sites = glob.glob(os.path.join(project_path, '*/sites'))
            path_list.extend([(site_path, site_template) for site_path in sites])
    for path, site_template in path_list:
        site_path = os.path.join(path, site_name)
        if os.path.isdir(site_path):
            site_script = os.path.join(site_path, 'root.py')
            if not os.path.isfile(site_script):
                site_script = None
            return dict(site_path=site_path,
                            site_template=site_template,
                            site_script = site_script)

def getGnrConfig(config_path=None):
    config = Bag()
    config_path = config_path or gnrConfigPath()
    if os.path.isdir(config_path):
        config = Bag(config_path)
    return config

def gnrConfigPath():
    if os.environ.has_key('VIRTUAL_ENV'):
        config_path = expandpath(os.path.join(os.environ['VIRTUAL_ENV'],'etc','gnr'))
    elif sys.platform == 'win32':
        config_path = '~\gnr'
    else:
        config_path = '~/.gnr'
    config_path  = expandpath(config_path)
    return config_path
        


