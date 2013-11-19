# -*- coding: UTF-8 -*-

import datetime

from decimal import Decimal
import pytz
from babel import numbers, dates, Locale
from gnr.core.gnrlang import GnrException

DEFAULT_LOCALE = 'en_US'

def localize(obj, format=None, currency=None, locale=None):
    """TODO
    
    :param obj: TODO
    :param format: TODO
    :param currency: TODO
    :param locale: the current locale (e.g: en, en_us, it)"""
    locale = (locale or DEFAULT_LOCALE).replace('-', '_').split(';')[0]
    if obj is None: return u''
    if format and format.startswith('auto_'):
        format = DEFAULT_FORMATS_DICT.get(format[5:])
        
    obj,handler = formatHandler(obj)
    if handler:
        return handler(obj, locale, format=format, currency=currency)
    else:
        return unicode(obj)

def formatHandler(obj):
    if isinstance(obj,basestring) and '::' in obj:
        obj,dtype = obj.rsplit('::',1)
    else:
        dtype = type(obj)
    if dtype=='HTML':
        obj = '%s::HTML' %obj
    return obj,TYPES_LOCALIZERS_DICT.get(dtype)

        
def localize_number(obj, locale, format=None, currency=None):
    """TODO
    
    :param obj: TODO
    :param locale: the current locale (e.g: en, en_us, it)
    :param format: TODO
    :param currency: TODO"""
    if format:
        flist = format.split(';')
        if len(flist) > 2:
            if obj == 0:
                return flist[2]
            else:
                format = '%s;%s' % (flist[0], flist[1])
        if currency:
            print currency
            return numbers.format_currency(obj, currency=currency, format=format, locale=locale)
        else:
            return numbers.format_decimal(obj, format=format, locale=locale)
    else:
        return numbers.format_number(obj, locale=locale)
        
def localize_date(obj, locale, format=None, **kwargs):
    """TODO
    
    :param obj: TODO
    :param locale: the current locale (e.g: en, en_us, it)
    :param format: TODO"""
    format = format or 'short'
    return dates.format_date(obj, format=format, locale=locale)
    
def localize_boolean(obj, locale='en', format=None, **kwargs):
    format = format or 'tf'
    format = getBoolKeywords(format,locale=locale)[0]  
    format = format.split(';')
    if obj is None and len(format)>2:
        return format[2]
    if obj:
        return format[0]
    return format[1]

def localize_datetime(obj, locale, format=None, **kwargs):
    """TODO
    
    :param obj: TODO
    :param locale: the current locale (e.g: en, en_us, it)
    :param format: TODO"""
    format = format or 'short'
    return dates.format_datetime(obj, format=format, locale=locale)
    
def localize_time(obj, locale, format=None, **kwargs):
    """TODO
    
    :param obj: TODO
    :param locale: the current locale (e.g: en, en_us, it)
    :param format: TODO"""
    format = format or 'short'
    dt = datetime.datetime(1970, 1, 1, obj.hour, obj.minute, obj.second, obj.microsecond, obj.tzinfo)
    return dates.format_time(obj, format=format, locale=locale)
    

def localize_img(value, locale, format=None, **kwargs):
    """format='x:34,y:56,z:1,r:38,h:45,w:134'   or dict"""
    if not format:
        return value
    if format == 'img':
        return """<img src="%s"/>""" %value
    cropper_zoom = None
    if isinstance(format,basestring) and format.startswith('auto'):
        cropper_zoom = float(format.split(':')[1]) if ':' in format else None
        if '?' in value:
            value,format = value.split('?')
            format = format.replace('=',':').replace('&',',').replace('v_','')
        else:
            format = dict()
    if isinstance(format,basestring):
        format = dict([p.split(':') for p in format.split(',')])
    format.update(kwargs)
    cropper = '%s'
    format.setdefault('style','')
    if 'h' in format and 'w' in format:
        format['cropper_style'] =''
        if cropper_zoom:
            format['h'] =float(format['h']) * cropper_zoom
            format['w'] =float(format['w']) * cropper_zoom
        c = '<div style="height:%(h)spx;width:%(w)spx;overflow:hidden;%(style)s">' %format
        format.pop('style',None)
        if cropper_zoom:
            cropper_style = """-webkit-transform:scale(%f);-webkit-transform-origin:0px 0px;-moz-transform:scale(%f);-moz-transform-origin:0px 0px;""" %(cropper_zoom,cropper_zoom)
            cropper = c+'<div style="%s">' %cropper_style
            cropper = cropper+'%s'+'</div></div>'
        else:
            cropper = c+'%s</div>'
    styleimg = dict(margin_top=format.get('y') or 0,margin_left=format.get('x') or 0,
                       zoom=format.get('z') or 1,rotate=format.get('r') or 0)

    styleimg = """margin-top:-%(margin_top)spx;
                  margin-left:-%(margin_left)spx;
                  -webkit-transform:scale(%(zoom)s) rotate(%(rotate)sdeg);
                  -moz-transform:scale(%(zoom)s) rotate(%(rotate)sdeg);
                    """ %styleimg
    styleimg = styleimg.replace('--','')
    styleimg = 'style="%s %s;"' %(styleimg,(format.get('style') or ''))
    value = '<img %s src="%s"/>' %(styleimg,value)
    return cropper %value
    
