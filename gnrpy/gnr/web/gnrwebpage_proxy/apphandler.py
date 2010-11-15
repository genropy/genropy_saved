# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package           : GenroPy web - see LICENSE for details
# module gnrwebcore : core module for genropy web framework
# Copyright (c)     : 2004 - 2007 Softwell sas - Milano 
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


"""
core.py

Created by Giovanni Porcari on 2007-03-24.
Copyright (c) 2007 Softwell. All rights reserved.
"""
import os
import re
import time

from gnr.core.gnrlang import gnrImport

import logging
gnrlogger = logging.getLogger('gnr.web.gnrwebcore')

from gnr.core.gnrbag import Bag
from gnr.core import gnrlist

from gnr.core.gnrlang import getUuid
from gnr.core.gnrstring import templateReplace, splitAndStrip, toText, toJson
from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy
ESCAPE_SPECIAL=re.compile(r'[\[\\\^\$\.\|\?\*\+\(\)\]\{\}]')

class GnrWebAppHandler(GnrBaseProxy): 
        
    def init(self, **kwargs):
        self.gnrapp = self.page.site.gnrapp
        siteStatus = self.page.siteStatus
        if siteStatus['resetLocalizationTime'] and self.gnrapp.localizationTime < siteStatus['resetLocalizationTime']:
            self.gnrapp.buildLocalization()
            
    def event_onEnd(self):
        self._finalize(self)
    
    def _finalize(self, page):
        self.db.closeConnection()
        
    @property
    def db(self):
        return self.page.db
        
    def getDb(self, dbId=None):
        return self.db # TODO: is a __getitem__ for back compatibility: see gnrsqldata DataResolver
    __getitem__ = getDb

    def _getAppId(self):
        if not hasattr(self, '_appId'):
            instances=self.page.site.config['instances'].keys()
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
            self.page.setInClientData(resultpath, result,attributes=dict(_error=error, __cls=_cls))
        else:
            return batch.run(**kwargs)
            
    def _batchFinder(self, batch):
        modName, clsName = batch.split(':')
        modPath = self.page.getResource(modName, 'py') or []
        if modPath:
            m = gnrImport(modPath)
            return getattr(m,clsName)
        else:
            raise Exception('Cannot import component %s' % modName)


    
    def rpc_getRecordCount(self, field=None, value=None,
                           table='',distinct=False, columns='',where='', 
                           relationDict=None, sqlparams=None, condition=None,
                           **kwargs):
        #sqlargs = dict(kwargs)
        if field:
            if not table:
                pkg, table, field = splitAndStrip(field, '.', fixed=-3)
                table = '%s.%s' % (pkg, table)
            where = '$%s = :value' % field
            kwargs['value'] = value
        tblobj = self.db.table(table)
        if isinstance(where, Bag):
            where, kwargs = self._decodeWhereBag(tblobj,where,kwargs)
        if condition:
            where = '(%s) AND (%s)' % (where, condition)
        return tblobj.query(columns=columns, distinct=distinct, where=where,
                            relationDict=relationDict, sqlparams=sqlparams, **kwargs).count()
                            
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
                          sqlContextName=None, one_one=None,virtual_columns=None, **kwargs):
        if one_one is not None:
            raise 'error'
            
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
                                            sqlContextName=sqlContextName,virtual_columns=virtual_columns, **kwargs)
                               
        if sqlContextName:
            joinBag = self._getSqlContextConditions(sqlContextName,target_fld=target_fld,from_fld=from_fld)
            if joinBag and joinBag['applymethod']:
                applyPars = self._getApplyMethodPars(kwargs)
                self.page.getPublicMethod('rpc', joinBag['applymethod'])(record,**applyPars)
        return (record,recInfo)
        
    def setContextJoinColumns(self, table,contextName='', reason=None, path=None, columns=None):
        tblobj = self.db.table(table)
        relation = tblobj.model.getRelation(path)
        target_fld = relation['many'].replace('.','_')
        from_fld = relation['one'].replace('.','_')
        ctxpath = '_sqlctx.columns.%s.%s_%s'  % (contextName,target_fld,from_fld)
        with self.page.pageStore() as store:
            reasons = store.getItem('%s._reasons' %ctxpath)
            if reasons is None:
                reasons = Bag()
                store.setItem('%s._reasons' %ctxpath,reasons)
            reasons.setItem(reason or '*',columns)
            query_set = set()
            for columns in reasons.values():
                query_set.update(columns.split(','))
            store.setItem(ctxpath, ','.join(query_set))

    def rpc_getRelatedSelection(self, from_fld, target_fld, relation_value=None,
                                columns='', query_columns=None, 
                                order_by=None, condition=None, 
                                js_resolver_one='relOneResolver', 
                                sqlContextName=None, **kwargs):
        if columns:
            raise 'COLUMNS PARAMETER NOT EXPECTED!!'
        columns = columns or query_columns
        t = time.time()
        joinBag = None
        if sqlContextName :
            joinBag = self._getSqlContextConditions(sqlContextName,target_fld=target_fld,from_fld=from_fld)
            if not columns:
                columns = self._getSqlContextColumns(sqlContextName,target_fld=target_fld,from_fld=from_fld)
                
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
        
        joinBag = None
        if sqlContextName:
            self._joinConditionsFromContext(query, sqlContextName)
            conditionKey = '%s_%s' % (target_fld.replace('.','_'), from_fld.replace('.','_'))
            rootCond = query.joinConditions.get(conditionKey)
            if rootCond:
                query.setJoinCondition(target_fld='*', from_fld='*', condition=rootCond['condition'], 
                                      one_one=rootCond['one_one'], **rootCond['params'])
        sel = query.selection()
        if joinBag and joinBag.get('applymethod'):
            applyPars = self._getApplyMethodPars(kwargs)
            self.page.getPublicMethod('rpc', joinBag['applymethod'])(sel,**applyPars)
                
        result = Bag()        
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
                            thermoId=None, thermofield=None, 
                            stopOnError=False, forUpdate=False, onRow=None, **kwargs):
        """ batchFactory: name of the Class, plugin of table, which executes the batch action
            thermoId:
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
                                    thermoId=thermoId, thermofield=thermofield, 
                                    stopOnError=stopOnError, forUpdate=forUpdate, onRow=onRow, **kwargs)
        return batch.run(pkeyList=pkeys)
            
    def setThermo(self, thermoId, progress_1=None, message_1=None, 
                   maximum_1=None, command=None, **kwargs):
        with self.page.pageStore() as store:
            if command == 'init':
                thermoBag = Bag()
            else:
                thermoBag = store.getItem('thermo_%s' % thermoId) or Bag()
            max = maximum_1 or thermoBag['t1.maximum']
            prog = progress_1 or thermoBag['t1.maximum']            
            if max and prog > max:
                command == 'end'
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
            store.setItem('thermo_%s' % thermoId, thermoBag)
        if thermoBag['stop']:
            return 'stop'
        
    def rpc_getThermo(self, thermoId, flag=None):
        with self.page.pageStore() as store:
            if flag=='stop':
                thermoBag = store.getItem('thermo_%s' % thermoId) or Bag()
                thermoBag['stop'] = True
                store.setItem('thermo_%s' % thermoId, thermoBag)
            else:
                thermoBag = store.getItem('thermo_%s' % thermoId) or Bag()
        return thermoBag
        
    def rpc_onSelectionDo(self, table, selectionName, command, callmethod=None, selectedRowidx=None, recordcall=False, **kwargs):
        result = None
        tblobj = self.db.table(table)
        selection = self.page.getUserSelection(table=tblobj, selectionName=selectionName,selectedRowidx=selectedRowidx)
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
        filename = filename or self.maintable or  self.request.uri.split('/')[-1]
        content = selection.output('tabtext', columns=columns, locale=locale)
        self.page.utils.sendFile(content,filename,'xls')
    
    def print_standard(self, selection, locale=None,**kwargs):
        columns = None # get columns from current view on client !
        if not columns:
            columns = [c for c in selection.allColumns if not c in ('pkey','rowidx')]
        outdata = selection.output('dictlist', columns=columns, asIterator=True)
        colAttrs = selection.colAttrs
        return self.page.pluginhandler.get_plugin('mako')(path='standard_print.tpl', striped='odd_row,even_row', outdata=outdata, colAttrs=colAttrs,
                title='Print List', header='Print List', columns=columns)
                
    def pdf_standard(self, selection, locale=None,**kwargs):
        columns = None # get columns from current view on client !
        if not columns:
            columns = [c for c in selection.allColumns if not c in ('pkey','rowidx')]
        outdata = selection.output('dictlist', columns=columns, asIterator=True)
        colAttrs = selection.colAttrs
        return self.page.rmlTemplate('standard_print.rml', outdata=outdata, colAttrs=colAttrs,
                title='Print List', header='Print List', columns=columns)
    
    def _getSqlContextConditions(self,contextName,target_fld=None,from_fld=None):
        result = self.page.pageStore().getItem('_sqlctx.conditions.%s' %contextName)
        if result and target_fld and from_fld:
            result = result[('%s_%s' %(target_fld, from_fld)).replace('.','_')]
        return result
        
    def _getSqlContextColumns(self,contextName,target_fld,from_fld):
        result = self.page.pageStore().getItem('_sqlctx.columns.%s' %contextName)
        if result:
            return result[('%s_%s' %(target_fld, from_fld)).replace('.','_')]

    def _joinConditionsFromContext(self, obj, sqlContextName):
        sqlContextBag = self._getSqlContextConditions(sqlContextName)
        storedata = self.page.pageStore().data
        if sqlContextBag:
            for joinBag in sqlContextBag.values():
                if joinBag['condition']: # may be a relatedcolumns only
                    params= (joinBag['params'] or Bag()).asDict(ascii=True)
                    for k,v in params.items():
                        if isinstance(v, basestring):
                            if v.startswith('^'):
                                params[k] = storedata[v[1:]]
                            elif hasattr(self, '%s_%s' % (sqlContextName, v)):
                                params[k] = getattr(self, '%s_%s' % (sqlContextName, v))()
                    obj.setJoinCondition(target_fld=joinBag['target_fld'], from_fld=joinBag['from_fld'], condition=joinBag['condition'], 
                                            one_one=joinBag['one_one'], **params)
      
    def _getApplyMethodPars(self,kwargs,**optkwargs):
        result= dict([(k[6:],v) for k,v in kwargs.items() if k.startswith('apply_')])
        if optkwargs:
            result.update(optkwargs)
        return result
        
    def rpc_getSelection(self, table='',distinct=False, columns='',where='',condition=None,
                            order_by=None, limit=None, offset=None, group_by=None, having=None,
                            relationDict=None, sqlparams=None, row_start='0', row_count='0',
                            recordResolver=True, selectionName='', structure=False, numberedRows=True,
                            pkeys=None, fromSelection=None, applymethod=None, totalRowCount=False,
                            selectmethod=None,selectmethod_prefix='rpc', expressions=None,sum_columns=None,
                            sortedBy=None,excludeLogicalDeleted=True, **kwargs):
        t = time.time()
        tblobj = self.db.table(table)

        row_start = int(row_start)
        row_count = int(row_count)
        newSelection=True
        formats={}
        for k in kwargs.keys():
            if k.startswith('format_'):
                formats[7:]=kwargs.pop(k)
        
        if selectionName.startswith('*'):
            if selectionName=='*':
                selectionName=self.page.page_id
            else:
                selectionName=selectionName[1:]
        elif selectionName:
            selection = self.page.unfreezeSelection(tblobj, selectionName)
            if selection is not None:
                if sortedBy and  ','.join(selection.sortedBy or [])!= sortedBy:
                    selection.sort(sortedBy)
                    selection.freezeUpdate()
                debug='fromPickle'
                resultAttributes={}
                newSelection=False            
        if newSelection:
            debug='fromDb'
            if selectmethod:
                selecthandler = self.page.getPublicMethod(selectmethod_prefix, selectmethod)
            else:
                selecthandler = self._default_getSelection   
            columns = self._getSelection_columns(tblobj,columns,expressions=expressions)
            selection = selecthandler(tblobj=tblobj, table=table,distinct=distinct, columns=columns,where=where,condition=condition,
                               order_by=order_by,limit=limit, offset=offset, group_by=group_by,having=having,
                               relationDict=relationDict, sqlparams=sqlparams, row_start=row_start,row_count=row_count,
                               recordResolver=recordResolver,selectionName=selectionName, structure=structure,pkeys=pkeys, fromSelection=fromSelection,
                               sortedBy=sortedBy,excludeLogicalDeleted=excludeLogicalDeleted, **kwargs)
            if applymethod:
                applyPars = self._getApplyMethodPars(kwargs)
                self.page.getPublicMethod('rpc', applymethod)(selection,**applyPars)
                
            if selectionName:
                selection.setKey('rowidx')
                selectionPath = self.page.freezeSelection(selection,selectionName)
                with self.page.userStore() as store:
                    store.setItem('current.table.%s.last_selection_path' %table.replace('.','_'),selectionPath)
            resultAttributes=dict(table=table, method='app.getSelection',selectionName=selectionName, row_count=row_count,
                                               totalrows=len(selection))
        generator = selection.output(mode='generator',offset=row_start,limit=row_count, formats=formats)
        _addClassesDict = dict([(k,v['_addClass']) for k,v in selection.colAttrs.items() if '_addClass' in v])
        data = self.gridSelectionData(selection, generator, logicalDeletionField=tblobj.logicalDeletionField,
                                      recordResolver=recordResolver, numberedRows=numberedRows,_addClassesDict=_addClassesDict)
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
        if sum_columns:
            for col in sum_columns.split(','):
                col=col.strip()
                resultAttributes['sum_%s' % col]=data.sum('#a.%s'%col)
            
        return (result,resultAttributes)
             
             
    def _getSelection_columns(self,tblobj,columns,expressions=None):
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
        return columns
        
        
    def _default_getSelection(self,tblobj=None, table=None,distinct=None, columns=None,where=None,condition=None,
                            order_by=None,limit=None, offset=None, group_by=None,having=None,
                            relationDict=None, sqlparams=None, row_start=None,row_count=None,
                            recordResolver=None, selectionName=None, pkeys=None, fromSelection=None,
                            sortedBy=None, sqlContextName=None,
                            excludeLogicalDeleted=True, **kwargs):
        sqlContextBag = None
        if sqlContextName:
            sqlContextBag = self._getSqlContextConditions(sqlContextName)
        if fromSelection:
            fromSelection = self.page.unfreezeSelection(tblobj, fromSelection)
            pkeys = fromSelection.output('pkeylist')
        if pkeys:
            where='t0.%s in :pkeys' % tblobj.pkey
            if isinstance(pkeys, basestring):
                pkeys = pkeys.split(',')
            kwargs['pkeys'] = pkeys
        elif isinstance(where, Bag):
            where, kwargs = self._decodeWhereBag(tblobj, where, kwargs)
        if condition and not pkeys:
            where = '( %s ) AND ( %s )' % (where, condition)
        query=tblobj.query(columns=columns,distinct=distinct, where=where,
                        order_by=order_by,limit=limit, offset=offset, group_by=group_by,having=having,
                        relationDict=relationDict, sqlparams=sqlparams,locale=self.page.locale,
                        excludeLogicalDeleted=excludeLogicalDeleted,**kwargs)
        if sqlContextName: 
            self._joinConditionsFromContext(query, sqlContextName)
        selection = query.selection(sortedBy=sortedBy, _aggregateRows=True)
       #if sqlContextBag: 
       #    THIS BLOCK SHOULD ALLOW US TO HAVE AN APPLYMETHOD INSIDE SQLCONTEXT.
       #    IT DOES NOT WORK BUT WE THINK IT'S USELESS
       #    joinBag = sqlContextBag['%s_%s' % (target_fld.replace('.','_'), from_fld.replace('.','_'))]
       #    if joinBag and joinBag.get('applymethod'):
       #        applyPars = self._getApplyMethodPars(kwargs)
       #        self.page.getPublicMethod('rpc', joinBag['applymethod'])(selection,**applyPars)
       #            
        return selection
        
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
    def _decodeWhereBag(self, tblobj, where, kwargs):
        if hasattr(self.page,'getSelection_filters'):
            selection_filters = self.page.getSelection_filters()
            if selection_filters:
                new_where=Bag()
                new_where.setItem('filter',selection_filters)
                new_where.setItem('where',where, jc='and')
                where=new_where
        page = self.page
        customOpCbDict=dict([(x[12:],getattr(page,x)) for x in dir(page) if x.startswith('customSqlOp_') ])
        return tblobj.sqlWhereFromBag(where, kwargs,customOpCbDict=customOpCbDict)
            
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
    
    def gridSelectionData(self, selection, outsource, recordResolver, numberedRows, logicalDeletionField,_addClassesDict=None):
        result = Bag()  
        for j,row in enumerate(outsource) :
            row = dict(row)
            _customClasses = (row.get('_customClasses','') or '').split(' ')
            pkey = row.pop('pkey', None)
            isDeleted=row.pop('_isdeleted',None)
            if isDeleted:
                _customClasses.append('logicalDeleted')
            if _addClassesDict:
                for fld,_class in _addClassesDict.items():
                    if row[fld]:
                        _customClasses.append(_class)
                        
            if numberedRows or not pkey:
                row_key='r_%i'%j
            else:
                row_key = toText(pkey).replace('.','_')
            result.setItem(row_key, None, _pkey=pkey or row_key,
                           _target_fld = '%s.%s' % (selection.dbtable.fullname, selection.dbtable.pkey),
                           _relation_value=pkey, _resolver_name='relOneResolver',
                           _attributes=row, _removeNullAttributes=False, _customClasses=' '.join(_customClasses))
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
    # 
    def _getRecord_locked(self,tblobj,record,recInfo):
        #locked,aux=self.page.site.lockRecord(self.page,tblobj.fullname,record[tblobj.pkey])
        locked=False
        aux=[]
        if locked:
            recInfo['lockId']=aux
            return
        for f in aux:
            recInfo['locking_%s'%f]=aux[f]
            
    def rpc_getRecord(self, table=None, dbtable=None, pkg=None, pkey=None,
                    ignoreMissing=True, ignoreDuplicate=True, lock=False,readOnly=False,
                    from_fld=None, target_fld=None, sqlContextName=None, applymethod=None,
                    js_resolver_one='relOneResolver', js_resolver_many='relManyResolver', 
                    loadingParameters=None, eager=None,virtual_columns=None,**kwargs):
        t = time.time()
        dbtable = dbtable or table
        if pkg:
            dbtable='%s.%s' % (pkg, dbtable)
        tblobj = self.db.table(dbtable)
        if pkey is not None: 
            kwargs['pkey'] = pkey
        elif lock:
            lock=False
        if lock:
            kwargs['for_update']=True
        rec = tblobj.record(eager=eager or self.page.eagers.get(dbtable),
                            ignoreMissing=ignoreMissing,ignoreDuplicate=ignoreDuplicate,
                            sqlContextName=sqlContextName,virtual_columns=virtual_columns,**kwargs)
        if sqlContextName:
            self._joinConditionsFromContext(rec, sqlContextName)
            
        if (pkey=='*newrecord*'):
            record = rec.output('newrecord', resolver_one=js_resolver_one, resolver_many=js_resolver_many)
        else:
            record = rec.output('bag', resolver_one=js_resolver_one, resolver_many=js_resolver_many)
        pkey = record[tblobj.pkey] or '*newrecord*'
        newrecord = pkey=='*newrecord*'
        recInfo = dict(_pkey=pkey,
                        caption=tblobj.recordCaption(record,newrecord),
                        _newrecord=newrecord, sqlContextName=sqlContextName)
        #if lock and not newrecord:
        if not newrecord and not readOnly:
            recInfo['updatable']=tblobj.check_updatable(record)
            recInfo['deletable']=tblobj.check_deletable(record)
            if lock:
                self._getRecord_locked(tblobj,record,recInfo)            
        loadingParameters = loadingParameters or {}
        defaultParameters=dict([(k[8:],v) for k,v in kwargs.items() if k.startswith('default_')])
        loadingParameters.update(defaultParameters)
        method = None
        if loadingParameters:
            method = loadingParameters.pop('method',None)
        if method:
            handler = self.page.getPublicMethod('rpc', method)
        else:
            if dbtable == self.page.maintable:
                method = 'onLoading' # TODO: fall back on the next case if onLoading is missing?
                                     #       (or maybe execute both if they exist)
            else:
                #self.page.gnotify('getRecord', dbtable, True)
                method = 'onLoading_%s' % dbtable.replace('.','_')
            handler = getattr(self.page, method, None)
            
        if handler:
            if defaultParameters and newrecord:
                self.setRecordDefaults(record,defaultParameters)
            handler(record, newrecord, loadingParameters,recInfo)
        elif newrecord and loadingParameters:
            self.setRecordDefaults(record,loadingParameters)

        if applymethod:
            applyPars = self._getApplyMethodPars(kwargs, newrecord=newrecord,loadingParameters=loadingParameters,
                                                          recInfo=recInfo,tblobj=tblobj)
            self.page.getPublicMethod('rpc', applymethod)(record,**applyPars)
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
        * columns: columns that are involved into the query
        * auxColumns: showed only as result, not involved in the search.
        * hiddenColumns: data that is retrieved but is not showed.
        * rowcaption: what you see into the field. Often is different from 
                      what you set with dbselect
        * condition: more condition into the query. Every kwargs params that 
                    starts with condition_  are the variables involved in the 'where' clause.
        * selectmethod: custom rpc_method you can use to make the query on the server.
        * weakCondition: will apply the condition if there is a result, but if there is no result for the condition
                         then the condition will not be used. A selectmethod over-rides this attribute.
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
        querycolumns = tblobj.getQueryFields(columns,captioncolumns)
        showcolumns = gnrlist.merge(captioncolumns, tblobj.columnsFromString(auxColumns))
        resultcolumns = gnrlist.merge(showcolumns, captioncolumns, tblobj.columnsFromString(hiddenColumns))
        if alternatePkey and not alternatePkey in resultcolumns:
            resultcolumns.append("$%s"%alternatePkey if not alternatePkey.startswith('$') else alternatePkey)
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
        columns_concat="ARRAY_TO_STRING(ARRAY[%s], ' ')" % ','.join(querycolumns)
        if len(result) == 0: # few results from the startswith query on first col
            #self.page.gnotify('dbselect','filter')
            regsrc = [x for x in re.split(" ", ESCAPE_SPECIAL.sub('',querystring)) if x]
            if regsrc:
                whereargs = dict([('w%i' % i, '(^|\\W)%s' % w.strip()) for i,w in enumerate(regsrc)])
                #where =" AND ".join(["(%s)  ~* :w%i" % (" || ' ' || ".join(querycolumns), i) for i,w in enumerate(regsrc)])
                where =" AND ".join(["(%s)  ~* :w%i" % (columns_concat, i) for i,w in enumerate(regsrc)])
                
                result = getSelection(where, **whereargs)
            
        if len(result) == 0:
            #self.page.gnotify('dbselect','contained')
            whereargs = dict([('w%i' % i, '%%%s%%' % w.strip()) for i,w in enumerate(srclist)])
            
            #where =" AND ".join(["(%s)  ILIKE :w%i" % (" || ' ' || ".join(querycolumns), i) for i,w in enumerate(srclist)])
            where =" AND ".join(["(%s)  ILIKE :w%i" % (columns_concat, i) for i,w in enumerate(srclist)])
            result = getSelection(where, **whereargs)
                        
        return result

    def _relPathToCaption(self, table, relpath):
        if not relpath: return ''
        tbltree = self.db.relationExplorer(table, dosort=False, pyresolver=True)
        fullcaption = tbltree.cbtraverse(relpath, lambda node: self.page._(node.getAttr('name_long')))
        return ':'.join(fullcaption)
                                                    
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
        filename = filename or self.page.maintable or  self.page.request.path_info.split('/')[-1]
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
        charwidths = {
            '0': 262.637,'1': 262.637,'2': 262.637,'3': 262.637,'4': 262.637,'5': 262.637,'6': 262.637,
            '7': 262.637,'8': 262.637,'9': 262.637,'a': 262.637,'b': 262.637,'c': 262.637,'d': 262.637,
            'e': 262.637,'f': 146.015,'g': 262.637,'h': 262.637,'i': 117.096,'j': 88.178,'k': 233.244,
            'l': 88.178,'m': 379.259,'n': 262.637,'o': 262.637,'p': 262.637,'q': 262.637,'r': 175.407,
            's': 233.244,'t': 117.096,'u': 262.637,'v': 203.852,'w': 321.422,'x': 203.852,'y': 262.637,
            'z': 233.244,'A': 321.422,'B': 321.422,'C': 350.341,'D': 350.341,'E': 321.422,'F': 291.556,
            'G': 350.341,'H': 321.422,'I': 146.015,'J': 262.637,'K': 321.422,'L': 262.637,'M': 379.259,
            'N': 321.422,'O': 350.341,'P': 321.422,'Q': 350.341,'R': 321.422,'S': 321.422,'T': 262.637,
            'U': 321.422,'V': 321.422,'W': 496.356,'X': 321.422,'Y': 321.422,'Z': 262.637,' ': 146.015,
            '!': 146.015,'"': 175.407,'#': 262.637,'$': 262.637,'%': 438.044,'&': 321.422,'\'': 88.178,
            '(': 175.407,')': 175.407,'*': 203.852,'+': 291.556,',': 146.015,'-': 175.407,'.': 146.015,
            '/': 146.015,':': 146.015,';': 146.015,'<': 291.556,'=': 291.556,'>': 291.556,'?': 262.637,
            '@': 496.356,'[': 146.015,'\\': 146.015,']': 146.015,'^': 203.852,'_': 262.637,'`': 175.407,
            '{': 175.407,'|': 146.015,'}': 175.407,'~': 291.556}
        def fitwidth(data, bold=False):
            '''Try to autofit Arial 10'''
            units = 220
            for char in str(data):
                if char in charwidths:
                    units += charwidths[char]
                else:
                    units += charwidths['0']
            if bold:
                units *= 1.1
            return max(units, 700)
        import xlwt
        w = xlwt.Workbook(encoding='latin-1')
        filename = self._exportFileNameClean(filename)
        ws = w.add_sheet(filename[:31])
        
        float_style = xlwt.XFStyle()
        float_style.num_format_str = '#,##0.00'
        int_style = xlwt.XFStyle()
        int_style.num_format_str = '#,##0'
        
        font0 = xlwt.Font()
        font0.name = 'Times New Roman'
        font0.bold = True
        hstyle = xlwt.XFStyle()
        hstyle.font = font0
        colsizes=dict()
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
            #self.page._(self.tblobj.column(header).name_long)
            ws.write(0, c, header, hstyle)
            colsizes[c]=max(colsizes.get(c,0),fitwidth(header))
            
            
        for i,row in enumerate(storebag):
            r = row.getAttr()
            for c,col in enumerate(columns):
                value=r.get(col)
                if coltype[col] in ('R', 'F','N'):
                    ws.write(i+1, c,value,  float_style)
                elif coltype[col] in ('L','I'):
                    ws.write(i+1, c, value, int_style)
                else:
                    value=self.page.toText(r.get(col))
                    ws.write(i+1, c, value)
                colsizes[c]=max(colsizes.get(c,0),fitwidth(value))
        
        for colindex,colsize in colsizes.items():
            ws.col(colindex).width=colsize
        if not filename.lower().endswith('.xls'):
            filename += '.xls'
        fpath = self.page.temporaryDocument(filename)
        w.save(fpath)
        return self.page.temporaryDocumentUrl(filename)
        
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
        if not filename.lower().endswith('.html') or filename.lower().endswith('.htm'):
            filename+='.html'
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
        
        result = self.page.pluginhandler.get_plugin('mako')(path=makotemplate, striped='odd_row,even_row', outdata=outdata, colAttrs=colAttrs,
                                            columns=columns, meta=kwargs)

        #fpath = self.page.pageLocalDocument(filename)
        fpath = self.page.temporaryDocument(filename)
        f = open(fpath, 'w')
        if isinstance(result, unicode):
            result = result.encode('utf-8')
        f.write(result)
        f.close()
        return self.page.temporaryDocumentUrl(filename)
        #return filename
        
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


    
class BatchExecutor(object):
    def __init__(self, page):
        #self._page = weakref.ref(page)
        self._page = page
        
    def _get_page(self):
        if self._page:
            #return self._page()
            return self._page
    page = property(_get_page)

