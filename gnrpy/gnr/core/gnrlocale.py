import datetime

try:
    from decimal import Decimal
    import pytz
    from babel import numbers, dates, Locale
except:
    pass

DEFAULT_LOCALE = 'en_US'

def localize(obj, format=None, currency=None, locale=None):
    locale = (locale or DEFAULT_LOCALE).replace('-', '_').split(';')[0]
    if obj is None: return u''
    if format and format.startswith('auto_'):
        format = DEFAULT_FORMATS_DICT.get(format[5:])
    f = TYPES_LOCALIZERS_DICT.get(type(obj))
    if f:
        return f(obj, locale, format=format, currency=currency)
    else:
        return unicode(obj)

def localize_number(obj, locale, format=None, currency=None):
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
    format = format or 'short'
    return dates.format_date(obj, format=format, locale=locale)

def localize_datetime(obj, locale, format=None, **kwargs):
    format = format or 'short'
    return dates.format_datetime(obj, format=format, locale=locale)

def localize_time(obj, locale, format=None, **kwargs):
    format = format or 'short'
    dt = datetime.datetime(1970, 1, 1, obj.hour, obj.minute, obj.second, obj.microsecond, obj.tzinfo)
    return dates.format_time(obj, format=format, locale=locale)


def parselocal_number(txt, locale):
    return numbers.parse_number(txt, locale)

def parselocal_float(txt, locale):
    return numbers.parse_decimal(txt, locale)

def parselocal_decimal(txt, locale):
    loc = Locale.parse(locale).number_symbols
    txt = txt.replace(loc['group'], '')
    txt = txt.replace(loc['decimal'], '.')
    return Decimal(txt)

def parselocal_date(txt, locale):
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
        return dates.parse_date(txt, locale)

def parselocal_datetime(txt, locale):
    return dates.parse_datetime(txt, locale)

def parselocal_time(txt, locale):
    return dates.parse_time(txt, locale)

def parselocal(txt, cls, locale=None):
    """:param cls: ???add
    :param locale: ???add
    
    :returns: an object of class cls
    """
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
    locale = (locale or DEFAULT_LOCALE).replace('-', '_')
    d = dict([(v.lower(), k) for k, v in dates.get_month_names(width='wide', locale=locale).items()])
    d.update([(v.lower(), k) for k, v in dates.get_month_names(width='abbreviated', locale=locale).items()])
    return d

def getDayNames(locale=None):
    locale = (locale or DEFAULT_LOCALE).replace('-', '_')
    d = dict([(v.lower(), k) for k, v in dates.get_day_names(width='wide', locale=locale).items()])
    d.update([(v.lower(), k) for k, v in dates.get_day_names(width='abbreviated', locale=locale).items()])
    return d

def getQuarterNames(locale=None):
    locale = (locale or DEFAULT_LOCALE).replace('-', '_')
    d = dict([(v.lower(), k) for k, v in dates.get_quarter_names(width='wide', locale=locale).items()])
    d.update([(v.lower(), k) for k, v in dates.get_quarter_names(width='abbreviated', locale=locale).items()])
    return d


def getDateKeywords(keyword, locale=None):
    locale = (locale or DEFAULT_LOCALE).replace('-', '_')
    keydict = DATEKEYWORDS.get(locale, {})
    if not keydict and len(locale) > 2: # like en_us
        keydict = DATEKEYWORDS.get(locale[:2], {})

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
                         datetime.time: localize_time
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

try: # python2.5 only
    TYPES_LOCALIZERS_DICT[Decimal] = localize_number
    TYPES_LOCALPARSERS_DICT[Decimal] = parselocal_decimal
except:
    pass