# -*- coding: utf-8 -*-
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
from gnr.core.gnrbag import Bag,DirectoryResolver
from gnr.core import gnrlist

from gnr.core.gnrlang import uniquify
from gnr.core.gnrdecorator import extract_kwargs,public_method
from gnr.core.gnrstring import templateReplace, splitAndStrip, toText, toJson,fromJson
from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy
from gnr.web.gnrwebstruct import cellFromField
from gnr.sql.gnrsql_exceptions import GnrSqlDeleteException
from gnr.sql.gnrsql import GnrSqlException


gnrlogger = logging.getLogger(__name__)


ESCAPE_SPECIAL = re.compile(r'[\[\\\^\$\.\|\?\*\+\(\)\]\{\}]')

class GnrWebAppHandler(GnrBaseProxy):
    """A class for web applications handlement"""
    def init(self, **kwargs):
        """TODO"""
        self.gnrapp = self.page.site.gnrapp

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
                             loadingParameters=None,_debug_info=None, **kwargs):
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
        return [dict(pkey=r['pkey'],caption=r['caption_field']) if caption_field else r['pkey'] for r in l]

    
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
        if selection is None:
            return False #no update required
        eventdict = {}
        for change in changelist:
            eventdict.setdefault(change['dbevent'],[]).append(change['pkey'])
        deleted = eventdict.get('D',[])
        if deleted:
            if bool(filter(lambda r: r['pkey'] in deleted,selection.data)):
                return True #update required delete in selection

        updated = eventdict.get('U',[])
        if updated:
            if bool(filter(lambda r: r['pkey'] in updated,selection.data)):
                return True #update required update in selection

        inserted = eventdict.get('I',[])
        kwargs.pop('where_attr',None)
        tblobj = self.db.table(table)
        wherelist = ['( $%s IN :_pkeys )' %tblobj.pkey]
        if isinstance(where,Bag):
            where, kwargs = self._decodeWhereBag(tblobj, where, kwargs)
        if where:
            wherelist.append(' ( %s ) ' %where)
        condition = kwargs.pop('condition',None)
        if condition:
            wherelist.append(condition)
        where = ' AND '.join(wherelist)
        kwargs.pop('columns',None)
        kwargs['limit'] = 1
        if bool(tblobj.query(where=where,_pkeys=inserted+updated,**kwargs).fetch()):
            return True #update required: insert or update not in selection but satisfying query

        return False


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
    def deleteFileRows(self,files=None,**kwargs):
        if isinstance(files,basestring):
            files = files.split(',')
        for f in files:
            self.page.site.storageNode(f).delete()

    @public_method      
    def getFileSystemSelection(self,folders=None,ext=None,include=None,exclude=None,
                                columns=None,hierarchical=False,applymethod=None,**kwargs):
        files = Bag()
        resultAttributes = dict()
        from gnr.lib.services.storage import StorageResolver

        def setFileAttributes(node,**kwargs):
            attr = node.attr
            if not node.value and node.attr:
                abs_path = attr['abs_path']
                attr['_pkey'] = abs_path
                attr['created_ts'] = datetime.fromtimestamp(attr['mtime'])
                attr['changed_ts'] = datetime.fromtimestamp(attr['mtime'])
                if columns and attr['file_ext'].lower() == 'xml':
                    with self.page.site.storageNode(abs_path).open('rb') as f:
                        b = Bag(f)
                    for c in columns.split(','):
                        c = c.replace('$','')
                        attr[c] = b[c]
        for f in folders.split(','):
            files[f] = StorageResolver(self.page.site.storageNode(f),include=include,exclude=exclude,ext=ext,_page=self.page)()
        files.walk(setFileAttributes,_mode='')
        if hierarchical:
            return files
        result = Bag([('r_%i' %i,None,t[1].attr) for i,t in enumerate(files.getIndex()) if t[1].attr and t[1].attr['file_ext']!='directory'])
        if applymethod:
            applyPars = self._getApplyMethodPars(kwargs)
            applyresult = self.page.getPublicMethod('rpc', applymethod)(result, **applyPars)
            if applyresult:
                resultAttributes.update(applyresult)
        return result,resultAttributes

    @public_method  
    def getSelection(self, table='', distinct=False, columns='', where='', condition=None,
                         order_by=None, limit=None, offset=None, group_by=None, having=None,
                         relationDict=None, sqlparams=None, row_start='0', row_count='0',filteringPkeys=None,
                         recordResolver=True, selectionName='',queryMode=None, structure=False, numberedRows=True,
                         pkeys=None, fromSelection=None, applymethod=None, totalRowCount=False,
                         selectmethod=None, expressions=None, sum_columns=None,
                         sortedBy=None, excludeLogicalDeleted=True,excludeDraft=True,hardQueryLimit=None,
                         savedQuery=None,savedView=None, externalChanges=None,prevSelectedDict=None,
                         checkPermissions=None,queryBySample=False,weakLogicalDeleted=False,
                         customOrderBy=None,queryExtraPars=None,joinConditions=None,multiStores=None,**kwargs):
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
        if multiStores:
            kwargs['_storename'] = multiStores
        formats = {}
        if queryExtraPars:
            kwargs.update(queryExtraPars.asDict(ascii=True))
        if limit is None and hardQueryLimit is not None:
            limit = hardQueryLimit
        wherebag = where if isinstance(where,Bag) else None
        resultAttributes = {}
        if checkPermissions is True:
            checkPermissions = self.page.permissionPars
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
                    self.page.freezeSelectionUpdate(selection)
                debug = 'fromPickle'
                newSelection = False
        if newSelection:
            debug = 'fromDb'
            if savedQuery:            
                userobject_tbl = self.db.table('adm.userobject')
                where = userobject_tbl.loadUserObject(code=savedQuery, 
                                objtype='query', tbl=tblobj.fullname)[0]
                if where['where']:
                    limit = where['queryLimit']
                    savedView = savedView or where['currViewPath']
                    customOrderBy = customOrderBy or where['customOrderBy']
                    where = where['where']
            if savedView:
                userobject_tbl = self.db.table('adm.userobject')
                columns = userobject_tbl.loadUserObject(code=savedView, objtype='view', tbl=tblobj.fullname)[0]
            if selectmethod:
                selecthandler = self.page.getPublicMethod('rpc', selectmethod)
            else:
                selecthandler = self._default_getSelection
            columns,external_queries = self._getSelection_columns(tblobj, columns, expressions=expressions)
            if fromSelection:
                fromSelection = self.page.unfreezeSelection(tblobj, fromSelection)
                pkeys = fromSelection.output('pkeylist')
            if customOrderBy:
                order_by = []
                for fieldpath,sorting in customOrderBy.digest('#v.fieldpath,#v.sorting'):
                    fieldpath = '$%s' %fieldpath if not fieldpath.startswith('@') else fieldpath
                    sorting = 'asc' if sorting else 'desc'
                    order_by.append('%s %s' %(fieldpath,sorting))
                order_by = ' , '.join(order_by)
                sortedBy = None
            if joinConditions:
                joinConditions = self._decodeJoinConditions(tblobj,joinConditions,kwargs)
                kwargs['joinConditions'] = joinConditions
            selection_pars = dict(tblobj=tblobj, table=table, distinct=distinct, columns=columns, where=where,
                                      condition=condition,queryMode=queryMode,
                                      order_by=order_by, limit=limit, offset=offset, group_by=group_by, having=having,
                                      relationDict=relationDict, sqlparams=sqlparams,
                                      recordResolver=recordResolver, selectionName=selectionName, 
                                      pkeys=pkeys, sortedBy=sortedBy, excludeLogicalDeleted=excludeLogicalDeleted,
                                      excludeDraft=excludeDraft,checkPermissions=checkPermissions ,filteringPkeys=filteringPkeys,**kwargs)

            selection = selecthandler(**selection_pars)
            if selection is False:
                return Bag()
            elif selectmethod and isinstance(selection,list):
                self._default_getSelection()

            if not selection and weakLogicalDeleted and \
                    excludeLogicalDeleted and excludeLogicalDeleted!='mark':
                selection_pars['excludeLogicalDeleted'] = 'mark'
                selection = selecthandler(**selection_pars)
            if external_queries:
                self._externalQueries(selection=selection,external_queries=external_queries)
            if applymethod:
                applyPars = self._getApplyMethodPars(kwargs)
                applyresult = self.page.getPublicMethod('rpc', applymethod)(selection, **applyPars)
                if applyresult:
                    resultAttributes.update(applyresult)

            if selectionName:
                selection.setKey('rowidx')
                selectionPath = self.page.freezeSelection(selection, selectionName,freezePkeys=True)
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
        if self.page.pageStore().getItem('slaveSelections.%s' %selectionName):
            with self.page.pageStore() as store:
                slaveSelections = store.getItem('slaveSelections.%s' %selectionName)
                if slaveSelections:
                    for page_id,grids in slaveSelections.items():
                        if self.page.site.register.exists(page_id,register_name='page'):
                            for nodeId in grids.keys():
                                self.page.clientPublish('%s_refreshLinkedSelection' %nodeId,value=True,page_id=page_id)
                        else:
                            slaveSelections.popNode(page_id)
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
        hasProtectionColumns = tblobj.hasProtectionColumns()
        if hasProtectionColumns:
            columns = '%s,$__is_protected_row AS _is_readonly_row' %columns

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
                    
    

    def _handleLinkedSelection(self,selectionName=None):
        with self.page.pageStore() as slaveStore:
            lsKey = 'linkedSelectionPars.%s' %selectionName
            linkedSelectionPars = slaveStore.getItem(lsKey)
            if not linkedSelectionPars:
                return
            linkedPkeys = linkedSelectionPars['pkeys']
            command = linkedSelectionPars['command']
            if command:
                linkedSelectionPars['command'] = None
                gridNodeId = linkedSelectionPars['gridNodeId']
                if linkedSelectionPars['linkedPageId']:
                    with self.page.pageStore(linkedSelectionPars['linkedPageId']) as masterStore:
                        slavekey = 'slaveSelections.%(linkedSelectionName)s' %linkedSelectionPars
                        slaveSelections = masterStore.getItem(slavekey) or Bag()
                        grids = slaveSelections[self.page.page_id] or Bag()
                        if command=='subscribe':
                            grids[gridNodeId] = True
                        else:
                            grids.popNode(gridNodeId)
                        if grids:
                            slaveSelections[self.page.page_id] = grids
                        else:
                            slaveSelections.popNode(self.page.page_id)
                        if slaveSelections:
                            masterStore.setItem(slavekey, slaveSelections)
                        else:
                            masterStore.popNode(slavekey)
                if command == 'unsubscribe':
                    for k in linkedSelectionPars.keys():
                        linkedSelectionPars[k] = None
                slaveStore.setItem(lsKey,linkedSelectionPars)
        if linkedSelectionPars['masterTable']:
            if not linkedPkeys:
                linkedPkeys = self.page.freezedPkeys(self.db.table(linkedSelectionPars['masterTable']),linkedSelectionPars['linkedSelectionName'],
                                                            page_id=linkedSelectionPars['linkedPageId'])
            where = ' OR '.join([" (%s IN :_masterPkeys) " %r for r in linkedSelectionPars['relationpath'].split(',')])
            return dict(where=' ( %s ) ' %where,linkedPkeys=linkedPkeys.split(',') if isinstance(linkedPkeys,basestring) else linkedPkeys)



    def _default_getSelection(self, tblobj=None, table=None, distinct=None, columns=None, where=None, condition=None,
                              order_by=None, limit=None, offset=None, group_by=None, having=None,
                              relationDict=None, sqlparams=None,recordResolver=None, selectionName=None,
                               pkeys=None,filteringPkeys=None, queryMode=None,
                              sortedBy=None, sqlContextName=None,
                              excludeLogicalDeleted=True,excludeDraft=True,_aggregateRows=True,
                              **kwargs):
        sqlContextBag = None
        if sqlContextName:
            sqlContextBag = self._getSqlContextConditions(sqlContextName)

        linkedSelectionKw = self._handleLinkedSelection(selectionName=selectionName) if selectionName else None
        if linkedSelectionKw:
            where = linkedSelectionKw['where']
            kwargs['_masterPkeys'] = linkedSelectionKw['linkedPkeys']
        elif pkeys:
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
        if queryMode in ('U','I','D'):
            _qmpkeys = self.page.freezedPkeys(tblobj,selectionName)
            queryModeCondition = '( $%s IN :_qmpkeys )' %tblobj.pkey
            kwargs['_qmpkeys'] = _qmpkeys
            if queryMode == 'U':
                where =' ( %s ) OR ( %s ) ' % (where, queryModeCondition)
            elif queryMode == 'I':
                where =' ( %s ) AND ( %s ) ' % (where, queryModeCondition)
            elif queryMode == 'D':
                where =' ( %s ) AND NOT ( %s ) ' % (queryModeCondition,where)  
        if filteringPkeys:
            if isinstance(filteringPkeys,basestring):
                filteringWhere = None
                if ',' in filteringPkeys:
                    filteringPkeys = filteringPkeys.split(',')
                else:
                    handler = self.page.getPublicMethod('rpc',filteringPkeys)
                    if handler:
                        filteringPkeys = handler(tblobj=tblobj, 
                                                where=where,relationDict=relationDict, 
                                                sqlparams=sqlparams,limit=limit,**kwargs)                      
                        if filteringPkeys and not isinstance(filteringPkeys,list):
                            if hasattr(filteringPkeys,'forcedOrderBy'):
                                order_by=filteringPkeys.forcedOrderBy
                                sortedBy=None
                            filteringPkeys = filteringPkeys.output('pkeylist')
                    else:
                        filteringPkeys = [filteringPkeys]
                if len(filteringPkeys)==0:
                    filteringWhere = 't0.%s IS NULL' % tblobj.pkey
                elif len(filteringPkeys)==1:
                    filteringWhere = 't0.%s =:_filteringPkey' % tblobj.pkey
                    kwargs['_filteringPkey'] = filteringPkeys[0]
                else:
                    filteringWhere = 't0.%s in :_filteringPkeys' % tblobj.pkey
                    kwargs['_filteringPkeys'] = filteringPkeys
                if filteringWhere:
                    where = filteringWhere if not where else ' ( %s ) AND ( %s ) ' %(filteringWhere, where)
        query = tblobj.query(columns=columns, distinct=distinct, where=where,
                             order_by=order_by, limit=limit, offset=offset, group_by=group_by, having=having,
                             relationDict=relationDict, sqlparams=sqlparams, locale=self.page.locale,
                             excludeLogicalDeleted=excludeLogicalDeleted,excludeDraft=excludeDraft, **kwargs)
        if sqlContextName:
            self._joinConditionsFromContext(query, sqlContextName)
        selection = query.selection(sortedBy=sortedBy, _aggregateRows=_aggregateRows)
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

    def _decodeJoinConditions(self,tblobj,joinConditions,kwargs):
        if not isinstance(joinConditions,Bag):
            return joinConditions
        result = dict()
        for jc in joinConditions.values():
            sqlcondition,kwargs = tblobj.sqlWhereFromBag(jc['condition'], kwargs)
            result[jc['relation']] = dict(condition=sqlcondition,one_one=jc['one_one'])
        return result

    def _columnsFromStruct(self, viewbag, columns=None):
        if columns is None:
            columns = []
        if not viewbag:
            return

        for node in viewbag:
            fld = node.getAttr('field')
            if node.getAttr('formula'):
                continue
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
            value = None 
            attributes = kw.get('_attributes')
            colAttrs = selection.colAttrs
            for k,v in attributes.items():
                if v and colAttrs.get(k,{}).get('dataType') == 'X':
                    attributes[k] = "%s::X" %v
            if attributes and '__value__' in attributes:
                value = attributes.pop('__value__')
            result.appendNode(row_key, value, **kw)
        return result
    
    @public_method
    def getFieldcellPars(self,field=None,table=None):
        tableobj = self.db.table(table)
        cellpars = cellFromField(field,tableobj,checkPermissions=self.page.permissionPars)
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
        if updated:
            updated =  dict(updated.digest('#a._pkey,#v'))
        deletedNode = changeset.popNode('deleted')
        tblobj = self.db.table(table)
        pkeyfield = tblobj.pkey
        result = Bag()
        wrongUpdates = Bag()
        insertedRecords = Bag()
        def cb(row):
            key = row[pkeyfield]
            c = updated.get(key)
            if c:
                for n in c:
                    if n.label in row:
                        if '_loadedValue' in n.attr and row[n.label] != n.attr['_loadedValue']:
                            wrongUpdates[key] = row
                            return
                        row[n.label] = n.value
                    else:
                        if '_loadedValue' in n.attr:
                            row[n.label] = n.value
        if updated:
            pkeys = [pkey for pkey in updated.keys() if pkey]
            tblobj.batchUpdate(cb,where='$%s IN :pkeys' %pkeyfield,pkeys=pkeys,bagFields=True)
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
    def duplicateDbRows(self, table, pkeys=None, unlinkfield=None,commit=True,protectPkeys=None,**kwargs):
        if not self.page.checkTablePermission(table,'readonly,ins'):
            raise self.page.exception('generic',description='Duplicate is not allowed in table % for user %s' %(table,self.user))
        tblobj = self.db.table(table)
        result_pkeys = []
        for pkey in pkeys:
            record = tblobj.duplicateRecord(pkey,**kwargs)
            result_pkeys.append(record[tblobj.pkey])
        self.db.commit()
        return result_pkeys

    @public_method    
    def deleteDbRows(self, table, pkeys=None, unlinkfield=None,commit=True,protectPkeys=None,**kwargs):
        """Method for deleting many records from a given table.
        
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param pkeys: TODO
        :returns: if it works, returns the primary key and the deleted attribute.
                  Else, return an exception"""
        if not self.page.checkTablePermission(table,'readonly,del'):
            raise self.page.exception('generic',description='Delete not allowed in table % for user %s' %(table,self.user))
        try:
            tblobj = self.db.table(table)
            rows = tblobj.query(where='$%s IN :pkeys' %tblobj.pkey, pkeys=pkeys,excludeLogicalDeleted=False,
                                for_update=True,addPkeyColumn=False,excludeDraft=False).fetch()
            now = datetime.now()
            caption_field = tblobj.attributes.get('caption_field')
            if not rows:
                return
            labelfield = tblobj.name
            if caption_field and (caption_field in rows[0]):
                labelfield = caption_field
            deltitle = 'Unlink records' if unlinkfield else 'Delete records'
            for r in self.page.utils.quickThermo(rows,maxidx=len(rows),labelfield=labelfield,title=deltitle):
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
    def archiveDbRows(self, table, pkeys=None, unlinkfield=None,commit=True,protectPkeys=None,archiveDate=None,**kwargs):
        """Method for deleting many records from a given table.
        
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param pkeys: TODO
        :returns: if it works, returns the primary key and the deleted attribute.
                  Else, return an exception"""
        try:
            tblobj = self.db.table(table)
            rows = tblobj.query(where='$%s IN :pkeys' %tblobj.pkey, pkeys=pkeys,
                                excludeLogicalDeleted=False,
                                for_update=True,addPkeyColumn=False,excludeDraft=False).fetch()
            ts = datetime(archiveDate.year,archiveDate.month,archiveDate.day) if archiveDate else None
            updated = False
            protectPkeys = protectPkeys or []
            for r in rows:
                if not (r[tblobj.pkey] in protectPkeys):
                    oldr = dict(r)
                    r[tblobj.logicalDeletionField] = ts 
                    tblobj.update(r,oldr)
                    updated = True
            if commit and updated:
                self.db.commit()
        except GnrSqlDeleteException, e:
            return ('archive_error', {'msg': e.message})

    @public_method
    def insertRecord(self,table=None,record=None,**kwargs):
        tblobj = self.db.table(table)
        tblobj.insert(record)
        self.db.commit()
        return record[tblobj.pkey]

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
        hasProtectionColumns = tblobj.hasProtectionColumns()

        if captioncolumns or hasProtectionColumns:
            columns_to_add = (captioncolumns or [])+(['__protecting_reasons','__is_protected_row'] if hasProtectionColumns else [])
            columns_to_add = [c.replace('$','') for c in columns_to_add]
            virtual_columns = virtual_columns.split(',') if virtual_columns else []
            vlist = tblobj.model.virtual_columns.items()
            virtual_columns.extend([k for k,v in vlist if v.attributes.get('always') or k in columns_to_add])
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
                       _newrecord=newrecord, 
                       sqlContextName=sqlContextName,_storename=_storename,
                       from_fld=from_fld,ignoreReadOnly=ignoreReadOnly)
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
        table_onLoading = getattr(tblobj,'onLoading',None)
        if table_onLoading:
            table_onLoading(record, newrecord, loadingParameters, recInfo)
        table_onloading_handlers = [getattr(tblobj,k) for k in dir(tblobj) if k.startswith('onLoading_')]
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
            

        if handler or table_onloading_handlers:
            if default_kwargs and newrecord:
                self.setRecordDefaults(record, default_kwargs)
            for h in table_onloading_handlers:
                h(record, newrecord, loadingParameters, recInfo)
            if handler:
                handler(record, newrecord, loadingParameters, recInfo)
        elif newrecord and loadingParameters:
            for k in default_kwargs:
                if k not in record:
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
        recInfo['caption'] = tblobj.recordCaption(record, newrecord)
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
                     notnull=None, weakCondition=False, _storename=None,preferred=None,
                     invalidItemCondition=None,**kwargs):
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
        if alternatePkey and alternatePkey not in resultcolumns:
            resultcolumns.append("$%s" % alternatePkey if not alternatePkey.startswith('$') else alternatePkey)
        selection = None
        identifier = 'pkey'
        rows = []
        resultAttrs = {}
        errors = []
        if _id:
            fullwhere = None
            if alternatePkey:
                where = '$%s = :id' % alternatePkey
            else:
                where = '$%s = :id' % identifier

            
            fullwhere =  '( %s ) AND ( %s ) ' % (where, condition) if condition else where
            whereargs = {}
            whereargs.update(kwargs)
            selection = tblobj.query(columns=','.join(resultcolumns),
                                     where=fullwhere, excludeLogicalDeleted=False,
                                     excludeDraft=excludeDraft,
                                     limit=1, id=_id,**kwargs).selection()
            if condition and not selection:
                selection = tblobj.query(columns=','.join(resultcolumns),
                                     where=where, excludeLogicalDeleted=False,
                                     excludeDraft=excludeDraft,
                                     limit=1, id=_id,**kwargs).selection()
                errors.append('current value does not fit condition')
            
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
            weakCondition = weakCondition or tblobj.attributes.get('weakCondition')
            if preferred:
                order_list.append('( %s ) desc' %preferred)
                resultcolumns.append("""(CASE WHEN %s IS NOT TRUE THEN 'not_preferred_row' ELSE '' END) AS _customclasses_preferred""" %preferred)
            if invalidItemCondition:
                resultcolumns.append("""(%s IS TRUE) AS _is_invalid_item""" %invalidItemCondition)
                #resultcolumns.append("""(CASE WHEN %s IS TRUE THEN 'is_invalid_row' ELSE '' END) AS _customclasses_invaliditemCondition""" %invalidItemCondition)
            #order_by = order_by or tblobj.attributes.get('order_by') or tblobj.attributes.get('caption_field')
            order_by = order_by or tblobj.attributes.get('order_by') or showcolumns[0]
            order_list.append(order_by if order_by[0] in ('$','@') else '$%s' %order_by)
            order_by = ', '.join(order_list)
            cond = '(%s) AND (%s)' %(condition or 'TRUE',weakCondition) if isinstance(weakCondition,basestring) else condition
            selection = selectHandler(tblobj=tblobj, querycolumns=querycolumns, querystring=querystring,
                                      resultcolumns=resultcolumns, condition=cond, exclude=exclude,
                                      limit=limit, order_by=order_by,
                                      identifier=identifier, ignoreCase=ignoreCase,excludeDraft=excludeDraft, **kwargs)
            if not selection and weakCondition:
                resultClass = 'relaxedCondition'
                selection = selectHandler(tblobj=tblobj, querycolumns=querycolumns, querystring=querystring,
                                          resultcolumns=resultcolumns, exclude=exclude,
                                          limit=limit, order_by=order_by,condition= None if weakCondition is True else condition,
                                          identifier=identifier, ignoreCase=ignoreCase,excludeDraft=excludeDraft, **kwargs)

        
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
        if errors:
            resultAttrs['errors'] = ','.join(errors)
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
                                **whereargs).selection(_aggregateRows=True)

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
        searchval = '%s%%' % ('%% '.join(srclist))
        sqlArgs = dict()
        cond = tblobj.opTranslate(querycolumns[0],'contains',searchval,sqlArgs=sqlArgs)
        result = getSelection(cond,**sqlArgs)
        if len(result) >= (limit or 50):
            cond = tblobj.opTranslate(querycolumns[0],'startswith',searchval,sqlArgs=sqlArgs)
            result = getSelection(cond,**sqlArgs)

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
    def getValuesString(self,table,caption_field=None,alt_pkey_field=None,**kwargs):
        tblobj = self.db.table(table)
        pkey = alt_pkey_field or tblobj.pkey
        caption_field = caption_field or tblobj.attributes.get('caption_field') or tblobj.pkey
        f = tblobj.query(columns='$%s,$%s' %(pkey,caption_field),**kwargs).fetch()
        return ','.join(['%s:%s' %(r[pkey],(r[caption_field] or '').replace(',',' ')) for r in f])

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
        fields = changesDict.pop('_fields',None)
        if not fields:
            fields = [field]
        def cb(row):
            for f in fields:
                row[f] = changesDict[row[tblobj.pkey]] if f==field else False
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
                               selectionName=None, struct=None,datamode=None,localized_data=None, downloadAs=None,
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
        return res_obj.gridcall(data=data, struct=struct, export_mode=export_mode,
                                    localized_data=localized_data, datamode=datamode,
                                    selectedRowidx=selectedRowidx,filename=downloadAs)


class BatchExecutor(object):
    def __init__(self, page):
        #self._page = weakref.ref(page)
        self._page = page

    def _get_page(self):
        if self._page:
            #return self._page()
            return self._page

    page = property(_get_page)

