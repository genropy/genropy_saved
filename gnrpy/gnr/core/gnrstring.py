# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy core - see LICENSE for details
# module gnrstring : gnr string implementation
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

import re
import cPickle
import zipfile
import StringIO
import logging
import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)
CONDITIONAL_PATTERN = re.compile("\\${([^}]*)}",flags=re.S)
try:
    from string import Template
    
    class BagTemplate(Template):
        idpattern = '[_a-z\@][_a-z0-9\.\@^]*'
        
    class NoneIsBlankMapWrapper(object):
        
        def __init__(self,data):
            self.data=data
                
        def __getitem__(self,k):
            value= self.data[k] 
            if value is None:
                value= ''
            return value
    
    class LocalizedWrapper(object):

        def __init__(self,data, locale=None,templates=None, formats=None,masks=None,editcols=None,df_templates=None,dtypes=None,
                         localizer=None,urlformatter=None,noneIsBlank=None,emptyMode=None):
            self.data=data
            self.locale=locale
            self.formats=formats or dict()
            self.masks = masks or dict()
            self.editcols = editcols or dict()
            self.df_templates = df_templates or dict()
            self.templates=templates
            self.noneIsBlank=noneIsBlank
            self.isBag = hasattr(self.data, '_htraverse')
            self.localizer = localizer
            self.urlformatter = urlformatter
            self.dtypes = dtypes or dict()
            self.emptyMode=emptyMode

        def __getitem__(self,k):
            as_name = k.replace('@','_').replace('.','_')
            if '^' in k:
                k = k.split('^')
                as_name = k[1]
                k = k[0]
            value = self.data[k]
            if not value:
                value = self.data[as_name]
            format = None
            mask = None
            formattedValue = None
            caption = ''
            if self.noneIsBlank and value is None:
                value= ''
            if self.isBag:
                if hasattr(value, '_htraverse'):
                    templatename = k.replace('.','_')
                    if self.templates and templatename in self.templates:
                        templateNode = self.templates.getNode(templatename)
                        if templateNode:
                            template = templateNode.value
                            joiner = templateNode.getAttr('joiner','')
                            result = []
                            for v in value.values():
                                result.append(templateReplace(template,v, locale=self.locale, 
                                                formats=self.formats,masks=self.masks,editcols=self.editcols,dtypes=self.dtypes, noneIsBlank=self.noneIsBlank))
                            return joiner.join(result)
                    elif as_name in self.df_templates:
                        templatepath = self.df_templates[as_name]
                        template = self.data[templatepath]
                        result = templateReplace(template,value,locale=self.locale, 
                                                formats=self.formats,masks=self.masks, 
                                                editcols=self.editcols,dtypes=self.dtypes,
                                                noneIsBlank=self.noneIsBlank)
                        empty=templateReplace(template,value,locale=self.locale, 
                                                formats=self.formats,editcols=self.editcols,
                                                masks=self.masks, dtypes=self.dtypes,
                                                noneIsBlank=self.noneIsBlank,emptyMode=True)
                        return result if result!=empty else ''
                    else:
                        return value.getFormattedValue(joiner='<br/>');
                else:
                    valueNode = self.data.getNode(k)
                    if valueNode:
                        value = valueNode.attr.get('_displayedValue') or value
                        formattedValue = valueNode.attr.get('_formattedValue')
                attrs = self.data.getAttr(k) or dict()
                format = attrs.get('format')
                mask = attrs.get('mask')
                caption = attrs.get('name_long','')
            format = self.formats.get(as_name) or format
            mask = self.masks.get(as_name) or mask
            dtype = self.dtypes.get(as_name)
            if dtype =='P' and self.urlformatter:
                value = self.urlformatter(value)
            if (isinstance(value,basestring) or isinstance(value,unicode)) and dtype:
                value = '%s::%s' %(value,dtype)
            if mask and '#' in mask:
                caption = self.localizer.localize(caption) if self.localizer else caption.replace('!!','')
                mask = mask.replace('#',caption)
            elif not format and formattedValue:
                value = formattedValue
            value = toText(value,locale=self.locale, format=format,mask=mask)
            return value if not self.emptyMode else ''
            

    
    class SubtemplateMapWrapper(object):
        
        def __init__(self,data,templates=None, locale=None):
            self.data=data
            self.templates=templates
            self.locale=locale
                
        def __getitem__(self,k):
            value= self.data[k] 
            if value is None:
                value= ''
            if hasattr(value, '_htraverse'):
                templateNode = self.templates.getNode(k)
                if templateNode:
                    template = templateNode.value
                    joiner = templateNode.getAttr('joiner','')
                    result = []
                    for k,v in value.items():
                        result.append(templateReplace(template,v, locale=self.locale))
                    value = joiner.join(result)
            return value
            
            
