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

import _mssql
import pymssql
from pymssql import Connection, Cursor
from gnr.sql.adapters._gnrbaseadapter import SqlDbAdapter as SqlDbBaseAdapter
from gnr.sql.adapters._gnrbaseadapter import GnrWhereTranslator as GnrWhereTranslator_base
from gnr.core.gnrlist import GnrNamedList
from gnr.core.gnrbag import Bag

#DBAPI.paramstyle = 'pyformat'
RE_SQL_PARAMS = re.compile(":(\w*)(\W|$)")

class DictCursorWrapper(Cursor):
    def __init__(self, *args, **kwargs):
        super(DictCursorWrapper, self).__init__(*args, **kwargs)
        self._query_executed = 0

    def fetchone(self, no_index=False):
        if self._query_executed and not no_index:
            self._build_index()
        return GnrNamedList(self.index, values=self.cursor.read_tuple())

    def fetchall(self):
        if self._query_executed:
            self._build_index()
        return [GnrNamedList(self.index, values=values) for values in [tuple([row[r] for r in sorted(row.keys()) if \
                    type(r) == int]) for row in self._source._conn]]
        #GnrNamedList(obj.index,values=obj.cursor.read_tuple())

    def fetchmany(self, size=None):
        if size == None:
            res = super(DictCursorWrapper, self).fetchmany()
        else:
            res = super(DictCursorWrapper, self).fetchmany(size)
        if self._query_executed:
            self._build_index()
        return res

    def next(self):
        if self._query_executed:
            self._build_index()
        res = super(DictCursorWrapper, self).fetchone()
        if res is None:
            raise StopIteration()
        return res

    def execute(self, operation, args=()):
        self.index = {}
        self._query_executed = 1
        return super(DictCursorWrapper, self).execute(operation, args)

    def _build_index(self):
        if self._query_executed == 1 and self.description:
            for i in range(len(self.description)):
                self.index[self.description[i][0]] = i
            self._query_executed = 0

class DictConnectionWrapper(Connection):
    def cursor(self):
        return DictCursorWrapper(self, False)

