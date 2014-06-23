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

import re
import select

from pg8000 import DBAPI
from pg8000.dbapi import require_open_cursor, require_open_connection, CursorWrapper, ConnectionWrapper
from pg8000.interface import DataIterator, Cursor
from gnr.sql.adapters._gnrbaseadapter import GnrDictRow, GnrWhereTranslator
from gnr.sql.adapters._gnrbaseadapter import SqlDbAdapter as SqlDbBaseAdapter
from gnr.core.gnrbag import Bag
from gnr.core.gnrlist import GnrNamedList

DBAPI.paramstyle = 'pyformat'
RE_SQL_PARAMS = re.compile(":(\w*)(\W|$)")

class DictCursorWrapper(CursorWrapper):
    def __init__(self, *args, **kwargs):
        super(DictCursorWrapper, self).__init__(*args, **kwargs)
        self._query_executed = 0

    @require_open_cursor
    def fetchone(self, no_index=False):
        if self._query_executed and not no_index:
            self._build_index()
        return GnrNamedList(self.index, values=self.cursor.read_tuple())

    @require_open_cursor
    def fetchall(self):
        if self._query_executed:
            self._build_index()
        return [GnrNamedList(self.index, values=values) for values in DataIterator(self.cursor, Cursor.read_tuple)]
        #GnrNamedList(obj.index,values=obj.cursor.read_tuple())

    @require_open_cursor
    def fetchmany(self, size=None):
        if size == None:
            res = super(DictCursorWrapper, self).fetchmany()
        else:
            res = super(DictCursorWrapper, self).fetchmany(size)
        if self._query_executed:
            self._build_index()
        return res

    @require_open_cursor
    def next(self):
        if self._query_executed:
            self._build_index()
        res = super(DictCursorWrapper, self).fetchone()
        if res is None:
            raise StopIteration()
        return res

    @require_open_cursor
    def execute(self, operation, args=()):
        self.index = {}
        self._query_executed = 1
        return super(DictCursorWrapper, self).execute(operation, args)

    def _build_index(self):
        if self._query_executed == 1 and self.description:
            for i in range(len(self.description)):
                self.index[self.description[i][0]] = i
            self._query_executed = 0

class DictConnectionWrapper(ConnectionWrapper):
    @require_open_connection
    def cursor(self):
        return DictCursorWrapper(self.conn, self)

