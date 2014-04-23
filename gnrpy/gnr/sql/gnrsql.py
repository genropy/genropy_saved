#-*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy sql - see LICENSE for details
# module gnrsql : Genro sql db connection.
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
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

from __future__ import with_statement

__version__ = '1.0b'

import logging

gnrlogger = logging.getLogger(__name__)
import cPickle
import os
import shutil
from time import time
from gnr.core.gnrlang import getUuid
from gnr.core.gnrlang import GnrObject
from gnr.core.gnrlang import importModule, GnrException
from gnr.core.gnrbag import Bag
from gnr.core.gnrclasses import GnrClassCatalog

#from gnr.sql.gnrsql_exceptions import GnrSqlException,GnrSqlExecutionException,\
#                                      GnrSqlSaveException,GnrSqlDeleteException
#
#from gnr.sql.adapters import *
from datetime import datetime
import re
import thread
import locale

def in_triggerstack(func):
    """TODO"""
    funcname = func.__name__
    def decore(self, *args, **kwargs):
        currentEnv = self.currentEnv
        trigger_stack = currentEnv.get('_trigger_stack')
        if not trigger_stack:
            trigger_stack = TriggerStack()
            currentEnv['_trigger_stack'] = trigger_stack
        trigger_stack.push(funcname,*args,**kwargs)
        result = func(self,*args,**kwargs)
        trigger_stack.pop()
        return result
        
    return decore

class GnrSqlException(GnrException):
    """Standard Gnr Sql Base Exception
    
    * **code**: GNRSQL-001
    * **description**: Genro SQL Base Exception
    """
    code = 'GNRSQL-001'
    description = '!!Genro SQL base exception'

class GnrSqlExecException(GnrSqlException):
    """Standard Gnr Sql Execution Exception
    
    * **code**: GNRSQL-002
    * **description**: Genro SQL Execution Exception
    """
    code = 'GNRSQL-002'
    description = '!!Genro SQL execution exception'
    
