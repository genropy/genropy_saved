# -*- coding: UTF-8 -*-
from gnr.core import gnrdate
import datetime

def test_relativeDay():
    workdate = datetime.date(2008,4,25)
    res = gnrdate.decodeDatePeriod("today", workdate=workdate)
    assert res == '2008-04-25'
    res = gnrdate.decodeDatePeriod("yesterday", workdate=workdate)
    assert res == '2008-04-24'
    res = gnrdate.decodeDatePeriod("tomorrow", workdate=workdate)
    assert res == '2008-04-26'

    workdate = datetime.date(2008,4,1)
    res = gnrdate.decodeDatePeriod("yesterday", workdate=workdate)
    assert res == '2008-03-31'

    workdate = datetime.date(2008,4,30)
    res = gnrdate.decodeDatePeriod("tomorrow", workdate=workdate)
    assert res == '2008-05-01'

def test_relativeDayLocal():
    workdate = datetime.date(2008,4,25)
    res = gnrdate.decodeDatePeriod("oggi", workdate=workdate, locale='it')
    assert res == '2008-04-25'
    res = gnrdate.decodeDatePeriod("ieri", workdate=workdate, locale='it')
    assert res == '2008-04-24'
    res = gnrdate.decodeDatePeriod("domani", workdate=workdate, locale='it')
    assert res == '2008-04-26'

def test_week():
    workdate = datetime.date(2008,4,25)
    res = gnrdate.decodeDatePeriod("this week", workdate=workdate)
    assert res == '2008-04-21;2008-04-27'

    res = gnrdate.decodeDatePeriod("next week", workdate=workdate)
    assert res == '2008-04-28;2008-05-04'

    res = gnrdate.decodeDatePeriod("last week", workdate=workdate)
    assert res == '2008-04-14;2008-04-20'

def test_month():
    workdate = datetime.date(2008,4,25)
    res = gnrdate.decodeDatePeriod("this month", workdate=workdate)
    assert res == '2008-04-01;2008-04-30'

    res = gnrdate.decodeDatePeriod("month", workdate=workdate)
    assert res == '2008-04-01;2008-04-30'

    res = gnrdate.decodeDatePeriod("next month", workdate=workdate)
    assert res == '2008-05-01;2008-05-31'

    res = gnrdate.decodeDatePeriod("last month", workdate=workdate)
    assert res == '2008-03-01;2008-03-31'

def test_monthLocal():
    workdate = datetime.date(2008,4,25)
    res = gnrdate.decodeDatePeriod("questo mese", workdate=workdate, locale='it')
    assert res == '2008-04-01;2008-04-30'

    res = gnrdate.decodeDatePeriod("mese", workdate=workdate, locale='it')
    assert res == '2008-04-01;2008-04-30'

def test_year():
    workdate = datetime.date(2008,4,25)
    res = gnrdate.decodeDatePeriod("2007", workdate=workdate)
    assert res == '2007-01-01;2007-12-31'

    res = gnrdate.decodeDatePeriod("07", workdate=workdate)
    assert res == '2007-01-01;2007-12-31'

    res = gnrdate.decodeDatePeriod("96", workdate=workdate)
    assert res == '1996-01-01;1996-12-31'

def test_monthName():
    workdate = datetime.date(2008,4,25)
    res = gnrdate.decodeDatePeriod("february", workdate=workdate)
    assert res == '2008-02-01;2008-02-29'

def test_periodTo():
    workdate = datetime.date(2008,4,25)
    res = gnrdate.decodeDatePeriod("to tomorrow", workdate=workdate)
    assert res == ';2008-04-26'
    
    res = gnrdate.decodeDatePeriod("to january", workdate=workdate)
    assert res == ';2008-01-31'

    res = gnrdate.decodeDatePeriod("to april", workdate=workdate)
    assert res == ';2008-04-30'

    res = gnrdate.decodeDatePeriod("to december", workdate=workdate)
    assert res == ';2007-12-31'

    res = gnrdate.decodeDatePeriod("to december 2007", workdate=workdate)
    assert res == ';2007-12-31'
    