def parselocal_number(txt, locale):
    """TODO
    
    :param txt: TODO
    :param locale: the current locale (e.g: en, en_us, it)"""
    return numbers.parse_number(txt, locale)
    
def parselocal_float(txt, locale):
    """TODO
    
    :param txt: TODO
    :param locale: the current locale (e.g: en, en_us, it)"""
    return numbers.parse_decimal(txt, locale)
    
def parselocal_decimal(txt, locale):
    """TODO
    
    :param txt: TODO
    :param locale: the current locale (e.g: en, en_us, it)"""
    loc = Locale.parse(locale).number_symbols
    txt = txt.replace(loc['group'], '')
    txt = txt.replace(loc['decimal'], '.')
    return Decimal(txt)
    
def parselocal_date(txt, locale):
    """TODO
    
    :param txt: TODO
    :param locale: the current locale (e.g: en, en_us, it)"""
    if txt.isdigit() and len(txt) in (6, 8): # is a date without separators: 101207
        result = {}
        format = dates.get_date_format(locale=locale).pattern.lower()
        year_idx = format.index('y')
        month_idx = format.index('m')
        if month_idx < 0:
            month_idx = format.index('l')
        day_idx = format.index('d')
        indexes = [(year_idx, 'Y'), (month_idx, 'M'), (day_idx, 'D')]
        indexes.sort()
        is8 = (len(txt) == 8)
        for i, k in indexes:
            w = 2
            if k == 'Y':
                if is8:
                    w = 4
                    result[k] = int(txt[:w])
                else:
                    year = int(txt[:w])
                    if year < 70:
                        result[k] = 2000 + year
                    else:
                        result[k] = 1900 + year
            else:
                result[k] = int(txt[:w])
            txt = txt[w:]
        return datetime.date(result['Y'], result['M'], result['D'])
    else:
        try:
            date = dates.parse_date(txt, locale)
        except:
            raise GnrException('Invalid date')
        return date
        
def parselocal_datetime(txt, locale):
    """TODO
    
    :param txt: TODO
    :param locale: the current locale (e.g: en, en_us, it)"""
    return dates.parse_datetime(txt, locale)
    
def parselocal_time(txt, locale):
    """TODO
    
    :param txt: TODO
    :param locale: the current locale (e.g: en, en_us, it)"""
    return dates.parse_time(txt, locale)
    
def parselocal(txt, cls, locale=None):
    """TODO
    
    :param txt: TODO
    :param cls: TODO
    :param locale: the current locale (e.g: en, en_us, it)"""
    locale = (locale or DEFAULT_LOCALE).replace('-', '_')
    if locale and '_' in locale:
        loc, country = locale.split('_')
        locale = '%s_%s' % (loc, country.upper())
    if not txt: return None
    f = TYPES_LOCALPARSERS_DICT.get(cls)
    if f:
        if locale:
            locale = Locale(locale)
        else:
            locale = Locale()
        return f(txt, locale)
        
def getMonthNames(locale=None):
    """TODO
    
    :param locale: the current locale (e.g: en, en_us, it)"""
    locale = (locale or DEFAULT_LOCALE).replace('-', '_')
    d = dict([(v.lower(), k) for k, v in dates.get_month_names(width='wide', locale=locale).items()])
    d.update([(v.lower(), k) for k, v in dates.get_month_names(width='abbreviated', locale=locale).items()])
    return d
    
