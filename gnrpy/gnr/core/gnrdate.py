# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy core - see LICENSE for details
# module gnrstring : gnr date implementation
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
import logging
import datetime
import calendar
import copy
import bisect

from gnr.core import gnrlocale
from gnr.core.gnrlocale import DEFAULT_LOCALE
from gnr.core.gnrstring import splitAndStrip, anyWordIn, wordSplit, toText
from dateutil import rrule

logger = logging.getLogger(__name__)

def checkDateKeywords(keywords,datestr,locale):
    return anyWordIn(gnrlocale.getDateKeywords(keywords, locale), datestr) or anyWordIn(
                gnrlocale.getDateKeywords(keywords, DEFAULT_LOCALE), datestr)

def yearDecode(datestr):
    """returns the year number as an int from a string of 2 or 4 digits:
    if 2 digits is given century is added
    
    :param datestr: the string including year"""
    year = None
    datestr = datestr.strip()
    if datestr and datestr.isdigit():
        year = int(datestr)
        if len(datestr) == 2:
            if year < 70:
                year = 2000 + year
            else:
                year = 1900 + year
    return year

def decodeOneDate(datestr, workdate=None, months=None, days=None, quarters=None, locale=None, isEndPeriod=False):
    """Parse a string representing a date or a period. Return ``datetime.date``
    or ``tuple(year,month)`` or ``None``
    
    :param datestr: the string to be interpreted
    :param workdate: the :ref:`workdate`
    :param months: names of months according to locale (just for caching)
    :param days: names of weekdays according to locale (just for caching)
    :param quarters: names of quarters according to locale (just for caching)
    :param locale: the current locale (e.g: en, en_us, it)
    :param isEndPeriod: if the string represents a period, return the end date
                        (default return the start date)
    
    Special keywords like ``today`` or the name of a month can be translated in all languages
    and support synonimous. (e.g: this month; e.g: month)
    
    The input string can be:
    
    * a year: e.g. 2007 or 07
    * today, yesterday, tomorrow (can be translated in all languages)
        * you can specify a number of days to add to today: e.g. 'today + 3' or 'today - 15'
    * this week, next week, last week (can be translated in all languages)
    * this month, next month, last month (can be translated in all languages )
        * can be specified a number of months to add to current month: e.g. 'this month + 3' or 'this month - 24'
    * the name of a quarter: e.g. Q1 or 1st quarter
    * the name of a month: e.g. april or apr
        * can be specified a year after the month: e.g. apr 07 or april 2007
        * returns a tuple (year, month): if year is not specified in datestr, year is returned None
    * the name of a weekday: e.g. monday or mon
        * the date returned is the date of the given weekday in this week (relative to workdate)
    * an iso date: e.g. 2008-04-28
    * a date formatted according to locale (see babel doc): e.g. 4 28, 2008 (en_us) or 28-4-08 (it)
                           various separators are admitted: 28-4-08, 28/4/08, 28 4 08"""
    
    def addToDay(datestr, date):
        if '+' in datestr:
            days = int(datestr.split('+')[1].strip())
            return date + datetime.timedelta(days)
        if '-' in datestr:
            days = int(datestr.split('-')[1].strip())
            return date - datetime.timedelta(days)
        return date

    def addToMonth(datestr, date, addmonth=0):#l'errore è nel chiamate che passa addmonth sbagliato
        delta=0
        if '+' in datestr:
            delta =  int(datestr.split('+')[1].strip())
        if '-' in datestr:
            delta = -int(datestr.split('-')[1].strip())
        month = date.month + addmonth+ delta
        year = date.year
        while month <= 0:
            month = month + 12
            year = year - 1
        while month > 12:
            month = month - 12
            year = year + 1
        return datetime.date(year, month, 1)
        
    datestr = datestr or ''
    datestr = datestr.strip()
    if datestr:
        months = months or gnrlocale.getMonthNames(locale)
        def_months = gnrlocale.getMonthNames(DEFAULT_LOCALE)
        days = days or gnrlocale.getDayNames(locale)
        def_days = gnrlocale.getDayNames(DEFAULT_LOCALE)
        quarters = quarters or gnrlocale.getQuarterNames(locale)
        def_quarters = gnrlocale.getQuarterNames(DEFAULT_LOCALE)
        dateStart = None
        dateEnd = None
        workdate = workdate or datetime.date.today()
        
        if datestr.isdigit() and len(datestr) in (2, 4):                          # a full year
            year = yearDecode(datestr)
            dateStart = datetime.date(year, 1, 1)
            if isEndPeriod:
                dateEnd = datetime.date(year, 12, 31)
                
        elif checkDateKeywords('today', datestr, locale):     # today
            dateStart = addToDay(datestr, workdate)
        elif checkDateKeywords('yesterday', datestr, locale): # yesterday
            dateStart = addToDay(datestr, workdate - datetime.timedelta(1))
        elif checkDateKeywords('tomorrow', datestr, locale):  # tomorrow
            dateStart = addToDay(datestr, workdate + datetime.timedelta(1))

        elif checkDateKeywords(('this week', 'next week', 'last week'), datestr, locale): # relative week
            j = workdate.weekday()
            dateStart = workdate - datetime.timedelta(j)
            if checkDateKeywords('last week', datestr, locale):
                dateStart = dateStart - datetime.timedelta(7)
            elif checkDateKeywords('next week', datestr, locale):
                dateStart = dateStart + datetime.timedelta(7)
            if '+' in datestr:
                 dateStart = dateStart + datetime.timedelta(7*int(datestr.split('+')[1]))
            if '-' in datestr:
                 dateStart = dateStart - datetime.timedelta(7*int(datestr.split('-')[1]))
            if isEndPeriod:
                dateEnd = dateStart + datetime.timedelta(6)
        elif checkDateKeywords(('this month', 'next month', 'last month'), datestr, locale): # relative month
            if checkDateKeywords('last month', datestr, locale):  
                dateStart = addToMonth(datestr, workdate, -1)
            elif checkDateKeywords('next month', datestr, locale):
                dateStart = addToMonth(datestr, workdate, 1)
            else:
                dateStart = addToMonth(datestr, workdate)
            if isEndPeriod:
                dateEnd = monthEnd(date=dateStart)
        elif anyWordIn(quarters.keys(), datestr): # quarter
            qt, year = splitAndStrip(datestr, sep=' ', n=1, fixed=2)
            year = yearDecode(year)
            qt = quarters[datestr]
            dateStart = (year, qt * 3 - 2)
            if isEndPeriod:
                dateEnd = (year, qt * 3)
        elif anyWordIn(def_quarters.keys(), datestr): # quarter
            qt, year = splitAndStrip(datestr, sep=' ', n=1, fixed=2)
            year = yearDecode(year)
            qt = def_quarters[datestr]
            dateStart = (year, qt * 3 - 2)
            if isEndPeriod:
                dateEnd = (year, qt * 3)
        elif anyWordIn(months.keys(), datestr):                                 # month name
            month, year = splitAndStrip(datestr, sep=' ', n=1, fixed=2)
            year = yearDecode(year)
            month = months[month]
            dateStart = (year, month)
        elif anyWordIn(def_months.keys(), datestr):                                 # month name
            month, year = splitAndStrip(datestr, sep=' ', n=1, fixed=2)
            year = yearDecode(year)
            month = def_months[month]
            dateStart = (year, month)
        elif datestr in days:                                                   # weekday name
            dateStart = workdate + datetime.timedelta(days[datestr] - workdate.weekday())
        elif datestr in def_days:                                                   # weekday name
            dateStart = workdate + datetime.timedelta(def_days[datestr] - workdate.weekday())
        elif re.match('\d{4}-\d{2}-\d{2}', datestr):                            # ISO date
            date_items = [int(el) for el in wordSplit(datestr)[0:3]]
            dateStart = datetime.date(*[int(el) for el in wordSplit(datestr)[0:3]])
        else:                                                                   # a date in local format
            dateStart = gnrlocale.parselocal(datestr, datetime.date, locale)
        if isEndPeriod and dateEnd:
            return dateEnd
        else:
            return dateStart
            