except:
    pass

try:
    try:
        import json
    except:
        import simplejson as json
    class JsonEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime.date):
                return obj.strftime('%m/%d/%Y')
            if isinstance(obj, Decimal):
                return str(obj)
            try:
                result = json.JSONEncoder.default(self, obj)
            except Exception:
                result = '*not JSON serializable*'
            return result

            
    class JsonEncoderJS(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime.time):
                return '%s::H' %str(obj)
                
            elif isinstance(obj, Decimal):
                    return str(obj)
            elif isinstance(obj, datetime.datetime):
                return '%s::DH' %str(obj)
            elif isinstance(obj, datetime.date):
                return '%s::D' %str(obj)
            return json.JSONEncoder.default(self, obj)
except:
    pass

from gnr.core.gnrlocale import localize, parselocal

REGEX_WRDSPLIT = re.compile(r'\W+')
BASE_ENCODE = {'/2': '01',
               '/8': '012345678',
               '/16': '0123456789ABCDEF',
               '/36': '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
}

def getUntil(myString, chunk, returnOriginal=False):
    """Search in a string a chunk: if it is present, return all the characters before this chunk.
    If not, return an empty string (or the original one, if returnOriginal is ``True``).
    
    :param myString: the string to be checked
    :param chunk: substring that bounds the result string
    :param returnOriginal: if ``True``, return the entire string if the chunk is not present in the string.
                           Default value is ``False``.
    :returns: a string until a given chunk
    
    >>> getUntil('teststring', 'st')
    'te'
    >>> getUntil('teststring', 'te')
    ''
    >>> getUntil('teststring', 'co')
    ''
    >>> getUntil('teststring', 'co', returnOriginal=True)
    'teststring'
    """
    p = myString.find(chunk)
    if p > -1:
        return myString[0:p]
    else:
        if returnOriginal:
            return myString
        else:
            return ''
            
def getUntilLast(myString, chunk):
    """Return a string until last occurence of a given chunk
    
    :param myString: the string to be checked
    :param chunk: substring that bounds the result string
    :returns: a string until last occurence of a given chunk
    
    >>> getUntilLast('teststring', 'st')
    'test'
    >>> getUntilLast('teststring', 'te')
    ''
    >>> getUntilLast('teststring', 'co')
    ''
    """
    p = myString.rfind(chunk)
    if p > -1:
        return myString[0:p]
    else:
        return ''
        
def getFrom(myString, chunk):
    """Return a string after a given chunk
    
    :param myString: the string to be checked
    :param chunk: substring that bounds the result string
    :returns: a string after a given chunk
    
    >>> getFrom('teststring', 'st')
    'string'
    >>> getFrom('teststring', 'te')
    'ststring'
    >>> getFrom('teststring', 'co')
    ''
    """
    p = myString.find(chunk)
    if p > -1:
        return myString[p + len(chunk):]
    else:
        return ''
        
def getFromLast(myString, chunk):
    """Return a string after the last occurence of a given chunk.
    
    :param myString: the string to be checked
    :param chunk: substring that bounds the result string
    :returns: a string after the last occurence of a given chunk
    
    >>> getFromLast('teststring', 'st')
    'ring'
    >>> getFromLast('teststring', 'ng')
    ''
    >>> getFromLast('teststring', 'co')
    ''
    """
    p = myString.rfind(chunk)
    if p > -1:
        return myString[p + len(chunk):]
    else:
        return ''
            
def wordSplit(text):
    """Return a list that contains the words of the given ``text``
        
    :param text: text to be splitted
    :returns: a list that contains the words of the given text
    
    >>> wordSplit('hello, my dear friend')
    ['hello', 'my', 'dear', 'friend']
    """
    return REGEX_WRDSPLIT.split(text)
    
