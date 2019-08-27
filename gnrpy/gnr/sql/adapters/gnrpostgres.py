#-*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy sql - see LICENSE for details
# module gnrpostgres : Genro postgres db connection.
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

from future import standard_library
standard_library.install_aliases()
from builtins import str
from past.builtins import basestring
import sys

import re
import select
try:
    import psycopg2
except ImportError:
    try:
        from psycopg2cffi import compat
        compat.register()
    except ImportError:
        try:
            from psycopg2ct import compat
            compat.register()
        except ImportError:
            pass
    import psycopg2

from psycopg2.extras import DictConnection, DictCursor, DictCursorBase
from psycopg2.extensions import cursor as _cursor
from psycopg2.extensions import connection as _connection

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, ISOLATION_LEVEL_READ_COMMITTED

from gnr.sql.adapters._gnrbaseadapter import GnrDictRow, GnrWhereTranslator, DbAdapterException
from gnr.sql.adapters._gnrbaseadapter import SqlDbAdapter as SqlDbBaseAdapter
from gnr.core.gnrbag import Bag
from gnr.sql.gnrsql_exceptions import GnrNonExistingDbException

RE_SQL_PARAMS = re.compile(r":(\S\w*)(\W|$)")
#IN_TO_ANY = re.compile(r'([$]\w+|[@][\w|@|.]+)\s*(NOT)?\s*(IN ([:]\w+))')
#IN_TO_ANY = re.compile(r'(?P<what>\w+.\w+)\s*(?P<not>NOT)?\s*(?P<inblock>IN\s*(?P<value>[:]\w+))',re.IGNORECASE)

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
import threading
import _thread



