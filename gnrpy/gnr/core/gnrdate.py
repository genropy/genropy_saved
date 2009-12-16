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

from gnr.core import gnrlocale
from gnr.core.gnrlocale import DEFAULT_LOCALE
from gnr.core.gnrstring import splitAndStrip, anyWordIn, wordSplit, toText

logger= logging.getLogger('gnr.core.gnrdate')


def yearDecode(datestr):
    "returns the year number as an int from a string of 2 or 4 digits: if 2 digits is given century is added."
    year = None
    datestr = datestr.strip()
    if datestr and datestr.isdigit():
        year = int(datestr)
        if len(datestr) == 2:
            if year < 70:
                year = 2000+year
            else:
                year = 1900+year
    return year

def decodeOneDate(datestr, workdate=None, months=None, days=None, quarters=None, locale=None, isEndPeriod=False):
    """Parse a string representing a date or a period and returns a datetime.date or a tuple (year, month) or None.
       Special keywords like 'today' or the name of a month can be translated in all languages and support synonimous,
       eg. 'this month' or 'month'
       The input string can be:
        - a year: eg. 2007 or 07
        - today, yesterday, tomorrow (can be translated in all languages)
            - can be specified a number of days to add to today: eg. 'today + 3' or 'today - 15'
        - this week, next week, last week (can be translated in all languages)
        - this month, next month, last month (can be translated in all languages )
            - can be specified a number of months to add to current month: eg. 'this month + 3' or 'this month - 24'
        - the name of a quarter: eg. Q1 or 1st quarter
        - the name of a month: eg. april or apr
            - can be specified a year after the month: eg. apr 07 or april 2007
            - returns a tuple (year, month): if year is not specified in datestr, year is returned None
        - the name of a weekday: eg. monday or mon
            - the date returned is the date of the given weekday in this week (relative to workdate)
        - an iso date: eg. 2008-04-28
        - a date formatted according to locale (see babel doc): eg. 4 28, 2008 (en_us) or 28-4-08 (it)
                               various separators are admitted: 28-4-08, 28/4/08, 28 4 08
       @param datestr: the string to be interpreted
       @param workdate: a date of reference for calculate relative periods (eg. tomorrow or this week)
       @param months: names of months according to locale (just for caching)
       @param days: names of weekdays according to locale (just for caching)
       @param quarters: names of quarters according to locale (just for caching)
       @locale: the current locale strig (eg. en, en_us, it)
       @isEndPeriod: if the string represents a period, return the end date (default return the start date)
    """
    def addToDay(datestr, date):
        if '+' in datestr:
            days = int(datestr.split('+')[1].strip())
            return date + datetime.timedelta(days)
        if '-' in datestr:
            days = int(datestr.split('-')[1].strip())
            return date - datetime.timedelta(days)
        return date
    def addToMonth(datestr, date, addmonth=0):
        if '+' in datestr:
            addmonth = int(datestr.split('+')[1].strip())
        if '-' in datestr:
            addmonth = -int(datestr.split('-')[1].strip())
        month = date.month + addmonth
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
                    
        if datestr.isdigit() and len(datestr) in (2,4):                          # a full year
            year = yearDecode(datestr)
            dateStart = datetime.date(year, 1, 1)
            if isEndPeriod: 
                dateEnd = datetime.date(year, 12, 31)
        
        elif anyWordIn(gnrlocale.getDateKeywords('today', locale), datestr) or anyWordIn(gnrlocale.getDateKeywords('today', DEFAULT_LOCALE), datestr):     # today
            dateStart = addToDay(datestr, workdate)
        elif anyWordIn(gnrlocale.getDateKeywords('yesterday', locale), datestr) or anyWordIn(gnrlocale.getDateKeywords('yesterday', DEFAULT_LOCALE), datestr): # yesterday
            dateStart = addToDay(datestr, workdate - datetime.timedelta(1))
        elif anyWordIn(gnrlocale.getDateKeywords('tomorrow', locale), datestr) or anyWordIn(gnrlocale.getDateKeywords('tomorrow', locale), DEFAULT_LOCALE):  # tomorrow
            dateStart = addToDay(datestr, workdate + datetime.timedelta(1))
            
        elif (datestr in gnrlocale.getDateKeywords(('this week', 'next week', 'last week'), locale)) or  (datestr in gnrlocale.getDateKeywords(('this week', 'next week', 'last week'), DEFAULT_LOCALE)): # relative week
            j = workdate.weekday()
            dateStart = workdate - datetime.timedelta(j)
            if (datestr in gnrlocale.getDateKeywords('last week', locale)) or (datestr in gnrlocale.getDateKeywords('last week', DEFAULT_LOCALE)):
                dateStart = dateStart - datetime.timedelta(7)
            elif (datestr in gnrlocale.getDateKeywords('next week', locale)) or (datestr in gnrlocale.getDateKeywords('next week', DEFAULT_LOCALE)):
                dateStart = dateStart + datetime.timedelta(7)
            if isEndPeriod:
                dateEnd = dateStart + datetime.timedelta(6)
        elif anyWordIn(gnrlocale.getDateKeywords(('this month', 'next month', 'last month'), locale), datestr) or anyWordIn(gnrlocale.getDateKeywords(('this month', 'next month', 'last month'), DEFAULT_LOCALE), datestr): # relative month
            if (datestr in gnrlocale.getDateKeywords('last month', locale)) or (datestr in gnrlocale.getDateKeywords('last month', DEFAULT_LOCALE)):
                dateStart = addToMonth(datestr, workdate, -1)
            elif (datestr in gnrlocale.getDateKeywords('next month', locale)) or (datestr in gnrlocale.getDateKeywords('next month', DEFAULT_LOCALE)):
                dateStart = addToMonth(datestr, workdate, 1)
            else:
                dateStart = addToMonth(datestr, workdate)
            if isEndPeriod:
                dateEnd = monthEnd(date=dateStart)
        elif anyWordIn(quarters.keys(), datestr): # quarter
            qt, year = splitAndStrip(datestr, sep=' ', n=1, fixed=2)
            year = yearDecode(year)
            qt = quarters[datestr]
            dateStart = (year, qt*3-2)
            if isEndPeriod:
                dateEnd = (year, qt*3)
        elif anyWordIn(def_quarters.keys(), datestr): # quarter
            qt, year = splitAndStrip(datestr, sep=' ', n=1, fixed=2)
            year = yearDecode(year)
            qt = def_quarters[datestr]
            dateStart = (year, qt*3-2)
            if isEndPeriod:
                dateEnd = (year, qt*3)
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
            date_items= [int(el) for el in wordSplit(datestr)[0:3]]
            dateStart = datetime.date(*[int(el) for el in wordSplit(datestr)[0:3]])
        else:                                                                   # a date in local format
            dateStart = gnrlocale.parselocal(datestr, datetime.date, locale)
        
        if isEndPeriod and dateEnd:
            return dateEnd
        else:
            return dateStart
            
