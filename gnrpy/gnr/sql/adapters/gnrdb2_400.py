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

from builtins import range
import re

import pyodbc
from pyodbc import Connection, Cursor
from gnr.sql.adapters._gnrbaseadapter import SqlDbAdapter as SqlDbBaseAdapter
from gnr.sql.adapters._gnrbaseadapter import GnrWhereTranslator as GnrWhereTranslator_base
from gnr.core.gnrlist import GnrNamedList
from gnr.core.gnrbag import Bag
from gnr.sql.gnrsql_exceptions import GnrNonExistingDbException
#DBAPI.paramstyle = 'pyformat'
RE_SQL_PARAMS = re.compile(":(\w*)(\W|$)")

class DictCursorWrapper(object):

    def __init__(self, connection_wrapper=None):
        self.connection = connection_wrapper
        self.cursor = self.connection._connection.cursor()
        self._query_executed = 0
        self.index = {}

    def __getattr__(self, attr):
        return getattr(self.cursor, attr)


    def tables(self):
        self._query_executed = 1
        self.cursor.tables()

    def columns(self, table=None):
        self._query_executed = 1
        self.cursor.columns(table=table)

    def fetchone(self, no_index=False):
        if self._query_executed and not no_index:
            self._build_index()
        result = self.cursor.fetchone()
        if result:
            return GnrNamedList(self.index, values=result)

    def fetchall(self):
        if self._query_executed:
            self._build_index()

        resultset = self.cursor.fetchall()
        return [GnrNamedList(self.index, values=values) for values in resultset]


    def fetchmany(self, size=None):
        if self._query_executed:
            self._build_index()
        resultset = self.cursor.fetchmany(size=size)
        return [GnrUpperNamedList(self.index, values=values) for values in resultset]


    def __next__(self):
        if self._query_executed:
            self._build_index()
        res = self.cursor.fetchone()
        if res is None:
            raise StopIteration()
        return res

    next=__next__

    def execute(self, operation, args=()):
        self.index = {}
        self._query_executed = 1
        self.cursor.execute(operation, args)
        return self

    def _build_index(self):
        if self._query_executed == 1 and self.description:
            for i in range(len(self.description)):
                self.index[self.description[i][0]] = i
            self._query_executed = 0


class DictConnectionWrapper(object):

    def __init__(self, connection=None):
        self._connection = connection

    def __getattr__(self, attr):
        return getattr(self._connection, attr)

    def cursor(self):
        return DictCursorWrapper(self)

