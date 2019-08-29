# -*- coding: utf-8 -*-
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


#from builtins import object
import os
import re
import hashlib
from gnr.app.gnrconfig import getGenroRoot
from gnr.core.gnrstring import flatten
from gnr.core.gnrbag import Bag,DirectoryResolver

SAFEAUTOTRANSLATE = re.compile(r"""(\%(?:\((?:.*?)\))?(?:.*?)[s|d|e|E|f|g|G|o|x|X|c|i|\%])""")

LOCREGEXP = re.compile(r"""("{3}|'|")\!\!(?:\[(?P<lang_emb>.{2})\])?(?:{(?P<key_emb>\w*)})?(?P<text_emb>.*?)\1|\[\!\!(?:\[(?P<lang>.{2})\])?(?:{(?P<key>\w*)})?(?P<text>.*?)\]|\b_T\(("{3}|'|")(?P<text_func>.*?)\6\)""")


TRANSLATION = re.compile(r"^\!\!(?:\[(?P<lang>.{2})\])?(?:{(\w*)})?(?P<value>.*)$|(?:\[\!\!(?:\[(?P<lang_emb>.{2})\])?)(?:{(\w*)})?(?P<value_emb>.*?)\]")

PACKAGERELPATH = re.compile(r".*/packages/(.*)")

class GnrLocString(str):
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
        self._translator = None
        self._languages = None
        roots = [os.path.join(self.genroroot,n) for n in ('gnrpy/gnr','gnrjs','resources/common','resources/mobile')]
        self.slots = [dict(roots=roots,destFolder=self.genroroot,code='core',protected=True,language='en')]
        for p in list(self.application.packages.values()):
            self.slots.append(dict(roots=[p.packageFolder],destFolder=p.packageFolder,
                                    code=p.id, protected = (p.project == 'gnrcore'),language=p.language))
        #if os.path.exists(self.application.customFolder):
        #    self.slots.append(dict(roots=[self.application.customFolder],destFolder=self.application.customFolder,
        #                                code='customization',protected=False))
        self.buildLocalizationDict()

    @property
    def translator(self):
        if not self._translator:
            if self.application.site:
                self._translator = self.application.site.getService('translation')
            else:
                self._translator = False
        return self._translator

    @property
    def languages(self):
        if not self._languages:
            if self.translator:
                self._languages = self.translator.languages
            else:
                self._languages = dict(en='English',it='Italian',fr='French')
        return self._languages

    def buildLocalizationDict(self):
        self.updatableLocBags = dict(all=[],unprotected=[])
        self.localizationDict = dict()
        for s in self.slots:
            if not s['protected']:
                self.updatableLocBags['unprotected'].append(s['destFolder'])
            self.updatableLocBags['all'].append(s['destFolder'])
            locbag = self.getLocalizationBag(s['destFolder'])
            if locbag:
                self.updateLocalizationDict(locbag,s['language'])

    def translate(self,txt,language=None):
        return self.getTranslation(txt,language=language)['translation']

    def getTranslation(self,txt,language=None):
        language = (language or self.application.locale).split('-')[0].lower()
        result = dict(status='OK',translation=None)
        if isinstance(txt,GnrLocString):
            lockey = txt.lockey
            translation_dict = self.localizationDict.get(lockey)
            if translation_dict:
                translation =  translation_dict.get(language)
                if not translation:
                    result['status'] = 'NOLANG'
                    translation = translation_dict.get('en') or translation_dict.get('base')
                if txt.args or txt.kwargs:
                    translation = translation.__mod__(*txt.args,**txt.kwargs)
            else:
                result['status'] = 'NOKEY'
                translation = txt
            result['translation'] = translation
            return result
        else:
            def translatecb(m):
                m = m.groupdict()
                lockey = m.get('key') or m.get('key_emb')
                loctext = m.get('value') or m.get('value_emb') or ''
                loclang = m.get('lang') or m.get('lang_emb') or 'en'
                if not lockey:
                    lockey = flatten(loctext)
                lockey = '%s_%s' %(loclang,lockey)
                translation_dict = self.localizationDict.get(lockey)
                if translation_dict:
                    translation = translation_dict.get(language)
                    if not translation:
                        result['status'] = 'NOLANG'
                        translation = translation_dict.get('en') or translation_dict.get('base')
                    return translation
                else:
                    result['status'] = 'NOKEY'
                    return loctext
            result['translation'] = TRANSLATION.sub(translatecb,txt) if txt else ''
            return result

    

    def autoTranslate(self,languages):
        languages = languages.split(',')
        def cb(m):
            safekey = '[%i]' %len(safedict)
            safedict[safekey] = m.group(1)
            return safekey
        for lockey,locdict in list(self.localizationDict.items()):
            safedict = dict()
            base_to_translate = SAFEAUTOTRANSLATE.sub(cb,locdict['base'])
            baselang = lockey.split('_',1)[0]
            for lang in languages:
                if lang==baselang:
                    locdict[lang] = base_to_translate
                    continue
                if not locdict.get(lang):
                    translated = self.translator.translate(base_to_translate,'%s-%s' %(baselang,lang))
                    for k,v in list(safedict.items()):
                        translated = translated.replace(k,v)
                    locdict[lang] = translated

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

    def updateLocalizationDict(self,locbag,language=None):
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
                    locdict_key = n.label
                    if len(n.label)<3 or n.label[2]!='_':
                        locdict_key = '%s_%s' %(language,n.label)
                    locdict[locdict_key] = loc
            locbag.walk(cb)
        self.localizationDict.update(locdict)    
        
    def updateLocalizationFiles(self,scan_all=True,localizationBlock=None):
        slots = self.slots
        if localizationBlock:
            slots = [r for r in slots if r.get('code')==localizationBlock]
        for s in slots:
            if scan_all or s['destFolder'] != self.genroroot:
                locbag = Bag()
                for root in s['roots']:
                    d = DirectoryResolver(root,include='*.py,*.js')()
                    d.walk(self._updateModuleLocalization,locbag=locbag,_mode='deep',destFolder=s['destFolder'] )
                locbag.toXml(os.path.join(s['destFolder'],'localization.xml'),pretty=True,typeattrs=False, typevalue=False)
        self.buildLocalizationDict()

    def _updateModuleLocalization(self,n,locbag=None,destFolder=None):
        if n.attr.get('file_ext') == 'directory':
            return
        moduleLocBag = Bag()
        def addToLocalizationBag(m):
            lockey = m.group('key_emb') or m.group('key')
            loctext = m.group('text_emb') or  m.group('text') or m.group('text_func')
            loclang = m.group('lang_emb') or m.group('lang') or 'en'
            if not loctext:
                return
            lockey = lockey or flatten(loctext)
            lockey = '%s_%s' %(loclang,lockey)
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


            