def periodCaption(dateFrom=None, dateTo=None, locale=None):
    localNoPeriod = gnrlocale.getDateKeywords('no period', locale)[0]
    localTo = gnrlocale.getDateKeywords('to', locale)[0]
    localFrom = gnrlocale.getDateKeywords('from', locale)[0]
    textFrom=toText(dateFrom, locale=locale)
    textTo=toText(dateTo, locale=locale)
    if dateFrom and dateTo:
        return '%s %s %s %s' % (localFrom, textFrom, localTo, textTo)
    if dateFrom:
        return '%s %s' % (localFrom, textFrom)
    elif dateTo:
        return '%s %s' % (localTo, textTo)
    else:
        return localNoPeriod
    
    
def decodeDatePeriod(datestr, workdate=None, locale=None, returnDate=False, dtype='D'):
    """Parse a string representing a date or a period and returns a string of one or two dates in iso format separated by ';'
       See doc of decodeOneDate for details on possible formats of a single date.
       The input string can be:
        - two dates separated by ';': eg. 22 4, 2008;28 4, 2008
        - two dates separated by ' to '
        - two dates in form 'from date to date' (can be translated and supports synonimous, eg. 'between date and date')
            - if a period is given as starting date, the start date of period is keep
            - if a period is given as end date, the end date of period is keep
            - if no year is specified, the year is relative to working date, keeping all periods in the past
                  eg. if working date is 2008-04-28, december is interpreted as december 2007
            - if a year is specified for the end date (or period) a relative year is calculated for the starting period
                  eg. from december to march 06: returns '2005-12-01;2006-03-31'
        - a starting date in form 'from date', if date is a period starting date is keep: eg. april returns '2008-04-01;'
        - an end date in form 'to date', if date is a period end date is keep: eg. april returns ';2008-04-30'
        - a single expression representing a period: eg. 2007 returns '2007-01-01;2007-12-31'
        - a single expression representing a single date: eg. today returns '2008-04-28'
    """
    workdate = workdate or datetime.date.today()
    months = gnrlocale.getMonthNames(locale)
    days = gnrlocale.getDayNames(locale)
    datestr = datestr.lower().strip().replace(',',';').replace(':',';')
    exercise = False  # TODO
    
    dateStart = None
    dateEnd = None
    
    localTo = gnrlocale.getDateKeywords('to', locale)
    localFrom = gnrlocale.getDateKeywords('from', locale)
    
    # check if the period is given with two separate date infos
    if ';' in datestr:
        # two dates or keywords separated by ";":   today;today+5
        dateStart, dateEnd = datestr.split(';')
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
            if month > workdate.month:        # if the starting month is in the future, change to last year
                year = year - 1
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
    if dtype=='DH':
        dateStart = datetime.datetime(dateStart.year,dateStart.month,dateStart.day)
        dateEnd = datetime.datetime(dateEnd.year,dateEnd.month,dateEnd.day)

    if returnDate:
        return (dateStart, dateEnd)
        
    if dateStart == dateEnd:
        return str(dateStart or '')
    else:
        return '%s;%s' % (dateStart or '', dateEnd or '')

def monthStart(year=None, month=None, date=None):
    "returns datetime.date of the first day of the month, if date is given year and month are readed from date."
    if date:
        year = date.year
        month = date.month
    return datetime.date(year, month, 1)
        
def monthEnd(year=None, month=None, date=None):
    "returns datetime.date of the first day of the month, if date is given year and month are readed from date."
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
    if not d: return
    if d.month == 2 and d.day==29:
        result = datetime.date(d.year - 1 , 2, 28)
    elif d.month == 2 and d.day==28 and calendar.isleap(d.year - 1):
        result = datetime.date(d.year - 1 , 2, 29)
    else:
        result = datetime.date(d.year - 1 , d.month, d.day)
    return result

if __name__=='__main__':
    workdate = datetime.date(2009,1,12)
    res = decodeDatePeriod(u"10 giugno,30 giugno", workdate=workdate, locale='it')
    print res

    