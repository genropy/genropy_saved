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

IN_OPERATOR_PATCH = re.compile(r'\s\S+\sIN\s\(\)')

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
    
    def __init__(self, implementation='sqlite', dbname='mydb',
                 host=None, user=None, password=None, port=None,
                 main_schema=None, debugger=None, application=None,
                 allow_eager_many=False, allow_eager_one=False):
        """This is the constructor method of the GnrSqlDb class.
        
        :param implementation: 'sqlite', 'postgres' or other sql implementations.
        :param dbname: the name for your db.
        :param host: the database server host (for sqlite is None)
        :param user: a database user's name (for sqlite is None)
        :param password: the user's password (for sqlite is None)
        :param port: the connection port (for sqlite is None)
        :param main_schema: the database main_schema. Default value is ``None``
        :param debugger: the database main_schema. Default value is ``None``
        :param application: the database main_schema. Default value is ``None``
        :param allow_eager_many: the database main_schema. Default value is ``False``
        :param allow_eager_one: the database main_schema. Default value is ``False``
        """
        
        self.implementation = implementation
        self.dbname = dbname
        self.host = host
        self.port = port
        self.user = user
        self.password = password
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
        self.allow_eager_one = allow_eager_one
        self.allow_eager_many = allow_eager_many
        self.stores_handler = DbStoresHandler(self)
        
    #------------------------Configure and Startup-----------------------------
    
    @property
    def debug(self):
        """add???"""
        return self.application.debug
        
    @property
    def dbstores(self):
        """add???
        
        :returns: add???
        """
        return self.stores_handler.dbstores
        
    def createModel(self):
        """add???
        
        :returns: add???
        """
        from gnr.sql.gnrsqlmodel import DbModel
        
        return DbModel(self)
        
    def startup(self):
        """Build the model.obj from the model.src"""
        self.model.build()
        self.started = True
        
    def packageSrc(self, name):
        """Return a DbModelSrc corresponding to the required package
        
        :param name: the package name
        :returns: add???
        """
        return self.model.src.package(name)
        
    def packageMixin(self, name, obj):
        """Register a mixin for a package.
        
        :param name: the target package's name
        :param obj: a class or an object to mixin
        """
        self.model.packageMixin(name, obj)
        
    def tableMixin(self, tblpath, obj):
        """Register an object or a class to mixin to a table.
        
        :param tblpath: add???
        :param obj: a class or an object to mixin
        """
        self.model.tableMixin(tblpath, obj)
        
    def loadModel(self, source=None):
        """Load the model.src from a XML source
        
        :param source: the XML model (diskfile or text or url). Default value is ``None``
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
        
        :param applyChanges: boolean. If True, all the changes are executed and committed. Default value is ``False``
        """
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
        """add???
        
        :returns: add???
        """
        return TempEnv(self, **kwargs)
        
    def _get_currentEnv(self):
        """property currentEnv - Return the env currently used in this thread"""
        return self._currentEnv.setdefault(thread.get_ident(), {})
        
    def _set_currentEnv(self, env):
        """set currentEnv for this thread"""
        self._currentEnv[thread.get_ident()] = env
        
    currentEnv = property(_get_currentEnv, _set_currentEnv)
        
    def _get_workdate(self):
        """property currentEnv it returns the workdate currently used in this thread"""
        return self.currentEnv.get('workdate') or datetime.today()
        
    def _set_workdate(self, workdate):
        self.currentEnv['workdate'] = workdate
        
    workdate = property(_get_workdate, _set_workdate)
        
    def _get_locale(self):
        """property currentEnv - Return the workdate currently used in this thread"""
        return self.currentEnv.get('locale') or locale.getdefaultlocale()[0]
        
    def _set_locale(self, locale):
        self.currentEnv['locale'] = locale
        
    locale = property(_get_locale, _set_locale)
        
    def updateEnv(self, **kwargs):
        """add???"""
        self.currentEnv.update(kwargs)
        
    def use_store(self, storename=None):
        """add???
        
        :param storename: add???. Default value is ``None``
        """
        self.updateEnv(storename=storename)
        
    def get_dbname(self):
        """add???"""
        storename = self.currentEnv.get('storename')
        if storename:
            return self.dbstores[storename]['database']
        else:
            return self.dbname
            
    def _get_localizer(self):
        if self.application and self.application.site and self.application.site.currentPage:
            return self.application.site.currentPage.localizer
            
    localizer = property(_get_localizer)
        
    def _get_connection(self):
        """property .connection
        If there's not connection open and return connection to database"""
        thread_ident = thread.get_ident()
        storename = self.currentEnv.get('storename') or '_main_db'
        thread_connections = self._connections.setdefault(thread_ident, {})
        connectionName = '%s_%s' % (storename, self.currentEnv.get('connectionName') or '_main_connection')
        connection = thread_connections.get(connectionName)
        if not connection:
            connection = self.adapter.connect()
            thread_connections[connectionName] = connection
        return connection
        #return thread_connections.setdefault(connectionName, self.adapter.connect()) 
            
    connection = property(_get_connection)
            
    def get_connection_params(self):
        storename = self.currentEnv.get('storename')
        if storename and storename != '_main_db':
            return self.dbstores[storename]
        else:
            return dict(host=self.host, database=self.dbname, user=self.user, password=self.password, port=self.port)
            
    def execute(self, sql, sqlargs=None, cursor=None, cursorname=None, autocommit=False, dbtable=None):
        """Execute the sql statement using given kwargs
        
        :param sql: add???
        :param sqlargs: add???. Default value is ``None``
        :param cursor: add???. Default value is ``None``
        :param cursorname: add???. Default value is ``None``
        :param autocommit: add???. Default value is ``None``
        :param dbtable: add???. Default value is ``None``
        :returns: add???
        """
        # transform list and tuple parameters in named values.
        # Eg.   WHERE foo IN:bar ----> WHERE foo in (:bar_1, :bar_2..., :bar_n)
        envargs = dict([('env_%s' % k, v) for k, v in self.currentEnv.items()])
        if not 'env_workdate' in envargs:
            envargs['env_workdate'] = self.workdate
        envargs.update(sqlargs or {})
        sqlargs = envargs
        if dbtable and not self.table(dbtable).use_dbstores():
            storename = '_main_db'
        else:
            storename = sqlargs.pop('storename', self.currentEnv.get('storename', '_main_db'))
        with self.tempEnv(storename=storename):
            for k, v in [(k, v) for k, v in sqlargs.items() if isinstance(v, list) or isinstance(v, tuple)]:
                sqllist = '(%s) ' % ','.join([':%s%i' % (k, i) for i, ov in enumerate(v)])
                sqlargs.pop(k)
                sqlargs.update(dict([('%s%i' % (k, i), ov) for i, ov in enumerate(v)]))
                sql = re.sub(':%s(\W|$)' % k, sqllist, sql)
            sql = re.sub(IN_OPERATOR_PATCH, ' FALSE', sql)
            sql, sqlargs = self.adapter.prepareSqlText(sql, sqlargs)
            #gnrlogger.info('Executing:%s - with kwargs:%s \n\n',sql,unicode(kwargs))
            #print 'sql:\n',sql
            try:
                if not cursor:
                    if cursorname:
                        if cursorname == '*':
                            cursorname = 'c%s' % re.sub('\W', '_', getUuid())
                        cursor = self.adapter.cursor(self.connection, cursorname)
                    else:
                        cursor = self.adapter.cursor(self.connection)
                cursor.execute(sql, sqlargs)
                if self.debugger:
                    self.debugger(debugtype='sql', sql=sql, sqlargs=sqlargs, dbtable=dbtable)
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
        
    def insert(self, tblobj, record, **kwargs):
        """Insert a record in the table.
        
        :param tblobj: the table object
        :param record: an object implementing dict interface as colname, colvalue
        """
        tblobj.checkPkey(record)
        tblobj.protect_validate(record)
        tblobj._doFieldTriggers('onInserting', record)
        tblobj.trigger_onInserting(record)
        self.adapter.insert(tblobj, record,**kwargs)
        tblobj.trigger_onInserted(record)
        
    def update(self, tblobj, record, old_record=None, pkey=None, **kwargs):
        """Update a table's record
        
        :param tblobj: the table object
        :param record: an object implementing dict interface as colname, colvalue
        :param old_record: the record to be overwritten. Default value is ``None``
        :param pkey: add???. Default value is ``None``
        """
        tblobj.protect_update(record, old_record=old_record)
        tblobj.protect_validate(record, old_record=old_record)
        tblobj._doFieldTriggers('onUpdating', record)
        tblobj.trigger_onUpdating(record, old_record=old_record)
        self.adapter.update(tblobj, record, pkey=pkey,**kwargs)
        tblobj.trigger_onUpdated(record, old_record=old_record)
        
    def delete(self, tblobj, record, **kwargs):
        """Delete a record from the table
        
        :param tblobj: the table object
        :param record: an object implementing dict interface as colname, colvalue
        """
        tblobj.protect_delete(record)
        tblobj._doFieldTriggers('onDeleting', record)
        tblobj.trigger_onDeleting(record)
        tblobj.deleteRelated(record)
        self.adapter.delete(tblobj, record,**kwargs)
        tblobj.trigger_onDeleted(record)
        
    def commit(self):
        """Commit a transaction"""
        self.connection.commit()
        
    def setConstraintsDeferred(self):
        """add???"""
        cursor = self.adapter.cursor(self.connection)
        if hasattr(cursor,'setConstraintsDeferred'):
            cursor.setConstraintsDeferred()
        
    def rollback(self):
        """Rollback a transaction """
        self.connection.rollback()
        
    def listen(self, *args, **kwargs):
        """Listen for a database event (postgres)"""
        self.adapter.listen(*args, **kwargs)
        
    def notify(self, *args, **kwargs):
        """Database Notify
        
        :param args: add???
        :param kwargs: add???
        """
        self.adapter.notify(*args, **kwargs)
        
    def analyze(self):
        """Analyze db"""
        self.adapter.analyze()
        
    def vacuum(self):
        """add???"""
        self.adapter.vacuum()
        
    #------------------ PUBLIC METHODS--------------------------
        
    def package(self, pkg):
        """Return a package object
        
        :param pkw: the package name
        :returns: the package object
        """
        return self.model.package(pkg)
            
    def _get_packages(self):
        """add???
        
        :param pkw: package name"""
        return self.model.obj
            
    packages = property(_get_packages)
            
    def tableTreeBag(self, packages=None, omit=None, tabletype=None):
        """add???
        
        :param packages: add???. Default value is ``None``
        :param omit: add???. Default value is ``None``
        :param tabletype: add???. Default value is ``None``
        :returns: add???
        """
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
        
        :param tblname: table name
        :param pkg: package name. Default value is ``None``
        :returns: a table object
        """
        return self.model.table(tblname, pkg=pkg).dbtable
            
    def query(self, table, **kwargs):
        """For more information, check gnrsqltable.SqlTable.query
        
        :param table: add???
        :returns: add???
        """
        return self.table(table).query(**kwargs)
            
    def colToAs(self, col):
        """add???
        
        :param col: add???
        :returns: add???
        """
        as_ = re.sub('\W', '_', col)
        if as_[0].isdigit(): as_ = '_' + as_
        return as_
            
    def relationExplorer(self, table, prevCaption='', prevRelation='',
                         translator=None, **kwargs):
        """add???
        
        :param table: add???
        :param prevCaption: add???. Default value is ``''``
        :param prevRelation: add???. Default value is ``''``
        :param translator: add???. Default value is ``None``
        :returns: add???
        """
        return self.table(table).relationExplorer(prevCaption=prevCaption,
                                                  prevRelation=prevRelation,
                                                  translator=translator, **kwargs)
                                                  
    def createDb(self, name, encoding='unicode'):
        """Create a db with a given name and an encoding
        
        :param name: the database's name
        :param encoding: The multibyte character encoding you choose. Default value is ``unicode`
        """
        self.adapter.createDb(name, encoding=encoding)
            
    def dropDb(self, name):
        """Drop a database with a given name
        
        :param name: the database's name
        """
        self.adapter.dropDb(name)
            
    def dump(self, filename):
        """Dump a database to a given path
        
        :param filename: the path on which the database will be dumped
        """
        self.adapter.dump(filename)

    def restore(self, filename):
        """Restore db to a given path
        
        :param name: the path on which the database will be restored
        """
        #self.dropDb(self.dbname)
        #self.createDb(self.dbname)
        self.adapter.restore(filename)
        
    def createSchema(self, name):
        """Create a database schema
        
        :param name: the schema's name
        """
        self.adapter.createSchema(name)
        
    def dropSchema(self, name):
        """Drop a db schema
        
        :param name: add???
        """
        self.adapter.dropSchema(name)

    def importXmlData(self, path):
        """Populates a database from an XML file
        
        :param path: the file path
        """
        data = Bag(path)
        for table, pkg in data.digest('#k,#a.pkg'):
            for n in data[table]:
                self.table(table, pkg=pkg).insertOrUpdate(n.attr)

    def unfreezeSelection(self, fpath):
        """Get a pickled selection
        
        :param fpath: add???
        :returns: add???
        """
        filename = '%s.pik' % fpath
        if not os.path.exists(filename):
            return
        f = file('%s.pik' % fpath, 'r')
        selection = cPickle.load(f)
        f.close()
        selection.dbtable = self.table(selection.tablename)
        return selection

class TempEnv(object):
    """add???
    
    Example::
    
        with db.tempEnv(foo=7) as db:
            # do something
            pass
    """
        
    def __init__(self, db, **kwargs):
        self.db = db
        self.kwargs = kwargs

    def __enter__(self):
        if self.db.adapter.support_multiple_connections:
            currentEnv = self.db.currentEnv
            self.savedEnv = dict(currentEnv)
            currentEnv.update(self.kwargs)
        return self.db

    def __exit__(self, type, value, traceback):
        if self.db.adapter.support_multiple_connections:
            self.db.currentEnv = self.savedEnv

class DbStoresHandler(object):
    """Handler for using multi-database"""
        
    def __init__(self, db):
        self.db = db
        self.config_folder = os.path.join(db.application.instanceFolder, 'dbstores')
        self.dbstores = {}
        self.load_config()
        self.create_stores()
        
    def load_config(self):
        """add???"""
        self.config = Bag()
        if os.path.isdir(self.config_folder):
            self.config = Bag(self.config_folder)['#0'] or Bag()
            
    def save_config(self):
        """add???"""
        try:
            shutil.rmtree(self.config_folder, True)
        except OSError:
            pass
        for name, params in self.config.digest('#a.file_name,#v.#0?#'):
            dbstore_config = Bag()
            dbstore_config.setItem('db', None, **params)
            dbstore_config.toXml(os.path.join(self.config_folder, '%s.xml' % name), autocreate=True)
            
    def create_stores(self):
        """add???"""
        for name in self.config.digest('#a.file_name'):
            self.add_store(name)
            
    def add_store(self, storename, check=False):
        """add???
        
        :param storename: add???
        :param check: add???. Default value is ``False``
        """
        attr = self.config.getAttr('%s_xml.db' % storename)
        self.dbstores[storename] = dict(database=attr.get('dbname', storename),
                                        host=attr.get('host', self.db.host), user=attr.get('user', self.db.user),
                                        password=attr.get('password', self.db.password),
                                        port=attr.get('port', self.db.port))
        if check:
            self.dbstore_align(storename)
            
    def drop_dbstore_config(self, storename):
        """add???
        
        :param storename: add???
        """
        self.config.pop('%s_xml' % storename)
        
    def add_dbstore_config(self, storename, dbname=None, host=None, user=None, password=None, port=None, save=True):
        """add???
        
        :param storename: add???
        :param dbname: add???. Default value is ``None``
        :param host: add???. Default value is ``None``
        :param user: add???. Default value is ``None``
        :param password: add???. Default value is ``None``
        :param port: add???. Default value is ``None``
        :param save: add???. Default value is ``True``
        """
        self.config.setItem('%s_xml' % storename, None, file_name=storename)
        self.config.setItem('%s_xml.db' % storename, None, dbname=dbname, host=host, user=user, password=password,
                            port=port)
        if save:
            self.save_config()
            self.load_config()
            self.add_store(storename, check=True)
            
    def dbstore_check(self, storename, verbose=False):
        """checks if dbstore exists and if it needs to be aligned
        
        :param storename: add???
        :param verbose: add???. Default value is ``False``
        """
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
        """add???
        
        :param storename: add???
        :param changes: add???. Default value is ``None``
        """
        with self.db.tempEnv(storename=storename):
            self.db.use_store(storename)
            changes = changes or self.db.model.check()
            if changes:
                self.db.model.applyModelChanges()
            self.db.use_store('_main_db')
            
if __name__ == '__main__':
    pass
        