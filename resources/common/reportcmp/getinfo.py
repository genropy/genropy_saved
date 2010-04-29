#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" info """
from gnr.core.gnrstring import toJson
from collections import defaultdict
from itertools import imap
from gnr.core.gnrstring import splitAndStrip,toText
from gnr.web.gnrwebpage import BaseComponent

class GetInfoPage(BaseComponent):
    py_requires='reportcmp/getinfo:QuickQueryTool'
    def rootPage(self,*args, **kwargs):
        if 'pagetemplate' in kwargs:
            kwargs.pop('pagetemplate')
        if args:
            method = getattr(self,'getinfo_%s'%args[0],self.getinfo_default)
        else:
            method = self.getinfo_default
        return method(**kwargs)
    
    def getinfo_default(self,*args,**kwargs):
        return 'You need to enter parameters to generate a query . . in the url'
    
    def gi_returnResultFromSelection(self, selection, mode='tabtext', filename='report.xls',**kwargs):
         if mode == 'xls':
             filepath=self.temporaryDocument(filename)
             selection.output(mode, filepath=filepath)
             fileurl=self.temporaryDocumentUrl(filename)
             return '<a href="%s">Download report</a>' % fileurl
         else:
             result = selection.output(mode)
             return result
             
    def getinfo_base(self,mode='tabtext', columns='',group_by='',order_by='',filename='report.xls', **kwargs):
        query = self.qqt_parametricQuery(table=self.maintable, columnsDict=self.columnsDict, columns=columns, 
                                        group_by=group_by, order_by=order_by, addPkeyColumn=False, **kwargs)
        return self.gi_returnResultFromSelection(query.selection(), mode=mode,filename=filename,**kwargs)
            
class QuickQueryTool(object):
    def qqt_prepareConditions(self, table, customColumns=None, **kwargs):
        return self.db.whereTranslator.whereFromDict(table, whereDict=kwargs, customColumns=customColumns)
                             
    def qqt_parametricQuery(self, table, columns='',group_by='',order_by='',
                            having=None, distinct=None, limit=None, columnsDict=None, **kwargs):
        columns_list = splitAndStrip(columns)
        group_list = [c for c in columns_list if not (c.startswith('COUNT(') or  c.startswith('SUM(') or c.startswith('AVG('))]
        if len(columns_list)>len(group_list):
            group_by=splitAndStrip(group_by) or []
            for g in group_list:
                if g and not g in group_by:
                    group_by.append(g)
        group_by=','.join(group_by).strip(',')
        columns = ','.join(columns_list).strip(',')
        wherelist, sqlArgs = self.qqt_prepareConditions(table, customColumns=columnsDict, **kwargs)
        tblobj= self.db.table(table)
        q= tblobj.query(columns=columns,
                       where=' AND '.join(wherelist),
                       group_by=group_by,
                       distinct=distinct,
                       limit=limit,
                       having=having,
                       addPkeyColumn=False,
                       relationDict=self.columnsDict,
                      **sqlArgs)
        return q