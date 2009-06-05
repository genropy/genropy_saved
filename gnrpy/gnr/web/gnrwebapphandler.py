# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package           : GenroPy web - see LICENSE for details
# module gnrwebcore : core module for genropy web framework
# Copyright (c)     : 2004 - 2007 Softwell sas - Milano 
# Written by        : Giovanni Porcari, Francesco Cavazzana
#                     Saverio Porcari, Francesco Porcari
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


"""
core.py

Created by Giovanni Porcari on 2007-03-24.
Copyright (c) 2007 Softwell. All rights reserved.
"""
import os
#import sys
import re
import time
#import datetime
#import traceback
#import weakref
#import random
#import itertools
#import urllib
#import zipfile
#import StringIO
#from decimal import Decimal

from gnr.core.gnrlog import gnrlogging
#from gnr.core.gnrlang import optArgs
from gnr.core.gnrlang import gnrImport

gnrlogger = gnrlogging.getLogger('gnr.web.gnrwebcore')

#from mod_python import apache, Session, Cookie
#from mako.template import Template

#try :
#    import json
#except:
#    import simplejson as json

#from mako.lookup import TemplateLookup

from gnr.core.gnrbag import Bag
#from gnr.core.gnrbag import DirectoryResolver, TraceBackResolver, TxtDocResolver, UrlResolver, XmlDocResolver, BagFormula

#from gnr.core.gnrlang import GnrObject
from gnr.core import gnrlist

from gnr.core.gnrlang import getUuid
from gnr.core.gnrstring import templateReplace, splitAndStrip, toText, toJson, concat
#from gnr.core import gnrdate

#from gnr.web.jsmin import jsmin

#from gnr.web.gnrwebstruct import GnrDomSrc_dojo_12, GnrDomSrc_dojo_11, GnrGridStruct
#from gnr.web.gnrwebapp import GnrWebApp

#from gnr.sql.gnrsqldata import SqlRelatedSelectionResolver, SqlRelatedRecordResolver
#from gnr.web.gnrwebsite import GnrWebSite

#class GnrProcessHandler(object):
#    def __init__(self):
#        self.start_time = time.time()
#        self.siteHandlers = {}
#        
#    def getSiteHandler(self, page):
#        siteKey = page.get_site_id()
#        if not siteKey in self.siteHandlers:
#            self.siteHandlers[siteKey] = {'applications':{}}
#        return self.siteHandlers[siteKey]

