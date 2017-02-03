#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Saverio Porcari on 2013-04-06.
#  Copyright (c) 2013 Softwell. All rights reserved.

import os
from gnr.core.gnrbaseservice import GnrBaseService
from gnr.core.gnrbag import Bag
from datetime import datetime
from gnr.core.gnrstring import toText

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    import pandas as pd 
    import numpy as np
except:
    pd = False
    np = False

class GnrDataFrame(object):
    """docstring for GnrDataFrame"""
    def __init__(self,service,filepath=None,tbl=None,where=None,columns=None,**kwargs):
        self.service = service
        if filepath:
            self.from_pickle(filepath)
        else:
            self.tbl = tbl
            self.tblobj = self.service.site.db.table(tbl)
            selection = self.tblobj.query(where=where,columns=columns or self.defaultColumns(),
                                                addPkeyColumn=False,
                                                **kwargs).selection()
            self.colAttrs = selection.colAttrs
            self.columns = selection.columns
            self.dataframe = pd.DataFrame(self.convertData(selection.data))

    def updateInfo(self,info):
        self.columns = info.keys()
        for k in self.colAttrs.keys():
            if k not in self.columns:
                self.colAttrs.pop(k)
        for k,v in info.items():
            d = self.colAttrs.setdefault(k,{})
            d['label'] = v['label']
            d['dataType'] = v['dataType'] 
            d['calc_series'] = v['calc_series']

    def convertData(self,data):
        decimalCols = [k for k,v in self.colAttrs.items() if v['dataType'] == 'N']
        dateCols = [k for k,v in self.colAttrs.items() if v['dataType'] == 'D']

        for r in data:
            c = dict(r)
            for col in decimalCols:
                v = c[col]
                if v is not None:
                    c[col] = float(v)
            for col in dateCols:
                v = c[col]
                if v is not None:
                    c[col] = datetime(v.year,v.month,v.day)
            yield c

    def getInfo(self):
        df = self.dataframe
        result = Bag()
        for c in self.columns:
            row = Bag()
            attr = self.colAttrs.get(c,{})
            row['fieldname'] = c
            row['dataType'] = attr.get('dataType')
            row['label'] = attr.get('label')
            row['element_count'] = len(df[c].unique())
            result.setItem(c,row)
        return result

    def pivotTableGrid(self,index=None,values=None,columns=None,aggr=None):
        struct = Bag()
        r = Bag()
        
        store = Bag()
        result = Bag(dict(store=store,struct=struct))
        pt = self.dataframe.pivot_table(index=index,values=values, columns=columns)
        values = values or list(pt.columns)
        struct['view_0.rows_0'] = r
        for i,col in enumerate(index+values):
            cattr = self.colAttrs[col]
            cattr['print_width'] = cattr['print_width'] or 10
            r.setItem('cell_%s' %i,None,field=col,
                            name=cattr.get('label'),
                            dtype=cattr.get('dataType'),
                            width='%(print_width)sem' %cattr,
                            format=cattr.get('format'))
        for k,r in enumerate(pt.to_records()):
            rec = {}
            for col in index:
                rec[col] = toText(r[col])
            for col in values:
                rec[col] = float(r[col])
            store.setItem('r_%s' %k,None,**rec)
        return result

    def defaultColumns(self):
        columns = []
        for f in self.tblobj.columns.keys() + self.tblobj.model.virtual_columns.keys():
            if self.tblobj.column(f).attributes.get('stats'):
                columns.append('$%s' %f)
        return ','.join(columns)


    def to_pickle(self,path):
        path = self.service.site.getStaticPath(path,autocreate=True)
        self.dataframe.to_pickle(os.path.join(path,'dataframe.pik'))
        with open(os.path.join(path,'meta.pik'), 'w') as storagefile:
            self.dump(storagefile)

    def from_pickle(self,path):
        path = self.service.site.getStaticPath(path)
        self.dataframe = pd.read_pickle(os.path.join(path,'dataframe.pik'))
        with open(os.path.join(path,'meta.pik'), 'r') as storagefile:
            self.load(storagefile)


    def dump(self,storagefile):
        pickle.dump(self.colAttrs,storagefile)
        pickle.dump(self.columns,storagefile)
        pickle.dump(self.tblobj.fullname,storagefile)

    def load(self,storagefile):
        self.colAttrs = pickle.load(storagefile)
        self.columns = pickle.load(storagefile)
        self.tbl = pickle.load(storagefile)
        self.tblobj = self.service.site.db.table(self.tbl)

class Main(GnrBaseService):
    def __init__(self, parent=None):
        self.site = parent

    def gnrDataFrame(self,tbl=None,filepath=None,**kwargs):
        return GnrDataFrame(self,tbl=tbl,filepath=filepath,**kwargs) 

    def dataframeInfo(self,df):
        result = Bag()
        result.setItem('values',Bag(),caption='Values')
        for col in df.columns:
            colelem = df[col]
            if pd.types.common.is_numeric_dtype(colelem):
                result.setItem('values.%s' %col,None,caption=col)
            elif pd.types.common.is_datetimelike(colelem): #alternativa pd.types.common.is_datetime64_dtype(colelem):
                continue
                #years = Bag()
                #result.setItem(col,years,caption=col)
                #for y in colelem.dt.year.unique():
                #    months = Bag()
                #    result.setItem(str(y),months,caption=y)
                #    for m in colelem.dt.to_period('m').unique():
                #        months.setItem(str(m),None,caption=str(m))
            else:
                for i,e in enumerate(colelem.unique()):
                    if e:
                        result.setItem('%s.r_%s' %(col,i),None,caption=e)
        return result




