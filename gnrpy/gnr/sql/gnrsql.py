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


import logging
import cPickle
import os
import shutil
from time import time
from gnr.core.gnrstring import boolean
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

MAIN_CONNECTION_NAME = '_main_connection'

__version__ = '1.0b'
gnrlogger = logging.getLogger(__name__)

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
    
class GnrMissedCommitException(GnrException):
    """Standard Gnr Sql Base Exception
    
    * **code**: GNRSQL-001
    * **description**: Genro SQL Base Exception
    """
    code = 'GNRSQL-099'
    description = '!!Genro Missed commit exception'

class GnrSqlDb(GnrObject):
    """This is the main class of the gnrsql module.
    
    A GnrSqlDb object has the following purposes:
    
    * manage the logical structure of a database, called database's model.
    * manage operations on db at high level, hiding adapter's layer and connections.
    """
    rootstore = '_main_db'
    
    
    def __init__(self, implementation='sqlite', dbname='mydb',
                 host=None, user=None, password=None, port=None,
                 main_schema=None, debugger=None, application=None,
                 read_only=None,**kwargs):
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
        self.dbname = self.dbpar(dbname)
        self.host = self.dbpar(host)
        self.port = self.dbpar(str(port) if port else None)
        self.user = self.dbpar(user)
        self.password = self.dbpar(password)
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
        self.exceptions = {
            'base':GnrSqlException,
            'exec':GnrSqlExecException,
            'missedCommit':GnrMissedCommitException
        }

    #-----------------------Configure and Startup-----------------------------

    def dbpar(self,parvalue):
        if parvalue and parvalue.startswith("$"):
            return os.environ.get(parvalue[1:])
        return parvalue

    @property
    def debug(self):
        """TODO"""
        return self.application.debug
        
    @property
    def dbstores(self):
        """TODO"""
        return self.stores_handler.dbstores
        
    @property
    def reuse_relation_tree(self):
        if self.application:
            return boolean(self.application.config['db?reuse_relation_tree']) is not False

    @property
    def auto_static_enabled(self):
        if self.application:
            return boolean(self.application.config['db?auto_static_enabled']) is not False

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

    @property
    def localizer(self):
        return self.application.localizer if self.application else DbLocalizer

    def importArchive(self,archive,thermo_wrapper=None):
        tables = archive.keys()
        if thermo_wrapper:
            tables = thermo_wrapper(tables, maximum=len(tables),message=lambda item, k, m, **kwargs: '%s %i/%i' % (item, k, m), line_code='tables')
        for tbl in tables:
            records = archive[tbl]
            if not records:
                continue
            tblobj = self.table(tbl.replace('/','.'))
            pkeysToAdd = [r[tblobj.pkey] for r in records] 
            f = tblobj.query(where='$%s IN :pkeys' %tblobj.pkey,pkeys=pkeysToAdd,
                            addPkeyColumns=False,excludeLogicalDeleted=False,
                            excludeDraft=False,columns='$%s' %tblobj.pkey
                            ).fetch()
            pkeysToAdd = set(pkeysToAdd)-set([r[tblobj.pkey] for r in f])
            rlist = [dict(r) for r in records if r[tblobj.pkey] in pkeysToAdd ]
            if rlist:
                self.setConstraintsDeferred()
                onArchiveImport = getattr(tblobj,'onArchiveImport',None)
                if onArchiveImport:
                    onArchiveImport(rlist)
                for r in rlist:
                    if r.get('__syscode'):
                        r['__syscode'] = None
                tblobj.insertMany(rlist)
        
    def autoRestore(self,path,sqltextCb=None,onRestored=None):
        assert os.path.exists(path),'Restore archive %s does not exist' %path
        extractpath = path.replace('.zip','')
        destroyFolder = False
        if not os.path.isdir(path):
            from zipfile import ZipFile
            myzip =  ZipFile(path, 'r')
            myzip.extractall(extractpath)
            destroyFolder = True
        stores = {}
        for f in os.listdir(extractpath):
            if f.startswith('.'):
                continue
            dbname = os.path.splitext(f)[0]
            stores[dbname] = os.path.join(extractpath,f)
        dbstoreconfig = Bag(stores.pop('_dbstores'))
        mainfilepath = stores.pop('mainstore',None)
        for s in self.stores_handler.dbstores.keys():
            self.stores_handler.drop_store(s)
        if mainfilepath:
            self._autoRestore_one(dbname=self.dbname,filepath=mainfilepath,sqltextCb=sqltextCb,onRestored=onRestored)
        for storename,filepath in stores.items():
            conf = dbstoreconfig.getItem(storename)
            dbattr = conf.getAttr('db')
            dbname = dbattr.pop('dbname')
            self._autoRestore_one(dbname=dbname,filepath=filepath,sqltextCb=sqltextCb,onRestored=onRestored)
            self.stores_handler.add_dbstore_config(storename,dbname=dbname,save=False,**dbattr)
        if destroyFolder:
            shutil.rmtree(extractpath)

    def _autoRestore_one(self,dbname=None,filepath=None,**kwargs):
        print 'drop',dbname
        self.dropDb(dbname)
        print 'create',dbname
        self.createDb(dbname)
        print 'restore',dbname,filepath
        self.restore(filepath,dbname=dbname,**kwargs)


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
                    conn.rollback()
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


    def getUserConfiguration(self,**kwargs):
        pass
        
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
        return  self.currentStorename == self.rootstore

    def usingMainConnection(self):
        return  self.currentConnectionName== MAIN_CONNECTION_NAME

    @property
    def currentStorename(self):
        return self.currentEnv.get('storename') or self.rootstore
    
    @property
    def currentConnectionName(self):
        return self.currentEnv.get('connectionName') or MAIN_CONNECTION_NAME
    

    def connectionKey(self,storename=None):
        storename = storename or self.currentEnv.get('storename') or self.rootstore
        return  '_'.join((storename or self.currentStorename,self.currentConnectionName))
            
    def _get_store_connection(self, storename):
        thread_ident = thread.get_ident()
        thread_connections = self._connections.setdefault(thread_ident, {})
        connectionTuple = (storename or self.currentStorename,self.currentConnectionName)
        connection = thread_connections.get(connectionTuple)
        if not connection:
            connection = self.adapter.connect(storename)
            connection.storename = storename
            connection.committed = False
            connection.connectionName = connectionTuple[1]
            thread_connections[connectionTuple] = connection
        return connection
    
    def _get_connection(self):
        """property .connection
        If there's not connection open and return connection to database"""
        storename = self.currentStorename
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
        if storename and storename != self.rootstore and storename in self.dbstores:
            storeattr = self.dbstores[storename]
            return dict(host=storeattr.get('host'),database=storeattr.get('database'),
                        user=storeattr.get('user'),password=storeattr.get('password'),
                        port=storeattr.get('port'))
        else:
            return dict(host=self.host, database=self.dbname if not storename or storename=='_main_db' else storename, user=self.user, password=self.password, port=self.port)
    
    def execute(self, sql, sqlargs=None, cursor=None, cursorname=None, 
                autocommit=False, dbtable=None,storename=None,_adaptArguments=True):
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
        envargs = dict([('env_%s' % k, v) for k, v in self.currentEnv.items() if not k.startswith('dbevents')])
        if not 'env_workdate' in envargs:
            envargs['env_workdate'] = self.workdate
        envargs.update(sqlargs or {})
        if storename is False:
            storename = self.rootstore
        storename = storename or envargs.get('env_storename', self.rootstore)
        sqlargs = envargs
        for k,v in sqlargs.items():
            if isinstance(v,basestring) and (v.startswith(r'\$') or v.startswith(r'\@')):
                sqlargs[k] = v[1:]
        if dbtable and self.table(dbtable).use_dbstores(**sqlargs) is False:
            storename = self.rootstore
        with self.tempEnv(storename=storename):
            if _adaptArguments:
                sql=sql.replace(r'\:',chr(1 ))
                sql, sqlargs = self.adapter.prepareSqlText(sql, sqlargs)
                sql=sql.replace(chr(1 ), ':')
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
                    self._multiCursorExecute(cursor,sql,sqlargs)
                    #for c in cursor:
                    #    c.execute(sql.replace("_STORENAME_" ,c.connection.storename), sqlargs)
                else:
                    #if sql.startswith('INSERT') or sql.startswith('UPDATE') or sql.startswith('DELETE'):
                    #    print sql.split(' ',1)[0],storename,self.currentEnv.get('connectionName'),'dbtable',dbtable
                    cursor.execute(sql, sqlargs)
                    cursor.connection.committed = False
                if self.debugger:
                    self.debugger(sql=sql, sqlargs=sqlargs, dbtable=dbtable,delta_time=time()-t_0)
            
            except Exception, e:
                #print sql
                gnrlogger.warning('error executing:%s - with kwargs:%s \n\n', sql, unicode(sqlargs))
                #if self.debugger:
                #    self.debugger(sql=sql, sqlargs=sqlargs, dbtable=dbtable, error=str(e))
                print str('error %s executing:%s - with kwargs:%s \n\n' % (
                str(e), sql, unicode(sqlargs).encode('ascii', 'ignore')))
                self.rollback()
                raise
        
            if autocommit:
                self.commit()
            
        return cursor

    def _multiCursorExecute(self, cursor_list, sql, sqlargs):
        from multiprocessing.pool import ThreadPool
        p = ThreadPool(4)
        def _executeOnThread(cursor):
            cursor.execute(sql.replace("_STORENAME_" ,cursor.connection.storename),sqlargs)
        
        #for c in cursor_list:
        #    _executeOnThread(c)
        p.map(_executeOnThread, cursor_list)

    def notifyDbEvent(self,tblobj,**kwargs):
        pass


    def _onDbChange(self,tblobj,evt,record,old_record=None,**kwargs):
        tblobj.updateTotalizers(record,old_record=old_record,evt=evt,**kwargs)
        if tblobj.attributes.get('logChanges'):
            tblobj.onLogChange(evt,record,old_record=old_record)
            self.table(self.changeLogTable).logChange(tblobj,evt=evt,record=record)
        

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
        self._onDbChange(tblobj,'I',record=record,old_record=None)
        tblobj._doFieldTriggers('onInserted', record)
        tblobj.trigger_onInserted(record)
        tblobj._doExternalPkgTriggers('onInserted', record)
    

    def insertMany(self, tblobj, records, **kwargs):
        self.adapter.insertMany(tblobj, records,**kwargs)

    def raw_insert(self, tblobj, record, **kwargs):
        self.adapter.insert(tblobj, record,**kwargs)
        self._onDbChange(tblobj,'I',record=record,
                        old_record=None,_raw=True,**kwargs)

    def raw_update(self, tblobj, record,old_record=None, **kwargs):
        self.adapter.update(tblobj, record,**kwargs)
        self._onDbChange(tblobj,'U',record=record,
                        old_record=old_record,_raw=True,**kwargs)

    def raw_delete(self, tblobj, record, **kwargs):
        self.adapter.delete(tblobj, record,**kwargs)
        self._onDbChange(tblobj,'D',record=record,
                        old_record=None,_raw=True,**kwargs)
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
        self._onDbChange(tblobj,'U',record=record,old_record=old_record,**kwargs)
        tblobj._doFieldTriggers('onUpdated', record, old_record=old_record)
        tblobj.trigger_onUpdated(record, old_record=old_record)
        tblobj._doExternalPkgTriggers('onUpdated', record, old_record=old_record)

    @in_triggerstack
    def delete(self, tblobj, record, **kwargs):
        """Delete a record from the :ref:`table`
        
        :param tblobj: the table object
        :param record: an object implementing dict interface as colname, colvalue"""
        deletable = tblobj.attributes.get('deletable',True)
        if isinstance(deletable,basestring):
            deletable = self.application.checkResourcePermission(deletable, self.currentEnv['userTags'])
        if not deletable:
            raise GnrSqlException('The records of table %s cannot be deleted' %tblobj.name_long)
        tblobj.protect_delete(record)
        tblobj._doFieldTriggers('onDeleting', record)
        tblobj.trigger_onDeleting(record)
        tblobj._doExternalPkgTriggers('onDeleting', record)
        tblobj.deleteRelated(record)
        self.adapter.delete(tblobj, record,**kwargs)
        self._onDbChange(tblobj,'D',record=record,**kwargs)
        tblobj._doFieldTriggers('onDeleted', record)
        tblobj.trigger_onDeleted(record)
        tblobj._doExternalPkgTriggers('onDeleted', record)
        tblobj.trigger_releaseCounters(record)

    def commit(self):
        trconns = self._connections.get(thread.get_ident(), {})
        while True:
            connections = filter(lambda c: not c.committed and c.connectionName==self.currentConnectionName,
                                trconns.values())
            if not connections:
                break
            connection = connections[0]
            with self.tempEnv(storename=connection.storename):
                self.onCommitting()
            connection.commit()
            connection.committed = True
        self.onDbCommitted()

    def onCommitting(self):
        deferreds = self.currentEnv.setdefault('deferredCalls_%s' %self.connectionKey(),Bag()) 
        with self.tempEnv(onCommittingStep=True):
            while deferreds:
                node =  deferreds.popNode('#0')
                cb,args,kwargs = node.value
                cb(*args,**kwargs)
                allowRecursion = getattr(cb,'deferredCommitRecursion',False)
                if not allowRecursion:
                    deferreds.popNode(node.label) #pop again because during triggers it could adding the same key to deferreds bag

    def deferToCommit(self,cb,*args,**kwargs):
        deferreds = self.currentEnv.setdefault('deferredCalls_%s' %self.connectionKey(),Bag())
        deferredId = kwargs.pop('_deferredId',None)
        if not deferredId:
            deferredId = getUuid()
        deferkw = kwargs
        if deferredId not in deferreds:
            deferreds.setItem(deferredId,(cb,args,deferkw))
        else:
            cb,args,deferkw = deferreds[deferredId]
        return deferkw
        

    def systemDbEvent(self):
        return self.currentEnv.get('_systemDbEvent',False)
    
    @property
    def dbevents(self):
        return self.currentEnv.get('dbevents_%s' %self.connectionKey())

    def autoCommit(self):
        if not self.dbevents:
            return
        if all([all(map(lambda v: v.get('autoCommit'),t)) for t in self.dbevents.values()]):
            self.commit()
        else:
            raise GnrMissedCommitException('Db events not committed')
            
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
    
    def setLocale(self):
        if self.currentEnv.get('locale'):
            self.adapter.setLocale(self.currentEnv['locale'])

    #------------------ PUBLIC METHODS--------------------------
        
    def package(self, pkg):
        """Return a package object
        
        :param pkg: the :ref:`package <packages>` object"""
        return self.model.package(pkg)
            
    def _get_packages(self):
        return self.model.obj
            
    packages = property(_get_packages)

    def tablesMasterIndex(self,hard=False,filterCb=None,filterPackages=None):
        packages = self.packages.keys()
        filterPackages = filterPackages or packages
        toImport = []
        dependencies = dict()
        for k,pkg in enumerate(packages):
            if pkg not in filterPackages:
                continue
            pkgobj = self.package(pkg)
            tables = pkgobj.tables.values()
            if filterCb:
                tables = filter(filterCb,tables)
            toImport.extend(tables)
            for tbl in tables:
                dset = set()
                for d,isdeferred in tbl.dependencies:
                    dpkg = d.split('.')[0]
                    if dpkg not in filterPackages:
                        continue
                    if not isdeferred and (packages.index(dpkg)<=k or hard):
                        dset.add(d)
                dependencies[tbl.fullname] = dset
        imported = set()
        deferred = dict()
        blocking = dict()
        result = Bag()
        self._tablesMasterIndex_step(toImport=toImport,imported=imported,dependencies=dependencies,result=result,deferred=deferred,blocking=blocking)
        if len(deferred)==0:
            return result
        for k,v in deferred.items():
            print 'table ',k,
            print '\t\t blocked by',v
        raise GnrSqlException(description='Blocked dependencies')


    def _tablesMasterIndex_step(self,toImport=None,imported=None,dependencies=None,result=None,deferred=None,blocking=None):
        while toImport:
            tbl = toImport.pop(0)
            tblname = tbl.fullname
            depset = dependencies[tblname]
            if depset.issubset(imported):  
                imported.add(tblname)
                result.setItem(tblname,None)
                result.setItem('_index_.%s' %tblname.replace('.','/'),None,tbl=tblname)
                blocked_tables = blocking.pop(tblname,None)
                if blocked_tables:
                    for k in blocked_tables:
                        deferred[k].remove(tblname)
                        if not deferred[k]:
                            deferred.pop(k)
                        m = self.table(k).model
                        if not m in toImport:
                            toImport.append(m)
            else:
                deltatbl = depset - imported
                deferred[tblname] = deltatbl
                for k in deltatbl:
                    blocking.setdefault(k,set()).add(tblname)


   #def tablesMasterIndex_new(self):
   #    packages = self.packages.keys()
   #    toImport = []
   #    for pkg in packages:
   #        pkgobj = self.package(pkg)
   #        toImport.extend(pkgobj.tables.values())
   #    imported = set()
   #    deferred = dict()
   #    blocking = dict()
   #    result = Bag()
   #    while toImport:
   #        tbl = toImport.pop(0)
   #        tblname = tbl.fullname
   #        print 'table',tblname
   #        depset = set(tbl.dependencies)
   #        if depset.issubset(imported):  
   #            imported.add(tblname)
   #            result.setItem(tblname,None)
   #            result.setItem('_index_.%s' %tbl.fullname.replace('.','/'),None,tbl=tblname)
   #            blocked_tables = blocking.pop(tblname,None)
   #            if blocked_tables:
   #                for k in blocked_tables:
   #                    deferred[k].remove(tblname)
   #                    if not deferred[k]:
   #                        deferred.pop(k)
   #                        #toImport.append(self.table(k).model)
   #                
   #        else:
   #            deltatbl = depset - imported
   #            if (tblname in deferred) and (deltatbl == deferred[tblname]):
   #                print 'cycling',tblname
   #            else:
   #                deferred[tblname] = deltatbl
   #                for k in deferred[tblname]:
   #                    blocking.setdefault(k,set()).add(tblname)
   #                toImport.append(tbl)

   #    print x
   #    return result

    def tableTreeBag(self, packages=None, omit=None, tabletype=None):
        """TODO
        
        :param packages: TODO
        :param omit: TODO
        :param tabletype: TODO"""
        result = Bag()
        packages = self.packages.keys() if packages == '*' else packages
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
              mode=None,_storename=None,aliasPrefix=None,ignoreTableOrderBy=None, subtable=None,**kwargs):
        q = self.table(table).query(columns=columns, where=where, order_by=order_by,
                         distinct=distinct, limit=limit, offset=offset,
                         group_by=group_by, having=having, for_update=for_update,
                         relationDict=relationDict, sqlparams=sqlparams,
                         excludeLogicalDeleted=excludeLogicalDeleted,excludeDraft=excludeDraft,
                         ignorePartition=ignorePartition,
                         addPkeyColumn=addPkeyColumn, locale=locale,_storename=_storename,
                         aliasPrefix=aliasPrefix,ignoreTableOrderBy=ignoreTableOrderBy,subtable=subtable)
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

    def dump(self, filename,dbname=None,**kwargs):
        """Dump a database to a given path
        
        :param filename: the path on which the database will be dumped"""
        return self.adapter.dump(filename,dbname=dbname,**kwargs)
        
    def restore(self, filename,dbname=None,sqltextCb=None,onRestored=None):
        """Restore db to a given path
        
        :param name: the path on which the database will be restored"""
        if sqltextCb:
            filename = sqltextCb(filename)
        #self.dropDb(self.dbname)
        #self.createDb(self.dbname)
        self.adapter.restore(filename,dbname=dbname)
        if onRestored:
            onRestored(self,dbname=dbname)


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

    def freezedPkeys(self,fpath):
        filename = '%s_pkeys.pik' % fpath
        if not os.path.exists(filename):
            return []
        with open(filename) as f:
            return cPickle.load(f)

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
                if currentEnv.get(k)==v:
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
        self.create_stores()

    def get_dbstore(self,storename):
        if storename in self.dbstores:
            return self.dbstores[storename]
        else:
            return self.add_store(storename)
        return
             
    def create_stores(self, check=False):
        """TODO"""
        if not (self.config_folder and os.path.exists(self.config_folder)):
            return
        for filename in os.listdir(self.config_folder):
            name,ext = os.path.splitext(filename)
            if ext!='.xml':
                continue
            self.add_store(name, check=check)
            
    def add_store(self, storename, check=False,dbattr=None):
        """TODO
        
        :param storename: TODO
        :param check: TODO"""
        if not dbattr:
            storefile = os.path.join(self.config_folder,'%s.xml' %storename)
            if not os.path.exists(storefile):
                return
            dbattr = Bag(os.path.join(self.config_folder,'%s.xml' %storename)).getAttr('db')
        self.dbstores[storename] = dict(database=dbattr.get('dbname', storename),
                                        host=dbattr.get('host', self.db.host), user=dbattr.get('user', self.db.user),
                                        password=dbattr.get('password', self.db.password),
                                        port=dbattr.get('port', self.db.port),
                                        remote_host=dbattr.get('remote_host'),
                                        remote_port=dbattr.get('remote_port'))
        if check:
            self.dbstore_align(storename)
        return dbattr
            
    def drop_dbstore_config(self, storename):
        """TODO
        
        :param storename: TODO"""
        dbstore = self.get_dbstore(storename)
        if dbstore:
            storefile = os.path.join(self.config_folder,'%s.xml' %storename)
            if os.path.exists(storefile):
                os.remove(storefile)
        self.dbstores.pop(storename,None)
    
    def drop_store(self,storename):
        dbstoreattr = self.get_dbstore(storename)
        self.db.dropDb(dbstoreattr['database'])
        self.drop_dbstore_config(storename)
        
        
    def add_dbstore_config(self, storename, dbname=None, host=None, user=None, password=None, port=None,save=None,**kwargs):
        """TODO
        
        :param storename: TODO
        :param dbname: the database name
        :param host: the database server host
        :param user: the username
        :param password: the username's password
        :param port: TODO
        :param save: TODO"""
        b = Bag()
        b.setItem('db',None,dbname=dbname, host=host, user=user, password=password,port=port)
        b.toXml(os.path.join(self.config_folder,'%s.xml' %storename))
        self.add_store(storename, check=save)
            
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

class DbLocalizer(object):
    def translate(self,v):
        return v

            
if __name__ == '__main__':
    pass