class GnrSqlDb(GnrObject):
    """This is the main class of the gnrsql module.
    
    A GnrSqlDb object has the following purposes:
    
    * manage the logical structure of a database, called database's model.
    * manage operations on db at high level, hiding adapter's layer and connections.
    """
    rootstore = '_main_db'
    
    def __init__(self, implementation='sqlite', dbname='mydb',
                 host=None, user=None, password=None, port=None,
                 main_schema=None, debugger=None, application=None, read_only=None,in_to_any=False,**kwargs):
        """
        This is the constructor method of the GnrSqlDb class.
        
        :param implementation: 'sqlite', 'postgres' or other sql implementations
        :param dbname: the name for your database
        :param host: the database server host (for sqlite is None)
        :param user: the username (for sqlite is None)
        :param password: the username's password (for sqlite is None)
        :param port: the connection port (for sqlite is None)
        :param main_schema: the database main schema
        :param debugger: TODO
        :param application: TODO
        """
        
        self.implementation = implementation
        self.dbname = dbname
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.read_only = read_only
        self.typeConverter = GnrClassCatalog()
        self.debugger = debugger
        self.application = application
        self.model = self.createModel()
        self.adapter = importModule('gnr.sql.adapters.gnr%s' % implementation).SqlDbAdapter(self)
        self.whereTranslator = self.adapter.getWhereTranslator()
        if main_schema is None:
            main_schema = self.adapter.defaultMainSchema()
        self.main_schema = main_schema
        self._connections = {}
        self.started = False
        self._currentEnv = {}
        self.stores_handler = DbStoresHandler(self)
        self.in_to_any = in_to_any

    #-----------------------Configure and Startup-----------------------------

    @property
    def debug(self):
        """TODO"""
        return self.application.debug
        
    @property
    def dbstores(self):
        """TODO"""
        return self.stores_handler.dbstores
        
    def createModel(self):
        """TODO"""
        from gnr.sql.gnrsqlmodel import DbModel
        
        return DbModel(self)
        
    def startup(self,restorepath=None):
        """Build the model.obj from the model.src"""
        if restorepath:
            self.autoRestore(restorepath)
        self.model.build()
        self.started = True
        
    def autoRestore(self,path):
        assert os.path.exists(path),'Restore archive %s does not exist' %path
        extractpath = path.replace('.zip','')
        if not os.path.isdir(path):
            from zipfile import ZipFile
            myzip =  ZipFile(path, 'r')
            myzip.extractall(extractpath)
        mainstorefile = os.path.join(extractpath,'mainstore')

        for s in self.stores_handler.dbstores.keys():
            self.stores_handler.drop_store(s)
        self.dropDb(self.dbname)
        self.createDb(self.dbname)
        self.restore(mainstorefile)
        auxstoresfiles = [f for f in os.listdir(extractpath) if not f.startswith('.') and f!='mainstore']
        for f in auxstoresfiles:
            dbname= '%s_%s' %(self.dbname,f)
            self.createDb(dbname)
            self.restore(os.path.join(extractpath,f),dbname=dbname)
            self.stores_handler.add_dbstore_config(f,dbname=dbname,save=False)
        self.stores_handler.save_config()
        shutil.rmtree(extractpath)
        #self.commit()


    def packageSrc(self, name):
        """Return a DbModelSrc corresponding to the required package
        
        :param name: the :ref:`package <packages>` name"""
        return self.model.src.package(name)
        
    def packageMixin(self, name, obj):
        """Register a mixin for a package.
        
        :param name: the target package's name
        :param obj: a class or an object to mixin"""
        self.model.packageMixin(name, obj)
        
    def tableMixin(self, tblpath, obj):
        """Register an object or a class to mixin to a table.
        
        :param tblpath: the path of the table
        :param obj: a class or an object to mixin"""
        self.model.tableMixin(tblpath, obj)
        
    def loadModel(self, source=None):
        """Load the model.src from a XML source
        
        :param source: the XML model (diskfile or text or url). 
        """
        self.model.load(source)
        
    def importModelFromDb(self):
        """Load the model.src extracting it from the database's information schema.
        """
        self.model.importFromDb()
        
    def saveModel(self, path):
        """Save the current model in the path as an XML file
        
        :param path: the file path
        """
        self.model.save(path)
        
    def checkDb(self, applyChanges=False):
        """Check if the database structure is compatible with the current model
        
        :param applyChanges: boolean. If ``True``, all the changes are executed and committed"""
        return self.model.check(applyChanges=applyChanges)
        
    def closeConnection(self):
        """Close a connection"""
        thread_ident = thread.get_ident()
        connections_dict = self._connections.get(thread_ident)
        if connections_dict:
            for conn_name in connections_dict.keys():
                conn = connections_dict.pop(conn_name)
                try:
                    conn.close()
                except Exception:
                    conn = None
                    
    def tempEnv(self, **kwargs):
        """Return a TempEnv class"""
        return TempEnv(self, **kwargs)
    
    def clearCurrentEnv(self):
        """Clear the current env"""
        self._currentEnv[thread.get_ident()] = {}
        
    def _get_currentEnv(self):
        """property currentEnv - Return the env currently used in this thread"""
        return self._currentEnv.setdefault(thread.get_ident(), {})
        
    def _set_currentEnv(self, env):
        """set currentEnv for the current thread"""
        self._currentEnv[thread.get_ident()] = env
        
    currentEnv = property(_get_currentEnv, _set_currentEnv)
        
    def _get_workdate(self):
        """currentEnv TempEnv. Return the workdate used in the current thread"""
        return self.currentEnv.get('workdate') or datetime.today()
        
    def _set_workdate(self, workdate):
        """Allow to set the workdate"""
        self.currentEnv['workdate'] = workdate
        
    workdate = property(_get_workdate, _set_workdate)
        
    def _get_locale(self):
        """property currentEnv - Return the workdate currently used in this thread"""
        return self.currentEnv.get('locale') or locale.getdefaultlocale()[0]
        
    def _set_locale(self, locale):
        self.currentEnv['locale'] = locale
        
    locale = property(_get_locale, _set_locale)
        
    def updateEnv(self, _excludeNoneValues=False,**kwargs):
        """Update the currentEnv"""
        if _excludeNoneValues:
            currentEnv = self.currentEnv
            for k,v in kwargs.items():
                if v is not None:
                    currentEnv[k] = v
        else:
            self.currentEnv.update(kwargs)
        
    def use_store(self, storename=None):
        """TODO
        
        :param storename: TODO. """
        self.updateEnv(storename=storename)
        
    def get_dbname(self):
        """TODO"""
        storename = self.currentEnv.get('storename')
        if storename:
            return self.dbstores[storename]['database']
        else:
            return self.dbname
    
    def usingRootstore(self):
        currentStore = self.currentEnv.get('storename')
        return  (currentStore is None) or (currentStore == self.rootstore)
            
    def _get_localizer(self):
        if self.application and self.application.site and self.application.site.currentPage:
            return self.application.site.currentPage.localizer
            
    localizer = property(_get_localizer)
    
    def _get_store_connection(self, storename):
        thread_ident = thread.get_ident()
        thread_connections = self._connections.setdefault(thread_ident, {})
        connectionName = '%s_%s' % (storename, self.currentEnv.get('connectionName') or '_main_connection')
        connection = thread_connections.get(connectionName)
        if not connection:
            connection = self.adapter.connect(storename)
            thread_connections[connectionName] = connection
        return connection
    
    def _get_connection(self):
        """property .connection
        
        If there's not connection open and return connection to database"""
        storename = self.currentEnv.get('storename') or self.rootstore
        
        if storename=='*' or ',' in storename:
            if storename=='*':
                storenames = self.dbstores.keys()
            else:
                storenames = storename.split(',')
            return [self._get_store_connection(s) for s in storenames]
        else:
            return self._get_store_connection(storename)
        #return thread_connections.setdefault(connectionName, self.adapter.connect()) 
            
    connection = property(_get_connection)
            
    def get_connection_params(self, storename=None):
        if storename and storename != self.rootstore:
            storeattr = self.dbstores[storename]
            return dict(host=storeattr.get('host'),database=storeattr.get('database'),
                        user=storeattr.get('user'),password=storeattr.get('password'),
                        port=storeattr.get('port'))
        else:
            return dict(host=self.host, database=self.dbname, user=self.user, password=self.password, port=self.port)
    
    def execute(self, sql, sqlargs=None, cursor=None, cursorname=None, autocommit=False, dbtable=None,storename=None):
        """Execute the sql statement using given kwargs. Return the sql cursor
        
        :param sql: the sql statement
        :param sqlargs: optional sql arguments
        :param cursor: an sql cursor
        :param cursorname: the name of the cursor
        :param autocommit: if ``True``, at the end of the execution runs the :meth:`commit()` method
        :param dbtable: specify the :ref:`database table <table>`. More information in the
                        :ref:`dbtable` section (:ref:`dbselect_examples_simple`)
        """
        # transform list and tuple parameters in named values.
        # Eg.   WHERE foo IN:bar ----> WHERE foo in (:bar_1, :bar_2..., :bar_n)
        #if 'adm.user' == dbtable:
        #    print x
        envargs = dict([('env_%s' % k, v) for k, v in self.currentEnv.items()])
        if not 'env_workdate' in envargs:
            envargs['env_workdate'] = self.workdate
        envargs.update(sqlargs or {})
        if storename is False:
            storename = self.rootstore
        storename = storename or envargs.get('env_storename', self.rootstore)
        sqlargs = envargs
        if dbtable and self.table(dbtable).use_dbstores(**sqlargs) is False:
            storename = self.rootstore
        with self.tempEnv(storename=storename):
            sql = self.adapter.adaptTupleListSet(sql,sqlargs)
            sql = self.adapter.empty_IN_patch(sql)
            sql, sqlargs = self.adapter.prepareSqlText(sql, sqlargs)
            #gnrlogger.info('Executing:%s - with kwargs:%s \n\n',sql,unicode(kwargs))
            #print 'sql:\n',sql
            try:
                t_0 = time()
                if not cursor:
                    if cursorname:
                        if cursorname == '*':
                            cursorname = 'c%s' % re.sub('\W', '_', getUuid())
                        cursor = self.adapter.cursor(self.connection, cursorname)
                    else:
                        cursor = self.adapter.cursor(self.connection)
                if isinstance(cursor, list):
                    for c in cursor:
                        c.execute(sql, sqlargs)
                else:
                    cursor.execute(sql, sqlargs)
                if self.debugger:
                    self.debugger(debugtype='sql', sql=sql, sqlargs=sqlargs, dbtable=dbtable,delta_time=time()-t_0)
            
            except Exception, e:
                #print sql
                gnrlogger.warning('error executing:%s - with kwargs:%s \n\n', sql, unicode(sqlargs))
                if self.debugger:
                    self.debugger(debugtype='sql', sql=sql, sqlargs=sqlargs, dbtable=dbtable, error=str(e))
                print str('error %s executing:%s - with kwargs:%s \n\n' % (
                str(e), sql, unicode(sqlargs).encode('ascii', 'ignore')))
                self.rollback()
                raise
            if autocommit:
                self.commit()
        return cursor

    def notifyDbEvent(self,tblobj,**kwargs):
        pass
        
    @in_triggerstack
    def insert(self, tblobj, record, **kwargs):
        """Insert a record in a :ref:`table`
        
        :param tblobj: the table object
        :param record: an object implementing dict interface as colname, colvalue"""
        tblobj.checkPkey(record)
        tblobj.protect_validate(record)
        tblobj._doFieldTriggers('onInserting', record)
        tblobj.trigger_onInserting(record)
        tblobj._doExternalPkgTriggers('onInserting', record)
        tblobj.trigger_assignCounters(record=record)
        if hasattr(tblobj,'dbo_onInserting'):
            tblobj.dbo_onInserting(record,**kwargs)
        if tblobj.draftField:
            if hasattr(tblobj,'protect_draft'):
                record[tblobj.draftField] = tblobj.protect_draft(record)
        self.adapter.insert(tblobj, record,**kwargs)
        tblobj._doFieldTriggers('onInserted', record)
        tblobj.trigger_onInserted(record)
        tblobj._doExternalPkgTriggers('onInserted', record)

        
    def insertMany(self, tblobj, records, **kwargs):
        self.adapter.insertMany(tblobj, records,**kwargs)

    def raw_insert(self, tblobj, record, **kwargs):
        self.adapter.insert(tblobj, record,**kwargs)

    def raw_update(self, tblobj, record, **kwargs):
        self.adapter.update(tblobj, record,**kwargs)

    def raw_delete(self, tblobj, record, **kwargs):
        self.adapter.delete(tblobj, record,**kwargs)

    @in_triggerstack
    def update(self, tblobj, record, old_record=None, pkey=None, **kwargs):
        """Update a :ref:`table`'s record
        
        :param tblobj: the table object
        :param record: an object implementing dict interface as colname, colvalue
        :param old_record: the record to be overwritten
        :param pkey: the record :ref:`primary key <pkey>`"""
        tblobj.protect_update(record, old_record=old_record)
        tblobj.protect_validate(record, old_record=old_record)
        tblobj._doFieldTriggers('onUpdating', record,old_record=old_record)
        tblobj.trigger_onUpdating(record, old_record=old_record)
        tblobj._doExternalPkgTriggers('onUpdating', record, old_record=old_record)
        if hasattr(tblobj,'dbo_onUpdating'):
            tblobj.dbo_onUpdating(record,old_record=old_record,pkey=pkey,**kwargs)
        tblobj.trigger_assignCounters(record=record,old_record=old_record)
        self.adapter.update(tblobj, record, pkey=pkey,**kwargs)
        tblobj.updateRelated(record,old_record=old_record)
        tblobj._doFieldTriggers('onUpdated', record, old_record=old_record)
        tblobj.trigger_onUpdated(record, old_record=old_record)
        tblobj._doExternalPkgTriggers('onUpdated', record, old_record=old_record)

    @in_triggerstack
    def delete(self, tblobj, record, **kwargs):
        """Delete a record from the :ref:`table`
        
        :param tblobj: the table object
        :param record: an object implementing dict interface as colname, colvalue"""
        tblobj.protect_delete(record)
        tblobj._doFieldTriggers('onDeleting', record)
        tblobj.trigger_onDeleting(record)
        tblobj._doExternalPkgTriggers('onDeleting', record)
        tblobj.deleteRelated(record)
        self.adapter.delete(tblobj, record,**kwargs)
        tblobj._doFieldTriggers('onDeleted', record)
        tblobj.trigger_onDeleted(record)
        tblobj._doExternalPkgTriggers('onDeleted', record)
        tblobj.trigger_releaseCounters(record)

    def commit(self):
        """Commit a transaction"""
        self.onCommitting()
        self.connection.commit()
        if not self.systemDbEvent():
            self.onDbCommitted()

    def onCommitting(self):
        deferreds = self.currentEnv.setdefault('deferredCalls',Bag()) 
        while deferreds:
            node =  deferreds.popNode('#0')
            cb,args,kwargs = node.value
            cb(*args,**kwargs)
            deferreds.popNode(node.label) #pop again because during triggers it could adding the same key to deferreds bag

    def deferToCommit(self,cb,*args,**kwargs):
        deferreds = self.currentEnv.setdefault('deferredCalls',Bag())
        deferredId = kwargs.pop('_deferredId',None)
        if not deferredId:
            deferredId = getUuid()
        if not deferredId in deferreds:
            deferreds.setItem(deferredId,(cb,args,kwargs))
    
    def deferredCommit(self):
        currentEnv = self.currentEnv
        dbstore = currentEnv.get('storename')
        assert dbstore, 'deferredCommit must have a dbstore'
        currentEnv.setdefault('_storesToCommit',set()).add(dbstore)
    
    def systemDbEvent(self):
        return self.currentEnv.get('_systemDbEvent',False)
    
    def onDbCommitted(self):
        """TODO"""
        pass
        
    def setConstraintsDeferred(self):
        """TODO"""
        cursor = self.adapter.cursor(self.connection)
        if hasattr(cursor,'setConstraintsDeferred'):
            cursor.setConstraintsDeferred()
        
    def rollback(self):
        """Rollback a transaction"""
        self.connection.rollback()
        
    def listen(self, *args, **kwargs):
        """Listen for a database event (postgres)"""
        self.adapter.listen(*args, **kwargs)
        
    def notify(self, *args, **kwargs):
        """Database Notify
        
        :param \*args: TODO
        :param \*\*kwargs: TODO"""
        self.adapter.notify(*args, **kwargs)
        
    def analyze(self):
        """Analyze db"""
        self.adapter.analyze()
        
    def vacuum(self):
        """TODO"""
        self.adapter.vacuum()

    #------------------ PUBLIC METHODS--------------------------
        
    def package(self, pkg):
        """Return a package object
        
        :param pkg: the :ref:`package <packages>` object"""
        return self.model.package(pkg)
            
    def _get_packages(self):
        return self.model.obj
            
    packages = property(_get_packages)
            
    def tableTreeBag(self, packages=None, omit=None, tabletype=None):
        """TODO
        
        :param packages: TODO
        :param omit: TODO
        :param tabletype: TODO"""
        result = Bag()
        for pkg, pkgobj in self.packages.items():
            if (pkg in packages and omit) or (not pkg in packages and not omit):
                continue
            pkgattr = dict(pkgobj.attributes)
            pkgattr['caption'] = pkgobj.attributes.get('name_long', pkg)
            result.setItem(pkg, Bag(), **pkgattr)
            for tbl, tblobj in pkgobj.tables.items():
                tblattr = dict(tblobj.attributes)
                if tabletype and tblattr.get('tabletype') != tabletype:
                    continue
                tblattr['caption'] = tblobj.attributes.get('name_long', pkg)
                result[pkg].setItem(tbl, None, **tblattr)
            if len(result[pkg]) == 0:
                result.pop(pkg)
        return result
            
    def table(self, tblname, pkg=None):
        """Return a table object
        
        :param tblname: the :ref:`database table <table>` name
        :param pkg: the :ref:`package <packages>` object"""
        return self.model.table(tblname, pkg=pkg).dbtable
            
    def query(self, table, **kwargs):
        """An sql :ref:`query`
        
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)"""
        return self.table(table).query(**kwargs)

    def queryCompile(self,table=None,columns='*', where=None, order_by=None,
              distinct=None, limit=None, offset=None,
              group_by=None, having=None, for_update=False,
              relationDict=None, sqlparams=None, excludeLogicalDeleted=True,
              excludeDraft=True,
              addPkeyColumn=True,ignorePartition=False, locale=None,
              mode=None,_storename=None,aliasPrefix=None, **kwargs):

        
        q = self.table(table).query(columns=columns, where=where, order_by=order_by,
                         distinct=distinct, limit=limit, offset=offset,
                         group_by=group_by, having=having, for_update=for_update,
                         relationDict=relationDict, sqlparams=sqlparams,
                         excludeLogicalDeleted=excludeLogicalDeleted,excludeDraft=excludeDraft,
                         ignorePartition=ignorePartition,
                         addPkeyColumn=addPkeyColumn, locale=locale,_storename=_storename,
                         aliasPrefix=aliasPrefix)
        result = q.sqltext
        if kwargs:
            prefix = str(id(kwargs))
            currentEnv = self.currentEnv
            for k,v in kwargs.items():
                newk = '%s_%s' %(prefix,k)
                currentEnv[newk] = v
                result = re.sub("(:)(%s)(\\W|$)" %k,lambda m: '%senv_%s%s'%(m.group(1),newk,m.group(3)), result)
        return result

        
    def colToAs(self, col):
        """TODO
        
        :param col: a table :ref:`column`"""
        as_ = re.sub('\W', '_', col)
        if as_[0].isdigit(): as_ = '_' + as_
        return as_
            
    def relationExplorer(self, table, prevCaption='', prevRelation='',
                         translator=None, **kwargs):
        """TODO
        
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param prevCaption: TODO
        :param prevRelation: TODO
        :param translator: TODO"""
        return self.table(table).relationExplorer(prevCaption=prevCaption,
                                                  prevRelation=prevRelation,
                                                  translator=translator, **kwargs)

    def localVirtualColumns(self,table):
        return None
                                                  
    def createDb(self, name, encoding='unicode'):
        """Create a database with a given name and an encoding
        
        :param name: the database's name
        :param encoding: The multibyte character encoding you choose"""
        self.adapter.createDb(name, encoding=encoding)
            
    def dropDb(self, name):
        """Drop a database with a given name
        
        :param name: the database's name"""
        self.adapter.dropDb(name)

    def dropTable(self,table,cascade=None):
        self.adapter.dropTable(self.table(table),cascade=cascade)

    def dropColumn(self,column,cascade=None):
        col = self.model.column(column)
        self.adapter.dropColumn(col.table.sqlfullname,col.sqlname,cascade=cascade)

    def dump(self, filename,dbname=None,extras=None,**kwargs):
        """Dump a database to a given path
        
        :param filename: the path on which the database will be dumped"""
        extras = extras or []
        self.adapter.dump(filename,dbname=dbname,extras=extras)
        
    def restore(self, filename,dbname=None):
        """Restore db to a given path
        
        :param name: the path on which the database will be restored"""
        #self.dropDb(self.dbname)
        #self.createDb(self.dbname)
        self.adapter.restore(filename,dbname=dbname)


        
    def createSchema(self, name):
        """Create a database schema
        
        :param name: the schema's name"""
        self.adapter.createSchema(name)
        
    def dropSchema(self, name):
        """Drop a db schema
        
        :param name: TODO"""
        self.adapter.dropSchema(name)
        
    def importXmlData(self, path):
        """Populates a database from an XML file
        
        :param path: the file path"""
        data = Bag(path)
        for table, pkg in data.digest('#k,#a.pkg'):
            for n in data[table]:
                self.table(table, pkg=pkg).insertOrUpdate(n.attr)
                
    def unfreezeSelection(self, fpath):
        """Get a pickled selection and return it
        
        :param fpath: the file path"""
        filename = '%s.pik' % fpath
        if not os.path.exists(filename):
            return
        with open('%s.pik' % fpath) as f:
            selection = cPickle.load(f)
        selection.dbtable = self.table(selection.tablename)
        return selection
        