def splitLast(myString, chunk):
    """Return a tuple of two strings created by splitting the string at the last
    occurence of a given chunk. If the chunk is not included in the string, return
    a tuple of two strings, with ``myString`` as the first one and with an
    empty string as the second one.
    
    :param myString: string to be splitted
    :param chunk: substring that bounds the result string
    :returns: a tuple of two strings
    
    >>> splitLast('hello my dear friend', 'e')
    ('hello my dear fri', 'nd')
    
    >>> splitLast(a, 'w')
    ('Hello my dear friend', '')
    """
    p = myString.rfind(chunk)
    if p > -1:
        return myString[0:p], myString[p + len(chunk):]
    else:
        return myString, ''
        
def getBetween(myString, startChunk, endChunk):
    """Return a string between two given chunks.
    
    :param myString: the string to be checked
    :param startChunk: substring that bounds the result string from left
    :param endChunk: substring that bounds the result string from right
    
    :returns: a string between two given chunks
    
    >>> getBetween('teststring', 'st','in')
    'str'
    >>> getBetween('teststring', 'st','te')
    ''
    >>> getBetween('teststring', 'te','te')
    ''
    """
    p1 = myString.find(startChunk)
    if p1 < 0:
        return ''
    else:
        p2 = myString.find(endChunk, p1 + len(startChunk))
        if p2 < 0:
            return ''
        else:
            return myString[p1 + len(startChunk):p2]
            
def like(s1, s2, wildcard='%'):
    """Return ``True`` if ... Return ``False`` if ... TODO
    
    :param s1: first string
    :param s2: second string
    :wildcard: a special string. Default value is ``%``
    :returns: TODO
    
    >>> like('*dog*', 'adogert', '*')
    True
    >>> like('dog*', 'adogert', '*')
    False
    >>> like('*dog', '*adogert', '*')
    False
    """
    if s1.startswith('^'):
        s1 = s1[1:].upper()
        s2 = s2.upper()
    if s1 == wildcard or s1 == s2: return True
    elif not wildcard in s1: return False
    if s1.startswith(wildcard):
        if s1.endswith(wildcard): return bool(s1[1:-1] in s2)
        return bool(s2.endswith(s1[1:]))
    if s1.endswith(wildcard): return bool(s2.startswith(s1[:-1]))
    return False
    
def ilike(s1, s2, wildcard='%'):
    """Return ``True`` if ... Return ``False`` if ... TODO
    
    :param s1: first string
    :param s2: second string
    :wildcard: a special string. Default value is ``%``
    :returns: TODO
    """
    return like(s1.upper(), s2.upper(), wildcard)
    
def filter(item, include=None, exclude=None, wildcard='%'):
    """TODO
    
    :param item: TODO
    :param include: TODO. 
    :param exclude: TODO. 
    :param wildcard: TODO. Default value is ``%``
    :returns: TODO
    """
    if include and isinstance(include, basestring):
        include = include.split(',')
    if exclude and isinstance(exclude, basestring):
        exclude = exclude.split(',')
    if exclude:
        for excl in exclude:
            if like(excl, item, wildcard):
                return False
    if include:
        for incl in include:
            if like(incl, item, wildcard):
                return True
        return False
    return True
    
def regexDelete(myString, pattern):
    """Return a string obtained deleting from the given string any occurrency
    of the given pattern.
    
    :param myString: the string to be shortened
    :param pattern: pattern of chars that must be deleted from myString
    :returns: a string
    
    >>> regexDelete('When he turns the steering wheel', 'he')
    'Wn  turns t steering wel'
    """
    return re.sub(pattern, '', myString)



def conditionalTemplate(myString,symbolDict=None):
    def cb(g):
        content = g.group(1)
        m = re.search("\\$([_a-zA-Z\\@][_a-zA-Z0-9\\.\\@]*)", content)
        if m and (m.group(1) in symbolDict) and (symbolDict[m.group(1)] not in (None,'')): 
            return content
        return ''
    return re.sub(CONDITIONAL_PATTERN, cb,myString)

    
