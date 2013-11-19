#!/usr/bin/env python
# encoding: utf-8
"""
utilsFM.py

Created by Jeff Edwards for Softwell on 2013-11-18.
Copyright (c) 2013 Softwell Pty Ltd. All rights reserved.
"""


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