class SqlDbAdapter(SqlDbBaseAdapter):
    typesDict = {'nvarchar': 'A', 'nchar': 'C', 'ntext': 'T',
                 'BOOLEAN': 'B', 'datetime': 'D', 'datetime': 'H', 'datetime': 'DH',
                 'datetime': 'DH',
                 'int': 'I', 'bigint': 'L', 'smallint': 'I','tinyint': 'I', 'real': 'R', 'float': 'R', 'binary': 'O'}

    revTypesDict = {'A': 'nvarchar', 'T': 'ntext', 'C': 'nchar',
                    'X': 'ntext', 'P': 'ntext', 'Z': 'ntext',
                    'B': 'BOOLEAN', 'D': 'datetime', 'H': 'datetime', 'DH': 'datetime',
                    'I': 'int', 'L': 'bigint', 'R': 'real', 'O': 'binary'}


    def defaultMainSchema(self):
        return 'dbo'

    def connect(self, storename=None):
        """Return a new connection object: provides cursors accessible by col number or col name
        @return: a new connection object"""
        dbroot = self.dbroot
        kwargs = self.dbroot.get_connection_params(storename=storename)
        #kwargs['as_dict']=True
        #kwargs = dict(host=dbroot.host, database=dbroot.dbname, user=dbroot.user, password=dbroot.password,
        #              port=dbroot.port, as_dict=True)
        kwargs = dict(
                [(k, v) for k, v in kwargs.items() if v != None]) # remove None parameters, psycopg can't handle them
        #kwargs['charset']='utf8'
        #conn = pymssql.connect(**kwargs)
        kwargs['server']=kwargs.pop('host')
        conn = _mssql.connect(**kwargs)
        
        return DictConnectionWrapper(conn, False)
        


    def prepareSqlText(self, sql, kwargs):
        """Change the format of named arguments in the query from ':argname' to '%(argname)s'.
        Replace the 'REGEXP' operator with '~*'
        
        :param sql: the sql string to execute
        :param kwargs: the params dict
        :returns: tuple (sql, kwargs)"""
        return RE_SQL_PARAMS.sub(r'%(\1)s\2', sql).replace('REGEXP', '~*'), kwargs

    def _managerConnection(self):
        dbroot = self.dbroot
        kwargs = dict(host=dbroot.host, database='master', user=dbroot.user,
                      password=dbroot.password, port=dbroot.port, as_dict=True)
        kwargs = dict([(k, v) for k, v in kwargs.items() if v != None])
        #conn =  psycopg2.connect(**kwargs)
        conn = pymssql.connect(**kwargs)
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
        pass

    def listen(self, msg, timeout=10, onNotify=None, onTimeout=None):
        """Listen for message 'msg' on the current connection using the Postgres LISTEN - NOTIFY method.
        onTimeout callbacks are executed on every timeout, onNotify on messages.
        Callbacks returns False to stop, or True to continue listening.
        @param msg: name of the message to wait for
        @param timeout: seconds to wait for the message
        @param onNotify: function to execute on arrive of message
        @param onTimeout: function to execute on timeout
        """
        pass

    def notify(self, msg, autocommit=False):
        """Notify a message to listener processes using the Postgres LISTEN - NOTIFY method.
        @param msg: name of the message to notify
        @param autocommit: if False (default) you have to commit transaction, and the message is actually sent on commit"""
        pass

    def listElements(self, elType, **kwargs):
        """Get a list of element names.
        @param elType: one of the following: schemata, tables, columns, views.
        @param kwargs: schema, table
        @return: list of object names"""
        query = getattr(self, '_list_%s' % elType)()
        result = self.dbroot.execute(query, kwargs).fetchall()
        return [r[0] for r in result]

    def _list_schemata(self):
        return """SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA 
              WHERE SCHEMA_NAME != 'INFORMATION_SCHEMA' AND SCHEMA_NAME != 'sys' AND SCHEMA_NAME NOT LIKE 'db__%%'"""

    def _list_tables(self):
        return """SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES
                                    WHERE TABLE_SCHEMA=:schema"""

    def _list_views(self):
        return """SELECT TABLE_NAME FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_SCHEMA=:schema"""

    def _list_columns(self):
        return """SELECT COLUMN_NAME AS col
                                  FROM INFORMATION_SCHEMA.COLUMNS 
                                  WHERE TABLE_SCHEMA=:schema 
                                  AND TABLE_NAME=:table 
                                  ORDER BY ORDINAL_POSITION"""

    def relations(self):
        """Get a list of all relations in the db. 
        Each element of the list is a list (or tuple) with this elements:
        [foreign_constraint_name, many_schema, many_tbl, [many_col, ...], unique_constraint_name, one_schema, one_tbl, [one_col, ...]]
        @return: list of relation's details
        """
        sql = """SELECT R.CONSTRAINT_NAME AS ref,
                C1.TABLE_SCHEMA AS ref_schema,
                C1.TABLE_NAME AS ref_tbl, 
                MCOLS.COLUMN_NAME AS ref_col,
                R.UNIQUE_CONSTRAINT_NAME AS un_ref,
                C2.TABLE_SCHEMA AS un_schema,
                C2.TABLE_NAME AS un_tbl,
                UCOLS.COLUMN_NAME AS un_col,
                R.UPDATE_RULE AS upd_rule
 
                FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS AS R
                        JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS C1
                                ON C1.CONSTRAINT_CATALOG = R.CONSTRAINT_CATALOG 
                                        AND C1.CONSTRAINT_SCHEMA = R.CONSTRAINT_SCHEMA
                                        AND C1.CONSTRAINT_NAME = R.CONSTRAINT_NAME 
                        JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS C2
                                ON C2.CONSTRAINT_CATALOG = R.UNIQUE_CONSTRAINT_CATALOG 
                                        AND C2.CONSTRAINT_SCHEMA = R.UNIQUE_CONSTRAINT_SCHEMA
                                        AND C2.CONSTRAINT_NAME = R.UNIQUE_CONSTRAINT_NAME
                        JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS MCOLS
                                ON MCOLS.CONSTRAINT_SCHEMA = R.CONSTRAINT_SCHEMA 
                                        AND MCOLS.CONSTRAINT_NAME= R.CONSTRAINT_NAME
                        JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS UCOLS
                                ON UCOLS.CONSTRAINT_SCHEMA = R.UNIQUE_CONSTRAINT_SCHEMA
                                        AND UCOLS.CONSTRAINT_NAME= R.UNIQUE_CONSTRAINT_NAME
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
        sql = """SELECT k.COLUMN_NAME        AS col
                FROM   INFORMATION_SCHEMA.KEY_COLUMN_USAGE      AS k 
                JOIN   INFORMATION_SCHEMA.TABLE_CONSTRAINTS     AS c
                ON     c.CONSTRAINT_CATALOG = k.CONSTRAINT_CATALOG 
                AND    c.CONSTRAINT_SCHEMA  = k.CONSTRAINT_SCHEMA
                AND    c.CONSTRAINT_NAME    = k.CONSTRAINT_NAME         
                WHERE  k.TABLE_SCHEMA       =:schema
                AND    k.TABLE_NAME         =:table 
                AND    c.CONSTRAINT_TYPE    ='PRIMARY KEY'
                ORDER BY k.ORDINAL_POSITION"""
        return [r['col'] for r in self.dbroot.execute(sql, dict(schema=schema, table=table)).fetchall()]

    def getIndexesForTable(self, table, schema):
        """Get a (list of) dict containing details about all the indexes of a table.
        Each dict has this info: name, primary (bool), unique (bool), columns (comma separated string)
        @param table: table name
        @param schema: schema name
        @return: list of index infos"""
        sql = """SELECT INDCLS.RELNAME AS name, INDISUNIQUE AS unq, INDISPRIMARY AS prim, INDKEY AS columns
                    FROM PG_INDEX
               LEFT JOIN PG_CLASS AS indcls ON INDEXRELID=INDCLS.OID 
               LEFT JOIN PG_CLASS AS tblcls ON INDRELID=TBLCLS.OID 
               LEFT JOIN PG_NAMESPACE ON PG_NAMESPACE.OID=TBLCLS.RELNAMESPACE 
                   WHERE NSPNAME=:schema AND TBLCLS.RELNAME=:table;"""
        #indexes = self.dbroot.execute(sql, dict(schema=schema, table=table)).fetchall()
        indexes = []
        return indexes

    def getTableContraints(self, table=None, schema=None):
        """Get a (list of) dict containing details about a column or all the columns of a table.
        Each dict has those info: name, position, default, dtype, length, notnull
        Every other info stored in information_schema.columns is available with the prefix '_pg_'"""
        sql = """SELECT CONSTRAINT_TYPE,COLUMN_NAME,TC.TABLE_NAME,TC.TABLE_SCHEMA,TC.CONSTRAINT_NAME
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS tc 
            JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE AS CU 
                ON CU.CONSTRAINT_NAME=TC.CONSTRAINT_NAME  
                WHERE CONSTRAINT_TYPE='UNIQUE'
                %s%s;"""
        filtertable = ""
        if table:
            filtertable = " AND TC.TABLE_NAME=:table"
        filterschema = ""
        if schema:
            filterschema = " AND TC.TABLE_SCHEMA=:schema"
        result = self.dbroot.execute(sql % (filtertable,filterschema),
                                      dict(schema=schema,
                                           table=table)).fetchall()

        res_bag = Bag()
        for row in result:
            row=dict(row)
            res_bag.setItem('%(TABLE_SCHEMA)s.%(TABLE_NAME)s.%(COLUMN_NAME)s'%row,row['CONSTRAINT_NAME'])
        return res_bag

    def _filterColInfo(self, colinfo, prefix):
        """Utility method to be used by getColInfo implementations.
        Prepend each non-standard key in the colinfo dict with prefix.

        :param colinfo: dict of column infos
        :param prefix: adapter specific prefix
        :returns: a new colinfo dict"""
        d = dict([(k, v) for k, v in colinfo.items() if
                  k in ('name', 'dflt', 'notnull', 'dtype', 'position', 'length')])
        default = d.pop('dflt',None)
        if default:
            d['default']=default
        d.update(dict([(prefix + k, v) for k, v in colinfo.items() if
                       k not in ('name', 'dflt', 'notnull', 'dtype', 'position', 'length')]))
        return d

    def getColInfo(self, table, schema, column=None):
        """Get a (list of) dict containing details about a column or all the columns of a table.
        Each dict has those info: name, position, default, dtype, length, notnull
        Every other info stored in information_schema.columns is available with the prefix '_pg_'"""
        sql = """SELECT COLUMN_NAME AS name,
                        ORDINAL_POSITION AS position, 
                        COLUMN_DEFAULT AS dflt, 
                        IS_NULLABLE AS notnull, 
                        DATA_TYPE AS dtype, 
                        CHARACTER_MAXIMUM_LENGTH AS length,
                        *
                      FROM INFORMATION_SCHEMA.COLUMNS 
                      WHERE TABLE_SCHEMA=:schema 
                      AND TABLE_NAME=:table 
                      %s
                      ORDER BY position"""
        filtercol = ""
        if column:
            filtercol = "AND COLUMN_NAME=:column"
        columns = self.dbroot.execute(sql % filtercol,
                                      dict(schema=schema,
                                           table=table,
                                           column=column)).fetchall()
        result = []
        for col in columns:
            col = dict(col)
            col = self._filterColInfo(col, '_ms_')
            col['dtype'] = self.typesDict.get(col['dtype'], 'T') #for unrecognized types default dtype is T
            col['notnull'] = (col['notnull'] == 'NO')
            result.append(col)
        if column:
            result = result[0]
        return result
        
    def getWhereTranslator(self):
        return GnrWhereTranslator(self.dbroot)
    
    def compileSql(self, maintable, columns, distinct='', joins=None, where=None,
                   group_by=None, having=None, order_by=None, limit=None, offset=None, for_update=None):
        def _smartappend(x, name, value):
            if value:
                x.append('%s %s' % (name, value))
        
        if limit:
            limit= 'TOP %i '%limit
        else:
            limit=''
        result = ['SELECT  %s%s%s' % (limit,distinct, columns)]
        result.append(' FROM %s AS t0' % (maintable, ))
        joins = joins or []
        for join in joins:
            result.append('       %s' % join)

        _smartappend(result, 'WHERE', where)
        _smartappend(result, 'GROUP BY', group_by)
        _smartappend(result, 'HAVING', having)
        _smartappend(result, 'ORDER BY', order_by)
        _smartappend(result, 'OFFSET', offset)
        if for_update:
            result.append(self._selectForUpdate())
        return '\n'.join(result)
        
class GnrWhereTranslator(GnrWhereTranslator_base):
    def op_startswith(self, column, value, dtype, sqlArgs):
        "Starts with"
        return '%s LIKE :%s' % (column, self.storeArgs('%s%%' % value, dtype, sqlArgs))

    def op_contains(self, column, value, dtype, sqlArgs):
        "Contains"
        return '%s LIKE :%s' % (column, self.storeArgs('%%%s%%' % value, dtype, sqlArgs))