class TempEnv(object):
    """TODO
    
    Example::
    
        with db.tempEnv(foo=7) as db:
            # do something
            pass"""
    
    def __init__(self, db, **kwargs):
        self.db = db
        self.kwargs = kwargs

    def __enter__(self):
        if self.db.adapter.support_multiple_connections:
            currentEnv = self.db.currentEnv
            self.savedValues = dict()
            self.addedKeys = []
            for k,v in self.kwargs.items():
                if k in currentEnv:
                    self.savedValues[k] = currentEnv.get(k) 
                else:
                    self.addedKeys.append((k,v))
                currentEnv[k] = v
        return self.db
        
        
    def __exit__(self, type, value, traceback):
        if self.db.adapter.support_multiple_connections:
            currentEnv = self.db.currentEnv
            for k,v in self.addedKeys:
                if currentEnv[k]==v:
                    currentEnv.pop(k,None)
            currentEnv.update(self.savedValues)
            

class TriggerStack(object):
    def __init__(self):
        self.stack = []

    def push(self,event,tblobj,record=None,old_record=None,**kwargs):
        self.stack.append(TriggerStackItem(self,event,tblobj,record=record,old_record=old_record))

    def pop(self):
        self.stack.pop()

    def __len__(self):
        return len(self.stack)

    @property
    def parentItem(self):
        return self.stack[-1] if len(self)>0 else None

    def item(self,n):
        try:
            return self.stack[n]
        except Exception:
            return None