class SqlDbAdapter(SqlDbBaseAdapter):
    typesDict = {'character varying': 'A', 'character': 'C', 'text': 'T',
                 'boolean': 'B', 'date': 'D', 'time without time zone': 'H', 'timestamp without time zone': 'DH',
                 'timestamp with time zone': 'DH',
                 'integer': 'I', 'bigint': 'L', 'smallint': 'I', 'double precision': 'R', 'real': 'R', 'bytea': 'O'}

    revTypesDict = {'A': 'character varying', 'T': 'text', 'C': 'character',
                    'X': 'text', 'P': 'text', 'Z': 'text',
                    'B': 'boolean', 'D': 'date', 'H': 'time without time zone', 'DH': 'timestamp without time zone',
                    'I': 'integer', 'L': 'bigint', 'R': 'real',
                    'serial': 'serial8', 'O': 'bytea'}


    def defaultMainSchema(self):
        return 'public'

    def connect(self):
        """Return a new connection object: provides cursors accessible by col number or col name
        @return: a new connection object"""
        dbroot = self.dbroot
        kwargs = dict(host=dbroot.host, database=dbroot.dbname, user=dbroot.user, password=dbroot.password,
                      port=dbroot.port)
        kwargs = dict(
                [(k, v) for k, v in kwargs.items() if v != None]) # remove None parameters, psycopg can't handle them
        #kwargs['charset']='utf8'
        conn = DictConnectionWrapper(**kwargs)
        return conn


    def prepareSqlText(self, sql, kwargs):
        """Change the format of named arguments in the query from ':argname' to '%(argname)s'.
        Replace the 'REGEXP' operator with '~*'
        
        :param sql: the sql string to execute
        :param kwargs: the params dict
        :returns: tuple (sql, kwargs)"""
        return RE_SQL_PARAMS.sub(r'%(\1)s\2', sql).replace('REGEXP', '~*'), kwargs

    def _managerConnection(self):
        dbroot = self.dbroot
        kwargs = dict(host=dbroot.host, database='template1', user=dbroot.user,
                      password=dbroot.password, port=dbroot.port)
        kwargs = dict([(k, v) for k, v in kwargs.items() if v != None])
        #conn =  psycopg2.connect(**kwargs)
        conn = DictConnectionWrapper(**kwargs)
        #conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn

    def createDb(self, name, encoding='unicode'):
        conn = self._managerConnection()
        curs = conn.cursor()
        curs.execute("CREATE DATABASE %s ENCODING '%s';" % (name, encoding))
        curs.close()
        conn.close()

    def dropDb(self, name):
        conn = self._managerConnection()
        curs = conn.cursor()
        curs.execute("DROP DATABASE %s;" % name)
        curs.close()
        conn.close()

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

    def listen(self, msg, timeout=10, onNotify=None, onTimeout=None):
        """Listen for message 'msg' on the current connection using the Postgres LISTEN - NOTIFY method.
        onTimeout callbacks are executed on every timeout, onNotify on messages.
        Callbacks returns False to stop, or True to continue listening.
        @param msg: name of the message to wait for
        @param timeout: seconds to wait for the message
        @param onNotify: function to execute on arrive of message
        @param onTimeout: function to execute on timeout
        """
        self.dbroot.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        curs = self.dbroot.execute('LISTEN %s;' % msg)
        listening = True
        while listening:
            if select.select([curs], [], [], timeout) == ([], [], []):
                if onTimeout != None:
                    listening = onTimeout()
            else:
                if curs.isready():
                    if onNotify != None:
                        listening = onNotify(curs.connection.notifies.pop())
        self.dbroot.connection.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)

    def notify(self, msg, autocommit=False):
        """Notify a message to listener processes using the Postgres LISTEN - NOTIFY method.
        @param msg: name of the message to notify
        @param autocommit: if False (default) you have to commit transaction, and the message is actually sent on commit"""
        self.dbroot.execute('NOTIFY %s;' % msg)
        if autocommit:
            self.dbroot.commit()

    def listElements(self, elType, **kwargs):
        """Get a list of element names.
        @param elType: one of the following: schemata, tables, columns, views.
        @param kwargs: schema, table
        @return: list of object names"""
        query = getattr(self, '_list_%s' % elType)()
        result = self.dbroot.execute(query, kwargs).fetchall()
        return [r[0] for r in result]

    def _list_schemata(self):
        return """SELECT schema_name FROM information_schema.schemata 
              WHERE schema_name != 'information_schema' AND schema_name NOT LIKE 'pg_%%'"""

    def _list_tables(self):
        return """SELECT table_name FROM information_schema.tables
                                    WHERE table_schema=:schema"""

    def _list_views(self):
        return """SELECT table_name FROM information_schema.views WHERE table_schema=:schema"""

    def _list_columns(self):
        return """SELECT column_name as col
                                  FROM information_schema.columns 
                                  WHERE table_schema=:schema 
                                  AND table_name=:table 
                                  ORDER BY ordinal_position"""

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
                r.update_rule AS upd_rule
 
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
        for (ref, schema, tbl, col, un_ref, un_schema, un_tbl, un_col, upd_rule) in ref_constraints:
            r = ref_dict.get(ref, None)
            if r:
                if not col in r[3]:
                    r[3].append(col)
                if not un_col in r[7]:
                    r[7].append(un_col)
            else:
                ref_dict[ref] = [ref, schema, tbl, [col], un_ref, un_schema, un_tbl, [un_col], upd_rule]
        return ref_dict.values()

    def getPkey(self, table, schema):
        """
        @param table: table name
        @param schema: schema name
        @return: list of columns which are the primary key for the table"""
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
        Each dict has this info: name, primary (bool), unique (bool), columns (comma separated string)
        @param table: table name
        @param schema: schema name
        @return: list of index infos"""
        sql = """SELECT indcls.relname AS name, indisunique AS unique, indisprimary AS primary, indkey AS columns
                    FROM pg_index
               LEFT JOIN pg_class AS indcls ON indexrelid=indcls.oid 
               LEFT JOIN pg_class AS tblcls ON indrelid=tblcls.oid 
               LEFT JOIN pg_namespace ON pg_namespace.oid=tblcls.relnamespace 
                   WHERE nspname=:schema AND tblcls.relname=:table;"""
        indexes = self.dbroot.execute(sql, dict(schema=schema, table=table)).fetchall()
        return indexes

    def getColInfo(self, table, schema, column=None):
        """Get a (list of) dict containing details about a column or all the columns of a table.
        Each dict has those info: name, position, default, dtype, length, notnull
        Every other info stored in information_schema.columns is available with the prefix '_pg_'"""
        sql = """SELECT column_name as name,
                        ordinal_position as position, 
                        column_default as default, 
                        is_nullable as notnull, 
                        data_type as dtype, 
                        character_maximum_length as length,
                        *
                      FROM information_schema.columns 
                      WHERE table_schema=:schema 
                      AND table_name=:table 
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
            col['dtype'] = self.typesDict.get(col['dtype'], 'T') #for unrecognized types default dtype is T
            col['notnull'] = (col['notnull'] == 'NO')
            result.append(col)
        if column:
            result = result[0]
        return result
        