class GnrBaseWebAppHandler(object): 
        
    def _finalize(self, page):
        self.db.closeConnection()
        
    def getDb(self, dbId=None):
        return self.db # TODO: is a __getitem__ for back compatibility: see gnrsqldata DataResolver
    __getitem__ = getDb

    def _getAppId(self):
        if not hasattr(self, '_appId'):
            instances=self.page.config['instances'].keys()
            if len(instances)==1:
                self._appId=instances[0]
            else:
                self._appId=self.page.request.uri.split['/'][2]
                if not self._appId in instances:
                    self._appId=instances[0]
        return self._appId
    appId = property(_getAppId) 

    def getPackages(self):
        return [[pkgobj.name_full,pkg] for pkg,pkgobj in self.db.packages.items()]
    rpc_getPackages = getPackages
    
    def getTables(self, pkg=None):
        tables= self.db.package(pkg).tables
        if tables:
            return [[tblobj.name_full.capitalize(),tbl] for tbl,tblobj in tables.items()]
        return []
    rpc_getTables = getTables

    def getTablesTree(self):
        result = Bag()
        for pkg,pkgobj in self.db.packages.items():
            if pkgobj.attributes.get('reserved','n').upper()!='Y':
                tblbag = Bag()
                label=pkgobj.name_full.capitalize()
                result.setItem(pkg, tblbag, label=label)
                for tbl,tblobj in pkgobj.tables.items():
                    label=tblobj.name_full.capitalize()
                    tblbag.setItem(tbl, None, label=label, tableid='%s.%s' % (pkg, tbl))
        return result
    rpc_getTablesTree = getTablesTree
    
    def getTableFields(self,pkg='',table='',**kwargs):
        if not pkg:
            pkg,table=table.split('.')
        return self.dbStructure(path='%s.tables.%s.relations' % (pkg,table))
    rpc_getTableFields = getTableFields
    
    def dbStructure(self, path='', **kwargs):
        result = Bag()
        curr = self.db.packages
        if path:
            curr = curr[path]
            path = path+'.'
        return self._dbStructureInner(curr, path)
    rpc_dbStructure = dbStructure
    
    def _dbStructureInner(self, where, path):
        result=Bag()
        for elem in where:
            if hasattr(elem,'resolver'):
                attributes={}
                attributes.update(elem.getAttr())
                if 'joiner' in attributes:
                    joiner=attributes.pop('joiner')
                    attributes.update(joiner[0] or {})
                label=elem.label
                attributes['caption']=attributes.get('name_long')
                if elem.resolver != None :
                    result.setItem(label,"genro.rpc.remoteResolver('app.dbStructure',{path:'%s'})"% (path+label), attributes, _T ='JS')
                else:
                    value=elem.value
                    if hasattr(value,'__len__'):
                        if len(value):
                            result.setItem(label,"genro.rpc.remoteResolver('app.dbStructure',{path:'%s'})"% (path+label), attributes, _T ='JS')
                        else:
                            result.setItem(label, None)
                    else:
                        result.setItem(label,elem.value,attributes)
            elif hasattr(where, '__getitem__'):
                if isinstance(where, Bag):
                    n = where.getNode(elem)
                    value=n.value
                    attributes = n.getAttr()
                else:
                    value = where[elem]
                    attributes = getattr(value, 'attributes', {})
                label = elem
                attributes['caption'] = attributes.get('name_long')
                if len(value):
                    result.setItem(label,"genro.rpc.remoteResolver('app.dbStructure',{path:'%s'})"% (path+label), attributes, _T ='JS')
                else:
                    result.setItem(label,None, attributes)
            else:
                result.setItem(elem,None) 
        return result
        
        
    def rpc_batchDo(self, batch, resultpath, forked=False, **kwargs):
        if forked:
            from processing import Process
            p = Process(target=self._batchExecutor, args=(batch, resultpath, forked), kwargs=kwargs)
            p.start()
            return None
        else:
            return self._batchExecutor(batch, resultpath, forked, **kwargs)
        
    def _batchExecutor(self, batch, resultpath, forked, **kwargs):
        batchClass = self._batchFinder(batch)
        batch = batchClass(self.page)
        if forked:
            try:
                result = batch.run(**kwargs)
                error = None
                _cls = None
            except Exception, err:
                result = self.page._errorPage(err, batch, kwargs)
                result._page = None
                error = 'serverError'
                _cls = 'domsource'
            self.page.setInClientData(resultpath, result, _error=error, __cls=_cls, save=True)
        else:
            return batch.run(**kwargs)
            
    def _batchFinder(self, batch):
        modName, clsName = batch.split(':')
        modPath = self.page.getResource(modName, 'py') or []
        if modPath:
            m = gnrImport(modPath)
            return getattr(m,clsName)
        else:
            raise GnrWebServerError('Cannot import component %s' % modName)

    def rpc_getSqlOperators(self):
        result = Bag()
        wt = self.db.whereTranslator
        for op in ('startswith','wordstart','contains','greater','greatereq','less','lesseq','between','isnull','in','equal','regex'):
            result.setItem('op.%s' % op, None, caption='!!%s' % wt.opCaption(op))
            
        for op in ('startswith','wordstart','contains','regex'):
            result.setAttr('op.%s' % op, onlyText=True)
            
        result.setItem('jc.and', None, caption='!!AND')
        result.setItem('jc.or', None, caption='!!OR')
        
        result.setItem('not.yes', None, caption='&nbsp;')
        result.setItem('not.not', None, caption='!!NOT')
        
        return result
    
    def rpc_getRecordCount(self, field=None, value=None,
                           table='',distinct=False, columns='',where='', 
                           relationDict=None, sqlparams=None, **kwargs):
        sqlargs = dict(kwargs)
        if field:
            if not table:
                pkg, table, field = splitAndStrip(field, '.', fixed=-3)
                table = '%s.%s' % (pkg, table)
            where = '$%s = :value' % field
        sqlargs['value'] = value
        tblobj = self.db.table(table)
        return tblobj.query(columns=columns, distinct=distinct, where=where,
                            relationDict=relationDict, sqlparams=sqlparams, **sqlargs).count()
                            
    def rpc_selectionCall(self,table, selectionName, method, freeze=False, **kwargs):
        tblobj = self.db.table(table)
        selection = self.page.unfreezeSelection(tblobj, selectionName)  
        if hasattr( selection,method):
            result= getattr(selection,method)(**kwargs)
            if freeze:
                selection.freezeUpdate()
            return result

    def rpc_getRelatedRecord(self, from_fld=None, target_fld=None, pkg=None, pkey=None, ignoreMissing=True, ignoreDuplicate=True, 
                          js_resolver_one='relOneResolver', js_resolver_many='relManyResolver',
                          sqlContextName=None, one_one=None, **kwargs):
        if one_one is not None:
            raise 'supercazzola'
            
        pkg, tbl, related_field = target_fld.split('.')
        table = '%s.%s' % (pkg, tbl)
        if pkey is None:
            tbl_pkey= self.db.table(table).pkey
            pkey=kwargs.pop(tbl_pkey,None)
        if pkey in (None,'') and not related_field in kwargs: # and (not kwargs): # related record from a newrecord or record without link
            pkey = '*newrecord*'
        record,recInfo = self.rpc_getRecord(table=table, from_fld=from_fld, target_fld=target_fld, pkey=pkey, 
                                            ignoreMissing=ignoreMissing, ignoreDuplicate=ignoreDuplicate, 
                                            js_resolver_one=js_resolver_one, js_resolver_many=js_resolver_many,
                                            sqlContextName=sqlContextName, **kwargs)
                               
        joinDict = {}
        if sqlContextName:
            ctx = self.page.session.pagedata['context.%s' % sqlContextName]
            if ctx:
                joinDict = ctx['%s_%s' % (target_fld.replace('.','_'), from_fld.replace('.','_'))]
        if joinDict and joinDict.get('applymethod'):
            self.page.getPublicMethod('rpc', joinDict['applymethod'])(record)
        return (record,recInfo)
        
    def setContextJoinColumns(self, table,contextName='', reason=None, path=None, columns=None):
        tblobj = self.db.table(table)
        relation = tblobj.model.getRelation(path)
        ctxpath = 'context.%s.%s_%s'  % (contextName,relation['many'].replace('.','_'),relation['one'].replace('.','_'))
        self.page.session.loadSessionData()
        pagedata = self.page.session.pagedata
        pagedata.setItem('%s._reasons.%s' %(ctxpath,reason ),columns)
        query_set = set()
        for columns in pagedata.getItem('%s._reasons' %ctxpath).values():
            query_set.update(columns.split(','))
        pagedata.setItem('%s.joincolumns' % ctxpath ,','.join(query_set))
        self.page.session.saveSessionData()

    def rpc_getRelatedSelection(self, from_fld, target_fld, relation_value=None,
                                columns='', query_columns=None, 
                                order_by=None, condition=None, 
                                js_resolver_one='relOneResolver', 
                                sqlContextName=None, **kwargs):
        
        relPath=self.page._rpc_resultPath.replace('.','_')
        if columns:
            raise 'COLUMNS PARAMETER NOT EXPECTED!!'
        columns = columns or query_columns
        #self.page.gnotify('columns', str(self.page.session.pagedata.keys()), always=True)
        t = time.time()
        if sqlContextName and not columns:
            ctx = self.page.session.pagedata['context.%s' % sqlContextName]
            if ctx:
                columns = ctx['%s_%s.joincolumns' % (target_fld.replace('.','_'), from_fld.replace('.','_'))]
                
        columns = columns or '*' 
        
        pkg, tbl, related_field = target_fld.split('.')
        dbtable = '%s.%s' % (pkg, tbl)
        if not relation_value:
            kwargs['limit']=0
        where = "$%s = :val_%s" % (related_field, related_field)
        kwargs[str('val_%s' % related_field)] = relation_value
        if condition:
            where = '(%s) AND (%s)' % (where, condition)
        query = self.db.query(dbtable, columns=columns, where=where, 
                              sqlContextName=sqlContextName, **kwargs)
        
        joinDict = {}
        if sqlContextName:
            self._joinConditionsFromContext(query, sqlContextName)
            ctx = self.page.session.pagedata['context.%s' % sqlContextName]
            if ctx:
                joinDict = ctx['%s_%s' % (target_fld.replace('.','_'), from_fld.replace('.','_'))]
                if joinDict and joinDict['condition']:
                    params = self._getParamsFromContext(sqlContextName, joinDict['params'].asDict(ascii=True))
                    query.setJoinCondition(target_fld='*', from_fld='*', condition=joinDict['condition'], 
                                        one_one=joinDict['one_one'], **params)
            
        sel = query.selection()
        if joinDict and joinDict.get('applymethod'):
            self.page.getPublicMethod('rpc', joinDict['applymethod'])(sel)
        
        result = Bag()
        content=None
        
        relOneParams = dict(_target_fld = '%s.%s' % (dbtable, self.db.table(dbtable).pkey),
                            _from_fld='', 
                            _resolver_name=js_resolver_one, 
                            _sqlContextName=sqlContextName
                           )
        for j,row in enumerate(sel) :
            row = dict(row)
            pkey = row.pop('pkey')
            spkey = toText(pkey)
            result.setItem('%s' % spkey, None, _pkey=spkey, _relation_value=pkey,
                                    _attributes=row, _removeNullAttributes=False, **relOneParams)
        
        relOneParams.update(dict([(k,None) for k in sel.colAttrs.keys() if not k=='pkey']))
        resultAttributes=dict(dbtable=dbtable, totalrows=len(sel))
        resultAttributes.update({'servertime': int((time.time() - t)*1000), 
                                 'newproc':getattr(self, 'self.newprocess', 'no'),
                                 'childResolverParams': '%s::JS' % toJson(relOneParams)
                                 })
        
        return (result,resultAttributes)

    def rpc_runSelectionBatch(self, table, selectionName=None, batchFactory=None, pkeys=None, 
                            thermoid=None, thermofield=None, 
                            stopOnError=False, forUpdate=False, onRow=None, **kwargs):
        """batchFactory: name of the Class, plugin of table, which executes the batch action
            thermoid:
            thermofield: the field of the main table to use for thermo display or * for record caption
            stopOnError: at the first error stop execution
            forUpdate: load records for update and commit at end (always use for writing batch)
            onRow: optional method to execute on each record in selection, use if no batchFactory is given
            """
        tblobj = self.db.table(table)
        if not pkeys:
            selection = self.page.unfreezeSelection(tblobj, selectionName)
            pkeys = selection.output('pkeylist')
            
        batch = tblobj.getPlugin(name=batchFactory or 'batch', thermoCb=self.setThermo, 
                                    thermoid=thermoid, thermofield=thermofield, 
                                    stopOnError=stopOnError, forUpdate=forUpdate, onRow=onRow, **kwargs)
        return batch.run(pkeyList=pkeys)
        
            
    def setThermo(self, thermoid, progress_1=None, message_1=None, 
                   maximum_1=None, command=None, **kwargs):
        #progress==None --> indeterminate
        #now = time.time()
        #if (not command) and now - self.lastThermoUpd < 1:
        #    return
        #self.lastThermoUpd = now
        
        session = self.page.session
        session.loadSessionData()
        if command == 'init':
            thermoBag = Bag()
        else:
            thermoBag = session.pagedata.getItem('thermo_%s' % thermoid) or Bag()

            
        max = maximum_1 or thermoBag['t1.maximum']
        prog = progress_1 or thermoBag['t1.maximum']            
        if max and prog > max:
            end = True
            
        if command == 'end':
            thermoBag['status']='end'
            thermoBag['message']='!!Execution completed'
        elif command == 'stopped':
            thermoBag['status']='stopped'
            thermoBag['message']='!!Execution stopped'
        else:
            params = dict(progress_1=progress_1, message_1=message_1, maximum_1=maximum_1)
            params.update(kwargs)
            for k,v in params.items():
                if v is not None:
                    key, thermo = k.split('_')
                    thermoBag['t%s.%s' % (thermo, key)] = v      
                              
        session.setInPageData('thermo_%s' % thermoid, thermoBag)
        session.saveSessionData()
        if thermoBag['stop']:
            return 'stop'
        
    def rpc_getThermo(self, thermoid, flag=None):
        session = self.page.session
        if flag=='stop':
            session.loadSessionData()
            thermoBag = session.pagedata.getItem('thermo_%s' % thermoid) or Bag()
            thermoBag['stop'] = True
            session.setInPageData('thermo_%s' % thermoid, thermoBag)
            session.saveSessionData()
        else:
            thermoBag = session.pagedata.getItem('thermo_%s' % thermoid) or Bag()
        return thermoBag
        
    def rpc_onSelectionDo(self, table, selectionName, command, callmethod=None, selectedRowidx=None, recordcall=False, **kwargs):
        result = None
        tblobj = self.db.table(table)
        selection = self.page.unfreezeSelection(tblobj, selectionName)
        if selectedRowidx:
            if isinstance(selectedRowidx, basestring):
                selectedRowidx = [int(x) for x  in selectedRowidx.split(',')]
            selectedRowidx = set(selectedRowidx)
            selection.filter(lambda r: r['rowidx'] in selectedRowidx)
        callmethod = callmethod or 'standard'
        if command in ('print', 'rpc', 'export', 'action', 'pdf'):
            handler = getattr(self.page, '%s_%s' % (command, callmethod), None)
            if not handler:
                handler = getattr(tblobj, '%s_%s' % (command, callmethod), None)
            if handler:
                if recordcall:
                    result = []
                    for r in selection:
                        onres = handler(tblobj.record(r['pkey']), locale=self.page.locale, **kwargs)
                        if onres != None:
                            result.append(onres)
                else:
                    result = handler(selection, locale=self.page.locale, **kwargs)
        return result
        
    def rpc_(self, table, selectionName, command, callmethod=None, selectedRowidx=None, recordcall=False, **kwargs):
        result = None
        tblobj = self.db.table(table)
        selection = self.page.unfreezeSelection(tblobj, selectionName)
        if selectedRowidx:
            if isinstance(selectedRowidx, basestring):
                selectedRowidx = [int(x) for x  in selectedRowidx.split(',')]
            selectedRowidx = set(selectedRowidx)
            selection.filter(lambda r: r['rowidx'] in selectedRowidx)
        callmethod = callmethod or 'standard'
        if command in ('print', 'rpc', 'export', 'action', 'pdf'):
            handler = getattr(self.page, '%s_%s' % (command, callmethod), None)
            if not handler:
                handler = getattr(tblobj, '%s_%s' % (command, callmethod), None)
            if handler:
                if recordcall:
                    result = []
                    for r in selection:
                        onres = handler(tblobj.record(r['pkey']), locale=self.page.locale, **kwargs)
                        if onres != None:
                            result.append(onres)
                else:
                    result = handler(selection, locale=self.page.locale, **kwargs)
        return result
        
    def export_standard(self, selection, locale=None,columns=None,filename=None,**kwargs):
        print 'export_standard'
        print selection.output('bag')
        filename = filename or self.maintable or  self.request.uri.split('/')[-1]
        content = selection.output('tabtext', columns=columns, locale=locale)
        self.page.utils.sendFile(content,filename,'xls')
    
    def print_standard(self, selection, locale=None,**kwargs):
        columns = None # get columns from current view on client !
        if not columns:
            columns = [c for c in selection.allColumns if not c in ('pkey','rowidx')]
        outdata = selection.output('dictlist', columns=columns, asIterator=True)
        colAttrs = selection.colAttrs
        return self.page.makoTemplate('standard_print.tpl', striped='odd_row,even_row', outdata=outdata, colAttrs=colAttrs,
                title='Print List', header='Print List', columns=columns)
                
    def pdf_standard(self, selection, locale=None,**kwargs):
        columns = None # get columns from current view on client !
        if not columns:
            columns = [c for c in selection.allColumns if not c in ('pkey','rowidx')]
        outdata = selection.output('dictlist', columns=columns, asIterator=True)
        colAttrs = selection.colAttrs
        return self.page.rmlTemplate('standard_print.rml', outdata=outdata, colAttrs=colAttrs,
                title='Print List', header='Print List', columns=columns)
                  
    def _joinConditionsFromContext(self, obj, sqlContextName):
        sessionCtx = self.page.session.pagedata['context.%s' % sqlContextName]
        if sessionCtx:
            for joinDict in sessionCtx.values():
                if joinDict['condition']: # may be a relatedcolumns only
                    params = self._getParamsFromContext(sqlContextName, joinDict['params'].asDict(ascii=True))
                    #raise str(dict(target_fld=joinDict['target_fld'], from_fld=joinDict['from_fld'], condition=joinDict['condition'], 
                    #                        one_one=joinDict['one_one'], **params))
                    obj.setJoinCondition(target_fld=joinDict['target_fld'], from_fld=joinDict['from_fld'], condition=joinDict['condition'], 
                                            one_one=joinDict['one_one'], **params)
        #else:
        #    raise str('%s \n\n %s' % (str(sqlContextName), str(self.page.session.pagedata['context'].keys())))

    def _getParamsFromContext(self, sqlContextName, params):
        if params:
            for k,v in params.items():
                if isinstance(v, basestring):
                    if v.startswith('^'):
                        params[k] = self.page.session.pagedata['context.%s' % v[1:]]
                    elif hasattr(self, '%s_%s' % (sqlContextName, v)):
                        params[k] = getattr(self, '%s_%s' % (sqlContextName, v))()
        return params
        
    def rpc_getSelection(self, table='',distinct=False, columns='',where='',condition=None,
                            order_by=None, limit=None, offset=None, group_by=None, having=None,
                            relationDict=None, sqlparams=None, row_start='0', row_count='0',
                            recordResolver=True, selectionName='', structure=False, numberedRows=True,
                            pkeys=None, fromSelection=None, applymethod=None, totalRowCount=False,
                            selectmethod=None, expressions=None,
                            sortedBy=None,excludeLogicalDeleted=True, **kwargs):
        t = time.time()
        #if 'sqlContextName' in kwargs:
        #    kwargs['sqlContext'] = dict(name=kwargs['sqlContextName'], ctxbag=self.page.session.pagedata['context'])
        #    kwargs['sqlContext'] = dict(name=kwargs['sqlContext'], fnc=getattr(self.page, kwargs['sqlContext']))
            
        tblobj = self.db.table(table)
        row_start = int(row_start)
        row_count = int(row_count)
        newSelection=True
        if selectionName.startswith('*'):
            if selectionName=='*':
                selectionName=getUuid()
            else:
                selectionName=selectionName[1:]
        elif selectionName:
            newSelection=False
        if newSelection:
            debug='fromDb'
            if selectmethod:
                selectmethod = self.page.getPublicMethod('rpc', selectmethod)
            else:
                selectmethod = self._default_getSelection   
            selection = selectmethod(tblobj=tblobj, table=table,distinct=distinct, columns=columns,where=where,condition=condition,
                               order_by=order_by,limit=limit, offset=offset, group_by=group_by,having=having,
                               relationDict=relationDict, sqlparams=sqlparams, row_start=row_start,row_count=row_count,
                               recordResolver=recordResolver,selectionName=selectionName, structure=structure,pkeys=pkeys, fromSelection=fromSelection,
                               expressions=expressions,sortedBy=sortedBy,
                               excludeLogicalDeleted=excludeLogicalDeleted, **kwargs)
            if applymethod:
                self.page.getPublicMethod('rpc', applymethod)(selection)
                
            if selectionName:
                selection.setKey('rowidx')
                self.page.freezeSelection(selection,selectionName)
            resultAttributes=dict(table=table, method='app.getSelection',selectionName=selectionName, row_count=row_count,
                                               totalrows=len(selection))
        else:
            selection = self.page.unfreezeSelection(tblobj, selectionName)
            if ','.join( selection.sortedBy)!= sortedBy:
                selection.sort(sortedBy)
                selection.freezeUpdate()
            debug='fromPickle'
            resultAttributes={}
        generator = selection.output(mode='generator',offset=row_start,limit=row_count)
        data = self.gridSelectionData(selection, generator, logicalDeletionField=tblobj.logicalDeletionField,
                                      recordResolver=recordResolver, numberedRows=numberedRows)
        if not structure:
            result = data
        else:
            result = Bag()
            result['data'] = data
            result['structure'] = self.gridSelectionStruct(selection)
        resultAttributes.update({'debug': debug, 'servertime': int((time.time() - t)*1000), 
                            'newproc':getattr(self, 'self.newprocess', 'no')})
        
        #ADDED CONDITION AND **KWARGS (PARAMETERS FOR CONDITION)
        if totalRowCount:
            resultAttributes['totalRowCount'] = tblobj.query(where=condition, excludeLogicalDeleted=excludeLogicalDeleted, **kwargs).count()
            
        return (result,resultAttributes)
        
    def rpc_createSelection(self, table='', selectionName='', distinct=False, columns='', where='', condition=None,
                            order_by=None, limit=None, offset=None, group_by=None, having=None,
                            relationDict=None, sqlparams=None, pkeys=None,
                            selectmethod=None, expressions=None, apply=None, sortedBy=None, **kwargs):
        """Create a new selection and freezes 
        @param table: tbale name
        @param selectionName: the name of the selection, empty or '*' will default to a new uuid
        @param pkeys: a json or comma separated list of pkey to find (overwrite the where parameter)
        @param selectmethod: a page method with rpc_ prefix which receive all parameters and has to return a selection object
        @param expressions: comma separated list of expr_ methods which returns the sql string for a column (probably a formula)
        @param apply: a page method with rpc_ prefix which will be applied to the selection (see gnrsqldata.SqlSelection.apply)
        @param sortedBy: sort the selection after apply, for sort in python with calculated columns available
        """
        t = time.time()
        tblobj = self.db.table(table)
        
        #if 'sqlContextName' in kwargs:
        #    kwargs['sqlContext'] = dict(name=kwargs['sqlContextName'], ctxbag=self.page.session.pagedata['context'])
        #    kwargs['sqlContext'] = dict(name=kwargs['sqlContext'], fnc=getattr(self.page, kwargs['sqlContext']))
        
        if selectionName=='*' or not selectionName:
            selectionName = getUuid()
            
        if selectmethod:
            selectmethod = getattr(self.page, 'rpc_%s' % selectmethod)
        else:
            selectmethod = self._default_getSelection            
        selection = selectmethod(tblobj=tblobj, table=table, distinct=distinct, columns=columns, where=where, condition=condition,
                           order_by=order_by, limit=limit, offset=offset, group_by=group_by, having=having,
                           relationDict=relationDict, sqlparams=sqlparams,
                           pkeys=pkeys, expressions=expressions, **kwargs)
        
        if apply:
            selection.apply(getattr(self.page, 'rpc_%s' % apply))
        if sortedBy:
            selection.sort(sortedBy)
        self.page.freezeSelection(selection, selectionName)
        resultAttributes = dict(table=table, selectionName=selectionName, 
                                servertime=int((time.time() - t)*1000), newproc=getattr(self, 'self.newprocess', 'no'))
        return (len(selection), resultAttributes)

    def _default_getSelection(self,tblobj=None, table=None,distinct=None, columns=None,where=None,condition=None,
                            order_by=None,limit=None, offset=None, group_by=None,having=None,
                            relationDict=None, sqlparams=None, row_start=None,row_count=None,
                            recordResolver=None, selectionName=None, pkeys=None, fromSelection=None,
                            expressions=None,sortedBy=None, sqlContextName=None,
                            excludeLogicalDeleted=True, **kwargs):
        if isinstance(columns, Bag):
            columns = self._columnsFromStruct(columns)
        if not columns:
            columns = tblobj.attributes.get('baseview') or '*'
        if '[' in columns:
            columns=columns.replace(' ','').replace('\n','').replace('\t','')
            maintable=[]
            colaux=columns.split(',')
            columns=[]
            for col in colaux:
                if '[' in col:
                    tbl,col=col.split('[')
                    maintable=[tbl]
                if col.endswith(']'):
                    col=col[:-1]
                columns.append('.'.join(maintable+[col.rstrip(']')]))
                if col.endswith(']'):
                    maintable=[]
            columns=','.join(columns)
        if expressions:
            expr_dict = getattr(self.page, 'expr_%s' %expressions)()
            expr_dict = dict([(k, '%s AS %s' % (v,k)) for k,v in expr_dict.items()])
            columns = templateReplace(columns, expr_dict, safeMode=True)
        if fromSelection:
            fromSelection = self.page.unfreezeSelection(tblobj, fromSelection)
            pkeys = fromSelection.output('pkeylist')
        if pkeys:
            where='t0.%s in :pkeys' % tblobj.pkey
            if isinstance(pkeys, basestring):
                pkeys = pkeys.split(',')
            kwargs['pkeys'] = pkeys
        elif isinstance(where, Bag):
            where._locale = self.page.locale
            where._workdate = self.page.workdate
            where, kwargs = tblobj.sqlWhereFromBag(where, kwargs)
        if condition:
            where = '(%s) AND (%s)' % (where, condition)
        sql_kwargs = dict([(str(k), v) for k,v in kwargs.items() if not k.startswith('frm_')])
        fmt_kwargs = dict([(str(k[4:]), v) for k,v in kwargs.items() if k.startswith('frm_')])
        query=tblobj.query(columns=columns,distinct=distinct, where=where,
                        order_by=order_by,limit=limit, offset=offset, group_by=group_by,having=having,
                        relationDict=relationDict, sqlparams=sqlparams,
                        excludeLogicalDeleted=excludeLogicalDeleted,**sql_kwargs)
        if sqlContextName: 
            self._joinConditionsFromContext(query, sqlContextName)
        selection = query.selection(sortedBy=sortedBy, _aggregateRows=True)
        if sqlContextName:
            ctx = self.page.session.pagedata['context.%s' % sqlContextName]
            if ctx and False:
                joinDict = ctx['%s_%s' % (target_fld.replace('.','_'), from_fld.replace('.','_'))]
                if joinDict and joinDict.get('applymethod'):
                    self.page.getPublicMethod('rpc', joinDict['applymethod'])(selection)
                    
        return selection
        
    def _columnsFromStruct(self, viewbag, columns=None):
        if columns is None:
            columns = []
        if not viewbag:
            return
            
        for node in viewbag:
            fld = node.getAttr('field')
            if fld:
                if not (fld[0] in ('$','@')):
                    fld = '$' + fld
                columns.append(fld)
            if isinstance(node.value, Bag):
                self._columnsFromStruct(node.value, columns)
        return ','.join(columns)
    
    def gridSelectionData(self, selection, outsource, recordResolver, numberedRows, logicalDeletionField):
        result = Bag()  
        for j,row in enumerate(outsource) :
            row_class=None
            row = dict(row)
            pkey = row.pop('pkey', None)
            isDeleted=row.pop('_isdeleted',None)
            if isDeleted:
                row_class='logicalDeleted'
            if numberedRows or not pkey:
                row_key='r_%i'%j
            else:
                row_key = toText(pkey).replace('.','_')
            result.setItem(row_key, None, _pkey=pkey or row_key,
                           _target_fld = '%s.%s' % (selection.dbtable.fullname, selection.dbtable.pkey),
                           _relation_value=pkey, _resolver_name='relOneResolver',
                           _attributes=row, _removeNullAttributes=False, _customClasses=row_class)
        return result
                
        
    def gridSelectionStruct(self,selection):
        structure = Bag()
        r = structure.child('view').child('row')
        for colname in selection.columns:
            if ((colname != 'pkey') and( colname!='rowidx')):
                kwargs=dict(selection.colAttrs.get(colname, {}))
                kwargs.pop('tag',None)
                kwargs['name']=kwargs.pop('label')
                if kwargs['dataType']=='D':
                    kwargs['format_date']='short'
                size=kwargs.pop('size',None)
                size=kwargs.pop('print_width',size)
                if size:
                    if isinstance(size,basestring):
                        if ':' in size:
                            size=size.split(':')[1]
                    size=int(size)
                    if size <3:
                        width=size*1.1
                    if size <6:
                            width=size
                    elif size<10:
                        width=size*.8
                    elif size<20:
                        width=size*.7
                    else:
                        width=size*.6
                    kwargs['width']='%iem' % (1+int(int(width)*.7))
                r.child('cell', childname=colname,field=colname,**kwargs)
        return structure
    #@timer_call()
    def rpc_getRecord(self, table=None, dbtable=None, pkg=None, pkey=None,
                    ignoreMissing=True, ignoreDuplicate=True, 
                    from_fld=None, target_fld=None, sqlContextName=None, applymethod=None,
                    js_resolver_one='relOneResolver', js_resolver_many='relManyResolver', 
                    loadingParameters=None, **kwargs):
        t = time.time()
        dbtable = dbtable or table
        if pkg:
            dbtable='%s.%s' % (pkg, dbtable)
        tblobj = self.db.table(dbtable)
        newrecord = False
        if pkey: 
            kwargs['pkey'] = pkey
        rec = tblobj.record(eager=self.page.eagers.get(dbtable),
                            ignoreMissing=ignoreMissing,ignoreDuplicate=ignoreDuplicate,
                            sqlContextName=sqlContextName,**kwargs)
        if sqlContextName:
            self._joinConditionsFromContext(rec, sqlContextName)
            
        if (pkey=='*newrecord*'):
            newrecord = True
            record = rec.output('newrecord', resolver_one=js_resolver_one, resolver_many=js_resolver_many)
        else:
            record = rec.output('bag', resolver_one=js_resolver_one, resolver_many=js_resolver_many)
            
        recInfo = dict(_pkey=record[tblobj.pkey] or '*newrecord*',
                        caption=tblobj.recordCaption(record,newrecord),
                        _newrecord=newrecord, sqlContextName=sqlContextName)
        method = None
        if loadingParameters:
            method = loadingParameters.pop('method')
        if method:
            handler = self.page.getPublicMethod('rpc', method)
        else:
            if dbtable == self.page.maintable:
                method = 'onLoading'
            else:
                #self.page.gnotify('getRecord', dbtable, True)
                method = 'onLoading_%s' % dbtable.replace('.','_')
            handler = getattr(self.page, method, None)
            
        if handler:
            handler(record, newrecord, loadingParameters,recInfo)
        elif newrecord and loadingParameters:
            self.setRecordDefaults(record,loadingParameters)

        if applymethod:
            self.page.getPublicMethod('rpc', applymethod)(record)
            
        recInfo['servertime'] = int((time.time() - t)*1000)
        if tblobj.lastTS:
            recInfo['lastTS'] = str(record[tblobj.lastTS])
        return (record,recInfo)
    
    def setRecordDefaults(self, record, defaults):
        for k,v in defaults.items():
            if k in record:
                record[k] = v
        #pass
       
    def rpc_dbSelect(self, dbtable=None, columns=None, auxColumns=None, hiddenColumns=None, rowcaption=None, 
                          _id=None, _querystring='', querystring=None, ignoreCase=True, exclude=None,
                          condition=None, limit=10, alternatePkey=None, order_by=None, selectmethod=None, 
                          notnull=None, weakCondition=False, **kwargs):
        """
        * dbtable: table source for the query
        * columns: columns that is involved into the query
        * auxColumns: showed only as result, not involved into the search.
        * hiddenColumns: data that is getted but is not showed.
        * rowcaption: what you see into the field. Often is different from 
                      what you set with dbselect
        * condition: more condition into the query. Every kwargs params that 
                    starts with condition_ ar the variables involved into the clause.
        * selectmethod: custom rpc_method you can use for make the query on the server.
        * weakCondition: if there's a condition and it's not defined a selectedmethod
        """
        resultClass=''
        if selectmethod or not condition:
            weakCondition=False
        t0 = time.time()
        querystring = _querystring or querystring # da cambiare nella gnrstores.js invece?
        limit = int(limit)
        result = Bag()
        tblobj = self.db.table(dbtable)
        
        captioncolumns = tblobj.rowcaptionDecode(rowcaption)[0]
        querycolumns = tblobj.getQueryFields(columns or captioncolumns)
        showcolumns = gnrlist.merge(querycolumns, tblobj.columnsFromString(auxColumns))
        resultcolumns = gnrlist.merge(showcolumns, captioncolumns, tblobj.columnsFromString(hiddenColumns))
        if alternatePkey and not alternatePkey in resultcolumns:
            resultcolumns.append(alternatePkey)
        selection = None
        identifier= 'pkey'
        rows=[]  
        if _id:
            if alternatePkey:
                where ='$%s = :id' % alternatePkey
            else:
                where ='$%s = :id' % identifier
            selection = tblobj.query(columns= ','.join(resultcolumns),
                                     where=where,excludeLogicalDeleted=False,
                                     limit=1, id=_id).selection()
        elif querystring:
            querystring = querystring.strip('*')
            if querystring.isdigit():
                querystring = "%s%s" % ('%',querystring)
            if selectmethod:
                selectHandler = self.page.getPublicMethod('rpc', selectmethod)
            else:
                selectHandler = self.rpc_dbSelect_default
            selection = selectHandler(tblobj=tblobj, querycolumns=querycolumns, querystring=querystring, 
                                    resultcolumns=resultcolumns, condition=condition, exclude=exclude,
                                    limit=limit, order_by=order_by,
                                    identifier=identifier, ignoreCase=ignoreCase, **kwargs)
            if not selection and weakCondition :
                resultClass='relaxedCondition'
                selection = selectHandler(tblobj=tblobj, querycolumns=querycolumns, querystring=querystring, 
                                    resultcolumns=resultcolumns, exclude=exclude,
                                    limit=limit, order_by=order_by,
                                    identifier=identifier, ignoreCase=ignoreCase, **kwargs)
        
        _attributes = {}
        resultAttrs = {}
        if selection:
            showcols = [tblobj.colToAs(c.lstrip('$')) for c in showcolumns]

            result = selection.output('selection', locale=self.page.locale, caption=rowcaption or True)
            
            colHeaders = [selection.colAttrs[k]['label'] for k in showcols]
            colHeaders = [self.page._(c) for c in colHeaders]
            resultAttrs = {'columns':','.join(showcols), 'headers':','.join(colHeaders)}
            
            if not notnull:
                result.setItem('null_row', None, caption='', _pkey=None)
        resultAttrs['resultClass']=resultClass
        resultAttrs['dbselect_time'] =  time.time()-t0
        return (result,resultAttrs)

    def rpc_dbSelect_selection(self, tblobj, querystring, columns=None, auxColumns=None, **kwargs):
        querycolumns = tblobj.getQueryFields(columns)
        showcolumns = gnrlist.merge(querycolumns, tblobj.columnsFromString(auxColumns))
        captioncolumns = tblobj.rowcaptionDecode()[0]
        resultcolumns = gnrlist.merge(showcolumns, captioncolumns)
        querystring = querystring or ''
        querystring = querystring.strip('*')
        return self.rpc_dbSelect_default(tblobj, querycolumns, querystring, resultcolumns, **kwargs)
        
                               
    def rpc_dbSelect_default(self, tblobj, querycolumns, querystring, resultcolumns,
                               condition=None, exclude=None, limit=None, order_by=None,
                               identifier=None, ignoreCase=None, **kwargs):
        
        def getSelection(where, **searchargs):
            whereargs = {}
            whereargs.update(kwargs)
            whereargs.update(searchargs)
            if where and condition:
                where = '%s AND %s' % (where, condition)
            else:
                where = where or condition
            return tblobj.query(where=where, columns=','.join(resultcolumns), limit=limit,
                                      order_by=order_by or querycolumns[0], exclude_list=exclude_list, **whereargs).selection()
        exclude_list = None
        if exclude:
            if isinstance(exclude, basestring):
                exclude_list = [t.strip() for t in exclude.split(',')]
            else:
                exclude_list = [t for t in exclude if t] # None values break the query
            if exclude_list:
                exclude_cond = 'NOT ($pkey IN :exclude_list )'
                if condition:
                    condition = '%s AND %s' % (condition, exclude_cond)
                else:
                    condition = exclude_cond

        kwargs.pop('where', None)
        srclist = querystring.split()
        
        if not srclist:
            return getSelection(None)
        
        result = getSelection("%s ILIKE :searchval" % querycolumns[0], searchval='%s%%' % ('%% '.join(srclist)))
        
        if len(result) == 0: # few results from the startswith query on first col
            #self.page.gnotify('dbselect','filter')
            regsrc = [x for x in re.split("\W", querystring) if x]
            if regsrc:
                whereargs = dict([('w%i' % i, '(^|\\W)%s' % w.strip()) for i,w in enumerate(regsrc)])
                where =" AND ".join(["(%s)  ~* :w%i" % (" || ' ' || ".join(querycolumns), i) for i,w in enumerate(regsrc)])
                result = getSelection(where, **whereargs)
            
        if len(result) == 0:
            #self.page.gnotify('dbselect','contained')
            whereargs = dict([('w%i' % i, '%%%s%%' % w.strip()) for i,w in enumerate(srclist)])
            
            where =" AND ".join(["(%s)  ILIKE :w%i" % (" || ' ' || ".join(querycolumns), i) for i,w in enumerate(srclist)])
            result = getSelection(where, **whereargs)
                        
        return result

    def rpc_listUserObject(self, objtype=None, tbl=None, **kwargs):
        result = Bag()
        if hasattr(self.page.package,'listUserObject'):
            objectsel = self.page.package.listUserObject(objtype=objtype, userid=self.page.user, tbl=tbl, authtags=self.page.userTags)
            if objectsel:
                for i,r in enumerate(objectsel.data):
                    attrs = dict([(str(k), v) for k,v in r.items()])
                    result.setItem(r['code'] or 'r_%i' % i, None, **attrs)
        return result

    def rpc_loadUserObject(self, userid=None, **kwargs):
        data, metadata = self.page.package.loadUserObject(userid=userid or self.page.user, **kwargs)
        return (data, metadata)
        
    def rpc_saveUserObject(self, userobject, userobject_attr):
        userobject_attr = dict([(str(k),v) for k,v in userobject_attr.items()])
        userobject_attr['userid'] = userobject_attr.get('userid') or self.page.user
        self.page.package.saveUserObject(userobject, **userobject_attr)
        self.db.commit()
        
    def rpc_deleteUserObject(self, id):
        self.page.package.deleteUserObject(id)
        self.db.commit()

    def _relPathToCaption(self, table, relpath):
        if not relpath: return ''
        tbltree = self.db.relationExplorer(table, dosort=False, pyresolver=True)
        fullcaption = tbltree.cbtraverse(relpath, lambda node: self.page._(node.getAttr('name_long')))
        return ':'.join(fullcaption)
        
        
    def rpc_relationExplorer(self, table, prevRelation='', prevCaption='', omit='', **kwargs):
        def buildLinkResolver(node, prevRelation, prevCaption):
            nodeattr = node.getAttr()
            if not 'name_long' in nodeattr:
                raise str(nodeattr)
            nodeattr['caption'] = nodeattr.pop('name_long')
            nodeattr['fullcaption'] = concat(prevCaption, self.page._(nodeattr['caption']), ':')
            if nodeattr.get('one_relation'):
                nodeattr['_T'] = 'JS'
                if nodeattr['mode']=='O':
                    relpkg, reltbl, relfld = nodeattr['one_relation'].split('.')
                else:
                    relpkg, reltbl, relfld = nodeattr['many_relation'].split('.')
                jsresolver = "genro.rpc.remoteResolver('app.relationExplorer',{table:'%s.%s', prevRelation:'%s', prevCaption:'%s', omit:'%s'})"
                node.setValue(jsresolver % (relpkg, reltbl, concat(prevRelation, node.label), nodeattr['fullcaption'], omit))
        result = self.db.relationExplorer(table=table, 
                                         prevRelation=prevRelation,
                                         omit=omit,
                                        **kwargs)
        result.walk(buildLinkResolver, prevRelation=prevRelation, prevCaption=prevCaption)
        return result
                                                    
    def rpc_getRecordForm(self, dbtable=None, fields=None, **kwargs):
        self.getRecordForm(self.newSourceRoot(), dbtable=dbtable, fields=fields, **kwargs)
    
    def formAuto(self,pane,table,columns='',cols=2):
        fb = pane.formbuilder(cols=cols)
        tblobj=self.db.table(table)
        if not columns:
            columns = [colname for colname, col in tblobj.columns.items() if not col.isReserved and not col.dtype=='X'and not col.dtype=='Z']
        elif isinstance(columns, basestring):
            columns = splitAndStrip(columns)
        fb.placeFields(','.join(columns))
        
    def rpc_pageLocalizationSave(self,data,**kwargs):
        locale= self.page.locale
        if '-' in locale:
            locale=locale.split('-')[0]
        self.page.application.updateLocalization(self.page.packageId,data,locale)
        self.page.siteStatus['resetLocalizationTime']=time.time()
        self.page.siteStatusSave()
        
    def rpc_pageLocalizationLoad(self):
        loc=self.page.session.pagedata['localization']
        locale= self.page.locale
        if '-' in locale:
            locale=locale.split('-')[0]
        b=Bag()
        loc_items=loc.items()
        loc_items.sort()
        for j,kv in enumerate(loc_items):
            k,v=kv
            if '|' in k:
                k=k.split('|')[1]
            b['r_%i.key'%j]=k
            b['r_%i.txt'%j]=v.get(locale)
        return b
        
    def rpc_pdfmaker(self, pdfmode, txt, **kwargs):
        filename = '%s.pdf' % self.page.getUuid()
        fpath = self.page.pageLocalDocument(filename)
        getattr(self.page, 'pdf_%s' % pdfmode)(fpath, txt, **kwargs)
        return filename
        
    def rpc_downloadPDF(self, filename, forcedownload=False, **kwargs):
        response = self.page.response
        response.content_type = "application/pdf"
        if forcedownload:
            response.add_header("Content-Disposition", str("attachment; filename=%s" % filename))
        else:
            response.add_header("Content-Disposition", str("filename=%s" % filename))
        
        fpath = self.page.pageLocalDocument(filename)
        response.sendfile(fpath)
        os.remove(fpath)
        
    def _exportFileNameClean(self, filename=None):
        filename = filename or self.page.maintable or  self.page.request.uri.split('/')[-1]
        filename = filename.replace(' ','_').replace('.','_').replace('/','_')[:64]
        filename = filename.encode('ascii', 'ignore')
        return filename
        
        
    def _getStoreBag(self, storebag):
        # da finire
        if isinstance(storebag, basestring):
            if storebag.startswith('gnrsel:'):
                x, tbl, filename = storebag.split(':', 2)
                sel = self.unfreezeSelection(self.app.db.table(tbl), filename)
                storebag = sel.output('grid')
            else:
                storebag = Bag(self.pageLocalDocument(storebag))
        return storebag
        
    def rpc_exportStaticGrid_xls(self, structbag, storebag, filename=None, **kwargs):
        import xlwt
        w = xlwt.Workbook(encoding='latin-1')
        ws = w.add_sheet(filename)
        
        float_style = xlwt.XFStyle()
        float_style.num_format_str = '#,##0.00'
        int_style = xlwt.XFStyle()
        int_style.num_format_str = '#,##0'
        
        font0 = xlwt.Font()
        font0.name = 'Times New Roman'
        font0.bold = True
        hstyle = xlwt.XFStyle()
        hstyle.font = font0
    
        storebag = self._getStoreBag(storebag)
        columns = []
        headers=[]
        coltype={}
        for view in structbag.values():
            for row in view.values():
                for cell in row:
                    col = self.db.colToAs(cell.getAttr('field'))
                    columns.append(col)
                    headers.append(cell.getAttr('name'))
                    coltype[col] = cell.getAttr('dtype')
                    
        ws.panes_frozen = True
        ws.horz_split_pos = 1
        
        for c,header in enumerate(headers):
            ws.write(0, c, header, hstyle)
            
        for i,row in enumerate(storebag):
            r = row.getAttr()
            for c,col in enumerate(columns):
                if coltype[col] in ('R', 'F'):
                    ws.write(i+1, c, r.get(col), float_style)
                elif coltype[col] in ('L','I'):
                    ws.write(i+1, c, r.get(col), int_style)
                else:
                    ws.write(i+1, c, self.page.toText(r.get(col)))
        

        filename = self._exportFileNameClean(filename)
        fpath = self.page.pageLocalDocument(filename)
        w.save(fpath)
        return filename
        
    def rpc_exportStaticGridDownload_xls(self, filename, **kwargs):
        fpath = self.page.pageLocalDocument(filename)
        f = open(fpath, 'r')
        result = f.read()
        f.close()
        #os.remove(fpath)
        self.page.utils.sendFile(result, filename, 'xls', encoding=None)

    def rpc_exportStaticGrid_csv(self, structbag, storebag, filename=None, **kwargs):
        def cleanCol(txt, dtype):
            txt = txt.replace('\n',' ').replace('\r',' ').replace('\t',' ').replace('"',"'")
            if txt:
                if txt[0] in ('+','=', '-'):
                    txt = ' %s' % txt
                elif txt[0].isdigit() and (dtype in ('T','A','',None)):
                    txt = '%s' % txt # how to escape numbers in text columns?
            return txt
            
        filename = self._exportFileNameClean(filename)
        storebag = self._getStoreBag(storebag)
        columns = []
        headers=[]
        coltype={}
        for view in structbag.values():
            for row in view.values():
                for cell in row:
                    col = self.db.colToAs(cell.getAttr('field'))
                    columns.append(col)
                    headers.append(cell.getAttr('name'))
                    coltype[col] = cell.getAttr('dtype')

        result=['\t'.join(headers)]
        for row in storebag:
            r = row.getAttr()
            result.append('\t'.join([cleanCol(self.page.toText(r.get(col)), coltype[col]) for col in columns]))
        result = '\n'.join(result)
        fpath = self.page.pageLocalDocument(filename)
        f = open(fpath, 'w')
        f.write(result.encode('utf-8'))
        f.close()
        return filename
        
    def rpc_exportStaticGridDownload_csv(self, filename, **kwargs):
        fpath = self.page.pageLocalDocument(filename)
        f = open(fpath, 'r')
        result = f.read()
        f.close()
        os.remove(fpath)
        self.page.utils.sendFile(result.decode('utf-8'), filename, 'xls', encoding='latin1')
        
    def _printCellStyle(self, colAttr):
        style = [colAttr.get('style')]
        styleAttrNames = ('height', 'width','top','left', 'right', 'bottom',
                              'visibility', 'overflow', 'float', 'clear', 'display',
                              'z_index', 'border','position','padding','margin',
                              'color','white_space','vertical_align')
        def isStyleAttr(name):
            for st in styleAttrNames:
                if name==st or name.startswith('%s_' % st):
                    return True
        
        for k,v in colAttr.items():
            if isStyleAttr(k):
                style.append('%s: %s;' % (k.replace('_','-'), v))
        style = ' '.join([v for v in style if v])
        return style
        
    def rpc_printStaticGrid(self, structbag, storebag, filename=None, makotemplate='standard_print.tpl', **kwargs): 
        filename = self._exportFileNameClean(filename)
        storebag = self._getStoreBag(storebag)
        columns = []
        colAttrs = {}
        for view in structbag.values():
            for row in view.values():
                for cell in row:
                    col = self.db.colToAs(cell.getAttr('field'))
                    columns.append(col)
                    colAttr = cell.getAttr()
                    dtype = colAttr.get('dtype')
                    if dtype and not ('format' in colAttr):
                        colAttr['format'] = 'auto_%s' % dtype
                    colAttr['style'] = self._printCellStyle(colAttr)
                    colAttrs[col] = colAttr
                    
        outdata = []
        for row in storebag:
            outdata.append(row.getAttr())
        
        result = self.page.makoTemplate(makotemplate, striped='odd_row,even_row', outdata=outdata, colAttrs=colAttrs,
                                            columns=columns, meta=kwargs)

        fpath = self.page.pageLocalDocument(filename)
        f = open(fpath, 'w')
        if isinstance(result, unicode):
            result = result.encode('utf-8')
        f.write(result)
        f.close()
        return filename
        
    def rpc_printStaticGridDownload(self, filename, **kwargs):
        fpath = self.page.pageLocalDocument(filename)
        f = open(fpath, 'r')
        result = f.read() 
        f.close()
        os.remove(fpath)
        return result.decode('utf-8')
    
    def rpc_recordToPDF(self,table,pkey,template, **kwargs):
        record = self.db.table(table).record(pkey).output('bag')
        return self.page.rmlTemplate(path=template, record=record)


    
    
class GnrWsgiWebAppHandler(GnrBaseWebAppHandler): 
    def __init__(self, page):
        self.page = page
        self.gnrapp = page.site.gnrapp
        siteStatus = page.siteStatus
        if siteStatus['resetLocalizationTime'] and self.gnrapp.localizationTime < siteStatus['resetLocalizationTime']:
            self.gnrapp.buildLocalization()
        self.db = self.gnrapp.db

class BatchExecutor(object):
    def __init__(self, page):
        #self._page = weakref.ref(page)
        self._page = page
        
    def _get_page(self):
        if self._page:
            #return self._page()
            return self._page
    page = property(_get_page)