def periodCaption(dateFrom=None, dateTo=None, locale=None):
    """Convert two dates to a string in the specified locale that
    :meth:`decodeDatePeriod` will understand
    
    :param dateFrom: the beginning period date
    :param dateTo: the ending period date
    :param locale: the current locale (e.g: en, en_us, it)"""
    localNoPeriod = gnrlocale.getDateKeywords('no period', locale)[0]
    localTo = gnrlocale.getDateKeywords('to', locale)[0]
    localFrom = gnrlocale.getDateKeywords('from', locale)[0]
    textFrom = toText(dateFrom, locale=locale)
    textTo = toText(dateTo, locale=locale)
    if dateFrom and dateTo:
        return '%s %s %s %s' % (localFrom, textFrom, localTo, textTo)
    if dateFrom:
        return '%s %s' % (localFrom, textFrom)
    elif dateTo:
        return '%s %s' % (localTo, textTo)
    else:
        return localNoPeriod
        
def decodeDatePeriod(datestr, workdate=None, locale=None, returnDate=False, dtype='D'):
    """Parse a string representing a date or a period and returns a string of one or two dates in iso format separated by ``;``.
    See doc of :meth:`decodeOneDate()` for details on possible formats of a single date
    
    :param datestr: the string representing a date or a period
    :param workdate: the :ref:`workdate`
    :param locale: the current locale (e.g: en, en_us, it)
    :param returnDate: boolean. If ``True``, return the following tuple: ``(dateStart, dateEnd)``
    :param dtype: the :ref:`datatype`
    
    The input *datestr* can be:
    
    * two dates separated by ``;``: e.g. ``22 4, 2008;28 4, 2008``
    * two dates separated by `` to ``
    * two dates in form ``from date to date`` (can be translated and supports synonimous, e.g. ``between date and date``)
    
        * if a period is given as starting date, the start date of period is kept
        * if a period is given as end date, the end date of period is kept
        * if no year is specified, the year is relative to :ref:`workdate`, keeping all periods in the past
          (e.g. if working date is 2008-04-28, december is interpreted as december 2007)
        * if a year is specified for the end date (or period) a relative year is calculated for the starting period
          (e.g. from december to march 06: returns ``'2005-12-01;2006-03-31'``)
    * a starting date in form ``from date``, if date is a period starting date is keep: e.g. april returns ``'2008-04-01;'``
    * an end date in form ``to date``, if date is a period end date is keep: e.g. april returns ``';2008-04-30'``
    * a single expression representing a period: e.g. 2007 returns ``'2007-01-01;2007-12-31'``
    * a single expression representing a single date: e.g. today returns ``'2008-04-28'``
    """
    workdate = workdate or datetime.date.today()
    months = gnrlocale.getMonthNames(locale)
    days = gnrlocale.getDayNames(locale)
    datestr = datestr or ''
    datestr = datestr.lower().strip().replace(',', ';').replace(':', ';')
    exercise = False  # TODO

    dateStart = None
    dateEnd = None

    localNoPeriod = gnrlocale.getDateKeywords('no period', locale)
    localTo = gnrlocale.getDateKeywords('to', locale)
    localFrom = gnrlocale.getDateKeywords('from', locale)

    # check if the period is given with two separate date infos
    if ';' in datestr:
        # two dates or keywords separated by ";":   today;today+5
        dateStart, dateEnd = datestr.split(';')
    elif [k for k in localNoPeriod if k in datestr]:
        dateStart = dateEnd = ''
    elif [k for k in localTo if datestr.startswith('%s ' % k)]:
        # only end date: to december
        dateStart = ''
        dateEnd = datestr.split(' ', 1)[1]
    elif [k for k in localTo if (' %s ' % k) in datestr]:
        # two dates or keywords separated by ' to ' and optionally starting with 'from ': from october to december
        if [k for k in localFrom if datestr.startswith('%s ' % k)]:
            datestr = datestr.split(' ', 1)[1]
        dateStart, dateEnd = datestr.split(' %s ' % [k for k in localTo if (' %s ' % k) in datestr][0])
    elif [k for k in localFrom if datestr.startswith('%s ' % k)]:
        # only start date: from december
        dateStart = datestr.split(' ', 1)[1]
        dateEnd = ''

    if dateStart is None and dateEnd is None:
        # the period is given as an unique string info
        dateStart = dateEnd = datestr

    dateStart = decodeOneDate(dateStart, workdate, months=months, days=days, locale=locale)
    dateEnd = decodeOneDate(dateEnd, workdate, months=months, days=days, locale=locale, isEndPeriod=True)

    if isinstance(dateStart, tuple): # is a month
        year, month = dateStart
        if year is None:                      # no year info is given, try to calculate
            year = workdate.year              # default year is this year
            #if month > workdate.month:        # if the starting month is in the future, change to last year
            #    year = year - 1
        endyear = None
        endmonth = None
        if isinstance(dateEnd, datetime.date):# dateend is yet decoded
            endyear = dateEnd.year
            endmonth = dateEnd.month
        elif isinstance(dateEnd, tuple):
            endyear, endmonth = dateEnd
        if endyear:
            if year > endyear:           # if start year (maybe automatic from workdate) is greater than dateEnd.year 
                year = endyear
            if year == endyear:
                if month > endmonth:     # if startmonth is greater than end month in the same year
                    year = year - 1
        dateStart = monthStart(year, month)

    if isinstance(dateEnd, tuple): # is a month
        year, month = dateEnd
        if year is None:                      # no year info is given, try to calculate
            year = workdate.year              # default year is this year
            if month > workdate.month:        # if the end month is in the future, change to last year
                year = year - 1
        if isinstance(dateStart, datetime.date): # if there is a starting date
            if year < dateStart.year:            # if end year (maybe automatic from workdate) is lesser than dateStart.year 
                year = dateStart.year
            if year == dateStart.year:
                if dateStart.month > month:      # if endmonth is lower than start month
                    year = year + 1              # end is in next year
        dateEnd = monthEnd(year, month)
    if dtype == 'DH':
        dateStart = datetime.datetime(dateStart.year, dateStart.month, dateStart.day)
        dateEnd = datetime.datetime(dateEnd.year, dateEnd.month, dateEnd.day)

    if returnDate:
        return (dateStart, dateEnd)

    if dateStart == dateEnd:
        return str(dateStart or '')
    else:
        return '%s;%s' % (dateStart or '', dateEnd or '')