def test_periodFrom():
    workdate = datetime.date(2008,4,25)
    res = gnrdate.decodeDatePeriod("from tomorrow + 2", workdate=workdate)
    assert res == '2008-04-28;'
    
    res = gnrdate.decodeDatePeriod("from december 07", workdate=workdate)
    assert res == '2007-12-01;'

    res = gnrdate.decodeDatePeriod("from december", workdate=workdate)
    assert res == '2008-12-01;'

    res = gnrdate.decodeDatePeriod("from february", workdate=workdate)
    assert res == '2008-02-01;'

def test_periodFull():
    workdate = datetime.date(2008,4,25)
    res = gnrdate.decodeDatePeriod("from february to today", workdate=workdate)
    assert res == '2008-02-01;2008-04-25'

    res = gnrdate.decodeDatePeriod("december to today", workdate=workdate)
    assert res == '2007-12-01;2008-04-25'

    res = gnrdate.decodeDatePeriod("from december 06 to march", workdate=workdate)
    assert res == '2006-12-01;2008-03-31'

    res = gnrdate.decodeDatePeriod("from december to march 06", workdate=workdate)
    assert res == '2005-12-01;2006-03-31'

    res = gnrdate.decodeDatePeriod("from december to this month", workdate=workdate)
    assert res == '2007-12-01;2008-04-30'

    res = gnrdate.decodeDatePeriod("between december and this month", workdate=workdate)
    assert res == '2007-12-01;2008-04-30'

    res = gnrdate.decodeDatePeriod("from last week to next month", workdate=workdate)
    assert res == '2008-04-14;2008-05-31'

def test_periodLocal():
    workdate = datetime.date(2008,4,25)
    res = gnrdate.decodeDatePeriod("da dicembre a mar 06", workdate=workdate, locale='it')
    assert res == '2005-12-01;2006-03-31'

    res = gnrdate.decodeDatePeriod("da dicembre a questo mese", workdate=workdate, locale='it')
    assert res == '2007-12-01;2008-04-30'

    res = gnrdate.decodeDatePeriod("da settimana scorsa al mese prossimo", workdate=workdate, locale='it')
    assert res == '2008-04-14;2008-05-31'
    
    res = gnrdate.decodeDatePeriod(u"da dicembre", workdate=workdate, locale='it')
    assert res == '2008-12-01;'

    res = gnrdate.decodeDatePeriod(u"a dicembre", workdate=workdate, locale='it')
    assert res == ';2007-12-31'
    
    res = gnrdate.decodeDatePeriod(u"dal 23-12-07 a aprile", workdate=workdate, locale='it')
    assert res == '2007-12-23;2008-04-30'

def test_weekDay():
    workdate = datetime.date(2008,4,25)
    res = gnrdate.decodeDatePeriod("monday", workdate=workdate)
    assert res == '2008-04-21'

    res = gnrdate.decodeDatePeriod(u"lunedì", workdate=workdate, locale='it')
    assert res == '2008-04-21'

    res = gnrdate.decodeDatePeriod(u"da lunedì a oggi", workdate=workdate, locale='it')
    assert res == '2008-04-21;2008-04-25'

    res = gnrdate.decodeDatePeriod(u"da lunedì a oggi", workdate=workdate, locale='it')
    assert res == '2008-04-21;2008-04-25'

def test_localDate():
    workdate = datetime.date(2008,4,25)
    # res = gnrdate.decodeDatePeriod(u"02 01, 2007", workdate=workdate, locale='en') ### TODO: fails in babel.dates.parse_date
    # assert res == '2007-02-01'

    res = gnrdate.decodeDatePeriod(u"02/01/08", workdate=workdate, locale='en_au')
    assert res == '2008-01-02'

    res = gnrdate.decodeDatePeriod(u"02/01/08", workdate=workdate, locale='it')
    assert res == '2008-01-02'

    res = gnrdate.decodeDatePeriod(u"02/01/2008", workdate=workdate, locale='it')
    assert res == '2008-01-02'

    res = gnrdate.decodeDatePeriod(u"02-01-2008", workdate=workdate, locale='it')
    assert res == '2008-01-02'

    res = gnrdate.decodeDatePeriod(u"02 01 2008", workdate=workdate, locale='it')
    assert res == '2008-01-02'
    
