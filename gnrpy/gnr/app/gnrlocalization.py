# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy app - see LICENSE for details
# module gnrapp : Genro application architecture.
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


import os
import re
import hashlib
from gnr.app.gnrconfig import getGenroRoot
from gnr.core.gnrstring import flatten
from gnr.core.gnrbag import Bag,DirectoryResolver


LOCREGEXP_EXCL = re.compile(r"""("{3}|'|")!!({\w*})?(.*?)\1""")

LOCREGEXP_CLS = re.compile(r"""\b_T\(("{3}|'|")(.*?)\1\)""")

PACKAGERELPATH = re.compile(r".*/packages/(.*)")

class GnrLocString(unicode):
    def __new__(cls,value,module=None,lockey=None):
        s = super(GnrLocString, cls).__new__(cls,value)
        s._module = module or __name__
        s._lockey = lockey or hashlib.md5('%s_%s' %(s._module,value)).hexdigest()
        return s

    def __mod__(self,*args,**kwargs):
        return GnrLocString(super(GnrLocString, self).__mod__(*args,**kwargs),module=self._module,lockey=self._lockey)

class ApplicationLocalizer(object):
    def __init__(self,filepath):
        self.module = os.path.relpath(filepath,getGenroRoot())
    def __call__(self,value):
        return GnrLocString(value,self.module)

class PackageLocalizer(ApplicationLocalizer):
    def __init__(self,filepath):
        self.module = PACKAGERELPATH.sub('\\1',filepath)

class CustomLocalizer(ApplicationLocalizer):
    def __init__(self,filepath):
        self.module = PACKAGERELPATH.sub('\\1',filepath)


class AppLocalizer(object):
    def __init__(self, application=None):
        self.application = application
        self.genroroot = getGenroRoot()
        roots = [os.path.join(self.genroroot,n) for n in ('gnrpy/gnr','gnrjs/js','resources/common','resources/mobile')]
        self.slots = [dict(roots=roots,destFolder=self.genroroot)]
        print self.application.packages.keys()
        for p in self.application.packages.values():
            self.slots.append(dict(roots=[p.packageFolder],destFolder=p.packageFolder))
        if os.path.exists(self.application.customFolder):
            self.slots.append(dict(roots=[self.application.customFolder],destFolder=self.application.customFolder))
        self.buildLocalizationDict()

    def buildLocalizationDict(self):
        self.localizationDict = dict()
        for s in self.slots:
            locbag = self.getLocalizationBag(s['destFolder'])
            if locbag:
                self.updateLocalizationDict(locbag)

    def getLocalizationBag(self,locfolder):
        destpath = os.path.join(locfolder,'localization.xml')
        if os.path.exists(destpath):
            try:
                locbag = Bag(destpath) 
            except Exception:
                locbag = Bag()
        else:
            locbag = Bag()
        return locbag

    def updateLocalizationDict(self,locbag):
        locdict = {}
        if locbag.filter(lambda n: n.attr.get('_key')):
            for n in locbag:
                loc = n.attr
                key = loc.pop('_key',None)
                if key:
                    loc.pop('_T',None)
                    loc['base'] = key
                    locdict[flatten(key)] = loc
        else:
            for m in locbag.values():
                #if not m:
                #    continue
                for n in m:
                    loc = dict(n.attr)
                    locdict[n.label] = loc
        self.localizationDict.update(locdict)    
        
    def updateLocalizationFiles(self,scan_all=None):
        for s in self.slots:
            if scan_all or s['destFolder'] != self.genroroot:
                locbag = Bag()
                for root in s['roots']:
                    d = DirectoryResolver(root,include='*.py,*.js')()
                    d.walk(self._updateModuleLocalization,locbag=locbag,_mode='deep')
                locbag.toXml(os.path.join(s['destFolder'],'localization.xml'),pretty=True,typeattrs=False, typevalue=False)

    def _updateModuleLocalization(self,n,locbag=None):
        if n.attr.get('file_ext') == 'directory':
            return
        moduleLocBag = Bag()
        def addToLocalizationBag(m):
            lockey = m.group(2)
            loctext = m.group(3)
            lockey = lockey or flatten(loctext)
            if not lockey in moduleLocBag:
                locdict = dict(self.localizationDict.get(lockey) or dict())
                locdict['base'] = loctext
                moduleLocBag.setItem(lockey,None,_attributes=locdict)
        with open(n.attr['abs_path'],'r') as f:
            filecontent = f.read() 
        LOCREGEXP_EXCL.sub(addToLocalizationBag,filecontent)
        if moduleLocBag:
            locbag[flatten(n.attr['rel_path'])] = moduleLocBag


            