def templateReplace(myString, symbolDict=None, safeMode=False,noneIsBlank=True,locale=None, 
                    formats=None,dtypes=None,masks=None,editcols=None,df_templates=None,localizer=None,
                    urlformatter=None,emptyMode=None,conditionalMode=True):
    """Allow to replace string's chunks.
    
    :param myString: template string
    :param symbolDict: dictionary that links symbol and values. .
    :param safeMode: if ``True`` (``False``) uses the ``safe_substitute()`` (``substitute()``) Python method.
                     Default value is ``False``.
    :param noneIsBlank: TODO. Default value is ``True``
    
    >>> templateReplace('$foo loves $bar but she loves $aux and not $foo', {'foo':'John','bar':'Sandra','aux':'Steve'})
    'John loves Sandra but she loves Steve and not John'"""
    myString = myString or ''
    templateBag=None
    if hasattr(myString, '_htraverse'):
        templateBag = myString.deepcopy()
        myString = templateBag.pop('main')
    if not '$' in myString or not symbolDict: return myString

    if hasattr(symbolDict, '_htraverse'):
        Tpl = BagTemplate
        #if templateBag:
        #    symbolDict = SubtemplateMapWrapper(symbolDict,templateBag, locale=locale)
        #elif noneIsBlank:
        #    symbolDict=NoneIsBlankMapWrapper(symbolDict)
        #  above is replaced by LocalizedWrapper
    else:
        Tpl = Template
    if conditionalMode and '${' in myString:
        myString = conditionalTemplate(myString,symbolDict=symbolDict)
    symbolDict = LocalizedWrapper(symbolDict, locale=locale, templates=templateBag, noneIsBlank=noneIsBlank, formats=formats,dtypes=dtypes,
                                    masks=masks,editcols=editcols,
                                    df_templates=df_templates,localizer=localizer,
                                    urlformatter=urlformatter,emptyMode=emptyMode)

    if safeMode:
        return Tpl(myString).safe_substitute(symbolDict)
    else:
        return Tpl(myString).substitute(symbolDict)
        
def asDict(myString, itemSep=',', argSep='=', symbols=None):
    """Return a dict from a key-value like string (or an empty dict, if there is no string)
    
    :param myString: a string that represent a list of key-value pairs.
    :param itemSep: the separator char between each key-value pair. Default value is ``,``
    :param argSep: the separator between keys and values. Default value is ``=``
    :param symbols: a dictionary that eventually contains value for templates in myString.
                    Default value is ``False``
    :returns: a dict from a key-value like string (or an empty dict, if there is no string)
    
    >>> asDict('height=22, weight=73')
    {'weight': '73', 'height': '22'}
    
    >>> asDict('height=$myheight, weight=73', symbols={'myheight':55})
    {'weight': '73', 'height': '55'}
    """
    if not myString: return {}
    if myString.startswith('('): myString = myString[1:-1]
    result = {}
    itemList = split(myString, itemSep)
    for item in itemList:
        item = item.strip().strip(itemSep)
        key, value = split(item, argSep)
        
        key = key.strip().encode()
        value = value.strip()
        if value.startswith("'"): result[key] = value.strip("'")
        elif value.startswith('"'): result[key] = value.strip('"')
        if value.startswith('(')and value.endswith(')'): result[key] = value[1:-1]
        else:
            if '$' in value: value = templateReplace(value, symbols)
            result[key] = value
    return result
    
def stringDict(myDict, itemSep=',', argSep='=',isSorted=False):
    """Return a string of key-value pairs taken from a dictionary.
    
    :param myDict: dictionary to transform in a string
    :param itemSep: the separator char between each key-value pair. Default value is ``,``
    :param argSep: the separator between keys and values. Default value is ``=``
    :returns: a string of key-value pairs taken from a dictionary
    
    >>> stringDict({'height':22,'width':33})
     'width=33,height=22'
    """
    keys = myDict.keys()
    if isSorted:
        keys = keys.sort()
    return itemSep.join([argSep.join((str(k), str(myDict[k]))) for k in keys])
    
def updateString(source, s, sep=','):
    """Append a new ``s`` string to the ``source`` string. The two strings are linked by 
    a ``sep`` char. If there isn't ``source`` string, return the ``s`` string.
    
    :param source: initial string
    :param s: string to be added
    :param sep: separator string. Default value is ``,``
    
    >>> updateString('I drink cola', 'beer')
    'I drink cola,beer'
    
    >>> updateString('I drink cola', 'beer', ' and ')
    'I drink cola and beer'
    """
    if not source: return s
    splitted = split(source, sep)
    if s in splitted: return source
    return sep.join(splitted + [s])
    
