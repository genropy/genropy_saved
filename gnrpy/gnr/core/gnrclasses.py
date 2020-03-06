# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy core - see LICENSE for details
# module gnrclasses : class catalog.
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

from __future__ import division
from __future__ import print_function

from builtins import str
from past.builtins import basestring, str as old_str
#from builtins import object
from past.utils import old_div
import datetime
import re
import six
from gnr.core import gnrstring
from gnr.core.gnrdate import decodeOneDate, decodeDatePeriod
from gnr.core.gnrlang import gnrImport, serializedFuncName
from decimal import Decimal
from dateutil.parser import parse as dateutil_parse
from dateutil.tz import tzlocal
from gnr.core.gnrlang import GnrException
import types

ISO_MATCH = re.compile(r'\d{4}\W\d{1,2}\W\d{1,2}')

class GnrMixinError(Exception):
    pass


class GnrMixinNotFound(Exception):
    pass

class GnrCastingError(GnrException):
    pass


class GnrClassCatalog(object):
    """TODO"""
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
        self.serializers = {'asText': {}, 'asRepr': {}}
        self.align = {}
        self.empty = {}
        self.typegetters = {}
        self.standardClasses()
        
    def addClass(self, cls, key, aliases=None, altcls=None, align='L', empty=None, typegetter=None):
        """Add a python class to the list of objects known by the Catalog.
            
        :param cls: the class itself by reference
        :param key: a string, is a short name of the class, as found in textual values to parse or write
        :param aliases: other keys to parse using this class. 
        :param altcls: other classes to write in the same way. All values will be parsed with the main class.
                       
        :param align: TODO. Default value is ``L``
        :param empty: the class or value to be used for empty parsed values (example ``''`` for strings).
                      
        """
        self.classes[key] = cls
        self.align[key] = align
        self.empty[key] = empty
        if typegetter:
            self.typegetters[cls]=typegetter
        if aliases:
            for n in aliases:
                self.classes[n] = cls
                
        self.names[cls] = key
        if altcls:
            for c in altcls:
                self.names[c] = key
        self.aliases[key] = aliases
        
    def getEmpty(self, key):
        """Add???
            
        :param key: TODO
        :returns: TODO
        """
        if isinstance(key, basestring):
            key = self.classes.get(key.upper())
        if key in self.names:
            v = self.empty.get(self.names[key])
        elif key.__class__ in self.names:
            v = self.empty.get(self.names[key.__class__])
        if type(v) == type:
            v = v()
        return v
        
    def getAlign(self, key):
        """Add???
            
        :param key: TODO
        :returns: TODO
        """
        if isinstance(key, basestring):
            key = self.classes.get(key.upper())
        if key in self.names:
            return self.align.get(self.names[key])
        elif key.__class__ in self.names:
            return self.align.get(self.names[key.__class__])
            
    def addSerializer(self, mode, cls, funct):
        """Given a mode and a class to convert, specifies the function to use for the actual conversion:
        
        :param mode: TODO
        :param cls: the class to be converted
        :param funct: is a function by reference or lambda, will receive an instance and return an appropriate value for the conversion mode
        """
        m = self.serializers.get(mode, {})
        m[cls] = funct
        self.serializers[mode] = m
        
    def addParser(self, cls, funct):
        """Given a class to convert, specifies the function to use for the actual conversion from text:
        
        :param cls: the class to be converted
        :param funct: is a function by reference or lambda, will receive a text and return an instance
        """
        self.parsers[cls] = funct
        clsname = self.names[cls]
        self.parsers[clsname] = funct
        for a in self.aliases[clsname]:
            self.parsers[a] = funct

    def getClassKey(self, o):
        """Add???
            
        :param o: TODO
        :returns: TODO
        """
        return self.names[type(o)]

    def getClass(self, name):
        """Add???
            
        :param name: TODO
        :returns: TODO
        """
        return self.classes[name]
    
    def asText(self, o, quoted=False, translate_cb=None,jsmode=False):
        """Add???
            
        :param o: TODO
        :param quoted: TODO. Default value is ``False``
        :param translate_cb: TODO. 
        :returns: TODO
        """
        if isinstance(o, basestring):
            result = o
            if translate_cb: # a translation is needed, if no locale leave all as is including "!!"
                result = translate_cb(result)
        else:
            objtype=type(o)
            if jsmode and objtype in(list,dict,tuple):
                f= self.toJsonJS
            else:
                f = self.serializers['asText'].get(objtype)
            if not f:
                result = str(o)
            else:
                result = f(o)
        if quoted:
            result = self.quoted(result)
        return result

    def quoted(self, s):
        """Add???
            
        :param s: TODO
        :returns: TODO
        """
        if '"' in s:
            s = "'%s'" % s
        else:
            s = '"%s"' % s
        return s

    def fromText(self, txt, clsname, **kwargs):
        """Add???
            
        :param txt: TODO
        :param clsname: TODO
        :returns: TODO
        """
        if not clsname:
            return txt
        if not txt:
            return self.getEmpty(clsname)
    
        if not isinstance(txt,basestring):
            if self.getType(txt)==clsname:
                return txt
            else:
                return self.fromText(str(txt),clsname,**kwargs)
            
        if clsname == 'JS':
            try:
                return self.fromJson(txt)
            except Exception as e:
                print('error decoding json ',e)
                return txt
        
        f = self.parsers.get(clsname, None)
        if f:
            return f(txt, **kwargs)
        else:
            return self.classes[clsname](txt)



    def isTypedText(self,txt,**kwargs):
        if not '::' in txt:
            return False
        return txt.split('::')[-1].upper() in ['HTML','JS','RPC','JSON','NN','BAG','A','T','L','N','I','B','D','H','HZ','DH','DHZ','P','X']

            
    def fromTypedText(self, txt, **kwargs):
        """Add???
            
        :param txt: TODO
        :returns: TODO
        """
        result = re.split('::(\w*)$', txt)
        if len(result) == 1:
            return txt
        elif result[1] == 'D':
            return self.fromText(result[0], result[1], **kwargs)
        else:
            return self.fromText(result[0], result[1])
            
    def asTypedText(self, o, quoted=False, translate_cb=None,jsmode=False):
        """Add???
            
        :param o: TODO
        :param quoted: TODO. Default value is ``False``
        :param translate_cb: TODO. 
        :returns: TODO
        """
        t = self.getType(o, fallback='T')
        if t == 'T':
            result = self.asText(o, translate_cb=translate_cb,jsmode=jsmode)
        else:
            result = "%s::%s" % (self.asText(o, translate_cb=translate_cb,jsmode=jsmode), self.names[type(o)])
        if quoted:
            result = self.quoted(result)
        return result
        
    def asTextAndType(self, o, translate_cb=None): 
        """Add???
            
        :param o: TODO
        :param translate_cb: TODO. 
        :returns: TODO
        """
        c = self.getType(o)
        if c:
            return (self.asText(o, translate_cb=translate_cb), c)
        return self.asTextAndType(repr(o))
        
    def getType(self, o, fallback=None):
        """Add???
            
        :param o: TODO
        :returns: TODO
        """
        obj_type = type(o)
        typegetter = self.typegetters.get(obj_type)
        if typegetter:
            return typegetter(o)
        return self.names.get(obj_type, fallback)
    

    def standardClasses(self):
        """TODO
        """
        from gnr.core.gnrbag import Bag
        
        self.addClass(cls=str, key='T', aliases=['TEXT', 'P', 'A','text'], altcls=[basestring, old_str, six.text_type], empty='')
        #self.addSerializer("asText", unicode, lambda txt: txt)
        
        self.addClass(cls=float, key='R', aliases=['REAL', 'FLOAT', 'F'], align='R', empty=0.0)
        self.addParser(float, self.parse_float)
        
        self.addClass(cls=int, key='L', aliases=['LONG', 'LONGINT', 'I', 'INT', 'INTEGER'], altcls=[int], align='R',
                      empty=0)
                      
        self.addClass(cls=bool, key='B', aliases=['BOOL', 'BOOLEAN'], empty=False)
        self.addParser(bool, lambda txt: (txt.upper() in ['Y', 'TRUE', 'YES', '1']))
        
        self.addClass(cls=datetime.date, key='D', aliases=['DATE'], empty=None)
        self.addParser(datetime.date, self.parse_date)
        
        self.addClass(cls=datetime.datetime, key='DH', aliases=['DATETIME', 'DT','DHZ'], empty=None, typegetter=self.typegetter_datetime)
        self.addParser(datetime.datetime, self.parse_datetime)
        self.addSerializer("asText", datetime.datetime, self.serialize_datetime)

       
        self.addClass(cls=datetime.timedelta, key='TD', aliases=['TIMEDELTA', 'TD'], empty=None)
        self.addParser(datetime.timedelta, self.parse_timedelta)
        self.addSerializer("asText", datetime.timedelta, self.serialize_timedelta)



  
        self.addClass(cls=datetime.time, key='H', aliases=['TIME','HZ'], empty=None)
        self.addParser(datetime.time, self.parse_time)


        self.addClass(cls=Bag, key='BAG', aliases=['BAG', 'GNRBAG', 'bag', 'gnrbag'], empty=Bag)
        self.addParser(Bag, lambda txt: Bag(txt))
        self.addSerializer("asText", Bag, lambda b: b.toXml(catalog=self))

        self.addClass(cls=type(None), key='NN', aliases=['NONE', 'NULL'], empty=None)
        self.addParser(type(None), lambda txt: None)
        self.addSerializer("asText", type(None), lambda txt: '')
        
        self.addClass(cls=Decimal, key='N', aliases=['NUMERIC', 'DECIMAL'], align='R', empty=Decimal('0'))
        self.addParser(Decimal, lambda txt: Decimal(txt))
        #self.addSerializer("asText",type(None), lambda txt: '')
        #self.addClass(cls=type(None), key='NN', aliases=['NONE', 'NULL'], empty=None)
        #self.addParser(type(None), lambda txt: None)
        #self.addSerializer("asText",type(None), lambda txt: '')
        
        self.addClass(cls=list, altcls=[dict, tuple], key='JS', empty=None)
        self.addSerializer("asText", list, self.toJson)
        self.addSerializer("asText", tuple, self.toJson)
        self.addSerializer("asText", dict, self.toJson)
        self.addClass(cls=type(self.__init__), key='RPC', altcls=[type(lambda s:s)], empty=None)
        self.addSerializer("asText", type(self.__init__), serializedFuncName)
        #self.addSerializer("asText", type(lambda s:s), self.funcName)
        
        self.addClass(cls=type, key='CLS', aliases=[],empty=None)
        self.addSerializer("asText", type, self.serializeClass)
        self.addParser(type, self.parseClass)
        

    def parseClass(self,txt):
        module,clsname = txt.split(':')
        m = gnrImport(module)
        c = getattr(m,clsname)
        if hasattr(c,'__safe__'):
            return c
        else:
            raise Exception('Unsecure class %s' %txt)

    def serializeClass(self,cls):
        return '%s:%s' %(cls.__module__,cls.__name__)


        
    def parse_float(self, txt):
        """Add???
            
        :param txt: TODO
        :returns: TODO
        """
        if txt.lower() != 'inf':
            return float(txt)
    
    def typegetter_datetime(self, ts):
        if ts.tzinfo:
            return 'DHZ'
        return 'DH'

    def parse_datetime(self, txt, workdate=None):
        """Add???
            
        :param txt: TODO
        :param workdate: the :ref:`workdate`"""
        return dateutil_parse(txt)

    def serialize_datetime(self,ts):
        if not ts.tzinfo:
            ts = ts.replace(tzinfo=tzlocal())
        return ts.isoformat()
        
    def parse_timedelta(self, txt, workdate=None):
        """Add???
            
        :param txt: TODO
        :param workdate: the :ref:`workdate`"""
        raise Exception

        
    def serialize_timedelta(self,td):
        microseconds = td.total_seconds() - td.seconds

        t = td.seconds
        seconds = t%60
        seconds += microseconds
        t = old_div(t,60)
        minutes = t%60
        t = old_div(t,60)
        hours = t%24
        days = old_div(t,24)
        result = "%02i:%02i:%02s" %(hours,minutes,('%.3f' %seconds).zfill(6)) 
        if days:
            "%s days %s" %(days,result)
        return result

    def parse_date(self, txt, workdate=None):
        """Add???
            
        :param txt: TODO
        :param workdate: the :ref:`workdate`"""
        if txt != '0000-00-00':
            if txt and ISO_MATCH.match(txt):
                year, month, day = gnrstring.wordSplit(txt)[0:3]
                return datetime.date(int(year), int(month), int(day[:2]))
                
            else:
                return decodeDatePeriod(txt, workdate=workdate, returnDate=True)
                
    def parse_time(self, txt):
        """Add???
            
        :param txt: TODO
        :returns: TODO
        """
        if txt:
            return datetime.time(*[int(el) for el in gnrstring.wordSplit(txt)])
            
    def toJson(self, data):
        """Add???
            
        :param data: TODO
        :returns: TODO
        """
        return gnrstring.toJson(data)
        
    def toJsonJS(self, data):
        """Add???
            
        :param data: TODO
        :returns: TODO
        """
        return gnrstring.toJsonJS(data)
        
    def fromJson(self, data):
        """Add???
            
        :param data: TODO
        :returns: TODO
        """
        return gnrstring.fromJson(data)
        
    #def getItaCatalog():
    #c = GnrClassCatalog()
    #c.addSerializer("asText", datetime.date, lambda d: d.strftime('%d/%m/%Y'))
    #c.addSerializer("asText", float, lambda nr: re.sub(r"([-+]?\d{1,3}(\,\d*)?)(?=(\d{3})*(\,|$))",r".\1", ('%.2f' % nr).replace('.',','))[1:])
    #c.addSerializer("asText", int, lambda nr: re.sub(r"([-+]?\d{1,3}(\,\d*)?)(?=(\d{3})*(\,|$))",r".\1", '%i' % nr)[1:])
    #c.addParser(float, lambda txt: c.parse_float(txt.replace('.','').replace(',','.')))
    #return c
        
