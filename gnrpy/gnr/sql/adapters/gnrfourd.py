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

import fourd

from gnr.sql.adapters._gnrbaseadapter import SqlDbAdapter as SqlDbBaseAdapter
from gnr.sql.adapters._gnrbaseadapter import GnrWhereTranslator
from gnr.core.gnrlist import GnrNamedList
from gnr.core.gnrbag import Bag
RE_SQL_PARAMS = re.compile(r":(\S\w*)(\W|$)")
import threading
import _thread

class GnrFourDCursor(fourd.FourD_cursor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._query_executed = 0

    def fetchone(self, no_index=False):
        if self._query_executed and not no_index:
            self._build_index()
        result = super().fetchone()
        if result:
            return GnrNamedList(self.index, values=result)

    def fetchall(self):
        if self._query_executed:
            self._build_index()
        
        resultset = super().fetchall()
        return [GnrNamedList(self.index, values=values) for values in resultset]
        

    def fetchmany(self, size=None):
        if self._query_executed:
            self._build_index()
        resultset = super().fetchmany(size=size)
        return [GnrNamedList(self.index, values=values) for values in resultset]
        

    def __next__(self):
        if self._query_executed:
            self._build_index()
        res = super().fetchone()
        if res is None:
            raise StopIteration()
        return res

    next=__next__

    def execute(self, operation, args=()):
        self.index = {}
        self._query_executed = 1
        super().execute(operation, args)
        return self

    def _build_index(self):
        if self._query_executed == 1 and self.description:
            for i in range(len(self.description)):
                self.index[self.description[i][0]] = i
            self._query_executed = 0


class SqlDbAdapter(SqlDbBaseAdapter):
    typesDict = {'VK_STRING': 'A',  'VK_TEXT': 'T',
                 'VK_BOOLEAN': 'B', 
                 'VK_TIMESTAMP': 'DH','VK_TIME':'DH', 
                 'VK_DURATION':'H', 
                  'VK_REAL': 'R', 'VK_FLOAT':'R', 'VK_WORD': 'I',
                 'VK_LONG': 'I', 'VK_LONG8': 'L',  'VK_BLOB': 'O'}

    revTypesDict = {'A': 'VK_STRING', 'T': 'VK_TEXT',
                    'X': 'VK_TEXT', 'P': 'VK_TEXT', 'Z': 'VK_TEXT', 
                    'B': 'VK_BOOLEAN', 
                    'DH': 'VK_TIMESTAMP',
                    'I': 'VK_LONG', 'L': 'VK_LONG8', 'R': 'VK_FLOAT',
                    'O': 'VK_BLOB'}

    _lock = threading.Lock()

    def __init__(self, *args, **kwargs):
        #self._lock = threading.Lock()

        super(SqlDbAdapter, self).__init__(*args, **kwargs)

    def use_schemas(self):
        return False

    def defaultMainSchema(self):
        return 'DEFAULT_SCHEMA'

    def connect(self, storename=None):
        """Return a new connection object: provides cursors accessible by col number or col name
        
        :returns: a new connection object"""
        kwargs = self.dbroot.get_connection_params(storename=storename)
        #kwargs = dict(host=dbroot.host, database=dbroot.dbname, user=dbroot.user, password=dbroot.password, port=dbroot.port)
        kwargs = dict(
                [(k, v) for k, v in list(kwargs.items()) if v != None]) # remove None parameters, psycopg can't handle them
        self._lock.acquire()
        if 'port' in kwargs:
            kwargs['port'] = int(kwargs['port'])
        try:
            kwargs['cursor_factory'] = GnrFourDCursor
            conn = fourd.connect(**kwargs)
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
        sql = sql.replace('ILIKE', 'LIKE')
        return RE_SQL_PARAMS.sub(r'%(\1)s\2', sql).replace('REGEXP', '~*'), kwargs
        
    def adaptSqlName(self,name):
        return f'[{name}]' 


    def asTranslator(self, as_):
        return f'[{as_}]'

    def listElements(self, elType, comment=None, **kwargs):
        """Get a list of element names
        
        :param elType: one of the following: schemata, tables, columns, views.
        :param kwargs: schema, table
        :returns: list of object names"""
        query = getattr(self, '_list_%s' % elType)()
        comment = kwargs.pop('comment', None)
        cursor = self.dbroot.execute(query, kwargs)
        result= cursor.fetchall()
        if comment:
            return [(r[0],None) for r in result]
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
        return 'SELECT "4d";'

    def _list_schemata(self):
        return """SELECT schema_name FROM _USER_SCHEMAS;"""

    def _list_tables(self):
        return """SELECT _USER_TABLES.TABLE_NAME FROM _USER_TABLES JOIN _USER_SCHEMAS ON _USER_TABLES.SCHEMA_ID=_USER_SCHEMAS.SCHEMA_ID
                                    WHERE _USER_SCHEMAS.SCHEMA_NAME=:schema;"""

    
    
    def _list_columns(self):
        return """SELECT _USER_COLUMNS.COLUMN_NAME as col
                                  FROM _USER_COLUMNS,_USER_TABLES,_USER_SCHEMAS
                                  
                                  WHERE 
                                    _USER_SCHEMAS.SCHEMA_NAME=:schema 
                                    AND _USER_TABLES.TABLE_NAME=:table 
                                    AND _USER_COLUMNS.TABLE_ID = _USER_TABLES.TABLE_ID
                                    AND _USER_TABLES.SCHEMA_ID=_USER_SCHEMAS.SCHEMA_ID
                                  ORDER BY _USER_COLUMNS.COLUMN_ID;"""


    def relations(self):
        """Get a list of all relations in the db. 
        Each element of the list is a list (or tuple) with this elements:
        [foreign_constraint_name, many_schema, many_tbl, [many_col, ...], unique_constraint_name, one_schema, one_tbl, [one_col, ...]]
        @return: list of relation's details
        """
        sql = """SELECT R.CONSTRAINT_ID AS ref,
                C.COLUMN_NAME AS col,
                C.TABLE_ID AS tbl_id,
                C.TABLE_NAME AS tbl,
                R.RELATED_TABLE_NAME AS un_tbl,
                C.RELATED_COLUMN_NAME AS un_col,
                R.RELATED_TABLE_ID AS un_tbl_id,
                R.DELETE_RULE AS del_rule

                FROM _USER_CONS_COLUMNS AS C,_USER_CONSTRAINTS AS R
                WHERE C.CONSTRAINT_ID = R.CONSTRAINT_ID AND
                R.RELATED_TABLE_NAME <> '';
                                        """
        tables_sql = """SELECT _USER_TABLES.TABLE_ID as tbl_id ,_USER_SCHEMAS.SCHEMA_NAME AS schema_name
            FROM _USER_TABLES,_USER_SCHEMAS WHERE _USER_TABLES.SCHEMA_ID=_USER_SCHEMAS.SCHEMA_ID;"""
        ref_constraints = self.dbroot.execute(sql).fetchall()
        tables = self.dbroot.execute(tables_sql).fetchall()
        tables_dict = dict([(t['tbl_id'],t) for t in tables])
        ref_dict = {}
        for (
        ref, col, tbl_id, tbl, un_tbl, un_col, un_tbl_id, del_rule) in ref_constraints:
            r = ref_dict.get(ref, None)
            table = tables_dict.get(tbl_id, dict())
            schema = table.get('schema_name')
            un_table = tables_dict.get(un_tbl_id, dict())
            un_schema = un_table.get('schema_name')
            init_defer = False
            upd_rule = None
            if r:
                if not col in r[3]:
                    r[3].append(col)
                if not un_col in r[7]:
                    r[7].append(un_col)
            else:
                ref_dict[ref] = [ref, schema, tbl, [col], '', un_schema, un_tbl, [un_col], upd_rule, del_rule,
                                 init_defer]
        return list(ref_dict.values())

    def getPkey(self, table, schema):
        """:param table: the :ref:`database table <table>` name, in the form ``packageName.tableName``
                      (packageName is the name of the :ref:`package <packages>` to which the table
                      belongs to)
        :param schema: schema name
        :return: list of columns wich are the primary key for the table"""
        sql = """SELECT _USER_CONS_COLUMNS.COLUMN_NAME AS col
                FROM   _USER_CONS_COLUMNS
                JOIN   _USER_CONSTRAINTS
                    ON     _USER_CONS_COLUMNS.CONSTRAINT_ID = _USER_CONSTRAINTS.CONSTRAINT_ID 
                JOIN   _USER_TABLES
                    ON     _USER_TABLES.TABLE_ID = _USER_CONS_COLUMNS.TABLE_ID
                JOIN   _USER_SCHEMAS
                    ON     _USER_SCHEMAS.SCHEMA_ID = _USER_TABLES.SCHEMA_ID 
                WHERE  _USER_SCHEMAS.SCHEMA_NAME       =:schema
                AND    _USER_TABLES.TABLE_NAME         =:table 
                AND    _USER_CONSTRAINTS.CONSTRAINT_TYPE    ='P'
                ORDER BY _USER_CONS_COLUMNS.COLUMN_ID;"""
        return [r['col'] for r in self.dbroot.execute(sql, dict(schema=schema, table=table)).fetchall()]

    def getIndexesForTable(self, table, schema):
        return []
        """Get a (list of) dict containing details about all the indexes of a table.
        Each dict has those info: name, primary (bool), unique (bool), columns (comma separated string)
        
        :param table: the :ref:`database table <table>` name, in the form ``packageName.tableName``
                      (packageName is the name of the :ref:`package <packages>` to which the table
                      belongs to)
        :param schema: schema name
        :returns: list of index infos"""
        sql = """SELECT INDEX_NAME AS name, False AS unique, indisprimary AS primary, indkey AS columns
                    FROM _USER_IND_COLUMNS
               LEFT JOIN pg_class AS indcls ON indexrelid=indcls.oid 
               LEFT JOIN pg_class AS tblcls ON indrelid=tblcls.oid 
               LEFT JOIN pg_namespace ON pg_namespace.oid=tblcls.relnamespace 
                   WHERE nspname=:schema AND tblcls.relname=:table;"""
        indexes = self.dbroot.execute(sql, dict(schema=schema, table=table)).fetchall()
        return indexes

    def getTableContraints(self, table=None, schema=None):
        return Bag()
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
        sql = """SELECT C.COLUMN_NAME as name, 
                        C.NULLABLE as notnull, 
                        C.DATA_TYPE as dtype, 
                        C.DATA_LENGTH as col_length
                      FROM _USER_COLUMNS AS C JOIN
                        _USER_TABLES AS T ON C.TABLE_ID=T.TABLE_ID JOIN
                        _USER_SCHEMAS AS S ON T.SCHEMA_ID=S.SCHEMA_ID
                        WHERE S.SCHEMA_NAME=:schema
                        AND T.TABLE_NAME =:table 
                      %s
                      ORDER BY C.COLUMN_ID;"""
        filtercol = ""
        if column:
            filtercol = "AND C.COLUMN_NAME=:column"
        columns = self.dbroot.execute(sql % filtercol,
                                      dict(schema=schema,
                                           table=table,
                                           column=column)).fetchall()
        result = []
        for position,col in enumerate(columns):
            size = None
            col = dict(col)
            col['position'] = position
            dtype = col['dtype'] = self.typesDict.get(fourd.FOURD_DATA_TYPES[col['dtype']], 'T') #for unrecognized types default dtype is T
            col['notnull'] = (col['notnull'] == 'NO')
            size = col.pop('col_length','-1')
            if dtype == 'A':
                size = int(size)
                if size:
                    col['size'] = ':%i' % size
                    col['length'] = size
                else:
                    dtype = col['dtype'] = 'T'
            elif dtype == 'C':
                col['size'] = str(col.get('col_length'))
            result.append(col)
        if column:
            result = result[0]
        return result

    def getWhereTranslator(self):
        return GnrWhereTranslatorFourD(self.dbroot)


class GnrWhereTranslatorFourD(GnrWhereTranslator):
    
    def op_startswithchars(self, column, value, dtype, sqlArgs,tblobj):
        "!!Starts with Chars"
        return self.unaccentTpl(tblobj,column,'LIKE',mask="CONCAT(:%s,'%%%%')")  % (column, self.storeArgs(value, dtype, sqlArgs))

    def op_equal(self, column, value, dtype, sqlArgs,tblobj):
        "!!Equal to"
        return self.unaccentTpl(tblobj,column,'=')  % (column, self.storeArgs(value, dtype, sqlArgs))

    def op_startswith(self, column, value, dtype, sqlArgs,tblobj):
        "!!Starts with"
        return self.unaccentTpl(tblobj,column,'LIKE',mask="CONCAT(:%s,'%%%%')")  % (column, self.storeArgs(value, dtype, sqlArgs))

    def op_wordstart(self, column, value, dtype, sqlArgs,tblobj):
        "!!Word start"
        value = value.replace('(', r'\(').replace(')', r'\)').replace('[', r'\[').replace(']', r'\]')
        return self.unaccentTpl(tblobj,column,'~*',mask="'(^|\\W)' || :%s")  % (column, self.storeArgs(value, dtype, sqlArgs))

    def op_contains(self, column, value, dtype, sqlArgs,tblobj):
        "!!Contains"
        return self.unaccentTpl(tblobj,column,'LIKE',mask="CONCAT('%%%%',:%s,'%%%%')")  % (column, self.storeArgs(value, dtype, sqlArgs))


    def unaccent(self,v):
        return 'unaccent(%s)' %v

