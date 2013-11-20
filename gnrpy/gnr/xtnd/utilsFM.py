#!/usr/bin/env python
# encoding: utf-8
"""
utilsFM.py

Created by Jeff Edwards for Softwell on 2013-11-18.
Copyright (c) 2013 Softwell Pty Ltd. All rights reserved.
"""

from datetime import datetime
import time
from gnr.core.gnrbag import Bag

class FmBagFromXml(object):

    def __init__(self, xmlpath):
        self.result_bag = Bag()
        self.columns=[]
        fmxmlbag = Bag(xmlpath)
        fieldnameBag = fmxmlbag.getItem('FMPXMLRESULT.METADATA')

        data = fmxmlbag.getItem('FMPXMLRESULT.RESULTSET')
        for i, v in enumerate(data.values()):
            rec_bag = Bag()
            for count, f in enumerate(v.values()):
                key = fieldnameBag.getNode('#%i'%count).getAttr('NAME').replace(' ','_')
                value =  f.getItem('DATA')
                rec_bag[key] = value
                if i==0:
                    self.columns.append(key)

            self.result_bag[str(i)] = rec_bag


    def getData(self):
        return self.result_bag

    def getColumns(self):
        return self.columns
    
    def __str__(self):
        return self.result_bag.__str__()

    @staticmethod
    def getIsoDateFromAusDate(austdatestring):
        if austdatestring:
            mylist = austdatestring.split('/')
            if len(mylist)==3:
                return '%s-%s-%s' %(mylist[2],mylist[1].zfill(2),mylist[0].zfill(2))


    @staticmethod
    def getIsoDTSFromAustDTS(austdts): #1/12/2013 23:34:01
        if austdts:
            datepart, timepart = austdts.split(' ')
            if datepart:
                mylist = datepart.split('/')
                if len(mylist)==3:
                    isodatepart = '%s-%s-%s' %(mylist[2],mylist[1].zfill(2),mylist[0].zfill(2))
            if isodatepart and timepart:
                return '%s %s' %(isodatepart,timepart)
            if isodatepart:
                return '%s %s' %(isodatepart,'00:00:00')

    
    @staticmethod
    def getTimeFromString(timestring):
        l = timestring.split(':')
        if not l or len(l) != 3:
            return None
        hours, mins, days = l[0], l[1], l[2]
        return (hours,mins,days)




