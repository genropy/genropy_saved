#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Saverio Porcari on 2013-04-06.
#  Copyright (c) 2013 Softwell. All rights reserved.

import os
from gnr.core.gnrbag import Bag
from datetime import datetime
from gnr.core.gnrstring import toText
from functools import wraps
from collections import OrderedDict


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

def remember(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        res = f(self,*args, **kwargs)
        if 'db' in kwargs:
            kwargs['db'] = None
        self.steps.append({'name':f.func_name,'args':args,'kwargs':kwargs})
        return res
    return wrapper


class GnrPandas(object):

    def __init__(self,path=None):
        self.defaultpath = path
        self.dataframes = OrderedDict()
        self.steps = []

    def __enter__(self):
        if self.defaultpath:
            if os.path.exists(self.defaultpath):
                self.load()
        return self

    def __exit__(self,type, value, tb):
        self.save()

    @remember
    def dataframeFromDb(self,dfname=None,db=None,tablename=None,columns=None,where=None,**kwargs):
        self.dataframes[dfname] = GnrDataframe(dfname)
        self.dataframes[dfname].dataframeFromDb(db=db,tablename=tablename,columns=columns,where=where,**kwargs)

    def save(self,path=None):
        path = path or self.defaultpath
        if not os.path.exists(path):
            os.makedirs(path)
        with open(os.path.join(path,'meta.pik'), 'wb') as storagefile:
            pickle.dump(self.steps,storagefile)
            pf = OrderedDict()
            for dfname,gnrdf in self.dataframes.items():
                pf[dfname] = os.path.join(path,dfname)
                gnrdf.to_pickle(path)
            pickle.dump(pf,storagefile)

    def load(self,path=None):
        path = path or self.defaultpath
        with open(os.path.join(path,'meta.pik'), 'rb') as storagefile:
            self.steps = pickle.load(storagefile)
            self.dataframes = pickle.load(storagefile)



    def __getitem__(self,dfname):
        df = self.dataframes[dfname]
        if isinstance(df,basestring):
            path = df
            df = GnrDataframe(dfname)
            df.from_pickle(path)
            self.dataframes[dfname] = df
        return df

class GnrDataframe(object):
    """docstring for GnrDataFrame"""
    def __init__(self,dfname):
        self.dfname = dfname
        self.steps = []

    @remember
    def dataframeFromDb(self,db=None,tablename=None,columns=None,where=None,**kwargs):
        tblobj = db.table(tablename)
        selection = tblobj.query(where=where,columns=columns or self.defaultColumns(tblobj),
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

    def defaultColumns(self,tblobj):
        columns = []
        for f in tblobj.columns.keys() + tblobj.model.virtual_columns.keys():
            if tblobj.column(f).attributes.get('stats'):
                columns.append('$%s' %f)
        return ','.join(columns)

    def to_pickle(self,path):
        folder = os.path.join(path,self.dfname)
        if not os.path.exists(folder):
            os.makedirs(folder)
        self.dataframe.to_pickle(os.path.join(folder,'dataframe.pik'))
        with open(os.path.join(folder,'meta.pik'), 'wb') as storagefile:
            self.dump(storagefile)

    def from_pickle(self,path):
        self.dataframe = pd.read_pickle(os.path.join(path,'dataframe.pik'))
        with open(os.path.join(path,'meta.pik'), 'rb') as storagefile:
            self.load(storagefile)

    def dump(self,storagefile):
        pickle.dump(self.steps,storagefile)
        pickle.dump(self.colAttrs,storagefile)
        pickle.dump(self.columns,storagefile)

    def load(self,storagefile):
        self.steps = pickle.load(storagefile)
        self.colAttrs = pickle.load(storagefile)
        self.columns = pickle.load(storagefile)
