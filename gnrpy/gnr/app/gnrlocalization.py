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

LOCREGEXP = re.compile(r"""("{3}|'|")\!\!(?:{(\w*)})?(.*?)\1|\[\!\!(?:{(\w*)})?(.*?)\]|\b_T\(("{3}|'|")(.*?)\6\)""")


TRANSLATION = re.compile(r"^\!\!(?:{(\w*)})?(.*)$")

PACKAGERELPATH = re.compile(r".*/packages/(.*)")

class GnrLocString(unicode):
    def __new__(cls,value,lockey=None,_tplargs=None,_tplkwargs=None):
        s = super(GnrLocString, cls).__new__(cls,value)
        s.lockey = lockey or flatten(value)
        s.args = _tplargs
        s.kwargs = _tplkwargs
        return s

    def __mod__(self,*args,**kwargs):
        return GnrLocString(super(GnrLocString, self).__mod__(*args,**kwargs),lockey=self.lockey,_tplargs=args,_tplkwargs=kwargs)


class AppLocalizer(object):
    def __init__(self, application=None):
        self.application = application
        self.genroroot = getGenroRoot()
        try: 
            from goslate import Goslate
            self.translator = Goslate()
            self.languages = self.translator.get_languages()
        except:
            self.translator = False
            self.languages = dict(en='English',it='Italian')
        roots = [os.path.join(self.genroroot,n) for n in ('gnrpy/gnr','gnrjs','resources/common','resources/mobile')]
        self.slots = [dict(roots=roots,destFolder=self.genroroot,code='core',protected=True)]
        for p in self.application.packages.values():

            self.slots.append(dict(roots=[p.packageFolder],destFolder=p.packageFolder,code=p.id, protected = (p.project == 'gnrcore') ))
        if os.path.exists(self.application.customFolder):
            self.slots.append(dict(roots=[self.application.customFolder],destFolder=self.application.customFolder,code='customization',protected=False))
        self.buildLocalizationDict()

    def buildLocalizationDict(self):
        self.updatableLocBags = dict(all=[],unprotected=[])
        self.localizationDict = dict()
        for s in self.slots:
            if not s['protected']:
                self.updatableLocBags['unprotected'].append(s['destFolder'])
            self.updatableLocBags['all'].append(s['destFolder'])
            locbag = self.getLocalizationBag(s['destFolder'])
            if locbag:
                self.updateLocalizationDict(locbag)

    def translate(self,txt,language=None):
        language = (language or self.application.locale).split('-')[0].lower()
        if isinstance(txt,GnrLocString):
            language = 'en'
            lockey = txt.lockey
            translations = self.localizationDict.get(lockey)
            if translations:
                translation =  translations.get(language) or translations.get('en') or translations.get('base')
                if txt.args or txt.kwargs:
                    translation = translation.__mod__(*txt.args,**txt.kwargs)
            else:
                translation = txt
            return translation
        else:
            m = TRANSLATION.match(txt)
            if not m:
                return txt
            lockey = m.group(1)
            if not lockey:
                lockey = flatten(m.group(2))
            translations = self.localizationDict.get(lockey)
            if translations:
                return translations.get(language) or translations.get('en') or translations.get('base')
            else:
                return m.group(2)

    def autoTranslate(self,languages):
        languages = languages.split(',')
        for k,v in self.localizationDict.items():
            for lang in languages:
                if not v.get(lang):
                    translated = self.translator.translate(v['base'],lang)
                    v[lang] = translated

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
            def cb(n):
                if not n.value:
                    loc = dict(n.attr)
                    locdict[n.label] = loc
            locbag.walk(cb)
        self.localizationDict.update(locdict)    
        
    def updateLocalizationFiles(self,scan_all=True):
        for s in self.slots:
            if scan_all or s['destFolder'] != self.genroroot:
                locbag = Bag()
                for root in s['roots']:
                    d = DirectoryResolver(root,include='*.py,*.js')()
                    d.walk(self._updateModuleLocalization,locbag=locbag,_mode='deep',destFolder=s['destFolder'])
                locbag.toXml(os.path.join(s['destFolder'],'localization.xml'),pretty=True,typeattrs=False, typevalue=False)

    def _updateModuleLocalization(self,n,locbag=None,destFolder=None):
        if n.attr.get('file_ext') == 'directory':
            return
        moduleLocBag = Bag()
        def addToLocalizationBag(m):
            lockey = m.group(2) or m.group(4)
            loctext = m.group(3) or  m.group(5) or m.group(7)
            if not loctext:
                return
            lockey = lockey or flatten(loctext)
            if not lockey in moduleLocBag:
                locdict = dict(self.localizationDict.get(lockey) or dict())
                locdict['base'] = loctext
                moduleLocBag.setItem(lockey,None,_attributes=locdict)
        with open(n.attr['abs_path'],'r') as f:
            filecontent = f.read() 
        LOCREGEXP.sub(addToLocalizationBag,filecontent)
        if moduleLocBag:
            modulepath = os.path.relpath(n.attr['abs_path'],destFolder)
            path,ext = os.path.splitext(modulepath)
            locbag.setItem(path.replace('/','.'),moduleLocBag,path=modulepath,ext=ext.replace('.',''))


            