def monthStart(year=None, month=None, date=None):
    """Return datetime.date of the first day of the month.
    If ``date`` is given, then ``year`` and ``month`` are readed from date.
    
    :param year: The year you specify
    :param month: The month you specify
    :param date: TODO"""
    if date:
        year = date.year
        month = date.month
    return datetime.date(year, month, 1)
    
def monthEnd(year=None, month=None, date=None):
    """Return datetime.date of the last day of the month.
    If ``date`` is given, then ``year`` and ``month`` are readed from date.
    
    :param year: The year you specify
    :param month: The month you specify
    :param date: TODO"""
    if date:
        year = date.year
        month = date.month
    if month == 12:
        month = 1
        year = year + 1
    else:
        month = month + 1
    return datetime.date(year, month, 1) - datetime.timedelta(1)
    
def dateLastYear(d):
    """TODO
    
    :param d: the date"""
    if not d: return
    if d.month == 2 and d.day == 29:
        result = datetime.date(d.year - 1, 2, 28)
    elif d.month == 2 and d.day == 28 and calendar.isleap(d.year - 1):
        result = datetime.date(d.year - 1, 2, 29)
    else:
        result = datetime.date(d.year - 1, d.month, d.day)
    return result
    
def dayIterator(period, wkdlist=None, locale=None, workdate=None, asDate=True):
    """TODO
    
    :param period: TODO
    :param wkdlist: TODO
    :param locale: the current locale (e.g: en, en_us, it)
    :param workdate: the :ref:`workdate`
    :param asDate: boolean. TODO"""
    dstart, dstop = decodeDatePeriod(period, returnDate=True, locale=locale, workdate=workdate)
    itr = rrule.rrule(rrule.DAILY, dtstart=dstart, until=dstop, byweekday=wkdlist)
    for d in itr:
        if asDate:
            yield d.date()
        else:
            yield d
            