def updateStringList(s1, s2, sep=','):
    """TODO
    
    :param s1: TODO
    :param s2: TODO
    :param sep: separator string. Default value is ``,``
    :returns: TODO
    """
    #what??
    l1 = set(splitAndStrip(s1))
    l2 = set(splitAndStrip(s2))
    s = set()
    
def makeSet(*args, **kwargs):
    """TODO
    """
    result = set()
    for myString in args:
        result.update(splitAndStrip(myString, sep=kwargs.get('sep', ',')))
    if not kwargs.get('keepEmpty', False):
        result.discard('')
    return result
    
def splitAndStrip(myString, sep=',', n=-1, fixed=0):
    """Split a string in a list of n+1 items, striping white spaces.
        
    :param myString: the string to be splitted
    :param sep: separation character. Default value is ``,``
    :param n: how many split operations must be done on myString. Default value is ``-1``
    :param fixed: use ``fixed`` if the resulting list must have a fixed length. Default value is ``0``
    
    >>> splitAndStrip('cola, beer, milk')
    ['cola', 'beer', 'milk']
    >>> splitAndStrip('cola, beer, milk', n=2)
    ['cola', 'beer, milk']
    """
    myString = myString.strip().strip(sep)
    r = myString.split(sep, n)
    result = [x.strip() for x in r]
    delta = abs(fixed) - len(result)
    if not fixed or delta == 0:
        return result
    if delta > 0:
        dlist = [''] * delta
        if fixed > 0:
            return result + dlist
        else:
            return dlist + result
    else:
        return result[0:abs(fixed)]
        
def countOf(myString, srcString):
    """Return the number of the recurrence of the ``srcString`` string
    into the ``myString`` string
        
    :param myString: the string to be compared with ``srcString``
    :param srcString: the string to compare
    :returns: the number of the recurrence of the ``srcString`` into ``myString``
    
    >>> a = 'hello hello heeeello hello helo hi'
    >>> b = 'hello'
    >>> countOf(a,b)
    3
    """
    return (len(myString) - len(myString.replace(srcString, ''))) / len(srcString)
    
def split(path, sep='.'):
    """Return a list splitting a path string at any occurrency of separation character.
    
    :param path: the path string to be splitted
    :param sep: separation character. Default value is ``.``
    
    >>> split('first.second.third')
    ['first', 'second', 'third']
    """
    
    if not path: return ['']
    extendedsep = sep[1:]
    sep = sep[0]
    result = []
    start = 0
    end = len(path)
    myre = re.compile("([^\%s\'\"\(\[\)\]]*)(?:(?P<enditem>\%s|$)|(\')|(\")|(\()|(\[)|(\))|(\]))" % (sep, sep))
    wch = []
    nextPos = start
    while start < end:
        startpos = start
        foundsep = False
        while not foundsep or wch:
            res = myre.match(path, nextPos)
            gr = res.groups()
            nextPos = res.end()
            if gr[1] == "": #End of string
                if wch: raise  ValueError("wrong level: missing :" + wch.pop())
                foundsep = True
                blockLen = res.end()
                
            elif not wch and gr[1] != None:
                foundsep = True
                blockLen = res.end() - 1
                if extendedsep and res.group('enditem') == sep:
                    if path[nextPos:].startswith(extendedsep):
                        nextPos = nextPos + len(extendedsep)
                    else:
                        foundsep = False
            else:
                char = gr[2] or gr[3] or gr[4] or gr[5] or gr[6] or gr[7]
                if char:
                    if char in """\'\"""": nextPos = path.index(char, nextPos) + 1
                    elif char == '(': wch.append(')')
                    elif char == '[': wch.append(']')
                    elif char in '])':
                        if char == wch[-1]: wch.pop()
                        else: raise ValueError("wrong level: missing :" + wch.pop())
                        
        result.append(path[startpos:blockLen])
        start = nextPos
    return result
    