def test_isoDate():
    workdate = datetime.date(2008,4,25)
    res = gnrdate.decodeDatePeriod(u"2008-01-02", workdate=workdate, locale='it')
    assert res == '2008-01-02'

    res = gnrdate.decodeDatePeriod(u"2008-01-02 to 2008-02-02", workdate=workdate)
    assert res == '2008-01-02;2008-02-02'
    

def test_localDateNoSep():
    workdate = datetime.date(2008,4,25)
    res = gnrdate.decodeDatePeriod(u"02012008", workdate=workdate, locale='it')
    assert res == '2008-01-02'

    res = gnrdate.decodeDatePeriod(u"020108", workdate=workdate, locale='it')
    assert res == '2008-01-02'
    
def test_localPeriodNoSep():
    workdate = datetime.date(2008,4,25)
    res = gnrdate.decodeDatePeriod(u"01012008 a 31012008", workdate=workdate, locale='it')
    assert res == '2008-01-01;2008-01-31'

    res = gnrdate.decodeDatePeriod(u"010108 a 310108", workdate=workdate, locale='it')
    assert res == '2008-01-01;2008-01-31'

def test_quarter():
    workdate = datetime.date(2008,4,25)
    res = gnrdate.decodeDatePeriod(u"1st quarter", workdate=workdate, locale='en')
    assert res == '2008-01-01;2008-03-31'

    res = gnrdate.decodeDatePeriod(u"from 1st quarter to 2nd quarter", workdate=workdate, locale='en')
    assert res == '2008-01-01;2008-06-30'

    res = gnrdate.decodeDatePeriod(u"Q1", workdate=workdate, locale='en')
    assert res == '2008-01-01;2008-03-31'

    res = gnrdate.decodeDatePeriod(u"from Q1 to Q2", workdate=workdate, locale='en')
    assert res == '2008-01-01;2008-06-30'

    res = gnrdate.decodeDatePeriod(u"1o trimestre", workdate=workdate, locale='it')
    assert res == '2008-01-01;2008-03-31'

    res = gnrdate.decodeDatePeriod(u"dal 1o trimestre al 2o trimestre", workdate=workdate, locale='it')
    assert res == '2008-01-01;2008-06-30'

    res = gnrdate.decodeDatePeriod(u"T1", workdate=workdate, locale='it')
    assert res == '2008-01-01;2008-03-31'

    res = gnrdate.decodeDatePeriod(u"da T1 a T2", workdate=workdate, locale='it')
    assert res == '2008-01-01;2008-06-30'

def test_addToDay():
    workdate = datetime.date(2008,4,25)
    res = gnrdate.decodeDatePeriod(u"today + 1", workdate=workdate)
    assert res == '2008-04-26'
    
    res = gnrdate.decodeDatePeriod(u"today + 6", workdate=workdate)
    assert res == '2008-05-01'
    
    res = gnrdate.decodeDatePeriod(u"tomorrow + 6", workdate=workdate)
    assert res == '2008-05-02'
    
    res = gnrdate.decodeDatePeriod(u"yesterday + 6", workdate=workdate)
    assert res == '2008-04-30'
    
    res = gnrdate.decodeDatePeriod(u"today - 6", workdate=workdate)
    assert res == '2008-04-19'
    
    res = gnrdate.decodeDatePeriod(u"from today - 6 to tomorrow + 2", workdate=workdate)
    assert res == '2008-04-19;2008-04-28'
    
    
def test_addToMonth():
    workdate = datetime.date(2008,4,25)
    res = gnrdate.decodeDatePeriod(u"this month + 1", workdate=workdate)
    assert res == '2008-05-01;2008-05-31'
    
    res = gnrdate.decodeDatePeriod(u"this month - 1", workdate=workdate)
    assert res == '2008-03-01;2008-03-31'
    
    res = gnrdate.decodeDatePeriod(u"from this month - 1 to this month + 1", workdate=workdate)
    assert res == '2008-03-01;2008-05-31'
    
    res = gnrdate.decodeDatePeriod(u"from this month - 6 to this month + 6", workdate=workdate)
    assert res == '2007-10-01;2008-10-31'
    
    res = gnrdate.decodeDatePeriod(u"from this month - 12 to this month + 12", workdate=workdate)
    assert res == '2007-04-01;2009-04-30'


    