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
from gnr.core.gnrdecorator import timer_call


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

from gnr.web.gnrasync import SharedObject



class PandasSharedObject(SharedObject):
    """docstring for TestSHaredObject"""
    __safe__ = True

    def onInit(self,**kwargs):
        if self.autoLoad:
            self.load()
        if 'commands' not in self.data:
            self.data['commands'] = Bag()
        self._data.subscribe('commandslog', any=self._on_command_trigger)
        

    def _on_command_trigger(self, node=None, ind=None, evt=None, pathlist=None,reason=None, **kwargs):
        if evt=='ins':
            print 'command',node,kwargs
        #self.changes=True
        #if reason=='autocreate':
        #    return
        #plist = pathlist[1:]
        #if evt=='ins' or evt=='del':
        #    plist = plist+[node.label]
        #path = '.'.join(plist)
        #data = Bag(dict(value=node.value,attr=node.attr,path=path,shared_id=self.shared_id,evt=evt))
        #from_page_id = reason
        #self.broadcast(command='som.sharedObjectChange',data=data,from_page_id=from_page_id)

    @property
    def commands(self):
        return self.data['commands']

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
        self.dataframes = {}
        self.steps = []

    def __enter__(self):
        if self.defaultpath:
            if os.path.exists(self.defaultpath):
                self.load()
        return self

    def __exit__(self,type, value, tb):
        self.save()

    @remember
    def dataframeFromDb(self,dfname=None,db=None,tablename=None,
                        columns=None,where=None,colInfo=None,**kwargs):
        gnrdf =  GnrDbDataframe(dfname,db=db)
        self.dataframes[dfname] = gnrdf
        gnrdf.query(tablename=tablename,columns=columns,where=where,**kwargs)
        if colInfo:
            gnrdf.setColInfo(colInfo)
        return gnrdf


    @timer_call()
    def save(self,path=None):
        path = path or self.defaultpath
        if not os.path.exists(path):
            os.makedirs(path)
        with open(os.path.join(path,'meta.pik'), 'wb') as storagefile:
            pickle.dump(self.steps,storagefile)
            pf = {}
            for dfname,gnrdf in self.dataframes.items():
                pf[dfname] = os.path.join(path,dfname)
                gnrdf.to_pickle(path)
            pickle.dump(pf,storagefile)

    @timer_call()
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
    base_pickle_attr = ['dfname','steps','colInfo']
    custom_pickle_attr = []

    @property
    def pickle_attr(self):
        return self.base_pickle_attr+self.custom_pickle_attr

    def __init__(self,dfname):
        self.dfname = dfname
        self.steps = []
        self.colInfo = {}


    def renameColumns(self,**kwargs):
        df = self.dataframe
        df.columns = [kwargs[k] if k in kwargs else k for k in df.columns]

    #def updateInfo(self,info):
    #    self.dbcolumns = info.keys()
    #    for k in self.colAttrs.keys():
    #        if k not in self.dbcolumns:
    #            self.colAttrs.pop(k)
    #    for k,v in info.items():
    #        d = self.colAttrs.setdefault(k,{})
    #        d['label'] = v['label']
    #        d['dataType'] = v['dataType'] 
    #        d['calc_series'] = v['calc_series']
    
    def columnInfo(self,colname):
        pass
   
    def getInfo(self):
        df = self.dataframe
        colInfo = self.colInfo
        result = Bag()
        for c in self.dataframe.columns:
            row = Bag()
            attr = colInfo.get(c,{})
            row['fieldname'] = c
            #row['dataType'] = attr.get('dtype')
            row['name'] = attr.get('name')
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
            cattr = self.colInfo[col]
            cattr['print_width'] = cattr.get('print_width') or 10
            r.setItem('cell_%s' %i,None,field=col,
                            name=cattr.get('name'),
                            dtype=cattr.get('dtype'),
                            width='%(print_width)sem' %cattr,
                            format=cattr.get('format'))
        k = 0
        for index_vals,sel_vals in pt.iterrows():
            rec = {}
            if isinstance(index_vals,tuple):
                for i,col in enumerate(index):
                    rec[col] = index_vals[i]
            else:
                rec[index[0]] = index_vals
            for col in values:
                rec[col] = float(sel_vals[col])
            store.setItem('r_%s' %k,None,**rec)
            k+=1
        return result

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
        for k in self.pickle_attr:
            pickle.dump(getattr(self,k),storagefile)


    def load(self,storagefile):
        for k in self.pickle_attr:
            setattr(self,k,pickle.load(storagefile))
        #self.steps = pickle.load(storagefile)
        #self.colAttrs = pickle.load(storagefile)
        #self.dbcolumns = pickle.load(storagefile)

class GnrDbDataframe(GnrDataframe):
    custom_pickle_attr = ['dbColAttrs','dbcolumns']

    def __init__(self,dfname,db=None,**kwargs):
        super(GnrDbDataframe, self).__init__(dfname)
        self.db = db

    @timer_call()
    @remember
    def query(self,tablename=None,columns=None,where=None,**kwargs):
        tblobj = self.db.table(tablename)
        selection = tblobj.query(where=where,columns=columns or self.defaultColumns(tblobj),
                                                addPkeyColumn=False,
                                                **kwargs).selection()
        self.dbColAttrs = selection.colAttrs
        self.dbcolumns = selection.columns
        for k,v in self.dbColAttrs.items():
            self.colInfo[k] = dict(name=v.get('label'),name_short=v.get('name_short'),
                                  width=v.get('print_width'),format=v.get('format'),
                                  dtype= v.get('dataType'))
        self.dataframe = pd.DataFrame(self.convertData(selection.data))
        return self.dataframe

    @remember
    def setColInfo(self,colInfo):
        for k,v in colInfo.items():
            self.colInfo[k].update(v)

    def convertData(self,data):
        decimalCols = [k for k,v in self.dbColAttrs.items() if v['dataType'] in ('N','R')]
        dateCols = [k for k,v in self.dbColAttrs.items() if v['dataType'] == 'D']
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


    def defaultColumns(self,tblobj):
        columns = []
        allcols = tblobj.columns.keys() + tblobj.model.virtual_columns.keys()
        for f in allcols:
            if tblobj.column(f).attributes.get('stats'):
                columns.append('$%s' %f)
        columns = columns or tblobj.columns.keys()
        return ','.join(columns) 


        
