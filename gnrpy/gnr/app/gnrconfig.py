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
import gnr
from collections import defaultdict

from gnr.core.gnrsys import expandpath
from gnr.core.gnrbag import Bag
from gnr.core.gnrlang import gnrImport
from gnr.core.gnrstring import slugify

from gnr.core.gnrstructures import  GnrStructData

class ConfigStruct(GnrStructData):
    config_method = 'config'
    def __init__(self,filepath=None,autoconvert=False,**kwargs):
        super(ConfigStruct, self).__init__()
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
            getattr(m,self.config_method)(self,**kwargs)
        elif ext=='.xml':
            self.fillFrom(filepath)
            if len(self) and autoconvert:
                self.toPython(filepath.replace('.xml','.py'))
        else:
            raise Exception('Wrong extension for filepath')


class InstanceConfigStruct(ConfigStruct):
    config_method = 'instanceconfig'
    def db(self, implementation='postgres', dbname=None,filename=None,**kwargs):
        return self.child('db',implementation=implementation,dbname=dbname,filename=filename,**kwargs)


class MenuStruct(ConfigStruct):
    def branch(self, label, basepath=None ,tags='', **kwargs):
        return self.child('branch',label=label,basepath=basepath,tags=tags,**kwargs)

    def webpage(self, label,filepath=None,tags='',multipage=None, **kwargs):
        return self.child('webpage',label=label,multipage=multipage,tags=tags,file=filepath,_returnStruct=False,**kwargs)

    def thpage(self, label,table=None,tags='',multipage=None, **kwargs):
        return self.child('thpage',label=label,table=table,
                            multipage=multipage,tags=tags,_returnStruct=False,**kwargs)

    def lookups(self,label,lookup_manager=None,tags=None,**kwargs):
        return self.child('lookups',label=label,lookup_manager=lookup_manager,tags=tags,_returnStruct=False,**kwargs)

    def toPython(self,filepath=None):
        filepath = filepath or 'menu.py'
        with open(filepath,'w') as f:
            text = """#!/usr/bin/env python
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

class IniConfStruct(ConfigStruct):

    def section(self,section=None,name=None,label=None):
        return self.child('section',name=name,section=section,childname=label or name,label=label)

    def parameter(self,parameter=None,value=None):
        return self.child('parameter',parameter=parameter,value=value,childname=parameter.replace('.','_'))

    def toIniConf(self,filepath):
        with open(filepath,'w') as f:
            self._toIniConfInner(f,self)

    def _toIniConfInner(self,filehandle,b):
        for n in b:
            kw = dict(n.attr)
            tag = kw.pop('tag',None)
            key = kw.pop(tag)
            if tag=='section':
                filehandle.write('\n')
                section_name = kw.get('name')
                filehandle.write('[%s]\n' %('%s:%s' %(key,section_name) if section_name else key))
                if n.value:
                    subsections = defaultdict(list)
                    for sn in n.value.nodes:
                        section = sn.attr.get('section')
                        if section:
                            subsections[section].append(sn.attr['name'])
                    if subsections:
                        for k,v in subsections.items():
                            filehandle.write('%ss=%s\n' %(k,','.join(v)))
                    
            elif tag=='parameter':
                parameter_value = kw.pop('value')
                parameter = kw.pop('parameter',key)
                if n.value:
                    parameter_value = n.value.keys()
                filehandle.write('%s=%s' %(key,parameter_value))
            if n.value:
                self._toIniConfInner(filehandle,n.value)
            filehandle.write('\n')

    def toPython(self,filepath=None):
        with open(filepath,'w') as f:
            text = """# encoding: utf-8
def config(root):"""         
            f.write(text)
            self._toPythonInner(f,self,'root')

    def _toPythonInner(self,filehandle,b,rootname):
        filehandle.write('\n')
        for n in b:
            kw = dict(n.attr)
            tag = kw.pop('tag')
            key = kw.pop(tag)
            label = kw.get('name') or key
            attrlist = ['u"%s"' %key]
            for k,v in kw.items():
                attrlist.append('%s="%s"' %(k,v))
            if n.value:
                varname = slugify(label).replace('-','_')
                filehandle.write('    %s = %s.%s(%s)' %(varname,rootname,tag,', '.join(attrlist)))
                self._toPythonInner(filehandle,n.value,varname) 
            else:
                filehandle.write('    %s.%s(%s)' %(rootname,tag,', '.join(attrlist)))
            filehandle.write('\n')

########################################
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

def setEnvironment(gnr_config):
    environment_xml = gnr_config['gnr.environment_xml']
    if environment_xml:
        for var, value in environment_xml.digest('environment:#k,#a.value'):
            var = var.upper()
            if not os.getenv(var):
                os.environ[str(var)] = str(value)

def getGnrConfig(config_path=None, set_environment=False):
    config_path = config_path or gnrConfigPath()
    if not config_path or not os.path.isdir(config_path):
        raise Exception('Missing genro configuration')
    gnr_config = Bag(config_path)
    if set_environment:
        setEnvironment(gnr_config)
    return gnr_config

def gnrConfigPath(force_return=False, no_virtualenv=False):
    if os.environ.has_key('GENRO_GNRFOLDER'):
        config_path = expandpath(os.environ['GENRO_GNRFOLDER'])
        if os.path.isdir(config_path):
            return config_path
    if (os.environ.has_key('VIRTUAL_ENV') or hasattr(sys, 'real_prefix')) and not no_virtualenv:
        prefix = os.environ.get('VIRTUAL_ENV', sys.prefix)
        config_path = expandpath(os.path.join(prefix,'etc','gnr'))
        if force_return or os.path.isdir(config_path):
            return config_path
    if sys.platform == 'win32':
        config_path = '~\gnr'
    else:
        config_path = '~/.gnr'
    config_path  = expandpath(config_path)
    if force_return or os.path.isdir(config_path):
        return config_path
    config_path = expandpath('/etc/gnr')
    if os.path.isdir(config_path):
        return config_path

def updateGnrEnvironment(updater):
    config_path = gnrConfigPath()
    environment_path = os.path.join(config_path,'environment.xml')
    environment_bag = Bag(environment_path) 
    environment_bag.update(updater)
    environment_bag.toXml(environment_path,pretty=True)

def getRmsOptions():
    config_path = gnrConfigPath()
    environment_path = os.path.join(config_path,'environment.xml')
    environment_bag = Bag(environment_path) 
    return environment_bag.getAttr('rms')

def setRmsOptions(**options):
    config_path = gnrConfigPath()
    environment_path = os.path.join(config_path,'environment.xml')
    environment_bag = Bag(environment_path) 
    environment_bag.setAttr('rms',**options)
    environment_bag.toXml(environment_path,pretty=True)

def getGenroRoot():
    return os.path.abspath(os.path.join(gnr.__file__,'..','..','..'))
        


