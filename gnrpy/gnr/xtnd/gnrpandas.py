#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#
#  Created by Saverio Porcari on 2013-04-06.
#  Copyright (c) 2013 Softwell. All rights reserved.

from future import standard_library
standard_library.install_aliases()
from builtins import str
from past.builtins import basestring
#from builtins import object
import os
from gnr.core.gnrbag import Bag
from datetime import datetime
from gnr.core.gnrstring import toText
#from gnr.core.gnrdecorator import timer_call
from collections import defaultdict,OrderedDict
from gnr.core.gnrstring import splitAndStrip

REPORT_INDEX_HTML = """
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
"http://www.w3.org/TR/html4/strict.dtd">
<html lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>%(title)s</title>
<meta name="author" content="Stats %(title)s">
<style type="text/css">    
    @import url("report.css?mtime=%(mtime)s");
</style>
</head>
<body class='reportbody'>
    <h1 class='report_title'>%(title)s</h1>
    <div class='report_summary'>%(summary)s</div>
    <div class='report_link_box'>
        %(report_links)s
    </div>
</body>

</html>
"""

REPORT_HTML = """
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
"http://www.w3.org/TR/html4/strict.dtd">
<html lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>%(title)s</title>
<meta name="author" content="Stats %(title)s">
<style type="text/css">    
    @import url("report.css?mtime=%(mtime)s");
</style>
</head>
<body class='reportbody'>
    <a class='report_index_url' href='%(index_url)s'>Index</a>
    <h1 class='report_title'>%(title)s</h1>
    <div class='report_summary'>%(summary)s</div>
    <div class='report_content'>
        %(content)s
    </div>
</body>

</html>
"""

try:
    import pickle as pickle
except ImportError:
    import pickle

try:
    import pandas as pd 
    pd.options.display.float_format = '{:,.2f}'.format
    import numpy as np
except:
    pd = False
    np = False

AGGFUNCDICT = {'sum':np.sum,'mean':np.mean,'count':len,'min':np.min,'max':np.max}