def getDayNames(locale=None):
    """TODO
    
    :param locale: the current locale (e.g: en, en_us, it)"""
    locale = (locale or DEFAULT_LOCALE).replace('-', '_')
    d = dict([(v.lower(), k) for k, v in dates.get_day_names(width='wide', locale=locale).items()])
    d.update([(v.lower(), k) for k, v in dates.get_day_names(width='abbreviated', locale=locale).items()])
    return d
    
def getQuarterNames(locale=None):
    """TODO
    
    :param locale: the current locale (e.g: en, en_us, it)"""
    locale = (locale or DEFAULT_LOCALE).replace('-', '_')
    d = dict([(v.lower(), k) for k, v in dates.get_quarter_names(width='wide', locale=locale).items()])
    d.update([(v.lower(), k) for k, v in dates.get_quarter_names(width='abbreviated', locale=locale).items()])
    return d

def _localeKey(self,locale):
    locale = (locale or DEFAULT_LOCALE).replace('-', '_')
    
    
def getDateKeywords(keyword, locale=None):
    return getKeywords(DATEKEYWORDS,keyword,locale=locale)

def getBoolKeywords(keyword, locale=None):
    return getKeywords(BOOLKEYWORDS,keyword,locale=locale)
      
    
def getKeywords(sourcedict,keyword, locale=None):
    """TODO
    
    :param keyword: TODO
    :param locale: the current locale (e.g: en, en_us, it)"""
    locale = (locale or DEFAULT_LOCALE).replace('-', '_')
    keydict = sourcedict.get(locale, {})
    if not keydict and len(locale) > 2: # like en_us
        keydict = sourcedict.get(locale[:2], {})
        
    if isinstance(keyword, basestring):
        keyword = [keyword]
    result = []
    for k in keyword:
        kloc = keydict.get(k, k)
        if isinstance(kloc, basestring):
            result.append(kloc)
        else:
            result.extend(kloc)
    return result
    
TYPES_LOCALIZERS_DICT = {int: localize_number,
                         long: localize_number,
                         float: localize_number,
                         datetime.date: localize_date,
                         datetime.datetime: localize_datetime,
                         datetime.time: localize_time,
                         bool:localize_boolean,
                         'P':localize_img

}

TYPES_LOCALPARSERS_DICT = {int: parselocal_number,
                           long: parselocal_number,
                           float: parselocal_float,
                           datetime.date: parselocal_date,
                           datetime.datetime: parselocal_datetime,
                           datetime.time: parselocal_time
}
DEFAULT_FORMATS_DICT = {'R': '0.00', 'D': 'short'}

DATEKEYWORDS = {
    'en': {'this week': ('this week', 'week'), 'next week': 'next week', 'last week': 'last week',
           'this month': ('this month', 'month'), 'next month': 'next month', 'last month': 'last month',
           'today': 'today', 'yesterday': 'yesterday', 'tomorrow': 'tomorrow',
           'to': ('to', 'and'), 'from': ('from', 'between'), 'no period': ('no period', 'always')},
    'it': {'this week': ('questa settimana', 'settimana'), 'next week': 'settimana prossima',
           'last week': 'settimana scorsa',
           'this month': ('questo mese', 'mese'), 'next month': 'mese prossimo', 'last month': 'mese scorso',
           'today': 'oggi', 'yesterday': 'ieri', 'tomorrow': 'domani',
           'from': ('da', 'dal', 'dalla'), 'to': ('a', 'al', 'alla', 'e'), 'no period': ('senza periodo', 'sempre')}
}

BOOLKEYWORDS = { 'en':{'tf':'True;False','tfu':'True;False;Undefined','yn':'Yes;No','ynu':'Yes;No;Unknown'},
                 'it':{'tf':'Vero;Falso','tfu':'Vero;Falso;Ignoto','yn':u'Sì;No','ynu':u'Sì;No;N.A'}}
    
try: # python2.5 only
    TYPES_LOCALIZERS_DICT[Decimal] = localize_number
    TYPES_LOCALPARSERS_DICT[Decimal] = parselocal_decimal
except:
    pass