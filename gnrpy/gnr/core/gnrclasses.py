# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy core - see LICENSE for details
# module gnrclasses : class catalog.
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Francesco Cavazzana
#                 Saverio Porcari, Francesco Porcari
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

import datetime
import re

from gnr.core import gnrstring
    
class GnrClassCatalog(object):
    __standard = None
    
    def convert(cls):
        if cls.__standard == None:
            cls.__standard = GnrClassCatalog()
        return cls.__standard
    convert = classmethod(convert)
    
    def __init__(self):
        self.names = {}
        self.classes = {}
        self.aliases = {}
        self.parsers = {}
        self.serializers = {'asText':{},'asRepr':{}}
        self.align={}
        self.empty = {}
        self.standardClasses()
        
    def addClass(self, cls, key, aliases=None, altcls=None, align='L', empty=None):
        """Add a python class to the list of objects known by the Catalog.
        cls: the class itself by reference
        key: a string, is a short name of the class, as found in textual values to parse or write
        altcls: other classes to write in the same way. All values will be parsed with the main class.
        aliases: other keys to parse using this class
        empty: the class or value to be used for empty parsed values, defualt None, example '' for strings"""
        self.classes[key] = cls
        self.align[key] = align
        self.empty[key] = empty
        if aliases:
            for n in aliases:
                self.classes[n] = cls
                
        self.names[cls] = key
        if altcls:
            for c in altcls:
                self.names[c] = key
        self.aliases[key] = aliases
    
    def getEmpty(self, key):
        if isinstance(key,basestring):
            key=self.classes.get(key.upper())
        if key in self.names:
            v = self.empty.get(self.names[key])
        elif key.__class__ in self.names:
            v = self.empty.get(self.names[key.__class__])
        if type(v)==type:
            v = v()
        return v
        
    def getAlign(self,key):
        if isinstance(key,basestring):
            key=self.classes.get(key.upper())
        if key in self.names:
            return self.align.get(self.names[key])
        elif key.__class__ in self.names:
            return self.align.get(self.names[key.__class__])

    
    def addSerializer(self, mode, cls, funct):
        """Given a mode and a class to convert, specifies the function to use for the actual conversion:
        funct: is a function by reference or lambda, 
               will receive an instance and return an appropriate value for the conversion mode"""
        m = self.serializers.get(mode,{})
        m[cls] = funct
        self.serializers[mode] = m

    def addParser(self, cls, funct):
        """Given a class to convert, specifies the function to use for the actual conversion from text:
        funct: is a function by reference or lambda, 
               will receive a text and return an instance"""
        self.parsers[cls] = funct
        clsname = self.names[cls]
        self.parsers[clsname] = funct
        for a in self.aliases[clsname]:
            self.parsers[a] = funct

    def getClassKey(self, o):
        return self.names[type(o)]
    
    def getClass(self, name):
        return self.classes[name]
        
    def asText(self, o, quoted=False, translate_cb=None):
        if isinstance(o, basestring):
            result = o
            if translate_cb and result.startswith('!!'): # a translation is needed, if no locale leave all as is including "!!"
                result = translate_cb(result[2:])
        else:
            f = self.serializers['asText'].get(type(o))
            if not f:
                result = str(o)
            else:
                result = f(o)
        if quoted:
            result = self.quoted(result)
        return result
    
    def quoted(self,s):
        if '"' in s:
            s="'%s'" % s
        else:
            s='"%s"' % s
        return s
    
    def fromText(self, txt, clsname):
        if not clsname:
            return txt
        if not txt:
            return self.getEmpty(clsname)
        if clsname == 'JS':
            try:
                return self.fromJson(txt)
            except:
                return txt
        f = self.parsers.get(clsname, None)
        if f:
            return f(txt)
        else:
            return self.classes[clsname](txt)
        
    def fromTypedText(self, txt):
        result = re.split('::(\w*)$', txt)
        if len(result) == 1:
            return txt
        else:
            return self.fromText(result[0], result[1])
    
    def asTypedText(self, o, quoted=False, translate_cb=None):
        t=self.names.get(type(o),'T')
        if t=='T': 
            result= self.asText(o, translate_cb=translate_cb)
        else:
            result= "%s::%s" % (self.asText(o, translate_cb=translate_cb), self.names[type(o)])
        if quoted:
            result=self.quoted(result)
        return result
    
    def asTextAndType(self, o, translate_cb=None):
        c = self.names.get(type(o))
        if c:
            return (self.asText(o, translate_cb=translate_cb), c)
        return self.asTextAndType(repr(o))

    def getType(self, o):
        return self.names.get(type(o))

    def standardClasses(self):
        from gnr.core.gnrbag import Bag
        self.addClass(cls=unicode, key='T', aliases=['TEXT','P','A'], altcls=[basestring,str], empty='')
        #self.addSerializer("asText", unicode, lambda txt: txt)
        
        
        self.addClass(cls=float, key='R', aliases=['REAL','FLOAT','F'], align='R', empty=0.0)
        self.addParser(float, self.parse_float)        
        
        self.addClass(cls=int, key='L', aliases=['LONG','LONGINT','I','INT','INTEGER'], altcls=[long], align='R', empty=0)
        
        self.addClass(cls=bool, key='B', aliases=['BOOL','BOOLEAN'], empty=False)

        self.addParser(bool,lambda txt: (txt.upper() in ['Y','TRUE','YES','1']))
        
        self.addClass(cls=datetime.date, key='D', aliases=['DATE'], empty=None)
        self.addParser(datetime.date, self.parse_date)
        
        self.addClass(cls=datetime.datetime, key='DH', aliases=['DATETIME','DT'], empty=None)
        self.addParser(datetime.datetime, lambda txt: datetime.datetime(*[int(el) for el in gnrstring.wordSplit(txt)]))

        self.addClass(cls=datetime.time, key='H', aliases=['TIME'], empty=None)
        self.addParser(datetime.time, self.parse_time)
        
        self.addClass(cls=Bag, key='BAG', aliases=['BAG', 'GNRBAG', 'bag', 'gnrbag'], empty=Bag)
        self.addParser(Bag,lambda txt: Bag(txt))
        
        self.addClass(cls=type(None), key='NN', aliases=['NONE', 'NULL'], empty=None)
        self.addParser(type(None), lambda txt: None)
        self.addSerializer("asText",type(None), lambda txt: '')
        
        self.addClass(cls=list, altcls=[dict, tuple], key='JS', empty=None)
        self.addSerializer("asText",list, self.toJson)
        self.addSerializer("asText",tuple, self.toJson)
        self.addSerializer("asText",dict, self.toJson)
        
        
    def parse_float(self, txt):
        if txt.lower()!='inf':
            return float(txt)

    def parse_date(self, txt):
        if txt and txt!='0000-00-00':
            return datetime.date(*[int(el) for el in gnrstring.wordSplit(txt)[0:3]])
        
    def parse_time(self, txt):
        if txt and txt!='00:00:00':
            return datetime.time(*[int(el) for el in gnrstring.wordSplit(txt)])
        
    def toJson(self, data):
        return gnrstring.toJson(data)

    def fromJson(self, data):
        return gnrstring.fromJson(data)
   