def smartjoin(mylist, on):
    """Join a list with the separator substring ``on`` escaping each occurrency
    of ``on`` within the given list
        
    :param mylist: the list to be joined
    :param on: separator substring
    :returns: the joined string
    
    >>> smartjoin(['Hello, dog', 'you', 'are', 'yellow'], ',')
    'Hello\\, dog,you,are,yellow'
    """
    escape = "\\" + on
    return on.join([x.replace(on, escape) for x in mylist])
    
def smartsplit(path, on):
    """Split the string ``path`` with the separator substring ``on`` ignoring the
    escaped separator chars
    
    :param path: the path to be splitted
    :param on: separator substring
    """
    
    escape = "\\" + on
    if escape in path:
        path = path.replace(escape, chr(1))
        pathList = path.split(on)
        pathList = [x.replace(chr(1), escape) for x in pathList]
    else:
        pathList = path.split(on)
    return pathList
    
def concat(s1, s2, sep='.'):
    """join two strings through the separator attribute ``sep``. If the first string is ``None``,
    return the second string.
    
    :param s1: the first string
    :param s2: the second string
    :param sep: separation character. Default value is ``.``
    :returns: a string with the two strings joined
    """
    if s1:
        return '%s%s%s' % (s1, sep, s2)
    else:
        return s2
        
def dotEsc(txt):
    """Return a text with all dot char escaped
    
    :param txt: the text
    :returns: the text with all dot char escaped
    """
    return txt.replace('.', '\\.')
    
#encoding and conversion functions


def baseEncode(number, base='/16', nChars=None):
    """Return a string that contains the given number in the specified base
       
    :param number: number to encode
    :param base: base of encoding. Default value is ``/16``
    :param nChar: number of characters of the result. """
    import math
    
    if base in BASE_ENCODE: base = BASE_ENCODE[base]
    b = len(base)
    result = []
    while (number >= 1):
        result.insert(0, base[int(math.fmod(number, b))])
        number = math.floor(number / b)
        
    if (len(result) > nChars): result = []
    elif (len(result) < nChars):
        for x in range(nChars - len(result)):
            result.insert(0, base[0])
    return ''.join(result)

def encode36(number, nChars=1):
    return baseEncode(number,'/36',nChars=nChars)


def baseDecode(s, base='/16'):
    if base in BASE_ENCODE: base = BASE_ENCODE[base]
    result = 0
    n = len(base)
    for v in s:
        result = result*n + base.index(v)

    return result

def decode36(s):
    return baseDecode(s,'/36')


def fromIsoDate(datestring):
    """TODO
        
    :param datestring: TODO"""
    if datestring and datestring != '0000-00-00':
        return datetime.date(*[int(el) for el in wordSplit(datestring)])
        
def fromText(mystring, obj, locale=None):
    """TODO
    
    :param mystring: TODO
    :param obj: TODO
    :param locale: the current locale (e.g: en, en_us, it)"""
    #what?
    return parselocal(mystring, obj, locale=locale)
    
def toText(obj, locale=None, format=None, mask=None, encoding=None, currency=None):
    """Return a unicode string representing an object of any class
    
    If there are ``locale`` or ``format`` parameters Babel is used to format the value
    according to the given localization or format
    
    :param obj: the object to be transformed in a string
    :param locale: the current locale (e.g: en, en_us, it)
    :param format: TODO
    :param mask: TODO
    :param encoding: The multibyte character encoding you choose
    :param currency: TODO"""
    if hasattr(obj, '_htraverse') and format:
        return templateReplace(format,obj)
    if isinstance(obj, list) or isinstance(obj, tuple):
        return ','.join([toText(v) for v in obj])
        #what?
    if obj in (None,''): return u''
    if not (locale or format):
        result = unicode(obj)
    else:
        result = localize(obj, locale=locale, format=format, currency=currency)
        
    if mask:
        result = mask % result
    return result
        
def guessLen(dtype, locale=None, format=None, mask=None, encoding=None):
    """TODO
    
    :param dtype: the :ref:`datatype`
    :param locale: the current locale (e.g: en, en_us, it)
    :param format: TODO
    :param mask: TODO
    :param encoding: The multibyte character encoding you choose"""
    typeSamples = {'B': 'true', 'D': datetime.date(2005, 10, 10), 'H': datetime.time(4, 5),
                   'DH': datetime.datetime.now(),
                   'I': 1234, 'L': 48205294, 'R': 34567.67, 'serial': 123445566}
    result = 10
    if dtype in typeSamples.keys():
        result = len(toText(typeSamples[dtype], format=format, mask=mask))
    return result
    
