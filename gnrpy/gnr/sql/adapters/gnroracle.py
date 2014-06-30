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

import sys

import re

import cx_Oracle
from cx_Oracle import Connection, Cursor
from gnr.core.gnrlist import GnrNamedList
#from gnr.sql.adapters._gnrbaseadapter import GnrDictRow, DbAdapterException
from gnr.sql.adapters._gnrbaseadapter import GnrWhereTranslator as GnrWhereTranslator_base
from gnr.sql.adapters._gnrbaseadapter import SqlDbAdapter as SqlDbBaseAdapter
from gnr.core.gnrbag import Bag
from gnr.sql.gnrsql_exceptions import GnrNonExistingDbException

RE_SQL_PARAMS = re.compile(":(\S\w*)(\W|$)")
#IN_TO_ANY = re.compile(r'([$]\w+|[@][\w|@|.]+)\s*(NOT)?\s*(IN ([:]\w+))')
#IN_TO_ANY = re.compile(r'(?P<what>\w+.\w+)\s*(?P<not>NOT)?\s*(?P<inblock>IN\s*(?P<value>[:]\w+))',re.IGNORECASE)

import threading

ORA_RESERVED = set(('ALL','ALTER', 'AND', 'ANY', 'AS', 'ASC', 'BETWEEN', 'BY', 'CHAR', 'CHECK', 'CLUSTER', 'COMMENT', 'COMPRESS', 'CONNECT', 'CREATE', 'CURRENT',
 'DATE', 'DECIMAL', 'DEFAULT', 'DELETE', 'DESC', 'DISTINCT', 'DROP', 'ELSE', 'EXCLUSIVE', 'EXISTS', 'FLOAT', 'FOR', 'FROM', 'GRANT', 'GROUP', 'HAVING',
 'IDENTIFIED', 'IN', 'INDEX', 'INSERT', 'INTEGER', 'INTERSECT', 'INTO', 'IS', 'LEVEL', 'LIKE', 'LOCK', 'LONG', 'MINUS', 'MODE', 'NOCOMPRESS', 'NOT',
 'NOWAIT', 'NULL', 'NUMBER', 'OF', 'ON', 'OPTION', 'OR', 'ORDER', 'PCTFREE', 'PRIOR', 'PUBLIC', 'RAW', 'RENAME', 'RESOURCE', 'REVOKE', 'SELECT', 'SET',
 'SHARE', 'SIZE', 'SMALLINT', 'START', 'SYNONYM', 'TABLE', 'THEN', 'TO', 'TRIGGER', 'UID', 'UNION', 'UNIQUE', 'UPDATE', 'USER', 'VALUES', 'VARCHAR',
 'VARCHAR2', 'VIEW', 'WHERE', 'WITH'))

class DictCursorWrapper(object):
    def __init__(self, connection):
        self.cursor = cx_Oracle.Cursor(connection._connection)
        self._connection = connection
        self._query_executed = 0
  

    connection = property(lambda self: self._getConnection())
  
    def _getConnection(self):
        return self._connection
  
    def __getattr__(self, name):
        if name in self.__dict__:
            return getattr(self, name)
        else:
            return getattr(self.cursor, name)

    def fetchone(self, no_index=False):
        if self._query_executed and not no_index:
            self._build_index()
        return GnrNamedList(self.index, values=self.cursor.fetchone())

    def fetchall(self):
        if self._query_executed:
            self._build_index()
        return [GnrNamedList(self.index, values=values) for values in self.cursor.fetchall()]
        

    def fetchmany(self, size=None):
        if size == None:
            res = self.cursor.fetchmany()
        else:
            res = self.cursor.fetchmany(size)
        if self._query_executed:
            self._build_index()
        return res

    def next(self):
        if self._query_executed:
            self._build_index()
        res = self.fetchone()
        if res is None:
            raise StopIteration()
        return res

    def execute(self, operation, kwargs):
        self.index = {}
        self._query_executed = 1
        operation = operation.replace('\n','')
        names_kwargs = dict()
        for k in kwargs.keys():
            key = k
            if k.upper() in ORA_RESERVED:
                key = '%s_gnrscpd' % k
                kwargs[key] = kwargs.pop(k)
            names_kwargs[k] = ':%s'%key
        operation = operation % names_kwargs
        print operation
        self.cursor.prepare(operation)
        binded = [n.upper() for n in self.cursor.bindnames()]
        for k in kwargs.keys():
            if k.upper() not in binded:
                kwargs.pop(k, None)
          #  elif isinstance(kwargs[k],unicode) or isinstance(kwargs[k], basestring):
           #     kwargs[k] = "'%s'"%kwargs[k]
        return self.cursor.execute(None, kwargs)
        
    def _build_index(self):
        if self._query_executed == 1 and self.description:
            for i in range(len(self.description)):
                self.index[self.description[i][0].lower()] = i
            self._query_executed = 0