if __name__ == '__main__':
    pass
    # NISO: The following lines don't work properly (asText() doesn't accept the "locale" attribute),
    #       so I put "pass" on the if __name__ == '__main__':
    #       PLEASE cancel the following lines if they are useless...
    
    #c = GnrClassCatalog()
    #d = datetime.date(2007, 10, 21)
    #    
    #for l in ('it', 'en', 'fr', 'de', 'es'):
    #    for f in ('SHORT', 'MEDIUM', 'LONG', 'FULL'):
    #        print c.asText(d, locale=l, format=f)
    #        
    #    print c.asText(2300.456)
    #    print c.asText(2300.456, locale=l).encode('utf-8')
    #    print c.asText(2300.456, locale=l, format='.2').encode('utf-8')
    #    print c.asText(2300.456, locale=l, format='curr').encode('utf-8')
    #    print c.asText(2300.456, locale=l, format='curr.3').encode('utf-8')
    #    print c.asText(0.45636, locale=l, format='%').encode('utf-8')
    #    print c.asText(0.45636, locale=l, format='%.2').encode('utf-8')
    #    
    #s = GnrClassCatalog.convert().fromTypedText('::B')
    #    
    #from gnr.core.gnrbag import Bag
    #    
    #b = Bag(
    #        '/Shared Items/ApplicazioniClienti/instances/sw/sync4d/data/2006-12-12/2006-12-12_125817_146241953_UT_Anagrafiche_1.xml')
    #        
    #s = GnrClassCatalog.convert().fromTypedText('123::L')
    #print s
    #import datetime
    #    
    #converter = GnrClassDict()
    #    
    #print converter.asText(24)
    ##>>> '24'
    #print converter.asTypedTuple(24)
    ##>>> ('24','I')
    #print converter.asTypedText(24)
    ##>>> '24::I'
    #print converter.asTypedText(3.7)
    #print repr(converter.asTypedText(u'��'))
    #print converter.asTypedText(datetime.date.today())
    #print converter.asTypedText(datetime.time(11, 23, 54))
    #print converter.asTypedText(datetime.datetime.now())
    #print converter.asTypedText(True)
    #print converter.asTypedText(False)
    #    
    #print converter.fromText('24', 'I')
    #print converter.fromTypedText('2004-12-2::D')
    #print converter.fromTypedText('2006-07-03 14:09:00.662801::DH')