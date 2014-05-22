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

#apphandler.py

#Created by Giovanni Porcari on 2007-03-24.
#Copyright (c) 2007 Softwell. All rights reserved.

import os
import re
import time
from datetime import datetime

from gnr.core.gnrlang import gnrImport

import logging

gnrlogger = logging.getLogger(__name__)

from gnr.core.gnrbag import Bag
from gnr.core import gnrlist

from gnr.core.gnrlang import uniquify
from gnr.core.gnrdecorator import extract_kwargs,public_method,debug_info
from gnr.core.gnrstring import templateReplace, splitAndStrip, toText, toJson,fromJson
from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy
from gnr.web.gnrwebstruct import cellFromField
from gnr.sql.gnrsql_exceptions import GnrSqlSaveException, GnrSqlDeleteException
from gnr.sql.gnrsql import GnrSqlException


ESCAPE_SPECIAL = re.compile(r'[\[\\\^\$\.\|\?\*\+\(\)\]\{\}]')

class GnrWebAppHandler(GnrBaseProxy):
    """A class for web applications handlement"""
    def init(self, **kwargs):
        """TODO"""
        self.gnrapp = self.page.site.gnrapp
        siteStatus = self.page.siteStatus
        if siteStatus['resetLocalizationTime'] and self.gnrapp.localizationTime < siteStatus['resetLocalizationTime']:
            self.gnrapp.buildLocalization()

    def event_onEnd(self):
        """TODO"""
        self._finalize(self)

    def _finalize(self, page):
        self.db.closeConnection()

    @property
    def db(self):
        """TODO"""
        return self.page.db

    def getDb(self, dbId=None):
        """TODO
        
        :param dbId: TODO"""
        return self.db # TODO: is a __getitem__ for back compatibility: see gnrsqldata DataResolver

    __getitem__ = getDb

    def _getAppId(self):
        if not hasattr(self, '_appId'):
            instances = self.page.site.config['instances'].keys()
            if len(instances) == 1:
                self._appId = instances[0]
            else:
                self._appId = self.page.request.uri.split['/'][2]
                if not self._appId in instances:
                    self._appId = instances[0]
        return self._appId

    appId = property(_getAppId)

    def getPackages(self):
        """TODO"""
        return [[pkgobj.name_full, pkg] for pkg, pkgobj in self.db.packages.items()]

    rpc_getPackages = getPackages

    def getTables(self, pkg=None):
        """Extract a couple with the istance names and the name of the
        :ref:`database tables <table>` from a :ref:`package <packages>` you specify
        with the *pkg* attribute. Return the extracted couples as a list of lists. If no
        tables are in the package then the method returns an empty list
        
        :param pkg: MANDATORY. The :ref:`package <packages>` from which
                    the tables are extracted"""
        tables = self.db.package(pkg).tables
        if tables:
            return [[tblobj.name_full.capitalize(), tbl] for tbl, tblobj in tables.items()]
        return []

    rpc_getTables = getTables

    def getTablesTree(self):
        """Set a :class:`Bag <gnr.core.gnrbag.Bag>` with the structure of the :ref:`database tables
        <table>` of a :ref:`package <packages>`"""
        result = Bag()
        for pkg, pkgobj in self.db.packages.items():
            if pkgobj.attributes.get('reserved', 'n').upper() != 'Y':
                tblbag = Bag()
                label = pkgobj.name_full.capitalize()
                result.setItem(pkg, tblbag, label=label)
                for tbl, tblobj in pkgobj.tables.items():
                    label = tblobj.name_full.capitalize()
                    tblbag.setItem(tbl, None, label=label, tableid='%s.%s' % (pkg, tbl))
        return result

    rpc_getTablesTree = getTablesTree

    def getTableFields(self, pkg='', table='', **kwargs):
        """TODO
        
        :param pkg: the :ref:`package <packages>`
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)"""
        if not pkg:
            pkg, table = table.split('.')
        return self.dbStructure(path='%s.tables.%s.relations' % (pkg, table))

    rpc_getTableFields = getTableFields

    def dbStructure(self, path='', **kwargs):
        """TODO
        
        :param path: the path of the database structure"""
        curr = self.db.packages
        if path:
            curr = curr[path]
            path = path + '.'
        return self._dbStructureInner(curr, path)

    rpc_dbStructure = dbStructure

    def _dbStructureInner(self, where, path):
        result = Bag()
        for elem in where:
            if hasattr(elem, 'resolver'):
                attributes = {}
                attributes.update(elem.getAttr())
                if 'joiner' in attributes:
                    joiner = attributes.pop('joiner')
                    attributes.update(joiner or {})
                label = elem.label
                attributes['caption'] = attributes.get('name_long')
                if elem.resolver != None:
                    result.setItem(label, "genro.rpc.remoteResolver('app.dbStructure',{path:'%s'})" % (path + label),
                                   attributes, _T='JS')
                else:
                    value = elem.value
                    if hasattr(value, '__len__'):
                        if len(value):
                            result.setItem(label,
                                           "genro.rpc.remoteResolver('app.dbStructure',{path:'%s'})" % (path + label),
                                           attributes, _T='JS')
                        else:
                            result.setItem(label, None)
                    else:
                        result.setItem(label, elem.value, attributes)
            elif hasattr(where, '__getitem__'):
                if isinstance(where, Bag):
                    n = where.getNode(elem)
                    value = n.value
                    attributes = n.getAttr()
                else:
                    value = where[elem]
                    attributes = getattr(value, 'attributes', {})
                label = elem
                attributes['caption'] = attributes.get('name_long')
                if len(value):
                    result.setItem(label, "genro.rpc.remoteResolver('app.dbStructure',{path:'%s'})" % (path + label),
                                   attributes, _T='JS')
                else:
                    result.setItem(label, None, attributes)
            else:
                result.setItem(elem, None)
        return result


    def rpc_batchDo(self, batch, resultpath, forked=False, **kwargs):
        """Execute a :ref:`batch`
        
        :param batch: the :ref:`batch` to be executed
        :param resultpath: TODO
        :param forked: boolean. TODO"""
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
            result = batch.run(**kwargs)
            error = None
            _cls = None
            self.page.setInClientData(resultpath, result, attributes=dict(_error=error, __cls=_cls))
        else:
            return batch.run(**kwargs)

    def _batchFinder(self, batch):
        modName, clsName = batch.split(':')
        modPath = self.page.getResource(modName, 'py') or []
        if modPath:
            m = gnrImport(modPath)
            return getattr(m, clsName)
        else:
            raise Exception('Cannot import component %s' % modName)
    
    @public_method    
    def getRecordCount(self, field=None, value=None,
                           table='', distinct=False, columns='', where='',
                           relationDict=None, sqlparams=None,condition=None,
                           **kwargs):
        """TODO
        
        :param field: TODO
        :param value: TODO
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param distinct: boolean, ``True`` for getting a "SELECT DISTINCT"
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        :param where: the sql "WHERE" clause. For more information check the :ref:`sql_where`
                      section
        :param relationDict: TODO
        :param sqlparams: TODO
        :param condition: the :ref:`sql_condition` of the count"""
        #sqlargs = dict(kwargs)
        if field:
            if not table:
                pkg, table, field = splitAndStrip(field, '.', fixed=-3)
                table = '%s.%s' % (pkg, table)
            where = '$%s = :value' % field
            kwargs['value'] = value
        tblobj = self.db.table(table)
        if isinstance(where, Bag):
            where, kwargs = self._decodeWhereBag(tblobj, where, kwargs)
        if condition:
            where = '( %s ) AND ( %s )' % (where, condition) if where else condition
        return tblobj.query(columns=columns, distinct=distinct, where=where,
                            relationDict=relationDict, sqlparams=sqlparams, **kwargs).count()

    
    @public_method
    def getRelatedRecord(self, from_fld=None, target_fld=None, pkg=None, pkey=None, ignoreMissing=True,
                             ignoreDuplicate=True,
                             js_resolver_one='relOneResolver', js_resolver_many='relManyResolver',
                             sqlContextName=None, virtual_columns=None,_eager_level=0,_eager_record_stack=None,_storename=None,resolver_kwargs=None,
                             loadingParameters=None, _debug_info=None,**kwargs):
        """TODO
        
        ``getRelatedRecord()`` method is decorated with the :meth:`public_method <gnr.core.gnrdecorator.public_method>` decorator
        
        :param from_fld: TODO
        :param target_fld: TODO
        :param pkg: the :ref:`package <packages>`
        :param pkey: the record :ref:`primary key <pkey>`
        :param ignoreMissing: boolean. TODO
        :param ignoreDuplicate: boolean. TODO
        :param js_resolver_one: TODO
        :param js_resolver_many: TODO
        :param sqlContextName: TODO
        :param virtual_columns: TODO"""
        
        pkg, tbl, related_field = target_fld.split('.')
        table = '%s.%s' % (pkg, tbl)
        if pkey is None:
            tbl_pkey = self.db.table(table).pkey
            pkey = kwargs.pop(tbl_pkey, None)
        if pkey in (None,
                    '') and not related_field in kwargs: # and (not kwargs): # related record from a newrecord or record without link
            pkey = '*newrecord*'
        loadingParameters = loadingParameters or dict()
        loadingParameters.update(resolver_kwargs or dict())
        record, recInfo = self.getRecord(table=table, from_fld=from_fld, target_fld=target_fld, pkey=pkey,
                                             ignoreMissing=ignoreMissing, ignoreDuplicate=ignoreDuplicate,
                                             js_resolver_one=js_resolver_one, js_resolver_many=js_resolver_many,
                                             sqlContextName=sqlContextName, virtual_columns=virtual_columns,_storename=_storename,
                                             _eager_level=_eager_level,_eager_record_stack=_eager_record_stack,loadingParameters=loadingParameters,**kwargs)

        if sqlContextName:
            joinBag = self._getSqlContextConditions(sqlContextName, target_fld=target_fld, from_fld=from_fld)
            if joinBag and joinBag['applymethod']:
                applyPars = self._getApplyMethodPars(kwargs)
                self.page.getPublicMethod('rpc', joinBag['applymethod'])(record, **applyPars)
        return (record, recInfo)


    @public_method
    def getRelatedSelection(self, from_fld, target_fld, relation_value=None,
                                columns='', query_columns=None,
                                condition=None, js_resolver_one='relOneResolver',
                                sqlContextName=None, **kwargs):
        """TODO
        
        ``getRelatedSelection()`` method is decorated with the :meth:`public_method <gnr.core.gnrdecorator.public_method>` decorator
        
        :param from_fld: TODO
        :param target_fld: TODO
        :param relation_value: TODO
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        :param query_columns: TODO
        :param condition: the :ref:`sql_condition` of the selection
        :param js_resolver_one: TODO
        :param sqlContextName: TODO"""
        if query_columns:
            print 'QUERY COLUMNS PARAMETER NOT EXPECTED!!'
        columns = columns or query_columns
        t = time.time()
        joinBag = None
        resultAttributes = dict()
        if sqlContextName:
            joinBag = self._getSqlContextConditions(sqlContextName, target_fld=target_fld, from_fld=from_fld)
          # if not columns:
          #     columns = self._getSqlContextColumns(sqlContextName, target_fld=target_fld, from_fld=from_fld)

        columns = columns or '*'
        pkg, tbl, related_field = target_fld.split('.')
        dbtable = '%s.%s' % (pkg, tbl)
        if not relation_value:
            kwargs['limit'] = 0
        where = "$%s = :val_%s" % (related_field, related_field)
        kwargs[str('val_%s' % related_field)] = relation_value
        if condition:
            where = ' ( %s ) AND ( %s ) ' % (where, condition)
        query = self.db.query(dbtable, columns=columns, where=where,
                              sqlContextName=sqlContextName, **kwargs)

        joinBag = None
        if sqlContextName:
            self._joinConditionsFromContext(query, sqlContextName)
            conditionKey = '%s_%s' % (target_fld.replace('.', '_'), from_fld.replace('.', '_'))
            rootCond = query.joinConditions.get(conditionKey)
            if rootCond:
                query.setJoinCondition(target_fld='*', from_fld='*', condition=rootCond['condition'],
                                       one_one=rootCond['one_one'], **rootCond['params'])
        sel = query.selection()
        if joinBag and joinBag.get('applymethod'):
            applyPars = self._getApplyMethodPars(kwargs)
            applyresult = self.page.getPublicMethod('rpc', joinBag['applymethod'])(sel, **applyPars)
            if applyresult:
                resultAttributes.update(applyresult)

        result = Bag()
        relOneParams = dict(_target_fld='%s.%s' % (dbtable, self.db.table(dbtable).pkey),
                            _from_fld='',
                            _resolver_name=js_resolver_one,
                            _sqlContextName=sqlContextName
                            )
        for j, row in enumerate(sel):
            row = dict(row)
            pkey = row.pop('pkey')
            spkey = toText(pkey)
            result.setItem('%s' % spkey, None, _pkey=spkey, _relation_value=pkey,
                           _attributes=row, _removeNullAttributes=False, **relOneParams)

        relOneParams.update(dict([(k, None) for k in sel.colAttrs.keys() if not k == 'pkey']))
        resultAttributes.update(dbtable=dbtable, totalrows=len(sel))
        resultAttributes.update({'servertime': int((time.time() - t) * 1000),
                                 'newproc': getattr(self, 'self.newprocess', 'no'),
                                 'childResolverParams': '%s::JS' % toJson(relOneParams)
                                 })

        return (result, resultAttributes)
        
    @public_method
    def runSelectionBatch(self, table, selectionName=None, batchFactory=None, pkeys=None,
                              thermoId=None, thermofield=None,
                              stopOnError=False, forUpdate=False, onRow=None, **kwargs):
        """TODO
        
        ``runSelectionBatch()`` method is decorated with the :meth:`public_method <gnr.core.gnrdecorator.public_method>` decorator
        
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param selectionName: TODO
        :param batchFactory: name of the Class, plugin of table, which executes the batch action
        :param pkeys: TODO
        :param thermoId: TODO
        :param thermofield: the field of the main table to use for thermo display or * for record caption
        :param stopOnError: at the first error stop execution
        :param forUpdate: load records for update and commit at end (always use for writing batch)
        :param onRow: optional method to execute on each record in selection, use if no batchFactory is given"""
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
        """TODO
        
        :param thermoId: TODO
        :param progress_1: TODO
        :param message_1: TODO
        :param maximum_1: TODO
        :param command: TODO"""
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
                thermoBag['status'] = 'end'
                thermoBag['message'] = '!!Execution completed'
            elif command == 'stopped':
                thermoBag['status'] = 'stopped'
                thermoBag['message'] = '!!Execution stopped'
            else:
                params = dict(progress_1=progress_1, message_1=message_1, maximum_1=maximum_1)
                params.update(kwargs)
                for k, v in params.items():
                    if v is not None:
                        key, thermo = k.split('_')
                        thermoBag['t%s.%s' % (thermo, key)] = v
            store.setItem('thermo_%s' % thermoId, thermoBag)
        if thermoBag['stop']:
            return 'stop'

    def rpc_getThermo(self, thermoId, flag=None):
        """TODO
        
        :param thermoId: TODO
        :param flag: TODO"""
        with self.page.pageStore() as store:
            if flag == 'stop':
                thermoBag = store.getItem('thermo_%s' % thermoId) or Bag()
                thermoBag['stop'] = True
                store.setItem('thermo_%s' % thermoId, thermoBag)
            else:
                thermoBag = store.getItem('thermo_%s' % thermoId) or Bag()
        return thermoBag

    def rpc_onSelectionDo(self, table, selectionName, command, callmethod=None, selectedRowidx=None, recordcall=False,
                          **kwargs):
        """TODO
        
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param selectionName: TODO
        :param command: TODO
        :param callmethod: TODO
        :param selectedRowidx: TODO
        :param recordcall: boolean. TODO"""
        result = None
        tblobj = self.db.table(table)
        selection = self.page.getUserSelection(table=tblobj, selectionName=selectionName, selectedRowidx=selectedRowidx)
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

    def export_standard(self, selection, locale=None, columns=None, filename=None, **kwargs):
        """TODO
        
        :param selection: TODO
        :param locale: TODO
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        :param filename: TODO"""
        filename = filename or self.maintable or  self.request.uri.split('/')[-1]
        content = selection.output('tabtext', columns=columns, locale=locale)
        self.page.utils.sendFile(content, filename, 'xls')

    def print_standard(self, selection, locale=None, **kwargs):
        """TODO
        
        :param selection: TODO
        :param locale: TODO"""
        columns = None # get columns from current view on client !
        if not columns:
            columns = [c for c in selection.allColumns if not c in ('pkey', 'rowidx')]
        outdata = selection.output('dictlist', columns=columns, asIterator=True)
        colAttrs = selection.colAttrs
        return self.page.pluginhandler.get_plugin('mako')(path='standard_print.tpl', striped='odd_row,even_row',
                                                          outdata=outdata, colAttrs=colAttrs,
                                                          title='Print List', header='Print List', columns=columns)

    def pdf_standard(self, selection, locale=None, **kwargs):
        """TODO
        
        :param selection: TODO
        :param locale: TODO"""
        columns = None # get columns from current view on client !
        if not columns:
            columns = [c for c in selection.allColumns if not c in ('pkey', 'rowidx')]
        outdata = selection.output('dictlist', columns=columns, asIterator=True)
        colAttrs = selection.colAttrs
        return self.page.rmlTemplate('standard_print.rml', outdata=outdata, colAttrs=colAttrs,
                                     title='Print List', header='Print List', columns=columns)

    def _getSqlContextConditions(self, contextName, target_fld=None, from_fld=None):
        result = self.page.pageStore().getItem('_sqlctx.conditions.%s' % contextName)
        if result and target_fld and from_fld:
            result = result[('%s_%s' % (target_fld, from_fld)).replace('.', '_')]
        return result

   #def _getSqlContextColumns(self, contextName, target_fld, from_fld):
   #    result = self.page.pageStore().getItem('_sqlctx.columns.%s' % contextName)
   #    if result:
   #        return result[('%s_%s' % (target_fld, from_fld)).replace('.', '_')]

    def _joinConditionsFromContext(self, obj, sqlContextName):
        sqlContextBag = self._getSqlContextConditions(sqlContextName)
        storedata = self.page.pageStore().data
        if sqlContextBag:
            for joinBag in sqlContextBag.values():
                if joinBag['condition']: # may be a relatedcolumns only
                    params = (joinBag['params'] or Bag()).asDict(ascii=True)
                    for k, v in params.items():
                        if isinstance(v, basestring):
                            if v.startswith('^'):
                                params[k] = storedata[v[1:]]
                            elif hasattr(self, '%s_%s' % (sqlContextName, v)):
                                params[k] = getattr(self, '%s_%s' % (sqlContextName, v))()
                    obj.setJoinCondition(target_fld=joinBag['target_fld'], from_fld=joinBag['from_fld'],
                                         condition=joinBag['condition'],
                                         one_one=joinBag['one_one'], **params)

    def _getApplyMethodPars(self, kwargs, **optkwargs):
        result = dict([(k[6:], v) for k, v in kwargs.items() if k.startswith('apply_')])
        if optkwargs:
            result.update(optkwargs)
        return result

    @public_method
    def freezedSelectionPkeys(self,table=None,selectionName=None,caption_field=None):
        selection = self.page.unfreezeSelection(dbtable=table, name=selectionName)
        l = selection.output('dictlist')
        return [dict(pkey=r['_pkey'],caption=r['caption_field']) if caption_field else r['_pkey'] for r in l]

    
    @public_method
    def checkFreezedSelection(self,changelist=None,selectionName=None,where=None,table=None,**kwargs):
        """TODO
        
        ``checkFreezedSelection()`` method is decorated with the :meth:`public_method
        <gnr.core.gnrdecorator.public_method>` decorator
        
        :param changelist: TODO
        :param selectionName: TODO
        :param where: the sql "WHERE" clause. For more information check the :ref:`sql_where` section
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)"""
        selection = self.page.unfreezeSelection(dbtable=table, name=selectionName)
        needUpdate = False
        if selection is not None:
            kwargs.pop('where_attr',None)
            tblobj = self.db.table(table)
            wherelist = ['( $%s IN :_pkeys )' %tblobj.pkey]
            if isinstance(where,Bag):
                where, kwargs = self._decodeWhereBag(tblobj, where, kwargs)
            if where:
                wherelist.append(' ( %s ) ' %where)
            where = ' AND '.join(wherelist)
            eventdict = {}
            for change in changelist:
                eventdict.setdefault(change['dbevent'],[]).append(change['pkey'])
            for dbevent,pkeys in eventdict.items():
                wasInSelection = bool(filter(lambda r: r['pkey'] in pkeys,selection.data))
                if dbevent=='D' and not wasInSelection:
                    continue
                kwargs.pop('columns',None)
                willBeInSelection = bool(tblobj.query(where=where,_pkeys=pkeys,limit=1,**kwargs).fetch())
                if dbevent=='I' and not willBeInSelection:
                    continue
                if dbevent=='U' and not wasInSelection and not willBeInSelection:
                    continue
                needUpdate = True
                break
        return needUpdate
    
    @public_method
    def counterFieldChanges(self,table=None,counterField=None,changes=None):
        updaterDict = dict([(d['_pkey'],d['new']) for d in changes] )
        pkeys = updaterDict.keys()
        tblobj = self.db.table(table)
        def cb(r):
            r[counterField] = updaterDict[r[tblobj.pkey]]
        tblobj.batchUpdate(cb, where='$%s IN:pkeys' %tblobj.pkey, pkeys=pkeys)
        self.db.commit()
        
    @public_method      
    def getSelection(self, table='', distinct=False, columns='', where='', condition=None,
                         order_by=None, limit=None, offset=None, group_by=None, having=None,
                         relationDict=None, sqlparams=None, row_start='0', row_count='0',
                         recordResolver=True, selectionName='', structure=False, numberedRows=True,
                         pkeys=None, fromSelection=None, applymethod=None, totalRowCount=False,
                         selectmethod=None, expressions=None, sum_columns=None,
                         sortedBy=None, excludeLogicalDeleted=True,excludeDraft=True,hardQueryLimit=None,
                         savedQuery=None,savedView=None, externalChanges=None,prevSelectedDict=None,**kwargs):
        """TODO
        
        ``getSelection()`` method is decorated with the :meth:`public_method
        <gnr.core.gnrdecorator.public_method>` decorator
        
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param distinct: boolean, ``True`` for getting a "SELECT DISTINCT"
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        :param where: the sql "WHERE" clause. For more information check the :ref:`sql_where` section
        :param condition: the :ref:`sql_condition` of the selection
        :param order_by: corresponding to the sql "ORDER BY" operator. For more information check the
                         :ref:`sql_order_by` section
        :param limit: number of result's rows. Corresponding to the sql "LIMIT" operator. For more
                      information, check the :ref:`sql_limit` section
        :param offset: TODO
        :param group_by: the sql "GROUP BY" clause. For more information check the :ref:`sql_group_by` section
        :param having: the sql "HAVING" clause. For more information check the :ref:`sql_having`
        :param relationDict: a dict to assign a symbolic name to a :ref:`relation`. For more information
                             check the :ref:`relationdict` documentation section
        :param sqlparams: a dictionary which associates sqlparams to their values
        :param row_start: TODO
        :param row_count: TODO
        :param recordResolver: TODO
        :param selectionName: TODO
        :param structure: TODO
        :param numberedRows: TODO
        :param pkeys: TODO
        :param fromSelection: TODO
        :param applymethod: a page method to be called after selecting the related records
        :param totalRowCount: TODO
        :param selectmethod: TODO
        :param expressions: TODO
        :param sum_columns: TODO
        :param sortedBy: TODO
        :param excludeLogicalDeleted: TODO
        :param excludeDraft: TODO
        :param savedQuery: TODO
        :param savedView: TODO
        :param externalChanges: TODO"""
        t = time.time()
        tblobj = self.db.table(table)
        row_start = int(row_start)
        row_count = int(row_count)
        newSelection = True
        formats = {}
        if hardQueryLimit is not None:
            limit = hardQueryLimit
        wherebag = where if isinstance(where,Bag) else None
        resultAttributes = {}
        for k in kwargs.keys():
            if k.startswith('format_'):
                formats[7:] = kwargs.pop(k)

        if selectionName.startswith('*'):
            if selectionName == '*':
                selectionName = self.page.page_id
            else:
                selectionName = selectionName[1:]
        elif selectionName:
            selection = self.page.unfreezeSelection(tblobj, selectionName)
            if selection is not None:
                if sortedBy and  ','.join(selection.sortedBy or []) != sortedBy:
                    selection.sort(sortedBy)
                    selection.freezeUpdate()
                debug = 'fromPickle'
                newSelection = False
        if newSelection:
            debug = 'fromDb'
            if savedQuery:            
                where = tblobj.pkg.loadUserObject(code=savedQuery, objtype='query', tbl=tblobj.fullname)[0]
            if savedView:
                columns = tblobj.pkg.loadUserObject(code=savedView, objtype='view', tbl=tblobj.fullname)[0]
            if selectmethod:
                selecthandler = self.page.getPublicMethod('rpc', selectmethod)
            else:
                selecthandler = self._default_getSelection
            columns,external_queries = self._getSelection_columns(tblobj, columns, expressions=expressions)
            if fromSelection:
                fromSelection = self.page.unfreezeSelection(tblobj, fromSelection)
                pkeys = fromSelection.output('pkeylist')
            selection = selecthandler(tblobj=tblobj, table=table, distinct=distinct, columns=columns, where=where,
                                      condition=condition,
                                      order_by=order_by, limit=limit, offset=offset, group_by=group_by, having=having,
                                      relationDict=relationDict, sqlparams=sqlparams,
                                      recordResolver=recordResolver, selectionName=selectionName, 
                                      pkeys=pkeys, sortedBy=sortedBy, excludeLogicalDeleted=excludeLogicalDeleted,excludeDraft=excludeDraft, **kwargs)
            if external_queries:
                self._externalQueries(selection=selection,external_queries=external_queries)
            if applymethod:
                applyPars = self._getApplyMethodPars(kwargs)
                applyresult = self.page.getPublicMethod('rpc', applymethod)(selection, **applyPars)
                if applyresult:
                    resultAttributes.update(applyresult)

            if selectionName:
                selection.setKey('rowidx')
                selectionPath = self.page.freezeSelection(selection, selectionName)
                self.page.userStore().setItem('current.table.%s.last_selection_path' % table.replace('.', '_'), selectionPath)
            resultAttributes.update(table=table, method='app.getSelection', selectionName=selectionName,
                                    row_count=row_count,
                                    totalrows=len(selection))
        generator = selection.output(mode='generator', offset=row_start, limit=row_count, formats=formats)
        _addClassesDict = dict([(k, v['_addClass']) for k, v in selection.colAttrs.items() if '_addClass' in v])
        data = self.gridSelectionData(selection, generator, logicalDeletionField=tblobj.logicalDeletionField,
                                      recordResolver=recordResolver, numberedRows=numberedRows,
                                      _addClassesDict=_addClassesDict)
        if not structure:
            result = data
        else:
            result = Bag()
            result['data'] = data
            result['structure'] = self.gridSelectionStruct(selection)
        resultAttributes.update({'debug': debug, 'servertime': int((time.time() - t) * 1000),
                                 'newproc': getattr(self, 'self.newprocess', 'no')})

        #ADDED CONDITION AND **KWARGS (PARAMETERS FOR CONDITION)
        if totalRowCount:
            resultAttributes['totalRowCount'] = tblobj.query(where=condition,
                                                             excludeLogicalDeleted=excludeLogicalDeleted,
                                                             excludeDraft=excludeDraft,
                                                             **kwargs).count()

        if sum_columns:
            sum_columns_list = sum_columns.split(',')
            sum_columns_filtered = [c for c in sum_columns_list if c in selection.columns]
            totals = selection.sum(sum_columns_filtered)
            if totals:
                for i,col in enumerate(sum_columns_filtered):
                    resultAttributes['sum_%s' % col] = totals[i]
                    sum_columns_list.remove(col)
            for col in sum_columns_list:
                resultAttributes['sum_%s' % col] = False

        if prevSelectedDict:
            keys = prevSelectedDict.keys()
            resultAttributes['prevSelectedIdx'] = map(lambda m: m['rowidx'],filter(lambda r: r['pkey'] in keys,selection.data))
        if wherebag:
            resultAttributes['whereAsPlainText'] = self.db.whereTranslator.toHtml(tblobj,wherebag)
        resultAttributes['hardQueryLimitOver'] = hardQueryLimit and resultAttributes['totalrows'] == hardQueryLimit
        return (result, resultAttributes)


    def _getSelection_columns(self, tblobj, columns, expressions=None):
        external_queries = {}
        if isinstance(columns, Bag):
            columns = self._columnsFromStruct(columns)
        if not columns:
            columns = tblobj.attributes.get('baseview') or '*'
        if '[' in columns or ':' in columns:
            columns = columns.replace('\n', '').replace('\t', '')
            maintable = []
            colaux = columns.split(',')
            columns = []
            for col in colaux:
                if ':' in col:
                    external_table,external_field = col.split(':')
                    external_queries.setdefault(external_table,[]).append(external_field)
                    continue
                if '[' in col:
                    tbl, col = col.split('[')
                    maintable = [tbl]
                if col.endswith(']'):
                    col = col[:-1]
                columns.append('.'.join(maintable + [col.rstrip(']')]))
                if col.endswith(']'):
                    maintable = []
            columns = ','.join(columns)
        if expressions:
            expr_dict = getattr(self.page, 'expr_%s' % expressions)()
            expr_dict = dict([(k, '%s AS %s' % (v, k)) for k, v in expr_dict.items()])
            columns = templateReplace(columns, expr_dict, safeMode=True)

        if tblobj.attributes.get('protectionColumn'):
            columns = '%s, $%s AS _is_readonly_row' %(columns,tblobj.attributes.get('protectionColumn'))
            if tblobj.column('__protection_tag') is not None and not '__protection_tag' in columns:
                columns = '%s,$__protection_tag' %columns

        return columns,external_queries
    
    def _externalQueries(self,selection=None,external_queries=None):
        storedict = dict()
        for r in selection.data:
            storedict.setdefault(r['_external_store'],[]).append(r)
        for store,subsel in storedict.items():
            with self.db.tempEnv(storename=store):
                for k,v in external_queries.items():
                    tblobj = self.db.table(k)
                    extfkeyname = '%s_fkey' %k.replace('.','_')
                    fkeys = [r[extfkeyname] for r in selection.data]
                    columns = ','.join(v+['$%s AS %s' %(tblobj.pkey,extfkeyname)])
                    resdict = tblobj.query(columns=columns,where='$%s IN :fkeys' %tblobj.pkey,fkeys=fkeys,addPkeyColumn=False).fetchAsDict(key=extfkeyname)
                    for r in subsel:
                        if r[extfkeyname] in resdict:
                            r.update(resdict[r[extfkeyname]])
                    
    
    def _default_getSelection(self, tblobj=None, table=None, distinct=None, columns=None, where=None, condition=None,
                              order_by=None, limit=None, offset=None, group_by=None, having=None,
                              relationDict=None, sqlparams=None,recordResolver=None, selectionName=None,
                               pkeys=None, 
                              sortedBy=None, sqlContextName=None,
                              excludeLogicalDeleted=True,excludeDraft=True,**kwargs):
        sqlContextBag = None
        if sqlContextName:
            sqlContextBag = self._getSqlContextConditions(sqlContextName)
        if pkeys:
            if isinstance(pkeys, basestring):
                pkeys = pkeys.strip(',').split(',')
            if len(pkeys)==0:
                kwargs['limit'] = 0
            elif len(pkeys)==1:
                where = 't0.%s =:_pkey' % tblobj.pkey
                kwargs['_pkey'] = pkeys[0]
            else:
                where = 't0.%s in :pkeys' % tblobj.pkey
                kwargs['pkeys'] = pkeys
        elif isinstance(where, Bag):
            kwargs.pop('where_attr',None)
            where, kwargs = self._decodeWhereBag(tblobj, where, kwargs)
        if condition and not pkeys:
            where = ' ( %s ) AND ( %s ) ' % (where, condition) if where else condition
        query = tblobj.query(columns=columns, distinct=distinct, where=where,
                             order_by=order_by, limit=limit, offset=offset, group_by=group_by, having=having,
                             relationDict=relationDict, sqlparams=sqlparams, locale=self.page.locale,
                             excludeLogicalDeleted=excludeLogicalDeleted,excludeDraft=excludeDraft, **kwargs)
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

 
    def _decodeWhereBag(self, tblobj, where, kwargs):
        currentFilter = kwargs.pop('currentFilter',None)
        if currentFilter:
            new_where = Bag()
            new_where.setItem('filter', currentFilter)
            new_where.setItem('where', where, jc='and')
            where = new_where
        page = self.page
        customOpCbDict = dict([(x[12:], getattr(page, x)) for x in dir(page) if x.startswith('customSqlOp_')])
        return tblobj.sqlWhereFromBag(where, kwargs, customOpCbDict=customOpCbDict)

    def _columnsFromStruct(self, viewbag, columns=None):
        if columns is None:
            columns = []
        if not viewbag:
            return

        for node in viewbag:
            fld = node.getAttr('field')
            if fld:
                if not (fld[0] in ('$', '@')):
                    fld = '$' + fld
                columns.append(fld)
            if isinstance(node.value, Bag):
                self._columnsFromStruct(node.value, columns)
        return ','.join(columns)

    def gridSelectionData(self, selection, outsource, recordResolver, numberedRows, logicalDeletionField,
                          _addClassesDict=None):
        """TODO
        
        :param selection: TODO
        :param outsource: TODO
        :param recordResolver: TODO
        :param numberedRows: TODO
        :param logicalDeletionField: TODO
        """
        result = Bag()
        for j, row in enumerate(outsource):
            row = dict(row)
            _customClasses = (row.get('_customClasses', '') or '').split(' ')
            pkey = row.pop('pkey', None)
            isDeleted = row.pop('_isdeleted', None)
            if isDeleted:
                _customClasses.append('logicalDeleted')
            if _addClassesDict:
                for fld, _class in _addClassesDict.items():
                    if row[fld]:
                        _customClasses.append(_class)

            if numberedRows or not pkey:
                row_key = 'r_%i' % j
            else:
                row_key = toText(pkey).replace('.', '_')
            kw = dict(_pkey=pkey or row_key,
                           _attributes=row,
                            _removeNullAttributes=False, 
                            _customClasses=' '.join(_customClasses))
            if recordResolver:
                kw.update(_target_fld='%s.%s' % (selection.dbtable.fullname, selection.dbtable.pkey),
                           _relation_value=pkey, 
                           _resolver_name='relOneResolver')
            result.setItem(row_key, None, **kw)
        return result
    
    @public_method
    def getFieldcellPars(self,field=None,table=None):
        tableobj = self.db.table(table)
        cellpars = cellFromField(field,tableobj)
        cellpars['field'] = field
        return Bag(cellpars)
        
    def gridSelectionStruct(self, selection):
        """TODO
        
        :param selection: TODO"""
        structure = Bag()
        r = structure.child('view').child('row')
        for colname in selection.columns:
            if ((colname != 'pkey') and( colname != 'rowidx')):
                kwargs = dict(selection.colAttrs.get(colname, {}))
                kwargs.pop('tag', None)
                kwargs['name'] = kwargs.pop('label')
                if kwargs['dataType'] == 'D':
                    kwargs['format_date'] = 'short'
                size = kwargs.pop('size', None)
                size = kwargs.pop('print_width', size)
                if size:
                    if isinstance(size, basestring):
                        if ':' in size:
                            size = size.split(':')[1]
                    size = int(size)
                    if size < 3:
                        width = size * 1.1
                    if size < 6:
                        width = size
                    elif size < 10:
                        width = size * .8
                    elif size < 20:
                        width = size * .7
                    else:
                        width = size * .6
                    kwargs['width'] = '%iem' % (1 + int(int(width) * .7))
                r.child('cell', childname=colname, field=colname, **kwargs)
        return structure

        #@timer_call()

    #
    def _getRecord_locked(self, tblobj, record, recInfo):
        #locked,aux=self.page.site.lockRecord(self.page,tblobj.fullname,record[tblobj.pkey])
        locked = False
        aux = []
        if locked:
            recInfo['lockId'] = aux
            return
        for f in aux:
            recInfo['locking_%s' % f] = aux[f]
    
    @public_method
    def saveEditedRows(self,table=None,changeset=None,commit=True):
        if not changeset:
            return
        inserted = changeset.pop('inserted')
        updated =  changeset.pop('updated')
        deletedNode = changeset.popNode('deleted')
        tblobj = self.db.table(table)
        pkeyfield = tblobj.pkey
        result = Bag()
        wrongUpdates = Bag()
        insertedRecords = Bag()
        def cb(row):
            key = row[pkeyfield]
            c = updated.getNode(key)
            if c:
                for n in c.value:
                    if '_loadedValue' in n.attr and row[n.label] != n.attr['_loadedValue']:
                        wrongUpdates[key] = row
                        return
                    row[n.label] = n.value
        if updated:
            pkeys = [pkey for pkey in updated.digest('#a._pkey') if pkey]
            tblobj.batchUpdate(cb,where='$%s IN :pkeys' %pkeyfield,pkeys=pkeys)
        if inserted:
            for k,r in inserted.items():
                tblobj.insert(r)
                insertedRecords[k] = r[pkeyfield]
        if deletedNode:
            deleted = deletedNode.value
            unlinkfield = deletedNode.attr.get('unlinkfield')
            pkeys = [pkey for pkey in deleted.digest('#a._pkey') if pkey]
            self.deleteDbRows(table,pkeys=pkeys,unlinkfield=unlinkfield,commit=False)
        if commit:
            self.db.commit()
        result['wrongUpdates'] = wrongUpdates
        result['insertedRecords'] = insertedRecords
        return result

    @public_method    
    def deleteDbRows(self, table, pkeys=None, unlinkfield=None,commit=True,protectPkeys=None,**kwargs):
        """Method for deleting many records from a given table.
        
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param pkeys: TODO
        :returns: if it works, returns the primary key and the deleted attribute.
                  Else, return an exception"""
        try:
            tblobj = self.db.table(table)
            rows = tblobj.query(where='$%s IN :pkeys' %tblobj.pkey, pkeys=pkeys,excludeLogicalDeleted=False,
                                for_update=True,addPkeyColumn=False,excludeDraft=False).fetch()
            now = datetime.now()
            for r in rows:
                if unlinkfield:
                    record = dict(r)
                    record[unlinkfield] = None
                    tblobj.update(record,r)
                else:
                    if protectPkeys and tblobj.logicalDeletionField and r[tblobj.pkey] in protectPkeys:
                        oldr = dict(r)
                        r[tblobj.logicalDeletionField] = now
                        tblobj.update(r,oldr)
                    else:
                        tblobj.delete(r)
            if commit:
                self.db.commit()
            
        except GnrSqlDeleteException, e:
            return ('delete_error', {'msg': e.message})

    @public_method
    def duplicateRecord(self,pkey=None,table=None,**kwargs):
        tblobj = self.db.table(table)
        record = tblobj.duplicateRecord(pkey,**kwargs)
        self.db.commit()
        return record[tblobj.pkey]

    @public_method
    def unifyRecords(self,sourcePkey=None,destPkey=None,table=None,**kwargs):
        tblobj = self.db.table(table)
        tblobj.unifyRecords(sourcePkey=sourcePkey,destPkey=destPkey)
        self.db.commit()
        return 
        
        
    @public_method
    @extract_kwargs(default=True,sample=True)
    def getRecord(self, table=None, dbtable=None, pkg=None, pkey=None,
                      ignoreMissing=True, ignoreDuplicate=True, lock=False, readOnly=False,
                      from_fld=None, target_fld=None, sqlContextName=None, applymethod=None,
                      js_resolver_one='relOneResolver', js_resolver_many='relManyResolver',
                      loadingParameters=None, default_kwargs=None, eager=None, virtual_columns=None,_storename=None,
                      _resolver_kwargs=None,
                      _eager_level=0,_eager_record_stack=None, onLoadingHandler=None,sample_kwargs=None,ignoreReadOnly=None,**kwargs):
        """TODO
        
        ``getRecord()`` method is decorated with the :meth:`extract_kwargs <gnr.core.gnrdecorator.extract_kwargs>`
        and the :meth:`public_method <gnr.core.gnrdecorator.public_method>` decorators
        
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param dbtable: specify the :ref:`database table <table>`. More information in the
                        :ref:`dbtable` section (:ref:`dbselect_examples_simple`)
        :param pkg: the :ref:`package <packages>` object
        :param pkey: the :ref:`primary key <pkey>`
        :param ignoreMissing: boolean. TODO
        :param ignoreDuplicate: boolean. TODO
        :param lock: boolean. TODO
        :param readOnly: boolean. the :ref:`readonly` attribute
        :param from_fld: TODO
        :param target_fld: TODO
        :param sqlContextName: TODO
        :param applymethod: a page method to be called after selecting the related records
        :param js_resolver_one: TODO
        :param js_resolver_many: TODO
        :param loadingParameters: TODO
        :param default_kwargs: TODO
        :param eager: TODO
        :param virtual_columns: TODO
        :param onLoadingHandler: TODO"""
        t = time.time()
        dbtable = dbtable or table
        if pkg:
            dbtable = '%s.%s' % (pkg, dbtable)
        tblobj = self.db.table(dbtable)
        if pkey is not None:
            kwargs['pkey'] = pkey
        elif lock:
            lock = False
        if lock:
            kwargs['for_update'] = True
        captioncolumns = tblobj.rowcaptionDecode()[0]
        if captioncolumns:
            captioncolumns = [caption.replace('$','') for caption in captioncolumns]
            virtual_columns = virtual_columns.split(',') if virtual_columns else []
            vlist = tblobj.model.virtual_columns.items()
            virtual_columns.extend([k for k,v in vlist if v.attributes.get('always') or k in captioncolumns])
            virtual_columns = ','.join(uniquify(virtual_columns or []))
        rec = tblobj.record(eager=eager or self.page.eagers.get(dbtable),
                            ignoreMissing=ignoreMissing, ignoreDuplicate=ignoreDuplicate,
                            sqlContextName=sqlContextName, virtual_columns=virtual_columns, 
                            _storename=_storename,**kwargs)
        if sqlContextName:
            self._joinConditionsFromContext(rec, sqlContextName)

        if pkey == '*newrecord*':
            record = rec.output('newrecord', resolver_one=js_resolver_one, resolver_many=js_resolver_many)
        elif pkey=='*sample*':
            record = rec.output('sample', resolver_one=js_resolver_one, resolver_many=js_resolver_many,sample_kwargs=sample_kwargs)
            return record,dict(_pkey=pkey,caption='!!Sample data')
        else:
            record = rec.output('bag', resolver_one=js_resolver_one, resolver_many=js_resolver_many)
        pkey = record[tblobj.pkey] or '*newrecord*'
        newrecord = pkey == '*newrecord*'
        recInfo = dict(_pkey=pkey,
                       caption=tblobj.recordCaption(record, newrecord),
                       _newrecord=newrecord, sqlContextName=sqlContextName,_storename=_storename,
                       from_fld=from_fld)
        #if lock and not newrecord:
        if not newrecord and not readOnly:
            recInfo['_protect_write'] =  tblobj._islocked_write(record) or not tblobj.check_updatable(record,ignoreReadOnly=ignoreReadOnly)
            recInfo['_protect_delete'] = tblobj._islocked_delete(record) or not tblobj.check_deletable(record)
            if lock:
                self._getRecord_locked(tblobj, record, recInfo)
        loadingParameters = loadingParameters or {}
        default_kwargs = default_kwargs or {}
        loadingParameters.update(default_kwargs)
        if _eager_record_stack:
            loadingParameters['_eager_record_stack'] = _eager_record_stack
        method = None
        onLoadingHandler = onLoadingHandler or  loadingParameters.pop('method', None)
        if onLoadingHandler:
            handler = self.page.getPublicMethod('rpc', onLoadingHandler)
        else:
            if dbtable == self.page.maintable:
                method = 'onLoading' # TODO: fall back on the next case if onLoading is missing?
                #       (or maybe execute both if they exist)
            else:
                #self.page.gnotify('getRecord', dbtable, True)
                method = self.page.onLoadingRelatedMethod(dbtable,sqlContextName=sqlContextName)
            handler = getattr(self.page, method, None)
            

        if handler:
            if default_kwargs and newrecord:
                self.setRecordDefaults(record, default_kwargs)
            handler(record, newrecord, loadingParameters, recInfo)
        elif newrecord and loadingParameters:

            for k in default_kwargs:
                if not k in record:
                    record[k]=None
        
            self.setRecordDefaults(record, loadingParameters)

        if applymethod:
            applyPars = self._getApplyMethodPars(kwargs, newrecord=newrecord, loadingParameters=loadingParameters,
                                                 recInfo=recInfo, tblobj=tblobj)
            applyresult = self.page.getPublicMethod('rpc', applymethod)(record, **applyPars)
            if applyresult:
                recInfo.update(applyresult)
        recInfo['servertime'] = int((time.time() - t) * 1000)
        if tblobj.lastTS:
            recInfo['lastTS'] = str(record[tblobj.lastTS])
        if tblobj.logicalDeletionField and record[tblobj.logicalDeletionField]:
            recInfo['_logical_deleted'] = True
        if tblobj.draftField and record[tblobj.draftField]:
            recInfo['_draft'] = True

        invalidFields_fld = tblobj.attributes.get('invalidFields')
        if invalidFields_fld and record[invalidFields_fld]:
            recInfo['_invalidFields'] = fromJson(record[invalidFields_fld])
        recInfo['table'] = dbtable
        _eager_record_stack = _eager_record_stack or []
        self._handleEagerRelations(record,_eager_level,_eager_record_stack=_eager_record_stack)
        if newrecord and tblobj.counterColumns():
            try:
                tblobj._sequencesOnLoading(record,recInfo)
            except GnrSqlException, e:
                recInfo['_onLoadingError'] = str(e)
        return (record, recInfo)
        
    def _handleEagerRelations(self,record,_eager_level,_eager_record_stack=None):
        for n in record.nodes:
            _eager_one = n.attr.get('_eager_one')
            if _eager_one is True or (_eager_one=='weak' and _eager_level==0):
                n._resolver = None
                attr=n.attr
                target_fld=str(attr['_target_fld'])
                kwargs={}
                resolver_kwargs = attr.get('_resolver_kwargs') or dict()
                for k,v in resolver_kwargs.items():
                    if str(v).startswith('='):
                        v = v[1:]
                        resolver_kwargs[k] = record.get(v[1:]) if v.startswith('.') else None
                kwargs['resolver_kwargs'] = resolver_kwargs
                kwargs[target_fld.split('.')[2]]=record[attr['_auto_relation_value']]
                relatedRecord,relatedInfo = self.getRelatedRecord(from_fld=attr['_from_fld'], target_fld=target_fld, 
                                                                        sqlContextName=attr.get('_sqlContextName'),
                                                                        virtual_columns=attr.get('_virtual_columns'),
                                                                        _eager_level= _eager_level+1,_storename=attr.get('_storename'),
                                                                        _eager_record_stack=[record]+_eager_record_stack,
                                                                        **kwargs)
                n.value = relatedRecord
                n.attr['_resolvedInfo'] = relatedInfo
                             
                                
    def setRecordDefaults(self, record, defaults):
        """TODO
        
        :param record: TODO
        :param defaults: TODO"""
        for k, v in defaults.items():
            if k in record:
                record[k] = v
                
    @public_method
    def dbSelect(self, dbtable=None, columns=None, auxColumns=None, hiddenColumns=None, rowcaption=None,
                     _id=None, _querystring='', querystring=None, ignoreCase=True, exclude=None, excludeDraft=True,
                     condition=None, limit=None, alternatePkey=None, order_by=None, selectmethod=None,
                     notnull=None, weakCondition=False, _storename=None,preferred=None,**kwargs):
        """dbSelect is a :ref:`filteringselect` that takes the values through a :ref:`query` on the
        database: user can choose between all the values contained into the linked :ref:`table` (the
        table is specified through the *dbtable* attribute). While user write in the dbSelect, partially
        matched values will be shown in a pop-up menu below the input text box. You can show more columns
        in the pop-up menu through the *auxColumns*
        
        ``dbSelect()`` method is decorated with the :meth:`public_method
        <gnr.core.gnrdecorator.public_method>` decorator
        
        :param dbtable: specify the :ref:`database table <table>`. More information in the
                        :ref:`dbtable` section (:ref:`dbselect_examples_simple`)
        :param columns: you can specify one or more columns in order to extend user query on these columns.
                        The columns must be precedeed with a "$" (:ref:`dbselect_examples_columns`)
        :param auxColumns: list of columns separated by a comma. Every columns must have a prefix (``$``).
                           Show the columns you specify here as auxiliary columns in a pop-up menu
                           (:ref:`dbselect_examples_auxcolumns`)
        :param hiddenColumns: data retrieved but not shown
        :param rowcaption: the textual representation of a record in a user query.
                           For more information, check the :ref:`rowcaption` section
        :param querystring: TODO
        :param ignoreCase: boolean. Set it ``True`` for a case insensitive query from characters typed
                           from user. Set to ``False`` for a case sensitive query
        :param exclude: TODO
        :param excludeDraft: boolean. TODO
        :param condition: more :ref:`sql_condition` into the query
        :param limit: string. Number of result's rows (default is 10, set limit to 0 to visualize
                      all data). Corresponding to the sql "LIMIT" operator. For more information,
                      check the :ref:`sql_limit` section
        :param alternatePkey: TODO
        :param order_by: corresponding to the sql "ORDER BY" operator. For more information check the
                         :ref:`sql_order_by` section
        :param selectmethod: custom rpc_method you can use to make the query on the server
        :param notnull: TODO
        :param weakCondition: boolean. It will apply the condition if there is a result, but if
                              there is no result for the condition then the condition will not
                              be used. The *selectmethod* attribute can be used to override this
                              attribute
        """
        if _storename:
            self.db.use_store(_storename)
        elif _storename is False:
            self.db.use_store()
        resultClass = ''
        if selectmethod or not condition:
            weakCondition = False
        t0 = time.time()
        querystring = _querystring or querystring # da cambiare nella gnrstores.js invece?
        if limit is None:
            limit = self.gnrapp.config.get('dbselect?limit', 10)
        limit = int(limit)
        result = Bag()
        tblobj = self.db.table(dbtable)
        captioncolumns = tblobj.rowcaptionDecode(rowcaption)[0]
        querycolumns = tblobj.getQueryFields(columns, captioncolumns)
        showcolumns = gnrlist.merge(captioncolumns, tblobj.columnsFromString(auxColumns))
        resultcolumns = gnrlist.merge(showcolumns, captioncolumns, tblobj.columnsFromString(hiddenColumns))
        if alternatePkey and not alternatePkey in resultcolumns:
            resultcolumns.append("$%s" % alternatePkey if not alternatePkey.startswith('$') else alternatePkey)
        selection = None
        identifier = 'pkey'
        rows = []
        if _id:
            if alternatePkey:
                where = '$%s = :id' % alternatePkey
            else:
                where = '$%s = :id' % identifier
            if condition:
                where =  '( %s ) AND ( %s ) ' % (where, condition)
            whereargs = {}
            whereargs.update(kwargs)
            selection = tblobj.query(columns=','.join(resultcolumns),
                                     where=where, excludeLogicalDeleted=False,
                                     excludeDraft=excludeDraft,
                                     limit=1, id=_id,**kwargs).selection()
        elif querystring:
            querystring = querystring.strip('*')
            if querystring.isdigit():
                querystring = "%s%s" % ('%', querystring)
            if selectmethod:
                selectHandler = self.page.getPublicMethod('rpc', selectmethod)
            else:
                selectHandler = self.dbSelect_default
            order_list = []
            preferred = tblobj.attributes.get('preferred') if preferred is None else preferred
            if preferred:
                order_list.append('%s desc' %preferred)
                resultcolumns.append("""(CASE WHEN %s IS NOT TRUE THEN 'not_preferred_row' ELSE '' END) AS _customclasses_preferred""" %preferred)
            #order_by = order_by or tblobj.attributes.get('order_by') or tblobj.attributes.get('caption_field')
            order_by = order_by or showcolumns[0]
            order_list.append(order_by if order_by[0] in ('$','@') else '$%s' %order_by)
            order_by = ', '.join(order_list)
            selection = selectHandler(tblobj=tblobj, querycolumns=querycolumns, querystring=querystring,
                                      resultcolumns=resultcolumns, condition=condition, exclude=exclude,
                                      limit=limit, order_by=order_by,
                                      identifier=identifier, ignoreCase=ignoreCase,excludeDraft=excludeDraft, **kwargs)
            if not selection and weakCondition:
                resultClass = 'relaxedCondition'
                selection = selectHandler(tblobj=tblobj, querycolumns=querycolumns, querystring=querystring,
                                          resultcolumns=resultcolumns, exclude=exclude,
                                          limit=limit, order_by=order_by,
                                          identifier=identifier, ignoreCase=ignoreCase,excludeDraft=excludeDraft, **kwargs)

        resultAttrs = {}
        if selection:
            showcols = [tblobj.colToAs(c.lstrip('$')) for c in showcolumns]

            result = selection.output('selection', locale=self.page.locale, caption=rowcaption or True)
            colHeaders = [selection.colAttrs[k].get('name_short') or selection.colAttrs[k]['label'] for k in showcols]
            colHeaders = [self.page._(c) for c in colHeaders]
            resultAttrs = {'columns': ','.join(showcols), 'headers': ','.join(colHeaders)}

            if not notnull:
                result.setItem('null_row', None, caption='', _pkey=None)
        resultAttrs['resultClass'] = resultClass
        resultAttrs['dbselect_time'] = time.time() - t0
        return (result, resultAttrs)
    
    @public_method
    def dbSelect_selection(self, tblobj, querystring, columns=None, auxColumns=None, **kwargs):
        """TODO
        
        ``dbSelect_selection()`` method is decorated with the :meth:`public_method
        <gnr.core.gnrdecorator.public_method>` decorator
        
        :param tblobj: TODO
        :param querystring: TODO
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        :param auxColumns: TODO"""
        querycolumns = tblobj.getQueryFields(columns)
        showcolumns = gnrlist.merge(querycolumns, tblobj.columnsFromString(auxColumns))
        captioncolumns = tblobj.rowcaptionDecode()[0]
        resultcolumns = gnrlist.merge(showcolumns, captioncolumns)
        querystring = querystring or ''
        querystring = querystring.strip('*')
        return self.dbSelect_default(tblobj, querycolumns, querystring, resultcolumns, **kwargs)
        
    @public_method
    def tableAnalyzeStore(self, table=None, where=None, group_by=None, **kwargs):
        t0 = time.time()
        page = self.page
        tblobj = page.db.table(table)
        columns = [x for x in group_by if not callable(x)]
        selection = tblobj.query(where=where, columns=','.join(columns), **kwargs).selection()
        explorer_id = page.getUuid()
        freeze_path = page.site.getStaticPath('page:explorers', explorer_id)
        t1 = time.time()
        totalizeBag = selection.totalize(group_by=group_by, collectIdx=False, keep=['pkey']) #provvisorio
        t2 = time.time()
        store = page.lazyBag(totalizeBag, name=explorer_id, location='page:explorer')()
        t3 = time.time()
        return store,dict(query_time=t1 - t0, totalize_time=t2 - t1, resolver_load_time=t3 - t2)

    def dbSelect_default(self, tblobj, querycolumns, querystring, resultcolumns,
                             condition=None, exclude=None, limit=None, order_by=None,
                             identifier=None, ignoreCase=None, **kwargs):
        """TODO
        
        :param tblobj: TODO
        :param querycolumns: TODO
        :param querystring: TODO
        :param resetcolumns: TODO
        :param condition: the :ref:`sql_condition` of the dbSelect
        :param exclude: TODO
        :param limit: number of result's rows. Corresponding to the sql "LIMIT" operator. For more
                      information, check the :ref:`sql_limit` section
        :param order_by: corresponding to the sql "ORDER BY" operator. For more information check the
                         :ref:`sql_order_by` section
        :param identifier: TODO
        :param ignoreCase: TODO"""
        def getSelection(where, **searchargs):
            whereargs = {}
            whereargs.update(kwargs)
            whereargs.update(searchargs)
            if where and condition:
                where = '( %s ) AND ( %s ) ' % (where, condition)
            else:
                where = where or condition
            return tblobj.query(where=where, columns=','.join(resultcolumns), limit=limit,
                                order_by=order_by or querycolumns[0], exclude_list=exclude_list,
                                **whereargs).selection()

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
        #columns_concat = "ARRAY_TO_STRING(ARRAY[%s], ' ')" % ','.join(querycolumns)
        columns_concat = " || ' ' || ".join(["CAST ( COALESCE(%s,'') AS TEXT ) " %c for c in querycolumns])
        if len(result) == 0: # few results from the startswith query on first col
            #self.page.gnotify('dbselect','filter')
            regsrc = [x for x in re.split(" ", ESCAPE_SPECIAL.sub('', querystring)) if x]
            if regsrc:
                whereargs = dict([('w%i' % i, '(^|\\W)%s' % w.strip()) for i, w in enumerate(regsrc)])
                #where =" AND ".join(["(%s)  ~* :w%i" % (" || ' ' || ".join(querycolumns), i) for i,w in enumerate(regsrc)])
                where = " AND ".join(["(%s)  ~* :w%i" % (columns_concat, i) for i, w in enumerate(regsrc)])

                result = getSelection(where, **whereargs)

        if len(result) == 0:
            #self.page.gnotify('dbselect','contained')
            whereargs = dict([('w%i' % i, '%%%s%%' % w.strip()) for i, w in enumerate(srclist)])

            #where =" AND ".join(["(%s)  ILIKE :w%i" % (" || ' ' || ".join(querycolumns), i) for i,w in enumerate(srclist)])
            where = " AND ".join(["(%s)  ILIKE :w%i" % (columns_concat, i) for i, w in enumerate(srclist)])
            result = getSelection(where, **whereargs)

        return result

    @public_method
    def getMultiFetch(self,queries=None):
        result = Bag()
        for query in queries:
            columns = query.attr.pop('columns','*')
            table = query.attr.pop('table')
            tblobj = self.db.table(table)
            columns = ','.join(tblobj.columnsFromString(columns))
            result[query.label] = tblobj.query(columns=columns,**query.attr).fetchAsBag('pkey')
        return result
        
    @public_method
    def updateCheckboxPkeys(self,table=None,field=None,changesDict=None):
        if not changesDict:
            return
        tblobj = self.db.table(table)
        def cb(row):
            row[field] = changesDict[row[tblobj.pkey]]
        tblobj.batchUpdate(cb,where='$%s IN :pkeys' %tblobj.pkey,pkeys=changesDict.keys())
        self.db.commit()
        
    def _relPathToCaption(self, table, relpath):
        if not relpath: return ''
        tbltree = self.db.relationExplorer(table, dosort=False, pyresolver=True)
        fullcaption = tbltree.cbtraverse(relpath, lambda node: self.page._(node.getAttr('name_long')))
        return ':'.join(fullcaption)

    def rpc_getRecordForm(self, dbtable=None, fields=None, **kwargs):
        """TODO
        
        :param dbtable: specify the :ref:`database table <table>`. More information in the
                        :ref:`dbtable` section (:ref:`dbselect_examples_simple`)
        :param fields: TODO"""
        self.getRecordForm(self.newSourceRoot(), dbtable=dbtable, fields=fields, **kwargs)

    def formAuto(self, pane, table, columns='', cols=2):
        """TODO
        
        :param pane: the :ref:`contentpane`
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        :param cols: a :ref:`formbuilder attribute <formbuilder_def>`"""
        fb = pane.formbuilder(cols=cols)
        tblobj = self.db.table(table)
        if not columns:
            columns = [colname for colname, col in tblobj.columns.items() if
                       not col.isReserved and not col.dtype == 'X'and not col.dtype == 'Z']
        elif isinstance(columns, basestring):
            columns = splitAndStrip(columns)
        fb.placeFields(','.join(columns))

    def rpc_pdfmaker(self, pdfmode, txt, **kwargs):
        """TODO
        
        :param pdfmode: TODO
        :param txt: TODO"""
        filename = '%s.pdf' % self.page.getUuid()
        fpath = self.page.pageLocalDocument(filename)
        getattr(self.page, 'pdf_%s' % pdfmode)(fpath, txt, **kwargs)
        return filename

    def rpc_downloadPDF(self, filename, forcedownload=False, **kwargs):
        """TODO
        
        :param filename: TODO
        :param forcedownload: boolean. TODO"""
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
        filename = filename.replace(' ', '_').replace('.', '_').replace('/', '_')[:64]
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

    def _printCellStyle(self, colAttr):
        style = [colAttr.get('style')]
        styleAttrNames = ('height', 'width', 'top', 'left', 'right', 'bottom',
                          'visibility', 'overflow', 'float', 'clear', 'display',
                          'z_index', 'border', 'position', 'padding', 'margin',
                          'color', 'white_space', 'vertical_align')

        def isStyleAttr(name):
            for st in styleAttrNames:
                if name == st or name.startswith('%s_' % st):
                    return True

        for k, v in colAttr.items():
            if isStyleAttr(k):
                style.append('%s: %s;' % (k.replace('_', '-'), v))
        style = ' '.join([v for v in style if v])
        return style

    def rpc_printStaticGrid(self, structbag, storebag, filename=None, makotemplate='standard_print.tpl', **kwargs):
        """TODO
        
        :param structbag: TODO
        :param storebag: TODO
        :param filename: TODO
        :param makotemplate: TODO"""
        filename = self._exportFileNameClean(filename)
        if not filename.lower().endswith('.html') or filename.lower().endswith('.htm'):
            filename += '.html'
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

        result = self.page.pluginhandler.get_plugin('mako')(mako_path=makotemplate, striped='odd_row,even_row',
                                                            outdata=outdata, colAttrs=colAttrs,
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
        """TODO
        
        :param filename: TODO"""
        fpath = self.page.pageLocalDocument(filename)
        f = open(fpath, 'r')
        result = f.read()
        f.close()
        os.remove(fpath)
        return result.decode('utf-8')

    def rpc_recordToPDF(self, table, pkey, template, **kwargs):
        """TODO
        
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param pkey: the record :ref:`primary key <pkey>`
        :param template: TODO"""
        record = self.db.table(table).record(pkey).output('bag')
        return self.page.rmlTemplate(path=template, record=record)

    def rpc_includedViewAction(self, action=None, export_mode=None, respath=None, table=None, data=None,
                               selectionName=None, struct=None,datamode=None, downloadAs=None,
                               selectedRowidx=None, **kwargs):
        """TODO
        
        :param action: TODO
        :param export_mode: TODO
        :param respath: TODO
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param data: TODO
        :param selectionName: TODO
        :param struct: TODO
        :param datamode: TODO
        :param downloadAs: TODO
        :param selectedRowidx: TODO"""
        page = self.page
        if downloadAs:
            import mimetypes

            page.response.content_type = mimetypes.guess_type(downloadAs)[0]
            page.response.add_header("Content-Disposition", str("attachment; filename=%s" % downloadAs))
        if not respath:
            respath = 'action/_common/%s' % action
        res_obj = self.page.site.loadTableScript(page=self.page, table=table,respath=respath, class_name='Main')
        if selectionName:
            data = self.page.getUserSelection(selectionName=selectionName,selectedRowidx=selectedRowidx).output('grid')
        return res_obj.gridcall(data=data, struct=struct, export_mode=export_mode, datamode=datamode,selectedRowidx=selectedRowidx,filename=downloadAs)


class BatchExecutor(object):
    def __init__(self, page):
        #self._page = weakref.ref(page)
        self._page = page

    def _get_page(self):
        if self._page:
            #return self._page()
            return self._page

    page = property(_get_page)