class SqlDbAdapter(SqlDbBaseAdapter):
    typesDict = {'character varying': 'A', 'character': 'C', 'text': 'T',
                 'boolean': 'B', 'date': 'D', 
                 'time without time zone': 'H',
                 'time with time zone': 'HZ',
                 'timestamp without time zone': 'DH',
                 'timestamp with time zone': 'DHZ',
                  'numeric': 'N', 'money': 'M',
                 'integer': 'I', 'bigint': 'L', 'smallint': 'I', 'double precision': 'R', 'real': 'R', 'bytea': 'O'}

    revTypesDict = {'A': 'character varying', 'T': 'text', 'C': 'character',
                    'X': 'text', 'P': 'text', 'Z': 'text', 'N': 'numeric', 'M': 'money',
                    'B': 'boolean', 'D': 'date', 
                    'H': 'time without time zone',
                    'HZ': 'time with time zone', 
                    'DH': 'timestamp without time zone',
                    'DHZ': 'timestamp with time zone',
                    'I': 'integer', 'L': 'bigint', 'R': 'real',
                    'serial': 'serial8', 'O': 'bytea'}

    _lock = threading.Lock()
    paramstyle = 'pyformat'

    def __init__(self, *args, **kwargs):
        #self._lock = threading.Lock()

        super(SqlDbAdapter, self).__init__(*args, **kwargs)

    def defaultMainSchema(self):
        return 'public'

    def connect(self, storename=None):
        """Return a new connection object: provides cursors accessible by col number or col name
        
        :returns: a new connection object"""
        kwargs = self.dbroot.get_connection_params(storename=storename)
        #kwargs = dict(host=dbroot.host, database=dbroot.dbname, user=dbroot.user, password=dbroot.password, port=dbroot.port)
        kwargs = dict(
                [(k, v) for k, v in list(kwargs.items()) if v != None]) # remove None parameters, psycopg can't handle them
        kwargs[
        'connection_factory'] = GnrDictConnection # build a DictConnection: provides cursors accessible by col number or col name
        self._lock.acquire()
        if 'port' in kwargs:
            kwargs['port'] = int(kwargs['port'])
        try:
            conn = psycopg2.connect(**kwargs)
        finally:
            self._lock.release()
        return conn
        
    def adaptTupleListSet(self,sql,sqlargs):
        for k,v in list(sqlargs.items()):
            if isinstance(v, list) or isinstance(v, set) or isinstance(v,tuple):
                if not isinstance(v,tuple):
                    sqlargs[k] = tuple(v)
                if len(v)==0:
                    re_pattern = """((t\\d+)(_t\\d+)*.\\"?\\w+\\"?" +)(NOT +)*(IN) *:%s""" %k
                    sql = re.sub(re_pattern,lambda m: 'TRUE' if m.group(4) else 'FALSE',sql,flags=re.I)
        return sql

    def prepareSqlText(self, sql, kwargs):
        """Change the format of named arguments in the query from ':argname' to '%(argname)s'.
        Replace the 'REGEXP' operator with '~*'.
        
        :param sql: the sql string to execute.
        :param kwargs: the params dict
        :returns: tuple (sql, kwargs)
        """
        sql = self.adaptTupleListSet(sql,kwargs)
        return RE_SQL_PARAMS.sub(r'%(\1)s\2', sql).replace('REGEXP', '~*'), kwargs
        
    def adaptSqlName(self,name):
        return '"%s"' %name

    def _managerConnection(self):
        dbroot = self.dbroot
        kwargs = dict(host=dbroot.host, database='template1', user=dbroot.user,
                      password=dbroot.password, port=dbroot.port)
        kwargs = dict([(k, v) for k, v in list(kwargs.items()) if v != None])
        #conn = PersistentDB(psycopg2, 1000, **kwargs).connection()
        conn = psycopg2.connect(**kwargs)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn

    def createDb(self, dbname=None, encoding='unicode'):
        if not dbname:
            dbname = self.dbroot.get_dbname()
        conn = self._managerConnection()
        curs = conn.cursor()
        try:
            curs.execute("""CREATE DATABASE "%s" ENCODING '%s';""" % (dbname, encoding))
            conn.commit()
        except:
            raise DbAdapterException("Could not create database %s" % dbname)
        finally:
            curs.close()
            conn.close()
            curs = None
            conn = None

    def lockTable(self, dbtable, mode='ACCESS EXCLUSIVE', nowait=False):
        if nowait:
            nowait = 'NO WAIT'
        else:
            nowait = ''
        sql = "LOCK %s IN %s MODE %s;" % (dbtable.model.sqlfullname, mode, nowait)
        self.dbroot.execute(sql)

    def createDbSql(self, dbname, encoding):
        return """CREATE DATABASE "%s" ENCODING '%s';""" % (dbname, encoding)

    def dropDb(self, name):
        conn = self._managerConnection()
        curs = conn.cursor()
        curs.execute('DROP DATABASE IF EXISTS "%s";' % name)
        curs.close()
        conn.close()
        

    def dropTable(self, dbtable,cascade=False):
        """Drop table"""
        command = 'DROP TABLE IF EXISTS %s;'
        if cascade:
            command = 'DROP TABLE %s CASCADE;'
        tablename = dbtable if isinstance(dbtable,basestring) else dbtable.model.sqlfullname
        self.dbroot.execute(command % tablename)

    def dump(self, filename,dbname=None,excluded_schemas=None, options=None,**kwargs):
        """Dump an existing database
        :param filename: db name
        :param excluded_schemas: excluded schemas
        :param filename: dump options"""
        available_parameters = dict(
            data_only='-a', clean='-c', create='-C', no_owner='-O',
            schema_only='-s', no_privileges='-x', if_exists='--if-exists',
            quote_all_identifiers='--quote-all-identifiers',
            compress = '--compress='
        )
        from subprocess import call
        dbname = dbname or self.dbroot.dbname
        pars = {'dbname':dbname,
                'user':self.dbroot.user,
                'password':self.dbroot.password,
                'host':self.dbroot.host or 'localhost',
                'port':self.dbroot.port or '5432'}
        excluded_schemas = excluded_schemas or []
        options = options or Bag()
        dump_options = []
        for excluded_schema in excluded_schemas:
            dump_options.append('-N')
            dump_options.append(excluded_schema)
        if options['plain_text']:
            dump_options.append('-Fp')
            file_extension = '.sql'
        else:
            dump_options.append('-Fc')
            file_extension = '.pgd'
        for parameter_name, parameter_label in list(available_parameters.items()):
            parameter_value = options[parameter_name]
            if parameter_value:
                if parameter_label.endswith('='):
                    parameter_value = '%s%s'%(parameter_label,parameter_value)
                else:
                    parameter_value = parameter_label
                dump_options.append(parameter_value)
        if not filename.endswith(file_extension):
            filename = '%s%s' % (filename, file_extension)
        #args = ['pg_dump', dbname, '-U', self.dbroot.user, '-f', filename]+extras
        args = ['pg_dump',
            '--dbname=postgresql://%(user)s:%(password)s@%(host)s:%(port)s/%(dbname)s' %pars, 
            '-f', filename]+dump_options
        callresult = call(args)
        return filename
        
    def restore(self, filename,dbname=None):
        """-- IMPLEMENT THIS --
        Drop an existing database
        
        :param filename: db name"""
        from subprocess import call
        dbname = dbname or self.dbroot.dbname
        if filename.endswith('.pgd'):
            call(['pg_restore',filename,'--dbname',dbname])
        else:
            return call(['psql', "dbname=%s user=%s password=%s" % (dbname, self.dbroot.user, self.dbroot.password), '-f', filename])
        

    def importRemoteDb(self, source_dbname,source_ssh_host=None,source_ssh_user=None,
                                source_dbuser=None,source_dbpassword=None,
                                source_dbhost=None,source_dbport=None,
                                dest_dbname=None):
        dest_dbname = dest_dbname or source_dbname
        import subprocess
        self.createDb(dbname=dest_dbname, encoding='unicode')
        srcdb = dict(user=source_dbuser or 'postgres',dbname=source_dbname,
                        password=source_dbpassword or 'postgres',
                        host = source_dbhost or 'localhost',
                        port = source_dbport or '5432')
        ps = subprocess.Popen((
            'ssh','%s@%s' %(source_ssh_user,source_ssh_host),
            '-C', "pg_dump --dbname=postgresql://%(user)s:%(password)s@%(host)s:%(port)s/%(dbname)s" %srcdb
            ),stdout=subprocess.PIPE)
        destdb = {'dbname':dest_dbname,
                'user':self.dbroot.user,
                'password':self.dbroot.password,
                'host':self.dbroot.host or 'localhost',
                'port':self.dbroot.port or '5432'
                }
        output = subprocess.check_output(('psql', 
                                        'dbname=%(dbname)s user=%(user)s password=%(password)s host=%(host)s port=%(port)s' %destdb),
                                        stdin=ps.stdout)
        ps.wait()


    def listRemoteDatabases(self,source_ssh_host=None,source_ssh_user=None,
                                source_dbuser=None,source_dbpassword=None,
                                source_dbhost=None,source_dbport=None):
        import subprocess
        srcdb = dict(user=source_dbuser or 'postgres',
                        password=source_dbpassword or 'postgres',
                        host = source_dbhost or 'localhost',
                        port = source_dbport or '5432')
        ps = subprocess.Popen((
            'ssh','%s@%s' %(source_ssh_user,source_ssh_host),
            '-C', 'psql','-l','-t', "user=%(user)s password=%(password)s host=%(host)s port=%(port)s" %srcdb
            ),stdout=subprocess.PIPE)
        res = ps.stdout.read()
        ps.wait()
        result = []
        if not res:
            return []
        for dbr in res.split('\n'):
            dbname = dbr.split('|')[0].strip()
            if dbname:
                result.append(dbname)
        return result

    
    def createTableAs(self, sqltable, query, sqlparams):
        self.dbroot.execute("CREATE TABLE %s WITH OIDS AS %s;" % (sqltable, query), sqlparams)
        
    def vacuum(self, table='', full=False): #TODO: TEST IT, SEEMS TO LOCK SUBSEQUENT TRANSACTIONS!!!
        """Perform analyze routines on the db"""
        self.dbroot.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        if full:
            self.dbroot.execute('VACUUM FULL ANALYZE %s;' % table)
        else:
            self.dbroot.execute('VACUUM ANALYZE %s;' % table)
        self.dbroot.connection.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
    
    def setLocale(self,locale):
        pass
        #if not locale:
        #    return
        #if len(locale)==2:
        #    locale = '%s_%s' %(locale.lower(),locale.upper())
        #self.dbroot.execute("SET lc_time = '%s' " %locale.replace('-','_'))
        
    def listen(self, msg, timeout=10, onNotify=None, onTimeout=None):
        """Listen for message 'msg' on the current connection using the Postgres LISTEN - NOTIFY method.
        onTimeout callbacks are executed on every timeout, onNotify on messages.
        Callbacks returns False to stop, or True to continue listening.
        
        :param msg: name of the message to wait for
        :param timeout: seconds to wait for the message
        :param onNotify: function to execute on arrive of message
        :param onTimeout: function to execute on timeout
        """
        self.dbroot.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        curs = self.dbroot.execute('LISTEN %s;' % msg)
        listening = True
        conn = curs.connection
        if psycopg2.__version__.startswith('2.0'):
            selector = curs
            #pg_go = curs.isready
        else:
            selector = conn
            #pg_go = conn.poll
        while listening:
            if select.select([selector], [], [], timeout) == ([], [], []):
                if onTimeout != None:
                    listening = onTimeout()
            else:
                if psycopg2.__version__.startswith('2.0'):
                    if curs.isready() and onNotify != None:
                        listening = onNotify(conn.notifies.pop())
                else:
                    conn.poll()
                    while conn.notifies and listening and onNotify != None:
                        listening = onNotify(conn.notifies.pop())
        self.dbroot.connection.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
        
    def notify(self, msg, autocommit=False):
        """Notify a message to listener processes using the Postgres LISTEN - NOTIFY method.
        
        :param msg: name of the message to notify
        :param autocommit: if False (default) you have to commit transaction, and the message is actually sent on commit"""
        self.dbroot.execute('NOTIFY %s;' % msg)
        if autocommit:
            self.dbroot.commit()

            
    def listElements(self, elType, **kwargs):
        """Get a list of element names
        
        :param elType: one of the following: schemata, tables, columns, views.
        :param kwargs: schema, table
        :returns: list of object names"""
        query = getattr(self, '_list_%s' % elType)()
        try:
            result = self.dbroot.execute(query, kwargs).fetchall()
        except psycopg2.OperationalError:
            raise GnrNonExistingDbException(self.dbroot.dbname)
        return [r[0] for r in result]
        
    def dbExists(self, dbname):
        conn = self._managerConnection()
        curs = conn.cursor()
        curs.execute(self._list_databases())
        dbnames = [dbn[0] for dbn in curs.fetchall()]
        curs.close()
        conn.close()
        curs = None
        conn = None
        return dbname in dbnames
        
    def _list_databases(self):
        return 'SELECT datname FROM pg_catalog.pg_database;'

    def _list_schemata(self):
        return """SELECT schema_name FROM information_schema.schemata 
              WHERE schema_name != 'information_schema' AND schema_name NOT LIKE 'pg_%%'"""

    def _list_tables(self):
        return """SELECT table_name FROM information_schema.tables
                                    WHERE table_schema=:schema"""

    def _list_views(self):
        return """SELECT table_name FROM information_schema.views WHERE table_schema=:schema"""

    def _list_extensions(self):
        return """SELECT name FROM pg_available_extensions;"""

    def _list_enabled_extensions(self):
        return """SELECT name FROM pg_available_extensions where installed_version IS NOT NULL;"""

    def _list_columns(self):
        return """SELECT column_name as col
                                  FROM information_schema.columns 
                                  WHERE table_schema=:schema 
                                  AND table_name=:table 
                                  ORDER BY ordinal_position"""


    def dropExtension(self, extensions):
        """Disable a specific db extension"""
        extensions = extensions.split(',')
        enabled = self.listElements('enabled_extensions')
        commit = False
        for extension in extensions:
            if extension in enabled:
                self.dbroot.execute(self.dropExtensionSql(extension))
                commit = True
        return commit

    def createExtension(self, extensions):
        """Enable a specific db extension"""
        extensions = extensions.split(',')
        enabled = self.listElements('enabled_extensions')
        commit = False
        for extension in extensions:
            if not extension in enabled:
                self.dbroot.execute(self.createExtensionSql(extension))
                commit = True
        return commit

    def createExtensionSql(self,extension):
        return """CREATE extension %s;""" %extension

    def dropExtensionSql(self,extension):
        return """DROP extension IF EXISTS %s;""" %extension

    def relations(self):
        """Get a list of all relations in the db. 
        Each element of the list is a list (or tuple) with this elements:
        [foreign_constraint_name, many_schema, many_tbl, [many_col, ...], unique_constraint_name, one_schema, one_tbl, [one_col, ...]]
        @return: list of relation's details
        """
        sql = """SELECT r.constraint_name AS ref,
                c1.table_schema AS ref_schema,
                c1.table_name AS ref_tbl, 
                mcols.column_name AS ref_col,
                r.unique_constraint_name AS un_ref,
                c2.table_schema AS un_schema,
                c2.table_name AS un_tbl,
                ucols.column_name AS un_col,
                r.update_rule AS upd_rule,
                r.delete_rule AS del_rule,
                c1.initially_deferred AS init_defer
                
                FROM information_schema.referential_constraints AS r
                        JOIN information_schema.table_constraints AS c1
                                ON c1.constraint_catalog = r.constraint_catalog 
                                        AND c1.constraint_schema = r.constraint_schema
                                        AND c1.constraint_name = r.constraint_name 
                        JOIN information_schema.table_constraints AS c2
                                ON c2.constraint_catalog = r.unique_constraint_catalog 
                                        AND c2.constraint_schema = r.unique_constraint_schema
                                        AND c2.constraint_name = r.unique_constraint_name
                        JOIN information_schema.key_column_usage as mcols
                                ON mcols.constraint_schema = r.constraint_schema 
                                        AND mcols.constraint_name= r.constraint_name
                        JOIN information_schema.key_column_usage as ucols
                                ON ucols.constraint_schema = r.unique_constraint_schema
                                        AND ucols.constraint_name= r.unique_constraint_name
                                        """
        ref_constraints = self.dbroot.execute(sql).fetchall()
        ref_dict = {}
        for (
        ref, schema, tbl, col, un_ref, un_schema, un_tbl, un_col, upd_rule, del_rule, init_defer) in ref_constraints:
            r = ref_dict.get(ref, None)
            if r:
                if not col in r[3]:
                    r[3].append(col)
                if not un_col in r[7]:
                    r[7].append(un_col)
            else:
                ref_dict[ref] = [ref, schema, tbl, [col], un_ref, un_schema, un_tbl, [un_col], upd_rule, del_rule,
                                 init_defer]
        return list(ref_dict.values())

    def getPkey(self, table, schema):
        """:param table: the :ref:`database table <table>` name, in the form ``packageName.tableName``
                      (packageName is the name of the :ref:`package <packages>` to which the table
                      belongs to)
        :param schema: schema name
        :return: list of columns wich are the primary key for the table"""
        sql = """SELECT k.column_name        AS col
                FROM   information_schema.key_column_usage      AS k 
                JOIN   information_schema.table_constraints     AS c
                ON     c.constraint_catalog = k.constraint_catalog 
                AND    c.constraint_schema  = k.constraint_schema
                AND    c.constraint_name    = k.constraint_name         
                WHERE  k.table_schema       =:schema
                AND    k.table_name         =:table 
                AND    c.constraint_type    ='PRIMARY KEY'
                ORDER BY k.ordinal_position"""
        return [r['col'] for r in self.dbroot.execute(sql, dict(schema=schema, table=table)).fetchall()]

    def getIndexesForTable(self, table, schema):
        """Get a (list of) dict containing details about all the indexes of a table.
        Each dict has those info: name, primary (bool), unique (bool), columns (comma separated string)
        
        :param table: the :ref:`database table <table>` name, in the form ``packageName.tableName``
                      (packageName is the name of the :ref:`package <packages>` to which the table
                      belongs to)
        :param schema: schema name
        :returns: list of index infos"""
        sql = """SELECT indcls.relname AS name, indisunique AS unique, indisprimary AS primary, indkey AS columns
                    FROM pg_index
               LEFT JOIN pg_class AS indcls ON indexrelid=indcls.oid 
               LEFT JOIN pg_class AS tblcls ON indrelid=tblcls.oid 
               LEFT JOIN pg_namespace ON pg_namespace.oid=tblcls.relnamespace 
                   WHERE nspname=:schema AND tblcls.relname=:table;"""
        indexes = self.dbroot.execute(sql, dict(schema=schema, table=table)).fetchall()
        return indexes

    def getTableContraints(self, table=None, schema=None):
        """Get a (list of) dict containing details about a column or all the columns of a table.
        Each dict has those info: name, position, default, dtype, length, notnull
        Every other info stored in information_schema.columns is available with the prefix '_pg_'"""
        sql = """SELECT constraint_type,column_name,tc.table_name,tc.table_schema,tc.constraint_name
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.constraint_column_usage AS cu 
                ON cu.constraint_name=tc.constraint_name  
                WHERE constraint_type='UNIQUE'
                %s%s;"""
        filtertable = ""
        if table:
            filtertable = " AND tc.table_name=:table"
        filterschema = ""
        if schema:
            filterschema = " AND tc.table_schema=:schema"
        result = self.dbroot.execute(sql % (filtertable,filterschema),
                                      dict(schema=schema,
                                           table=table)).fetchall()
            
        res_bag = Bag()
        for row in result:
            row=dict(row)
            res_bag.setItem('%(table_schema)s.%(table_name)s.%(column_name)s'%row,row['constraint_name'])
        return res_bag
            
    def getColInfo(self, table, schema, column=None):
        """Get a (list of) dict containing details about a column or all the columns of a table.
        Each dict has those info: name, position, default, dtype, length, notnull
        Every other info stored in information_schema.columns is available with the prefix '_pg_'"""
        sql = """SELECT c1.column_name as name,
                        c1.ordinal_position as position, 
                        c1.column_default as default, 
                        c1.is_nullable as notnull, 
                        c1.data_type as dtype, 
                        c1.character_maximum_length as length,
                        *
                      FROM information_schema.columns AS c1
                      WHERE c1.table_schema=:schema 
                      AND c1.table_name=:table 
                      %s
                      ORDER BY position"""
        filtercol = ""
        if column:
            filtercol = "AND column_name=:column"
        columns = self.dbroot.execute(sql % filtercol,
                                      dict(schema=schema,
                                           table=table,
                                           column=column)).fetchall()
        result = []
        for col in columns:
            col = dict(col)
            col = self._filterColInfo(col, '_pg_')
            dtype = col['dtype'] = self.typesDict.get(col['dtype'], 'T') #for unrecognized types default dtype is T
            col['notnull'] = (col['notnull'] == 'NO')
            if dtype == 'N':
                precision, scale = col.get('_pg_numeric_precision'), col.get('_pg_numeric_scale')
                if precision:
                    col['size'] = '%i,%i' % (precision, scale)
            elif dtype == 'A':
                size = col.get('length')
                if size:
                    col['size'] = '0:%i' % size
                else:
                    dtype = col['dtype'] = 'T'
            elif dtype == 'C':
                col['size'] = str(col.get('length'))
            result.append(col)
        if column:
            result = result[0]
        return result

    def getWhereTranslator(self):
        return GnrWhereTranslatorPG(self.dbroot)



