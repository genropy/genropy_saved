#-*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy sql - see LICENSE for details
# module gnrsqlclass : Genro sqlite connection
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
#import weakref
import os, re, time

import datetime
import pprint
import decimal

try:
    import sqlite3 as pysqlite
except:
    from pysqlite2 import dbapi2 as pysqlite

from gnr.sql.adapters._gnrbaseadapter import GnrDictRow, GnrWhereTranslator
from gnr.sql.adapters._gnrbaseadapter import SqlDbAdapter as SqlDbBaseAdapter
from gnr.core.gnrbag import Bag

import logging

logger = logging.getLogger(__name__)

class SqlDbAdapter(SqlDbBaseAdapter):
    typesDict = {'charactervarying': 'A', 'character varying': 'A', 'character': 'C', 'text': 'T', 'blob': 'X',
                 'boolean': 'B', 'date': 'D', 'time': 'H', 'timestamp': 'DH', 'numeric': 'N',
                 'integer': 'I', 'bigint': 'L', 'smallint': 'I', 'double precision': 'R', 'real': 'R', 'serial8': 'L'}

    revTypesDict = {'A': 'character varying', 'T': 'text', 'C': 'character',
                    'X': 'blob', 'P': 'text', 'Z': 'text',
                    'B': 'boolean', 'D': 'date', 'H': 'time', 'DH': 'timestamp',
                    'I': 'integer', 'L': 'bigint', 'R': 'real', 'N': 'numeric',
                    'serial': 'serial8'}

    support_multiple_connections = False
    paramstyle = 'named'

    def defaultMainSchema(self):
        return 'main'

    def regexp(self, expr, item):
        r = re.compile(expr, re.U)
        return r.match(item) is not None

    def connect(self,*args,**kwargs):
        """Return a new connection object: provides cursors accessible by col number or col name
        @return: a new connection object"""
        dbpath = self.dbroot.dbname
        conn = pysqlite.connect(dbpath, detect_types=pysqlite.PARSE_DECLTYPES | pysqlite.PARSE_COLNAMES, timeout=20.0)
        conn.create_function("regexp", 2, self.regexp)
        #conn.row_factory = pysqlite.Row
        conn.row_factory = GnrDictRow
        curs = conn.cursor(GnrSqliteCursor)
        attached = [self.defaultMainSchema()]
        if self.dbroot.packages:
            for schema, pkg in self.dbroot.packages.items():
                sqlschema = pkg.sqlschema
                if sqlschema:
                    if not sqlschema in attached:
                        attached.append(sqlschema)
                        self.attach('%s.db' % os.path.join(os.path.dirname(dbpath), sqlschema), sqlschema, cursor=curs)
        curs.close()
        return conn

    def cursor(self, connection, cursorname=None):
        return connection.cursor(GnrSqliteCursor)

    def attach(self, filepath, name, cursor=None):
        """A special sqlite only method for attach external database file as a schema for the current one
        @param filepath: external sqlite db file
        @param name: name of the schema containing the external db
        @param cursor: optional cursor object to use"""
        if not os.path.isfile(filepath):
            conn = pysqlite.connect(filepath)
            conn.close()
        if cursor:
            cursor.execute("ATTACH DATABASE '%s' AS %s;" % (filepath, name))
        else:
            self.dbroot.execute("ATTACH DATABASE '%s' AS %s;" % (filepath, name))

    def prepareSqlText(self, sql, kwargs):
        """Replace the 'REGEXP' operator with '~*'.
        Replace the ILIKE operator with LIKE: sqlite LIKE is case insensitive"""
        sql = sql.replace('ILIKE', 'LIKE').replace('ilike', 'like').replace('~*', ' REGEXP ')
        return sql, kwargs

    def _selectForUpdate(self,maintable_as=None):
        return ''

    def listElements(self, elType, **kwargs):
        """Get a list of element names.
        @param elType: one of the following: schemata, tables, columns, views.
        @param kwargs: schema, table
        @return: list of object names"""
        return getattr(self, '_list_%s' % elType)(**kwargs)

    def _list_schemata(self):
        return [r[1] for r in self.dbroot.execute("PRAGMA database_list;").fetchall()]

    def _list_tables(self, schema):
        query = "SELECT name FROM %s.sqlite_master WHERE type='table';" % (schema,)
        return [r[0] for r in self.dbroot.execute(query).fetchall()]

    def _list_views(self, schema):
        query = "SELECT name FROM %s.sqlite_master WHERE type='view';" % (schema,)
        return [r[0] for r in self.dbroot.execute(query).fetchall()]

    def _list_columns(self, schema, table):
        """cid|name|type|notnull|dflt_value|pk"""
        query = "PRAGMA %s.table_info(%s);" % (schema, table)
        return [r[1] for r in self.dbroot.execute(query).fetchall()]

    def relations(self):
        """Get a list of all relations in the db. 
        Each element of the list is a list (or tuple) with this elements:
        [foreign_constraint_name, many_schema, many_tbl, [many_col, ...], unique_constraint_name, one_schema, one_tbl, [one_col, ...]]
        @return: list of relation's details
        """
        #result = Bag()
        #for schema in self._list_schemata():
        #for tbl in self._list_tables(schema=schema):
        #result['%s.%s' % (schema,tbl)] = Bag()
        result = []
        for schema in self._list_schemata():
            for tbl in self._list_tables(schema=schema):
                query = "PRAGMA %s.foreign_key_list(%s);" % (schema, tbl)
                l = self.dbroot.execute(query).fetchall()

                for r in l:
                    un_tbl = r[2]
                    cols = [r[3]]
                    un_cols = [r[4]]
                    un_schema = schema
                    ref = tbl
                    un_ref = un_tbl

                    result.append([ref, schema, tbl, [col], un_ref, un_schema, un_tbl, [un_col]], None, None, None)
        return result

    def getPkey(self, table, schema):
        """
        @param table: table name
        @param schema: schema name
        @return: list of columns wich are the primary key for the table"""
        query = "PRAGMA %s.table_info(%s);" % (schema, table)
        l = self.dbroot.execute(query).fetchall()
        return [r[1] for r in l if r[5] == 1]


    def getColInfo(self, table, schema, column=None):
        """Get a (list of) dict containing details about a column or all the columns of a table.
        Each dict has those info: name, position, default, dtype, length, notnull
        Every other info stored in PRAGMA table_info is available with the prefix '_sl_'"""
        query = "PRAGMA %s.table_info(%s);" % (schema, table)
        cursor = self.dbroot.execute(query)
        columns = cursor.fetchall()
        if column:
            columns = [col for col in columns if col['name'] == column]
        result = []
        for col in columns:
            col = dict([(k[0], col[k[0]]) for k in cursor.description])
            col['position'] = col.pop('cid')
            col['default'] = col.pop('dflt_value')
            colType = col.pop('type').lower()
            if '(' in colType:
                col['length'] = colType[colType.find('(') + 1:colType.find(')')]
                col['size'] = col['length']
                colType = colType[:colType.find('(')]
            col['dtype'] = self.typesDict[colType]
            col['notnull'] = (col['notnull'] == 'NO')
            col = self._filterColInfo(col, '_sl_')
            if col['dtype'] in ('A','C') and col.get('length'):
                col['size'] = col['_sl_size'] if col['dtype']=='C' else '0:%s' %col['_sl_size']
                if col['size'] == '255':
                    col['size'] = None
                    col['dtype'] = 'T'
            elif col['dtype'] == 'N':
                col['size'] = col.get('_sl_size')
            result.append(col)
        if column:
            result = result[0]
        return result


    def listen(self, msg, timeout=None, onNotify=None, onTimeout=None):
        """Actually sqlite has no message comunications: so simply sleep and executes onTimeout
        TODO: could be implemented with pyro to notify messages
        onTimeout callbacks are executed on every timeout, onNotify on messages.
        Callbacks returns False to stop, or True to continue listening.
        @param msg: name of the message to wait for
        @param timeout: seconds to wait for the message
        @param onNotify: function to execute on arrive of message
        @param onTimeout: function to execute on timeout
        """
        listening = True
        while listening:
            time.sleep(timeout)
            if onTimeout != None:
                listening = onTimeout()

    def notify(self, msg, autocommit=False):
        """Actually sqlite has no message comunications: so simply pass"""
        pass

    def createDb(self, name, encoding='unicode'):
        """Create a new database file.
        Not really usefull with sqlite, just connecting will automatically create the database file
        WARNING: this method does not fail if the database jet exists, other adapters do.
        @param name: db name
        @param encoding: database text encoding
        """
        conn = pysqlite.connect(name)
        conn.close()

    def dropDb(self, name):
        """Drop an existing database file (actually delete the file) 
        @param name: db name
        """
        os.remove(name)

    def getIndexesForTable(self, table, schema):
        """Get a (list of) dict containing details about all the indexes of a table.
        Each dict has those info: name, primary (bool), unique (bool), columns (comma separated string)
        @param table: table name
        @param schema: schema name
        @return: list of index infos"""
        query = "PRAGMA %s.index_list(%s);" % (schema, table)
        idxs = self.dbroot.execute(query).fetchall()
        result = []
        for idx in idxs:
            query = "PRAGMA %s.index_info(%s);" % (schema, idx['name'])
            cols = self.dbroot.execute(query).fetchall()
            cols = [c['name'] for c in cols]
            result.append(dict(name=idx['name'], primary=None, unique=idx['unique'], columns=','.join(cols)))
        return result
        
    def getTableContraints(self, table=None, schema=None):
        """Get a (list of) dict containing details about a column or all the columns of a table.
        Each dict has those info: name, position, default, dtype, length, notnull
        
        Other info may be present with an adapter-specific prefix."""
        # TODO: implement getTableContraints
        return Bag()
        

    def addForeignKeySql(self, c_name, o_pkg, o_tbl, o_fld, m_pkg, m_tbl, m_fld, on_up, on_del, init_deferred):
        """Sqlite cannot add foreign keys, only define them in CREATE TABLE. However they are not enforced."""
        return ''

    def createSchemaSql(self, sqlschema):
        """Sqlite attached dbs cannot be created with an sql command. But they are automatically created in connect()"""
        return ''

    def createSchema(self, sqlschema):
        """Create a new database schema.
        sqlite specific implementation actually attach an external db file."""
        self.attach(sqlschema + '.db', sqlschema)

    def createIndex(self, index_name, columns, table_sql, sqlschema=None, unique=None):
        """create a new index
        sqlite specific implementation fix a naming difference: 
        schema must be prepended to index name and not to table name.
        @param index_name: name of the index (unique in schema)
        @param columns: comma separated list of columns to include in the index
        @param table_sql: actual sql name of the table
        @parm sqlschema: actual sql name of the schema
        @unique: boolean for unique indexing"""
        if sqlschema:
            index_name = '%s.%s' % (sqlschema, index_name)
        if unique:
            unique = 'UNIQUE '
        else:
            unique = ''
        return "CREATE %sINDEX %s ON %s (%s);" % (unique, index_name, table_sql, columns)

    def lockTable(self, dbtable, mode, nowait):
        """We use sqlite just for tests, so we don't care about locking at the moment."""
        pass