def toTime(t):
    """Convert a time, datetime or a string (``HH:MM:SS`` or ``HH:MM``) to a time.
    
    :param t: the time to convert"""
    if isinstance(t, datetime.datetime):
        return t.time()
    elif isinstance(t, datetime.time):
        return t
    elif isinstance(t, basestring):
        try:
            return datetime.time(*map(int, t.split(':')))
        except ValueError:
            raise ValueError, "toTime(%s) unrecognized string format" % repr(t)
    else:
        raise ValueError, "toTime(%s) accepts only times, datetimes or strings" % repr(t)

def toDate(date_or_datetime):
    """Convert a date or datetime to a date. Return it
    
    :param date_or_datetime: the date or datetime to convert in a date"""
    if isinstance(date_or_datetime, datetime.datetime):
        return date_or_datetime.date()
    elif isinstance(date_or_datetime, datetime.date):
        return date_or_datetime
    else:
        raise ValueError, "toDate(%s) accepts only dates or datetimes" % repr(date_or_datetime)

def dateRange(dstart, dstop):
    """Return an iterator over a range of dates.
    
    It works like the range() builtin, so it will return ``[dstart,dstart+1,...,dstop-1]``
    
    :param dstart: the start date
    :param dstop: the end date
    
    >>> a = datetime.date(year=2010,month=10,day=8)
    >>> b = datetime.date(year=2010,month=10,day=12)
    >>> for date in dateRange(a,b):
    ...     print date
    ... 
    2010-10-08
    2010-10-09
    2010-10-10
    2010-10-11"""
    dt = dstart
    while dt < dstop:
        yield dt
        dt = dt + datetime.timedelta(days=1)
        