def boolean(obj):
    """Return ``False`` if the given ``obj`` string is one of the following values:
    
    * 'n'
    * 'no'
    * 'f'
    * 'false'
    * '0'
    
    (the ``obj`` is lowered before comparing it)
    
    :param obj: The given object"""
    if obj and isinstance(obj, basestring):
        if obj.lower() in ('n', 'no', 'f', 'false', '0'):
            obj = False
    return bool(obj)
    
def pickleObject(obj, zipfilename=None):
    """Return the Pickle string for the given object
        
    :param obj: The given object
    :param zipfilename: TODO"""
    objstr = cPickle.dumps(obj)
    if zipfilename:
        objstr = zipString(objstr, zipfilename)
    return objstr
    
def unpickleObject(objstr, zipfilename=None):
    """Load an object from a pickle string and return it
        
    :param objstr: The given object string
    :param zipfilename: TODO"""
    if zipfilename:
        objstr = unzipString(objstr, zipfilename)
    return cPickle.loads(objstr)
    
def zipString(mystring, filename):
    """Return a zip compressed version of the *mystring* string
        
    :param mystring: The given string
    :param filename: name of the zipped file"""
    zipresult = StringIO.StringIO()
    zip = zipfile.ZipFile(zipresult, mode='w', compression=zipfile.ZIP_DEFLATED)
    zip.writestr(filename, mystring)
    zip.close()
    mystring = zipresult.getvalue()
    zipresult.close()
    return mystring
    
def unzipString(mystring, filename):
    """Extract a zip compressed string and return it
        
    :param mystring: the compressed string to decompress
    :param filename: the name of the unzipped file"""
    zipresult = StringIO.StringIO(mystring)
    zip = zipfile.ZipFile(zipresult, mode='r', compression=zipfile.ZIP_DEFLATED)
    result = zip.read(filename)
    zip.close()
    zipresult.close()
    return result
    
def toJson(obj):
    """TODO
        
    :param obj: TODO"""
    #non so come testare
    return json.dumps(obj, cls=JsonEncoder)
    
def toJsonJS(obj):
    """TODO
        
    :param obj: TODO"""
    return json.dumps(obj, cls=JsonEncoderJS)
    
def toSecureJsonJS(obj, key=None):
    """TODO
        
    :param obj: TODO
    :param key: TODO"""
    result = json.dumps(obj, cls=JsonEncoderJS)
    if key:
        n = 0
        nmax = len(key)
        umax = len(result)
        t = nmax * umax
        for k in result:
            if n >= nmax:
                n = 0
            t = (t + (t + (ord(k) * ord(key[n]))) % umax)
            n = n + 1
        return '@%s_%s' % (str(t % 10000).zfill(4), result)
    else:
        return result
        
def slugify(value):
    """TODO
        
    :param value: TODO"""
    import unicodedata
    value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)
    
def fromJson(obj):
    """TODO
        
    :param obj: TODO"""
    #non so come testare
    return json.loads(obj)
    
def anyWordIn(wordlist, mystring):
    """Return a list of all the elements included both in ``wordlist`` and in ``mystring``
        
    :param wordlist: the list of words to be searched in ``mystring``
    :param mystring: the string on which there will be executed the search"""
    return [k for k in wordlist if k in mystring]
    
def jsquote(str_or_unicode):
    """TODO
        
    :param str_or_unicode: the string to be quoted
    :returns: TODO
     
    >>> print jsquote('pippo')
    'pippo'
    >>> print jsquote(u'pippo')
    'pippo'"""
    if isinstance(str_or_unicode, str):
        return repr(str_or_unicode)
    elif isinstance(str_or_unicode, unicode):
        return repr(str_or_unicode.encode('utf-8'))
        
if __name__ == '__main__':
    incl = '%.py,%.css'
    excl = '_%,.%'
    lst = ['pippo.py', 'piero.txt', '_gino.py', '.ugo.css', 'mario.css', 'sergio.py']
    result = [x for x in lst if filter(x, include=incl, exclude=excl)]
    print toJson([1, 2, 4])
    print result
    