class GnrDictConnection(_connection):
    """A connection that uses DictCursor automatically."""


    def __init__(self, *args, **kwargs):
        super(GnrDictConnection, self).__init__(*args, **kwargs)

    def cursor(self, name=None):
        if name:
            cur = super(GnrDictConnection, self).cursor(name, cursor_factory=GnrDictCursor)
        else:
            cur = super(GnrDictConnection, self).cursor(cursor_factory=GnrDictCursor)
        return cur

class GnrDictCursor(_cursor):
    """Base class for all dict-like cursors."""

    def __init__(self, *args, **kwargs):
        row_factory = GnrDictRow
        super(GnrDictCursor, self).__init__(*args, **kwargs)
        self._query_executed = 0
        self.row_factory = row_factory

    def fetchone(self):
        if self._query_executed:
            self._build_index()
        return super(GnrDictCursor, self).fetchone()

    def fetchmany(self, size=None):
        if size == None:
            res = super(GnrDictCursor, self).fetchmany()
        else:
            res = super(GnrDictCursor, self).fetchmany(size)
        if self._query_executed:
            self._build_index()
        return res

    def fetchall(self):
        if self._query_executed:
            self._build_index()
        return super(GnrDictCursor, self).fetchall()

    def __next__(self):
        if self._query_executed:
            self._build_index()
        res = super(GnrDictCursor, self).fetchone()
        if res is None:
            raise StopIteration()
        return res

    def execute(self, query, vars=None, async_=0):
        self.index = {}
        self._query_executed = 1
        if psycopg2.__version__.startswith('2.0'):
            return super(GnrDictCursor, self).execute(query, vars, async_)
        return super(GnrDictCursor, self).execute(query, vars)
    
    def setConstraintsDeferred(self):
        self.execute("SET CONSTRAINTS all DEFERRED;")

    def callproc(self, procname, vars=None):
        self.index = {}
        self._query_executed = 1
        return super(GnrDictCursor, self).callproc(procname, vars)

    def _build_index(self):
        if self._query_executed == 1 and self.description:
            i = 0
            for desc_rec in self.description:
                desc = desc_rec[0]
                if desc not in self.index:
                    self.index[desc] = i
                    i+=1
            self._query_executed = 0

class GnrWhereTranslatorPG(GnrWhereTranslator):
    def op_similar(self, column, value, dtype, sqlArgs,tblobj):
        "!!Similar"
        phonetic_column =  tblobj.column(column).attributes['phonetic']
        phonetic_mode = tblobj.column(column).table.column(phonetic_column).attributes['phonetic_mode']
        return '%s = %s(:%s)' % (phonetic_column, phonetic_mode, self.storeArgs(value, dtype, sqlArgs))

    def unaccent(self,v):
        return 'unaccent(%s)' %v