#def getItaCatalog():
    #c = GnrClassCatalog()
    #c.addSerializer("asText", datetime.date, lambda d: d.strftime('%d/%m/%Y'))
    #c.addSerializer("asText", float, lambda nr: re.sub(r"([-+]?\d{1,3}(\,\d*)?)(?=(\d{3})*(\,|$))",r".\1", ('%.2f' % nr).replace('.',','))[1:])
    #c.addSerializer("asText", int, lambda nr: re.sub(r"([-+]?\d{1,3}(\,\d*)?)(?=(\d{3})*(\,|$))",r".\1", '%i' % nr)[1:])
    #c.addParser(float, lambda txt: c.parse_float(txt.replace('.','').replace(',','.')))        
    #return c

if __name__=='__main__':
    c = GnrClassCatalog()
    d = datetime.date(2007, 10, 21)
    
    for l in ('it', 'en', 'fr', 'de', 'es'):
        for f in ('SHORT', 'MEDIUM', 'LONG', 'FULL'):
            print c.asText(d, locale=l, format=f)
    
        print c.asText(2300.456)
        print c.asText(2300.456, locale=l).encode('utf-8')
        print c.asText(2300.456,  locale=l, format='.2').encode('utf-8')
        print c.asText(2300.456,  locale=l, format='curr').encode('utf-8')
        print c.asText(2300.456,  locale=l, format='curr.3').encode('utf-8')
        print c.asText(0.45636,  locale=l, format='%').encode('utf-8')
        print c.asText(0.45636,  locale=l, format='%.2').encode('utf-8')

    s = GnrClassCatalog.convert().fromTypedText('::B')
    

    from gnr.core.gnrbag import Bag
    b = Bag('/Shared Items/ApplicazioniClienti/instances/sw/sync4d/data/2006-12-12/2006-12-12_125817_146241953_UT_Anagrafiche_1.xml')
    
    
    s=GnrClassCatalog.convert().fromTypedText('123::L')
    print s
    import datetime
    converter = GnrClassDict()
    
    print converter.asText(24)
    #>>> '24'
    print converter.asTypedTuple(24)
    #>>> ('24','I')
    print converter.asTypedText(24)
    #>>> '24::I'
    print converter.asTypedText(3.7)
    print repr(converter.asTypedText(u'��'))
    print converter.asTypedText(datetime.date.today())
    print converter.asTypedText(datetime.time(11,23,54))
    print converter.asTypedText(datetime.datetime.now())
    print converter.asTypedText(True)
    print converter.asTypedText(False)

    
    print converter.fromText('24','I')
    print converter.fromTypedText('2004-12-2::D')
    print converter.fromTypedText('2006-07-03 14:09:00.662801::DH')
    
    
    