def time_to_minutes(t):
    """Return the total minutes from midnight to the given
    datetime.datetime object
    
    :param t: the datetime.datetime object
    
    >>> from gnr.core.gnrdate import time_to_minutes as t
    >>> import datetime
    >>> now = datetime.datetime(2011, 10, 8, 15, 26, 32)
    >>> t(now)
    926"""
    return t.hour * 60 + t.minute

def minutes_to_time(mins):
    """Returns a datetime.time given the number of minutes since midnight
    
    :param mins: int - number of minutes
    
    >>> minutes_to_time(480)
    datetime.time(8, 0)"""
    hours = mins / 60
    mins = mins % 60
    return datetime.time(hours, mins)

class TimeInterval(object):
    """A span of time (start, end).
    
    You can create TimeIntervals from ``datetime.time`` objects or strings:
    
    >>> from datetime import time
    >>> TimeInterval(time(8,30),time(10,30))
    TimeInterval('8:30-10:30')
    >>> TimeInterval('8:30-10:30')
    TimeInterval('8:30-10:30')
    >>> start = time(8,30)
    >>> stop = time(10,30)
    >>> tup = (start,stop)
    >>> TimeInterval(start,stop) == TimeInterval( tup )
    True
    >>> TimeInterval((start, '10:30'))
    TimeInterval('8:30-10:30')
    
    You can also create them supplying their length and their start or stop time:
    
    >>> TimeInterval(start='8:30',minutes=60)
    TimeInterval('8:30-9:30')
    >>> TimeInterval(stop='9:30',minutes=60)
    TimeInterval('8:30-9:30')
    
    As you can see, str() and repr() are both implemented in a sensible way.
    
    Several operators are available:
    
    ============ ==================================================
      Operator    Meaning
    ============ ==================================================
      a < b       a ends before b starts
      a <= b      a starts before or when b starts
      a > b       b ends before a starts
      a >= b      b starts before or when a ends        
      a == b      a.start == b.start and a.stop == b.stop
      a in b      a overlaps b
    ============ ==================================================
    
    All of these operators accept as their second parameter a TimeInterval or a string
    (or a tuple of datetime.time or strings)
    
    >>> a = TimeInterval('8:30-10:30')
    >>> b = TimeInterval('10:00-12:00')
    >>> a < b
    False
    >>> a <= b
    True
    >>> a == b
    False
    >>> a == a
    True
    >>> a in b
    True"""
    def __init__(self, start=None, stop=None, minutes=None):
        if minutes:
            if not stop:
                stop = minutes_to_time(time_to_minutes(toTime(start)) + minutes)
            elif not start:
                start = minutes_to_time(time_to_minutes(toTime(stop)) - minutes)
            else:
                raise ValueError, "TimeInterval() constructor: please specify either 'start' or 'stop' when specifying 'minutes'"
        if not stop:
            if isinstance(start, TimeInterval):
                other = start
                start = other.start
                stop = other.stop
            elif isinstance(start, basestring):
                (start, sep, stop) = start.partition('-')
            else:
                start, stop = start
        self.start = toTime(start)
        self.stop = toTime(stop)
        if self.start >= self.stop:
            raise ValueError, "TimeInterval(start=%s,stop=%s): start must be earlier than stop" % (
            repr(start), repr(stop))

    def __str__(self):
        return "%d:%02d-%d:%02d" % (self.start.hour, self.start.minute, self.stop.hour, self.stop.minute)

    def __repr__(self):
        return "TimeInterval(%s)" % repr(str(self))

    def __eq__(self, other):
        if not isinstance(other, TimeInterval):
            try:
                other = TimeInterval(other)
            except ValueError:
                return NotImplemented
        return (self.start == other.start) and (self.stop == other.stop)

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        """Test if 'self' ends earlier than 'other' starts.
        
        This is, test the following condition::
        
            [self]
                [other]"""
        if not isinstance(other, TimeInterval):
            try:
                other = TimeInterval(other)
            except ValueError:
                return NotImplemented
        return self.stop < other.start

    def __le__(self, other):
        """Test if 'self' starts earlier than or when 'other' starts *and* 'self' ends earlier than or when 'other' ends.
        
        This is, test the following condition::
        
            [self]
                [other]"""
        if not isinstance(other, TimeInterval):
            try:
                other = TimeInterval(other)
            except ValueError:
                return NotImplemented
        return (self.start <= other.start) and (self.stop <= other.stop)

    @staticmethod
    def cmp(one, other):
        """Compare two TimeIntervals
        
        It guarantees total order (while the other TimeInterval's comparison operators do not)"""
        if not isinstance(one, TimeInterval):
            one = TimeInterval(one)
        if not isinstance(other, TimeInterval):
            other = TimeInterval(other)
        return cmp(one.start, other.start) and cmp(one.stop, other.stop)
        
    @staticmethod
    def sorted(iterable):
        """Sort TimeIntervals.
        
        Guarantees total order.
        
        >>> ti = TimeInterval('9:00-10:00')
        >>> tp = TimePeriod('8:00-12:00')
        >>> tp.remove(ti)
        >>> tp
        TimePeriod('8:00-9:00, 10:00-12:00')
        >>> lst = [ti] + tp.intervals
        >>> TimeInterval.sorted(lst)
        [TimeInterval('8:00-9:00'), TimeInterval('9:00-10:00'), TimeInterval('10:00-12:00')]
        """
        return sorted(iterable, cmp=TimeInterval.cmp)


    def __contains__(self, other):
        """Test if 'other' overlaps with us."""
        if not isinstance(other, TimeInterval):
            try:
                other = TimeInterval(other)
            except ValueError:
                return NotImplemented
        return (self.start <= other.stop) and (other.start <= self.stop)

    NO_OVERLAP = 0
    FULLY_CONTAINS = -1
    FULLY_CONTAINED = 1
    COVER_LEFT = -2
    COVER_RIGHT = 2

    def overlaps(self, other):
        """Checks if *other* attribute overlaps with this interval
        
        Returns a constant describing the relationship between ``self`` and ``other``:
        TimeInterval.xxx where xxx is ``NO_OVERLAP``, ``FULLY_CONTAINED``, ``FULLY_CONTAINS``, 
        ``COVER_RIGHT`` or ``COVER_LEFT``
        
        :param other: a TimeInterval or a string represting it"""
        if not isinstance(other, TimeInterval):
            other = TimeInterval(other)
        if self < other or self > other:
            return TimeInterval.NO_OVERLAP

        if (self.start <= other.start):
            if self.stop < other.stop:
                return TimeInterval.COVER_LEFT
            else:
                return TimeInterval.FULLY_CONTAINS
        else:
            if self.stop > other.stop:
                return TimeInterval.COVER_RIGHT
            else:
                return TimeInterval.FULLY_CONTAINED

    @property
    def minutes(self):
        """The duration of this TimeInterval in minutes from the start"""
        return (self.stop.hour * 60 + self.stop.minute) - (self.start.hour * 60 + self.start.minute)

    @minutes.setter
    def minutes(self, value):
        mins = self.start.hour * 60 + self.start.minute + value
        hours = mins / 60
        mins = mins % 60
        self.stop = datetime.time(hours, mins)