class GnrSqliteCursor(pysqlite.Cursor):
    def _get_index(self):
        if not hasattr(self, '_index') or self._index is None:
            self._index = {}
            for i in range(len(self.description)):
                self._index[self.description[i][0]] = i
        return self._index

    index = property(_get_index)

    def execute(self, sql, params=None, *args, **kwargs):
        global logger
        if params:
            if isinstance(params, str):
                params = unicode(params)
            elif isinstance(params, list):
                params = map(lambda s: unicode(s) if isinstance(s, str) else s, params)
            elif isinstance(params,dict):
                for k,v in params.items():
                    if isinstance(v, str):
                        params[k] = unicode(v)
            args = (params, ) + args

        if not sql.startswith('ATTACH'):
            logger.debug(u"gnrsqlite.execute()\n" + sql)
            if params:
                logger.debug(u"Parameters:\n" + pprint.pformat(params)+"\n")

        self._index = None
        try:
            return pysqlite.Cursor.execute(self, sql, *args, **kwargs)
        except Exception, e:
            logger.exception(e)
            raise

# ------------------------------------------------------------------------------------------------------- Add support for time fields to sqlite3 module

def adapt_time(val):
    return val.isoformat()

def convert_time(val):
    return datetime.time(*map(int, val.split(':')))

pysqlite.register_adapter(datetime.time, adapt_time)
pysqlite.register_converter("time", convert_time)

# ------------------------------------------------------------------------------------------------------- Add support for decimal fields to sqlite3 module

pysqlite.register_adapter(decimal.Decimal, lambda x: float(x))
pysqlite.register_converter('numeric', lambda x: decimal.Decimal(str(x)))

# ------------------------------------------------------------------------------------------------------- Fix issues with datetimes and dates

def convert_date(val):
    val = val.partition(' ')[0] # take just the date part, if we received a datetime string
    return datetime.date(*map(int, val.split("-")))

pysqlite.register_converter("date", convert_date)