class DictConnectionWrapper(object):
  
  
    def __init__(self, connection):
        self._connection = connection
        
    def __getattr__(self, name):
        if name in self.__dict__:
            return getattr(self, name)
        else:
            return getattr(self._connection, name)

    def cursor(self):
        cursor = DictCursorWrapper(self)
        return cursor
  

class SqlDbAdapter(SqlDbBaseAdapter):
    typesDict = {'nvarchar2': 'A','varchar2': 'A', 'character': 'C', 'nclob': 'T',
                 'smallint': 'B', 'date': 'D', 'time without time zone': 'H', 'timestamp': 'DH',
                 'timestamp with time zone': 'DH', 'NUMBER': 'N', 'money': 'M',
                 'integer': 'I', 'bigint': 'L', 'smallint': 'I', 'double precision': 'R', 'real': 'R', 'bytea': 'O'}

    revTypesDict = {'A': 'nvarchar2', 'T': 'nclob', 'C': 'character',
                    'X': 'nclob', 'P': 'nclob', 'Z': 'nclob', 'N': 'number', 'M': 'money',
                    'B': 'smallint', 'D': 'date', 'H': 'timestamp', 'DH': 'timestamp',
                    'I': 'integer', 'L': 'long', 'R': 'real',
                    'serial': 'serial8', 'O': 'bytea'}

    _lock = threading.Lock()
    paramstyle = 'pyformat'
    supports_schema = False
    quote_names = True
    def __init__(self, *args, **kwargs):
        #self._lock = threading.Lock()

        super(SqlDbAdapter, self).__init__(*args, **kwargs)

    def defaultMainSchema(self):
        return 'public'

    def connect(self, storename=None):
        """Return a new connection object: provides cursors accessible by col number or col name
        
        :returns: a new connection object"""
        kwargs = self.dbroot.get_connection_params(storename=storename)
        self._lock.acquire()
        if 'port' in kwargs:
            port = int(kwargs['port'] or 1521) 
        else:
            port = 1521 
        sid = kwargs.get('sid', 'XE')
        try:
            dsn = cx_Oracle.makedsn(kwargs['host'],port, sid)
            conn = cx_Oracle.connect(kwargs['user'], kwargs['password'], dsn)
        except Exception, e:
            raise
        finally:
            self._lock.release()
        return DictConnectionWrapper(conn)
        
    def adaptTupleListSet(self,sql,sqlargs):
        for k,v in sqlargs.items():
            if isinstance(v, list) or isinstance(v, set) or isinstance(v,tuple):
                if not isinstance(v,tuple):
                    sqlargs[k] = tuple(v)
                if len(v)==0:
                    re_pattern = "((t\\d+)(_t\\d+)*.\\w+ +)(NOT +)*(IN) *:%s" %k
                    sql = re.sub(re_pattern,lambda m: 'TRUE' if m.group(4) else 'FALSE',sql,flags=re.I)
        return sql

    def prepareSqlText(self, sql, kwargs):
        """Replace the 'REGEXP' operator with '~*'.
        Replace the ILIKE operator with LIKE: sqlite LIKE is case insensitive"""
        sql = self.adaptTupleListSet(sql,kwargs)
        sql = sql.replace('nclob UNIQUE', 'nvarchar2(1000) UNIQUE')
        sql = re.sub(" +IS +(NOT +)?(TRUE|FALSE)",self._booleanSubCb,sql,flags=re.I)
        return RE_SQL_PARAMS.sub(r'%(\1)s\2', sql).replace('REGEXP', '~*'), kwargs

    def dropIndex(self, index_name, sqlschema=None):
        """Drop an index
        
        :param index_name: name of the index (unique in schema)
        :param sqlschema: actual sql name of the schema. For more information check the :ref:`about_schema`
                          documentation section"""
        if sqlschema:
            index_name = '%s' % (self.sqlIndexName(index_name))
        return 'DROP INDEX "%s"' % index_name


    def _booleanSubCb(self,m):
        op = '!=' if m.group(1) else '='
        val = '1' if m.group(2).lower() == 'true' else '0'
        return ' %s%s ' %(op,val)  

    def _managerConnection(self):
        dbroot = self.dbroot
        kwargs = dict(host=dbroot.host, database='template1', user=dbroot.user,
                      password=dbroot.password, port=dbroot.port)
        kwargs = dict([(k, v) for k, v in kwargs.items() if v != None])
        if 'port' in kwargs:
            port = int(kwargs['port']) 
        else:
            port = 1521 
        sid = kwargs.get('sid', 'XE')
        dsn = cx_Oracle.makedsn(kwargs['host'],port, sid)
        conn = cx_Oracle.connect(kwargs['user'], kwargs['password'], dsn)
        
        return conn


    def createTableAs(self, sqltable, query, sqlparams):
        self.dbroot.execute("CREATE TABLE %s WITH OIDS AS %s;" % (sqltable, query), sqlparams)

    def addColumnDefinition(self, sqltable, sqlcol):
        return 'ALTER TABLE %s ADD %s' % (sqltable, sqlcol)    

    def alterColumnDefinition(self, sqltable, sqlcol, sqlType):
        return 'ALTER TABLE %s MODIFY %s %s' % (sqltable, sqlcol, sqlType)

    def renameColumn(self, sqltable, sqlname,sqlnewname):
        #automag_deposito_sede_id_idx
        kwargs = dict(sqltable=sqltable,sqlname=sqlname,sqlnewname=sqlnewname)
        tbl_flatname = sqltable.split('.')[1]
        kwargs['old_index_name'] = '%s_%s_idx' %(sqltable,sqlname)
        kwargs['new_index_name'] = '%s_%s_idx' %(tbl_flatname,sqlnewname)

        kwargs['old_fkey_name'] = 'fk_%s_%s' %(tbl_flatname,sqlname)
        kwargs['new_fkey_name'] = 'fk_%s_%s' %(tbl_flatname,sqlnewname)

        command = """
            ALTER TABLE %(sqltable)s RENAME COLUMN %(sqlname)s TO %(sqlnewname)s;
            DROP INDEX IF EXISTS %(old_index_name)s;
            ALTER TABLE %(sqltable)s DROP CONSTRAINT %(old_fkey_name)s;
        """
        self.dbroot.execute(command %kwargs)


    def dropColumn(self, sqltable,sqlname,cascade=False):
        """Drop column"""
        command = 'ALTER TABLE %s DROP COLUMN %s;'
        if cascade:
            command = 'ALTER TABLE %s DROP COLUMN %s CASCADE;'
        self.dbroot.execute(command % (sqltable,sqlname))

    def sqlIndexName(self, index_name):
        return index_name[:30]

    def createIndex(self, index_name, columns, table_sql, sqlschema=None, unique=None):
        """Create a new index
        
        :param index_name: name of the index (unique in schema)
        :param columns: comma separated string (or list or tuple) of :ref:`columns` to include in the index
        :param table_sql: actual sql name of the table
        :param sqlschema: actual sql name of the schema. For more information check the :ref:`about_schema`
                          documentation section
        :unique: boolean for unique indexing"""
        if sqlschema:
            table_sql = '%s.%s' % (sqlschema, table_sql)
        if unique:
            return
            unique = 'UNIQUE '
        else:
            unique = ''
        return "CREATE %sINDEX %s ON %s (%s)" % (unique, index_name[:30], table_sql, columns)


    def columnSqlDefinition(self, sqlname, dtype, size, notnull, pkey, unique):
        """Return the statement string for creating a table's column
        """
        sql = '%s %s' % (sqlname, self.columnSqlType(dtype, size))
        if notnull:
            sql = sql + ' NOT NULL'
        if pkey:
            sql = sql + ' PRIMARY KEY'
        if unique:
            sql = sql + ' UNIQUE'
        return sql

    def listElements(self, elType, **kwargs):
        """Get a list of element names
        
        :param elType: one of the following: schemata, tables, columns, views.
        :param kwargs: schema, table
        :returns: list of object names"""
        query = getattr(self, '_list_%s' % elType)()
        try:
            result = self.dbroot.execute(query, kwargs).fetchall()
        except Exception, e:
            raise
        #except cx_Oracle.DatabaseError:
        #    raise GnrNonExistingDbException(self.dbroot.dbname)
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
        return "SELECT lower('%s') FROM DUAL"%self.dbroot.user

    def _list_schemata(self):
        return "SELECT lower(USER) FROM DUAL"

    def _list_tables(self):
        return """SELECT lower(table_name) FROM user_tables"""

    def _list_views(self):
        return """SELECT view_name FROM user_views"""

    def _list_columns(self):
        return """SELECT lower(column_name) as col
                                  FROM cols
                                  WHERE table_name=:table 
                                  ORDER BY column_id"""


    def relations(self):
        """Get a list of all relations in the db. 
        Each element of the list is a list (or tuple) with this elements:
        [foreign_constraint_name, many_schema, many_tbl, [many_col, ...], unique_constraint_name, one_schema, one_tbl, [one_col, ...]]
        @return: list of relation's details
        """
        
        sql = """SELECT lower(a.constraint_name) ref,
            lower(c.owner) ref_schema,
            lower(c.table_name )ref_tbl,
            lower(a.column_name) ref_col,
            c.R_CONSTRAINT_NAME un_ref,
            lower(c_pk.owner) un_schema,
            lower(a_pk.table_name) un_tbl,
            lower(a_pk.column_name) un_col,
            'NO' upd_rule,
            c.delete_rule del_rule,
            c.deferred init_defer
                FROM user_cons_columns a JOIN user_constraints c ON a.owner = c.owner
                            AND a.constraint_name = c.constraint_name
                        JOIN user_constraints c_pk ON c.r_owner = c_pk.owner
                           AND c.r_constraint_name = c_pk.constraint_name 
                        JOIN user_cons_columns a_pk ON a_pk.owner = c_pk.owner
                            AND a_pk.constraint_name = c_pk.constraint_name"""
        
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
        return ref_dict.values()

    def getPkey(self, table, schema):
        """:param table: the :ref:`database table <table>` name, in the form ``packageName.tableName``
                      (packageName is the name of the :ref:`package <packages>` to which the table
                      belongs to)
        :param schema: schema name
        :return: list of columns wich are the primary key for the table"""
        sql = """SELECT lower(a.column_name)        AS col
                FROM user_cons_columns a
                        JOIN user_constraints c ON a.owner = c.owner
                            AND a.constraint_name = c.constraint_name
                WHERE  c.owner       = :schema
                AND    lower(c.table_name)        = :table
                AND    c.constraint_type    ='P'"""
        return [r['col'] for r in self.dbroot.execute(sql, dict(schema=schema, table=table)).fetchall()]

    def createSchemaSql(self, sqlschema):
        """Sqlite attached dbs cannot be created with an sql command. But they are automatically created in connect()"""
        return ''

    def createSchema(self, sqlschema):
        pass

    def defaultMainSchema(self):
        return self.dbroot.user

    def getIndexesForTable(self, table, schema):
        """Get a (list of) dict containing details about all the indexes of a table.
        Each dict has those info: name, primary (bool), unique (bool), columns (comma separated string)
        
        :param table: the :ref:`database table <table>` name, in the form ``packageName.tableName``
                      (packageName is the name of the :ref:`package <packages>` to which the table
                      belongs to)
        :param schema: schema name
        :returns: list of index infos"""
        sql = "SELECT lower(user_indexes.index_name) AS name, uniqueness, lower(column_name) AS columns FROM user_indexes JOIN user_ind_columns ON user_indexes.index_name=user_ind_columns.index_name WHERE lower(user_indexes.table_name) = :table "
        indexes = self.dbroot.execute(sql, dict(schema=schema, table=table)).fetchall()
        for index in indexes:
            if index['uniqueness']=='UNIQUE':
                index['unique'] = True
            else:
                index['unique'] = False
            index['primary'] = False
        return indexes

    def getTableContraints(self, table=None, schema=None):
        """Get a (list of) dict containing details about a column or all the columns of a table.
        Each dict has those info: name, position, default, dtype, length, notnull
        Every other info stored in information_schema.columns is available with the prefix '_pg_'"""
        sql = """SELECT uc.constraint_type,ucc.column_name,ucc.table_name,USER as table_schema, lower(ucc.constraint_name) as constraint_name
            FROM user_constraints uc, user_cons_columns ucc
            WHERE uc.table_name = ucc.table_name
            AND uc.constraint_name = ucc.constraint_name%s"""

        filtertable = ""
        if table:
            filtertable = " AND ucc.table_name = :table"
        filterschema = ""
        #if schema:
        #    filterschema = " AND tc.table_schema=:schema"
        result = self.dbroot.execute(sql % filtertable,
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
        sql = "SELECT lower(column_name) as name, "\
              "column_id as position, "\
              "data_default, "\
              "nullable, "\
              "data_type as dtype, "\
              "data_precision, data_scale, "\
              "char_length "\
              "FROM all_tab_columns "\
              "WHERE lower(table_name) = :table %s"\
              "ORDER BY column_id"
        

        #sql = """SELECT column_name FROM all_tab_columns WHERE column_name = 'demo' """
        filtercol = ""
        if column:
            filtercol = "AND column_name = :column_name "
        columns = self.dbroot.execute(sql % filtercol,
                                      dict(schema=schema,
                                           table=table,
                                           column=column)).fetchall()
        result = []
        for col in columns:
            col = dict(col)
            col['length'] = col.pop('char_length', None)
            #col = self._filterColInfo(col, '_pg_')
            dtype = col['dtype'] = self.typesDict.get(col['dtype'].lower(), 'T') #for unrecognized types default dtype is T
            col['notnull'] = (col['nullable'] == 'N')
            if dtype == 'N':
                precision, scale = col.get('data_precision'), col.get('data_scale')
                if precision:
                    col['size'] = '%i,%i' % (precision, scale)
            elif dtype == 'A':
                size = col.get('length')
                if size:
                    col['size'] = '0:%i' % int(size)
                else:
                    dtype = col['dtype'] = 'T'
            elif dtype == 'C':
                col['size'] = str(col.get('char_length'))
            result.append(col)
        if column:
            result = result[0]
        return result

    def getWhereTranslator(self):
        return GnrWhereTranslator(self.dbroot)



    def compileSql(self, maintable, columns, distinct='', joins=None, where=None,
                   group_by=None, having=None, order_by=None, limit=None, offset=None, for_update=None,maintable_as=None):
        def _smartappend(x, name, value):
            if value:
                x.append('%s %s' % (name, value))
        
        result = ['SELECT  %s%s' % (distinct, columns)]
        result.append(' FROM %s t0 ' % (maintable, ))
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
        sql =  '\n'.join(result)
        #sql = sql.replace('*', 't0.*')
        if limit:
            sql = "SELECT * FROM (%s) WHERE ROWNUM <=%i"%(sql, limit)
        return sql

class GnrWhereTranslator(GnrWhereTranslator_base):
    def op_startswith(self, column, value, dtype, sqlArgs):
        "Starts with"
        return 'lower(%s) LIKE lower(:%s)' % (column, self.storeArgs('%s%%' % value, dtype, sqlArgs))

    def op_contains(self, column, value, dtype, sqlArgs):
        "Contains"
        return 'lower(%s) LIKE lower(:%s)' % (column, self.storeArgs('%%%s%%' % value, dtype, sqlArgs))