class GnrPandas(object):
    AGGFUNCDICT = AGGFUNCDICT

    def __init__(self,path=None,language=None,stats_code=None,
                report_folderpath=None,report_folderurl=None,
                report_cssbase=None):
        self.defaultpath = path
        self.dataframes = {}
        self.steps = []
        self.language = language
        self.stats_code = stats_code
        self.publish_info = defaultdict(str)
        self.report_links = {}
        self.report_folderpath = report_folderpath
        self.report_folderurl = report_folderurl
        self.report_cssbase = report_cssbase

    def updatePublishInfo(self,**kwargs):
        self.publish_info.update(kwargs)
        self.buildReportSite()

    def addReportHtml(self,df,pars):
        pars['html'] = df.to_html()
        self.report_links[pars['code']] = pars

    def buildReportSite(self):
        if not self.publish_info['published']:
            return False
        if not os.path.exists(self.report_folderpath):
            os.makedirs(self.report_folderpath)
        li_list = []
        build_ts = datetime.now().microsecond
        index_url = os.path.join(self.report_folderurl,'index.html?_no_cache=%s' %build_ts)
        for k,v in list(self.report_links.items()):
            li_list.append('<li><a href="%(url)s?_no_cache=%(build_ts)s">%(title)s</a></li>' %dict(build_ts=build_ts,
                                                                                title=v['title'],url=os.path.join(self.report_folderurl,'%s.html' %k)))
            with open(os.path.join(self.report_folderpath,'%s.html' %k),'w') as f:
                f.write(REPORT_HTML  %dict(content=v['html'],title=v['title'],
                                            summary=v['summary'] or v['comment'],
                                            index_url=index_url,mtime=build_ts))
        if li_list:
            self.publish_info['report_links'] = ''.join(li_list)
        self.publish_info['mtime'] = build_ts
        html = REPORT_INDEX_HTML %self.publish_info
        with open(os.path.join(self.report_folderpath,'index.html'),'w') as f:
            f.write(html)
        with open(os.path.join(self.report_folderpath,'report.css'),'w') as f:
            f.write(self.report_cssbase)

    def __enter__(self):
        if self.defaultpath:
            if os.path.exists(self.defaultpath):
                self.load()
        return self

    def __exit__(self,type, value, tb):
        self.save()

    def dataframeFromDb(self,dfname=None,db=None,tablename=None,
                        columns=None,where=None,colInfo=None,comment=None,thermocb=None,**kwargs):
        gnrdf =  GnrDbDataframe(dfname,parent=self,db=db,language=self.language,
                                comment=comment,thermocb=thermocb)
        self.dataframes[dfname] = gnrdf
        gnrdf.query(tablename=tablename,columns=columns,where=where,**kwargs)
        if colInfo:
            gnrdf.setColInfo(colInfo)
        return gnrdf

    def registerDataFrame(self,dfname=None,dataframe=None,comment=None):
        gnrdf = GnrDataframe(dfname,parent=self,language=self.language,dataframe=dataframe,comment=comment)
        self.dataframes[dfname] = gnrdf
        return gnrdf.getInfo()

    def save(self,path=None):
        path = path or self.defaultpath
        if not os.path.exists(path):
            os.makedirs(path)
        with open(os.path.join(path,'meta.pik'), 'wb') as storagefile:
            pickle.dump(self.steps,storagefile)
            pf = {}
            for dfname,gnrdf in list(self.dataframes.items()):
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
    base_pickle_attr = ['dfname','steps','colInfo']
    custom_pickle_attr = []

    @property
    def pickle_attr(self):
        return self.base_pickle_attr+self.custom_pickle_attr

    def __init__(self,dfname,parent=None,language=None,comment=None,dataframe=None,thermocb=None,**kwargs):
        self.dfname = dfname
        self.parent = parent
        self.steps = []
        self.colInfo = {}
        self.language = language
        self.comment = comment
        self.thermocb = thermocb
        if dataframe is not None:
            self.dataframe = dataframe


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

    def applyChanges(self,changedDataframeInfo,inplace=None):
        colToDel = dict(self.colInfo)
        df = self.dataframe
        for v in list(changedDataframeInfo.values()):
            cname = v['fieldname']
            formula = v['formula']
            if v['newserie'] and formula:
                newcol = Bag(v)
                newcol.pop('newserie')
                if ' AS ' in formula:
                    from_field,cast = formula.split(' AS ')
                    from_field = from_field.strip()
                    cast = cast.strip()
                    if hasattr(df[from_field],'dt'):
                        df[cname] = df[from_field].dt.to_period(cast)
                else:
                    df.eval('%(fieldname)s = %(formula)s' %v,inplace=True) 
                self.colInfo[cname] = newcol.asDict(ascii=True)
            else:
                self.colInfo[cname].update(v.asDict(ascii=True))
                colToDel.pop(cname)

        for k in list(colToDel.keys()):
            df.drop(k, axis=1, inplace=True)
            self.colInfo.pop(k)
        return self.getInfo()

    
    def columnInfo(self,colname):
        pass
   
    def getInfo(self):
        df = self.dataframe
        colInfo = self.colInfo
        result = Bag()
        for ind in self.dataframe.index.names:
            if ind:
                row = Bag()
                attr = colInfo.get(ind,{})
                row['fieldname'] = ind
                row['datatype'] = 'index'
                #row['dataType'] = attr.get('dtype')
                row['name'] =ind
                result.setItem(ind,row)
        for c in self.dataframe.columns:
            row = Bag()
            cname = '_'.join(c) if isinstance(c,tuple) else c
            attr = colInfo.get(cname,{})
            row['fieldname'] = cname
            row['datatype'] = attr.get('dtype') or df[c].dtype.name
            #row['dataType'] = attr.get('dtype')
            row['name'] = attr.get('name')
            row['element_count'] = len(df[c].unique())
            result.setItem(cname,row)
        return result

    def pivotTableGrid(self,index=None,values=None,columns=None,filters=None,
                        out_xls=None,out_html=None,margins=None):
        funckeys = set()
        values_list =[]
        index_list = []
        cols_list = []
        df = self.filteredDataframe(filters)
        store = Bag()
        if df.empty:
            return df,store
        adict = AGGFUNCDICT

        def nodecb(node,vlist):
            node_attr = node.attr
            field = node_attr.get('field')
            if field and node_attr.get('fn'):
                fn = node_attr['fn'].split('.')
                s = df[field.replace('$','').replace('.','_').replace('@','_')]
                for subfn in fn:
                    s = getattr(s,subfn)
                df[node.label] = s
            vlist.append(node.label)
        if isinstance(index,Bag):
            for index_node in index:
                nodecb(index_node,index_list)
        else:
            index_list = index
        if isinstance(columns,Bag):
            for col_node in columns:
                nodecb(col_node,cols_list)
        else:
            cols_list = columns
        if isinstance(values,Bag):
            values_dict = OrderedDict()
            values_list = []
            for k,v in list(values.items()):
                values_list.append(k)
                aggregators = v['aggregators']
                if not aggregators:
                    values_dict[k] = adict['sum']
                if k not in values_dict:
                    values_dict[k] = [adict[aggkey] for aggkey in aggregators.split(',')] if ',' in aggregators else adict[aggregators]
        else:
            values_list = values
            values = None
        pt = df.pivot_table(index=index_list or None,
                            values=values_list or None, 
                            columns=cols_list or None,aggfunc= values_dict or [np.sum],
                            fill_value=0,margins=margins)
        if out_html:
            self.parent.addReportHtml(pt,out_html)
        values = values or Bag()
        k = 0
        for index_vals,sel_vals in pt.iterrows():
            rec = Bag()
            if isinstance(index_vals,tuple):
                for i,col in enumerate(pt.index.names):
                    rec[col] = str(index_vals[i])
            else:
                rec[pt.index.names[0]] = str(index_vals)
            for c in sel_vals.index:
                if isinstance(c,tuple):
                    ckey = '_'.join([str(z) for z in c]).replace('-','_').replace('.','_').replace(' ','_').replace('__','_')
                    rec.setItem(ckey,float(sel_vals[c]),dtype='R',format='###,###.00',name='<br/>'.join(ckey.split('_')))
                else:
                    rec.setItem(c,float(sel_vals[c]),dtype='R',format='###,###.00',name='<br/>'.join(c.split('_')))
            store.setItem('r_%s' %k,rec)
            k+=1
        
        return pt,store

    def filteredDataframe(self,filters=None):
        if not filters:
            return self.dataframe
        querylist = []
        mylocals = locals()
        for col,values in list(filters.items()):
            if values:
                mapper =  dict([(str(p),p)for p in self.dataframe[col]])
                mylocals['filter_%s'%col] = [mapper[v] for v in values.split(',')]
                querylist.append('%s in @filter_%s' %(col,col))
        if not querylist:
            return self.dataframe
        result = self.dataframe.query(' & '.join(querylist))
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
        super(GnrDbDataframe, self).__init__(dfname,**kwargs)
        self.db = db
        self.dbcolumns  = None

    def translate(self,txt=None):
        return self.db.application.localizer.translate(txt,language=self.language)
        

    def query(self,tablename=None,columns=None,where=None,**kwargs):
        tblobj = self.db.table(tablename)
        self.gnrquery = tblobj.query(where=where,columns=columns or self.defaultColumns(tblobj),
                                                addPkeyColumn=False,
                                                **kwargs)
        cursor = self.gnrquery.cursor()                            
        #selection = tblobj.query(where=where,columns=columns or self.defaultColumns(tblobj),
        #                                        addPkeyColumn=False,
        #                                        **kwargs).selection()
        
        self.dataframe = pd.DataFrame(self.convertData(cursor))
        return self.dataframe

    def setColInfo(self,colInfo):
        for k,v in list(colInfo.items()):
            self.colInfo[k].update(v)

    def convertData(self,cursor):
        thermocursor = cursor
        if self.thermocb:
            thermocursor = self.thermocb(cursor,maxidx=cursor.rowcount,labelfield='record')
        decimalCols = []
        dateCols = []
        textCols = []
        for r in thermocursor:
            c = dict(r)
            if not hasattr(self,'dbColAttrs'):
                self.dbColAttrs = self.gnrquery._prepColAttrs(cursor.index)
                for k,v in list(self.dbColAttrs.items()):
                    self.colInfo[k] = dict(name=self.translate(v.get('label')),
                                        name_short=self.translate(v.get('name_short')),
                                        width=v.get('print_width'),format=v.get('format'),
                                        dtype= v.get('dataType'))
                for k,v in list(self.dbColAttrs.items()):
                    dtype = v['dataType']
                    if dtype in ('N','R'):
                        decimalCols.append(k)
                    elif dtype == 'D':
                        dateCols.append(k)
                    elif dtype in ('A','T','C','X','P'):
                        textCols.append(k)
            for col in decimalCols:
                v = c[col]
                if v is not None:
                    c[col] = float(v)
            for col in dateCols:
                v = c[col]
                if v is not None:
                    c[col] = datetime(v.year,v.month,v.day)
            for col in textCols:
                v = c[col]
                if v is None:
                    c[col] = ''
            yield c


    def defaultColumns(self,tblobj):
        columns = []
        allcols = list(tblobj.columns.keys()) + list(tblobj.model.virtual_columns.keys())
        for f in allcols:
            if tblobj.column(f).attributes.get('stats'):
                columns.append('$%s' %f)
        columns = columns or list(tblobj.columns.keys())
        return ','.join(columns) 

    

    def fieldsSourceBag(self,tblobj):
        result = Bag()
        for col in self.dbcolumns:
            column = tblobj.column(col)
            attr = column.attributes
            stats = attr.get('stats',True)
            dtype = attr.get('dtype')
            caption = attr.get('name_long')
            label = col.replace('$','').replace('.','_').replace('@','_')
            if dtype in ('N','L','I','R'):
                result.setItem(label,Bag(dict(caption=caption or label,dtype=dtype,
                                field=col,stat_type='numeric',agg='sum' if stats is True else stats,
                                pkey=label)))
            else:
                result.setItem(label,Bag(dict(caption=caption or label,
                                field=col,stat_type='index',dtype=dtype,
                                pkey=label)))
        return result

    def configPivotTree(self,tblobj,default_values=None,default_columns=None,default_rows=None):
        result = Bag()
        self.dbcolumns = self.dbcolumns or self.defaultColumns(tblobj).split(',')
        fields = self.fieldsSourceBag(tblobj)
        def extract_defaults(deflist=None,numeric=None):
            res = Bag()
            if not deflist:
                return res
            for f in deflist:
                aggr = None
                if numeric:
                    f = f.split('_')
                    field = '_'.join(f[0:-1])
                    n = fields.getNode(field)
                    aggr = f[-1]
                else:
                    n = fields.getNode(f)
                v = res.getItem(n.label)
                if not v:
                    v = Bag(n.value)
                    res.setItem(n.label,v)
                if aggr:
                    v['aggregators'] = v['aggregators'] or ''
                    v['aggregators'] = '%s,%s' %(v['aggregators'],aggr) if v['aggregators'] else aggr
            return res
        result.setItem('fields',fields,caption='!!Fields')
        result.setItem('rows',extract_defaults(default_rows),caption='!!Rows')
        result.setItem('columns',extract_defaults(default_columns),caption='!!Columns')
        result.setItem('values',extract_defaults(default_values,numeric=True),caption='!!Values')
        return result