class TriggerStackItem(object):
    def __init__(self,trigger_stack, event,tblobj,record=None,old_record=None):
        self.trigger_stack = trigger_stack
        lastItem = trigger_stack.stack[-1] if trigger_stack.stack else None
        self.parent = lastItem
        self.event = event
        self.table = tblobj.fullname
        self.record = record
        self.old_record = old_record






class DbStoresHandler(object):
    """Handler for using multi-database"""
        
    def __init__(self, db):
        self.db = db
        if db.application:
            self.config_folder = os.path.join(db.application.instanceFolder, 'dbstores')
        else:
            self.config_folder = None
        self.dbstores = {}
        self.load_config()
        self.create_stores()
        
    def load_config(self):
        """TODO"""
        self.config = Bag()
        if self.config_folder and os.path.isdir(self.config_folder):
            self.config = Bag(self.config_folder)['#0'] or Bag()
            
    def save_config(self):
        """TODO"""
        config = self.config.digest('#a.file_name,#v.#0?#')
        try:
            if os.path.isdir(self.config_folder):
                config_files = os.listdir(self.config_folder)
                for config_file in config_files:
                    filepath = os.path.join(self.config_folder, config_file)
                    if os.path.isfile(filepath):
                        os.remove(filepath)
        except OSError:
            pass
        for name, params in config:
            dbstore_config = Bag()
            dbstore_config.setItem('db', None, **params)
            dbstore_config.toXml(os.path.join(self.config_folder, '%s.xml' % name), autocreate=True)
            
    def create_stores(self, check=False):
        """TODO"""
        for name in self.config.digest('#a.file_name'):
            self.add_store(name, check=check)
            
    def add_store(self, storename, check=False,dbattr=None):
        """TODO
        
        :param storename: TODO
        :param check: TODO"""
        attr = dbattr or self.config.getAttr('%s_xml.db' % storename)
        self.dbstores[storename] = dict(database=attr.get('dbname', storename),
                                        host=attr.get('host', self.db.host), user=attr.get('user', self.db.user),
                                        password=attr.get('password', self.db.password),
                                        port=attr.get('port', self.db.port),
                                        remote_host=attr.get('remote_host'),
                                        remote_port=attr.get('remote_port'))
        if check:
            self.dbstore_align(storename)
            
    def drop_dbstore_config(self, storename):
        """TODO
        
        :param storename: TODO"""
        return self.config.pop('%s_xml' % storename)
    
    def drop_store(self,storename):
        config = self.drop_dbstore_config(storename)
        if not config:
            return
        try:
            self.db.dropDb(config['db?dbname'])
        except Exception:
            print Exception
        self.save_config()
        
        
    def add_dbstore_config(self, storename, dbname=None, host=None, user=None, password=None, port=None, save=True):
        """TODO
        
        :param storename: TODO
        :param dbname: the database name
        :param host: the database server host
        :param user: the username
        :param password: the username's password
        :param port: TODO
        :param save: TODO"""
        self.config.setItem('%s_xml' % storename, None, file_name=storename)
        self.config.setItem('%s_xml.db' % storename, None, dbname=dbname, host=host, user=user, password=password,
                            port=port)
        if save:
            self.save_config()
            self.load_config()
            self.add_store(storename, check=True)
            
    def dbstore_check(self, storename, verbose=False):
        """checks if dbstore exists and if it needs to be aligned
        
        :param storename: TODO
        :param verbose: TODO"""
        with self.db.tempEnv(storename=storename):
            self.db.use_store(storename)
            changes = self.db.model.check()
            if changes and not verbose:
                return False
            elif changes and verbose:
                return changes
            else: #not changes
                return True
                
    def dbstore_align(self, storename, changes=None):
        """TODO
        
        :param storename: TODO
        :param changes: TODO. """
        with self.db.tempEnv(storename=storename):
            changes = changes or self.db.model.check()
            if changes:
                self.db.model.applyModelChanges()
            
if __name__ == '__main__':
    pass