class SqlDbAdapter(SqlDbBaseAdapter):
    typesDict = {'CHAR': 'A', 'DECIMAL':'N',
                 'int': 'I', 'bigint': 'L', 'smallint': 'I','tinyint': 'I', 'real': 'R', 'float': 'R', 'binary': 'O'}

    revTypesDict = {'A': 'CHAR', 'T': 'CHAR', 'C': 'CHAR',
                    'X': 'CHAR', 'P': 'CHAR', 'Z': 'CHAR', 'serial':'int',
                    'N':'DECIMAL',
                    'B': 'BIT', 'D': 'datetime', 'H': 'datetime', 'DH': 'datetime',
                    'I': 'int', 'L': 'bigint', 'R': 'real', 'O': 'binary'}


    def defaultMainSchema(self):
        return 'main'

    def connect(self, storename=None):
        """Return a new connection object: provides cursors accessible by col number or col name
        @return: a new connection object"""
        dbroot = self.dbroot
        kwargs = self.dbroot.get_connection_params(storename=storename)
        kwargs = dict(
                [(k, v) for k, v in list(kwargs.items()) if v != None]) # remove None parameters, psycopg can't handle them
        kwargs['server']=kwargs.pop('host',None)
        dsn = kwargs.get('dsn') or kwargs.get('database')
        try:
            conn = pyodbc.connect(dsn=dsn)
        except Exception as e:
            raise GnrNonExistingDbException(dsn)
        return DictConnectionWrapper(connection=conn)

    def adaptSqlName(self,name):
        return name
        return '{name}'.format(name=name)


    def adaptSqlSchema(self,name):
        pass

    def use_schemas(self):
        return False

    def prepareSqlText(self, sql, kwargs):
        """Change the format of named arguments in the query from ':argname' to '%(argname)s'.
        Replace the 'REGEXP' operator with '~*'

        :param sql: the sql string to execute
        :param kwargs: the params dict
        :returns: tuple (sql, kwargs)"""
        sqlargs = []
        def subArgs(m):
            key = m.group(1)
            sqlargs.append(kwargs[key])
            return '? '
        #sql = RE_SQL_PARAMS.sub(r'%(\1)s\2', sql).replace('REGEXP', '~*')
        sql = RE_SQL_PARAMS.sub(subArgs, sql)
        sql= sql.replace('REGEXP', '~*')

        return sql, tuple(sqlargs)

    def columnSqlDefinition(self, sqlname, dtype, size, notnull, pkey, unique):
        """Return the statement string for creating a table's column
        """
        if dtype =='T' and (unique or pkey):
            dtype ='A'
            size = ':3000'

        sql = '"%s" %s' % (sqlname, self.columnSqlType(dtype, size))
        if notnull:
            sql = sql + ' NOT NULL'
        if pkey:
            sql = sql + ' PRIMARY KEY'
        if unique:
            sql = sql + ' UNIQUE'
        return sql

    def _managerConnection(self, **kwargs):
        dbroot = self.dbroot
        conn_kwargs = dict(host=dbroot.host, database='master', user=dbroot.user,
                      password=dbroot.password, port=dbroot.port, as_dict=True, **kwargs)
        conn_kwargs = dict([(k, v) for k, v in list(conn_kwargs.items()) if v != None])
        conn = pyodbc.connect(**conn_kwargs)
        return conn

    def createDb(self, dbname=None, encoding='unicode'):
        pass
        #if not dbname:
        #    dbname = self.dbroot.get_dbname()
        #conn = self._managerConnection(autocommit=True)
        #curs = conn.cursor()
        #curs.execute(self.createDbSql(dbname, encoding))
        #curs.close()
        #conn.close()

    def createDbSql(self, dbname, encoding):
        pass
        #return """CREATE DATABASE "%s";""" % (dbname)

    def dropDb(self, name):
        pass
        #conn = self._managerConnection()
        #curs = conn.cursor()
        #curs.execute("DROP DATABASE %s;" % name)
        #curs.close()
        #conn.close()

    def createTableAs(self, sqltable, query, sqlparams):
        pass
        #self.dbroot.execute("CREATE TABLE %s WITH OIDS AS %s;" % (sqltable, query), sqlparams)



    def listElements(self, elType, **kwargs):
        """Get a list of element names.
        @param elType: one of the following: schemata, tables, columns, views.
        @param kwargs: schema, table
        @return: list of object names"""
        lister = getattr(self, '_list_db2_400_%s' % elType,None)
        if not lister:
            return []
        return lister(**kwargs)


    def _list_enabled_extensions(self):
        return ''

    def _list_db2_400_schemata(self, schema=None, comment=None):
        if comment:
            return [('_main_','')]
        return ['_main_']

    def _list_db2_400_tables(self, schema=None, comment=None):
        cursor = self.cursor(self.dbroot.connection)
        cursor.tables()
        rows = cursor.fetchall()
        if comment:
            return [(r['table_name'],r['remarks']) for r in rows]
        return [r['table_name'] for r in rows]


    def _list_db2_400_columns(self, table=None, schema=None, comment=None):
        cursor = self.cursor(self.dbroot.connection)
        cursor.colums(table=table)
        rows = cursor.fetchall()
        if comment:
            return [(r['column_name'],r['remarks']) for r in rows]
        return [r['column_name'] for r in rows]

    def relations(self):
        return []
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
                R.UPDATE_RULE AS upd_rule,
                R.DELETE_RULE AS del_rule,
                C1.INITIALLY_DEFERRED AS init_defer

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
        for (ref, schema, tbl, col, un_ref, un_schema, un_tbl, un_col, upd_rule, del_rule, init_defer) in ref_constraints:
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
        print(table)
        """
        @param table: table name
        @param schema: schema name
        @return: list of columns which are the primary key for the table"""
        sql = """WITH xx (CST_NAME, CST_COL_CNT, CST_SCHEMA, CST_TABLE) AS
                (
                    SELECT CONSTRAINT_NAME, CONSTRAINT_KEYS, CONSTRAINT_SCHEMA, TABLE_NAME FROM QSYS2.SYSCST A
                    WHERE CONSTRAINT_TYPE = 'PRIMARY KEY' AND TABLE_NAME=:table
                )
                SELECT CONSTRAINT_SCHEMA, TABLE_NAME, CONSTRAINT_NAME, COLUMN_NAME AS "col" FROM QSYS2.SYSCSTCOL, xx where
                xx.CST_SCHEMA = CONSTRAINT_SCHEMA AND
                xx.CST_TABLE = TABLE_NAME AND
                xx.CST_NAME = CONSTRAINT_NAME"""
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
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS "tc"
            JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE AS "CU"
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



    def getColInfo(self, table, schema, column=None):
        """Get a (list of) dict containing details about a column or all the columns of a table.
        Each dict has those info: name, position, default, dtype, length, notnull
        Every other info stored in information_schema.columns is available with the prefix '_pg_'"""
        cursor = self.cursor(self.dbroot.connection)
        cursor.columns(table=table)
        rows = cursor.fetchall()
        result = []
        for row in rows:
            if column and row['column_name']!= column:
                continue
            result.append(dict(
                dtype = self.typesDict.get(row['type_name'], 'T') ,
                name = row['column_name'],
                length = row['column_size'],
                position = row['ordinal_position'],
                dflt = row['column_def'],
                default = row['column_def'],
                description = row['remarks'],
                notnull = not row['is_nullable']
                ))
        
        if column:
            result = result[0]
        return result

    def addForeignKeySql(self, c_name, o_pkg, o_tbl, o_fld, m_pkg, m_tbl, m_fld, on_up, on_del, init_deferred):
        pass
        #statement = 'ALTER TABLE %s.%s ADD CONSTRAINT %s FOREIGN KEY (%s) REFERENCES %s.%s (%s)' % (
        #m_pkg, m_tbl, c_name, m_fld, o_pkg, o_tbl, o_fld)
        #drop_statement = 'ALTER TABLE %s.%s DROP CONSTRAINT IF EXISTS %s;' % (m_pkg, m_tbl, c_name)

        ##for on_command, on_value in (('ON DELETE', on_del), ('ON UPDATE', on_up)):
        ##    if init_deferred:
        ##        on_value = 'NO ACTION'
        ##    if on_value: statement += ' %s %s' % (on_command, on_value)
        #statement = '%s %s' % (drop_statement,statement) # MSSQL doesn't support DEFERRED
        #return statement

    def getWhereTranslator(self):
        return GnrWhereTranslator(self.dbroot)

    def compileSql(self, maintable, columns, distinct='', joins=None, where=None,
                   group_by=None, having=None, order_by=None, limit=None, offset=None, for_update=None,maintable_as=None):
        def _smartappend(x, name, value):
            if value:
                x.append('%s %s' % (name, value))

        if limit:
            limit= 'TOP %i '%limit
        else:
            limit=''
        maintable_as = maintable_as or 't0'
        result = ['SELECT  %s%s%s' % (limit,distinct, columns)]
        result.append(' FROM %s AS "%s"' % (maintable, maintable_as))
        joins = joins or []
        for join in joins:
            result.append('       %s' % join)

        _smartappend(result, 'WHERE', where)
        _smartappend(result, 'GROUP BY', group_by)
        _smartappend(result, 'HAVING', having)
        _smartappend(result, 'ORDER BY', order_by)
        _smartappend(result, 'OFFSET', offset)
        if for_update:
            result.append(self._selectForUpdate(maintable_as=maintable_as))
        return '\n'.join(result)


class GnrWhereTranslator(GnrWhereTranslator_base):
    def op_startswith(self, column, value, dtype, sqlArgs,tblobj):
        "Starts with"
        return '%s LIKE :%s' % (column, self.storeArgs('%s%%' % value, dtype, sqlArgs))

    def op_contains(self, column, value, dtype, sqlArgs,tblobj):
        "Contains"
        return '%s LIKE :%s' % (column, self.storeArgs('%%%s%%' % value, dtype, sqlArgs))