class TimePeriod(object):
    """A non-overlapping set of TimeIntervals.
    
    You can create a TimePeriod by calling the constructor with:
    
        - zero or more TimeIntervals, or their string representations;
        - a comma separated string of TimeInterval's string representations.
        
    You can add or remove intervals to a TimePeriod.

    >>> p = TimePeriod('8:00-12:00','16:00-20:00')
    >>> for i in ('8:00-9:00','9:30-10:00','10:00-11:30','16:00-16:30','17:00-18:00','18:00-19:00','19:00-20:00'): p.remove(i)
    >>> str(p)
    '9:00-9:30, 11:30-12:00, 16:30-17:00'
    
    If you attach custom attributes to your TimeIntervals (or if you derive your own subclasses), they are preserved when
    intervals are sliced:
    
    >>> iv1 = TimeInterval('8:00-12:00')
    >>> iv1.name = 'morning'
    >>> iv2 = TimeInterval('16:00-20:00')
    >>> iv2.name = 'afternoon'
    >>> p = TimePeriod(iv1,iv2)
    >>> for i in ('8:00-9:00','9:30-10:00','10:00-11:30','16:00-16:30','17:00-18:00','18:00-19:00','19:00-20:00'): p.remove(i)
    >>> str(p)
    '9:00-9:30, 11:30-12:00, 16:30-17:00'
    >>> [i.name for i in p.intervals]
    ['morning', 'morning', 'afternoon']
    
    TimePeriod also supports ``len()``, ``iter()`` and getitem operations"""

    def __init__(self, *intervals):
        self._intervals = []
        if len(intervals) == 1:
            iv = intervals[0]
            if isinstance(iv, basestring):
                intervals = [s.strip() for s in iv.split(',')]
        for interval in intervals:
            self.add(interval)
        #map(self.add, intervals)

    def add(self, item):
        """Add the new TimeInterval or a TimePeriod.
        
        If it overlaps with any existing interval in this TimePeriod, they'll be merged
        
        :param item: TimeInterval or TimePeriod or string"""
        if isinstance(item, TimePeriod):
            intervals = item.intervals
        else:
            intervals = [item]
        for interval in intervals:
            if not isinstance(interval, TimeInterval):
                new = TimeInterval(interval)
            else:
                new = interval
            left = bisect.bisect_left(self._intervals, new)
            merged = new
            right = left
            while right < len(self._intervals):
                existing = self._intervals[right]
                if merged in existing:
                    merged.start = min(merged.start, existing.start)
                    merged.stop = max(merged.stop, existing.stop)
                    right += 1
                else:
                    break
            self._intervals[left:right] = [merged]

    def remove(self, item):
        """Remove a TimeInterval or a TimePeriod.
        
        Overlapping intervals will be adjusted
        
        :param item: TimeInterval or TimePeriod"""
        if isinstance(item, TimePeriod):
            intervals = item.intervals
        else:
            intervals = [item]
        for interval in intervals:
            if not isinstance(interval, TimeInterval):
                removed = TimeInterval(interval)
            else:
                removed = interval
            left = bisect.bisect_left(self._intervals, removed)
            right = left
            while right < len(self._intervals):
                existing = self._intervals[right]
                o = removed.overlaps(existing)
                if (o == TimeInterval.FULLY_CONTAINS):
                    del self._intervals[right]
                elif o == TimeInterval.FULLY_CONTAINED:
                    if removed.start == existing.start:
                        existing.start = removed.stop
                        right += 1
                    elif removed.stop == existing.stop:
                        existing.stop = removed.start
                        right += 1
                    else:
                        second_half = copy.copy(existing)
                        existing.stop = removed.start
                        second_half.start = removed.stop
                        self._intervals.insert(right + 1, second_half)
                        right += 2
                elif o == TimeInterval.COVER_LEFT:
                    existing.start = removed.stop
                    right += 1
                elif o == TimeInterval.COVER_RIGHT:
                    existing.stop = removed.start
                    right += 1
                else:
                    break # NO_OVERLAP, we're done

    def __str__(self):
        return ", ".join(map(str, self._intervals))

    def __repr__(self):
        return "TimePeriod(%s)" % repr(str(self))

    def __len__(self):
        return len(self._intervals)

    def __getitem__(self, key):
        return self._intervals[key]

    def __eq__(self, other):
        """Check if a TimePeriod is equal to another."""
        if not isinstance(other, TimePeriod):
            other = TimePeriod(other)
        return self._intervals == other.intervals

    @property
    def intervals(self):
        """Returns the intervals in this TimePeriod"""
        return copy.copy(self._intervals) # make a shallow copy, so they can't mess with the ordering of intervals

def seconds_to_text(seconds):
    """Convert number of seconds to a string

    >>> print seconds_to_text(0)
    0s
    >>> print seconds_to_text(10)
    10s
    >>> print seconds_to_text(60)
    1m
    >>> print seconds_to_text(3600)
    1h
    >>> print seconds_to_text(3672)
    1h 1m 12s"""
    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    parts = []
    for value, unit in ((hours,'h'),(minutes,'m'),(seconds,'s')):
        if value != 0:
            parts.append("%d%s" % (value, unit))
    if parts:
        return " ".join(parts)
    else:
        return "0s"
        
if __name__ == '__main__':
    import doctest

    doctest.testmod()
    