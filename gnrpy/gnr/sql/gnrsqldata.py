#-*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy sql - see LICENSE for details
# module gnrsqldata : Genro SQL query and data
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
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU.
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import os
import shutil
import re
#import weakref
import cPickle
import itertools
import hashlib
from xml.sax import saxutils
from gnr.core.gnrdict import GnrDict,dictExtract
from gnr.core.gnrlang import deprecated, uniquify
import tempfile
from gnr.core.gnrdate import decodeDatePeriod
from gnr.core.gnrlist import GnrNamedList
from gnr.core import gnrclasses
from gnr.core import gnrstring
from gnr.core import gnrlist
from gnr.core.gnrclasses import GnrClassCatalog
from gnr.core.gnrbag import Bag, BagResolver, BagAsXml
from gnr.core.gnranalyzingbag import AnalyzingBag
from gnr.core.gnrdecorator import debug_info
from gnr.sql.gnrsql_exceptions import GnrSqlException,SelectionExecutionError, RecordDuplicateError,\
    RecordNotExistingError, RecordSelectionError,\
    GnrSqlMissingField, GnrSqlMissingColumn

COLFINDER = re.compile(r"(\W|^)\$(\w+)")
RELFINDER = re.compile(r"(\W|^)(\@([\w.@:]+))")
PERIODFINDER = re.compile(r"#PERIOD\s*\(\s*((?:\$|@)?[\w\.\@]+)\s*,\s*:?(\w+)\)")

ENVFINDER = re.compile(r"#ENV\(([^,)]+)(,[^),]+)?\)")
PREFFINDER = re.compile(r"#PREF\(([^,)]+)(,[^),]+)?\)")
THISFINDER = re.compile(r'#THIS\.([\w\.@]+)')

class SqlCompiledQuery(object):
    """SqlCompiledQuery is a private class used by the :class:`SqlQueryCompiler` class.
       It is used to store all parameters needed to compile a query string."""
       
    def __init__(self, maintable, relationDict=None,maintable_as=None):
        """Initialize the SqlCompiledQuery class
        
        :param maintable: the name of the main table to query. For more information, check the
                          :ref:`maintable` section.
        :param relationDict: a dict to assign a symbolic name to a :ref:`relation`. For more information
                             check the :ref:`relationdict` documentation section"""
        self.maintable = maintable
        self.relationDict = relationDict or {}
        self.aliasDict = {}
        self.resultmap = Bag()
        self.distinct = ''
        self.columns = ''
        self.joins = []
        self.where = None
        self.group_by = None
        self.having = None
        self.order_by = None
        self.limit = None
        self.offset = None
        self.for_update = None
        self.explodingColumns = []
        self.aggregateDict = {}
        self.pyColumns = []
        self.maintable_as = maintable_as
 
    def get_sqltext(self, db):
        """Compile the sql query string based on current query parameters and the specific db
        adapter for the current db in use.
        
        :param db: am instance of the :class:`GnrSqlDb <gnr.sql.gnrsql.GnrSqlDb>` class"""
        kwargs = {}
        for k in (
        'maintable', 'distinct', 'columns', 'joins', 'where', 'group_by', 'having', 'order_by', 'limit', 'offset',
        'for_update'):
            kwargs[k] = getattr(self, k)
        return db.adapter.compileSql(maintable_as=self.maintable_as,**kwargs)

        
        
class SqlQueryCompiler(object):
    """SqlQueryCompiler is a private class used by SqlQuery and SqlRecord to build an SqlCompiledQuery instance.
    
    The ``__init__`` method passes:
    
    :param tblobj: the main table to query: an instance of SqlTable, you can get it using db.table('pkgname.tablename')
    :param joinConditions: special conditions for joining related tables. See the
                           :meth:`setJoinCondition() <gnr.sql.gnrsqldata.SqlQuery.setJoinCondition()>`
                           method
    :param sqlContextName: the name of the sqlContext to be reported for subsequent related selection.
                            (see the
                           :meth:`setJoinCondition() <gnr.web.gnrwebpage.GnrWebPage.setJoinCondition>` method)
    :param sqlparams: a dict of parameters used in "WHERE" clause
    :param locale: the current locale (e.g: en, en_us, it)"""
    def __init__(self, tblobj, joinConditions=None, sqlContextName=None, sqlparams=None, locale=None,aliasPrefix = None):
        self.tblobj = tblobj
        self.db = tblobj.db
        self.dbmodel = tblobj.db.model
        self.relations = tblobj.newRelationResolver(cacheTime=-1)
        self.sqlparams = sqlparams
        self.joinConditions = joinConditions
        self.sqlContextName = sqlContextName
        self.cpl = None
        self._currColKey = None
        self.aliasPrefix = aliasPrefix or 't'
        self.locale = locale
        
    def aliasCode(self,n):
        return '%s%i' %(self.aliasPrefix,n)


    def init(self, lazy=None, eager=None):
        """TODO
        
        :param lazy: TODO. 
        :param eager: TODO. 
        """
        self._explodingRows = False
        self._explodingTables = []
        self.lazy = lazy or []
        self.eager = eager or []
        self.aliases = {self.tblobj.sqlfullname: self.aliasCode(0)}
        self.fieldlist = []
        
    def getFieldAlias(self, fieldpath, curr=None,basealias=None):
        """Internal method. Translate fields path and related fields path in a valid sql string for the column.
        
        It translates ``@relname.@rel2name.colname`` to ``t4.colname``.
        
        It has nothing to do with the AS operator, nor the name of the output columns.
        
        It automatically adds the join tables as needed.
        
        It can be recursive to resolve :ref:`table_virtualcolumn`\s.
        
        :param fieldpath: a field path. (e.g: '$colname'; e.g: '@relname.@rel2name.colname')
        :param curr: TODO. 
        :param basealias: TODO. """

        def expandThis(m):
            fld = m.group(1)
            return self.getFieldAlias(fld,curr=curr,basealias=alias)

        def expandPref(m):
            """#PREF(myprefpath,default)"""
            prefpath = m.group(1)
            dflt=m.group(2)[1:] if m.group(2) else None
            return str(curr_tblobj.pkg.getPreference(prefpath,dflt))
        
        def expandEnv(m):
            what = m.group(1)
            par2 = None
            if m.group(2):
                par2 = m.group(2)[1:]
            if what in self.db.currentEnv:
                return "'%s'" % gnrstring.toText(self.db.currentEnv[what])
            elif par2 and par2 in self.db.currentEnv:
                return "'%s'" % gnrstring.toText(self.db.currentEnv[par2])
            if par2:
                env_tblobj = self.db.table(par2)
            else:
                env_tblobj = curr_tblobj
            handler = getattr(env_tblobj, 'env_%s' % what, None)
            if handler:
                return handler()
            else:
                return 'Not found %s' % what
        pathlist = fieldpath.split('.')
        fld = pathlist.pop()
        curr = curr or self.relations
        newpath = []
        basealias = basealias or self.aliasCode(0)
        if pathlist:
            alias, curr = self._findRelationAlias(list(pathlist), curr, basealias, newpath)
        else:
            alias = basealias
        if not fld in curr.keys():
            curr_tblobj = self.db.table(curr.tbl_name, pkg=curr.pkg_name)
            fldalias = curr_tblobj.model.virtual_columns[fld]
            if fldalias == None:
                raise GnrSqlMissingField('Missing field %s in table %s.%s (requested field %s)' % (
                fld, curr.pkg_name, curr.tbl_name, '.'.join(newpath)))
            elif fldalias.relation_path: #resolve 
            #pathlist.append(fldalias.relation_path)
            #newfieldpath = '.'.join(pathlist)        # replace the field alias with the column relation_path
            # then call getFieldAlias again with the real path
                return self.getFieldAlias(fldalias.relation_path, curr=curr,
                                          basealias=alias)  # call getFieldAlias recursively
            elif fldalias.sql_formula or fldalias.select or fldalias.exists:
                sql_formula = fldalias.sql_formula
                attr = dict(fldalias.attributes)
                select_dict = dictExtract(attr,'select_')
                if not sql_formula:
                    sql_formula = '#default' if fldalias.select else 'EXISTS(#default)'
                    select_dict['default'] = fldalias.select or fldalias.exists
                if select_dict:
                    for susbselect,sq_pars in select_dict.items():
                        if isinstance(sq_pars,basestring):
                            sq_pars = getattr(self.tblobj.dbtable,'subquery_%s' %sq_pars)()
                        sq_pars = dict(sq_pars)
                        cast = sq_pars.pop('cast',None)
                        tpl = ' CAST( ( %s ) AS ' +cast +') ' if cast else ' ( %s ) '
                        sq_table = sq_pars.pop('table')
                        sq_where = sq_pars.pop('where')
                        sq_pars.setdefault('ignorePartition',True)
                        sq_pars.setdefault('excludeDraft',False)
                        sq_pars.setdefault('excludeLogicalDeleted',False)
                        aliasPrefix = '%s_t' %alias
                        sq_where = THISFINDER.sub(expandThis,sq_where)
                        sql_text = self.db.queryCompile(table=sq_table,where=sq_where,aliasPrefix=aliasPrefix,addPkeyColumn=False,ignoreTableOrderBy=True,**sq_pars)
                        sql_formula = re.sub('#%s\\b' %susbselect, tpl %sql_text,sql_formula)
                subreldict = {}
                sql_formula = self.updateFieldDict(sql_formula, reldict=subreldict)
                sql_formula = ENVFINDER.sub(expandEnv, sql_formula)
                sql_formula = PREFFINDER.sub(expandPref, sql_formula)
                sql_formula = THISFINDER.sub(expandThis,sql_formula)
                sql_formula_var = dictExtract(attr,'var_')
                if sql_formula_var:
                    prefix = str(id(sql_formula_var))
                    currentEnv = self.db.currentEnv
                    for k,v in sql_formula_var.items():
                        newk = '%s_%s' %(prefix,k)
                        currentEnv[newk] = v
                        sql_formula = re.sub("(:)(%s)(\\W|$)" %k,lambda m: '%senv_%s%s'%(m.group(1),newk,m.group(3)), sql_formula)
                subColPars = {}
                for key, value in subreldict.items():
                    subColPars[key] = self.getFieldAlias(value, curr=curr, basealias=alias)
                sql_formula = gnrstring.templateReplace(sql_formula, subColPars, safeMode=True)
                return sql_formula
            elif fldalias.py_method:
                self.cpl.pyColumns.append((fld,getattr(self.tblobj.dbtable,fldalias.py_method,None)))
                return 'NULL'
            else:
                raise GnrSqlMissingColumn('Invalid column %s in table %s.%s (requested field %s)' % (
                fld, curr.pkg_name, curr.tbl_name, '.'.join(newpath)))
        return '%s.%s' % (alias, fld)
        
    def _findRelationAlias(self, pathlist, curr, basealias, newpath):
        """Internal method: called by getFieldAlias to get the alias (t1, t2...) for the join table.
        It is recursive to resolve paths like ``@rel.@rel2.@rel3.column``"""
        p = pathlist.pop(0)
        joiner = curr['%s?joiner' % p]
        if joiner == None:
            tblalias = self.db.table(curr.tbl_name, pkg=curr.pkg_name).model.table_aliases[p]
            if tblalias == None:
                #DUBBIO: non esiste più GnrSqlBadRequest
                #from gnr.sql.gnrsql import 
                #raise GnrSqlBadRequest('Missing field %s in requested field %s' % (p, fieldpath))
                raise GnrSqlMissingField('Missing field %s in table %s.%s (requested field %s)' % (
                p, curr.pkg_name, curr.tbl_name, '.'.join(newpath)))
            else:
                pathlist = tblalias.relation_path.split(
                        '.') + pathlist # set the alias table relation_path in the current path
        else:                                                           # then call _findRelationAlias recursively
            alias, newpath = self.getAlias(joiner, newpath, basealias)
            basealias = alias
            curr = curr[p]
        if pathlist:
            alias, curr = self._findRelationAlias(pathlist, curr, basealias, newpath)
        return alias, curr
            
    def getAlias(self, attrs, path, basealias):
        """Internal method: returns the alias (t1, t2...) for the join table of the current relation.
        If the relation is traversed for the first time, it builds the join clause.
        Here case_insensitive relations and joinConditions are addressed.
        
        :param attrs: TODO
        :param path: TODO
        :param basealias: TODO"""
        #ref = attrs['many_relation'].split('.')[-1]
        ref = attrs['many_relation'].split('.', 1)[-1] #fix 25-11-09
        newpath = path + [ref]
        pw = tuple(newpath+[basealias])
        if pw in self.aliases: # if the requested join table is yet added by previous columns
            if pw in self._explodingTables:
                if not self._currColKey in self.cpl.explodingColumns:
                    self.cpl.explodingColumns.append(self._currColKey)
            return self.aliases[pw], newpath # return the joint table alias
       # alias = '%s%i' % (self.aliasPrefix,len(self.aliases))    # else add it to the join clauses
        alias = self.aliasCode(len(self.aliases))
        self.aliases[pw] = alias
        manyrelation = False
        if attrs['mode'] == 'O':
            target_tbl = self.dbmodel.table(attrs['one_relation'])
            target_column = attrs['one_relation'].split('.')[-1]
            from_tbl = self.dbmodel.table(attrs['many_relation'])
            from_column = attrs['many_relation'].split('.')[-1]
        else:
            target_tbl = self.dbmodel.table(attrs['many_relation'])
            target_column = attrs['many_relation'].split('.')[-1]
            from_tbl = self.dbmodel.table(attrs['one_relation'])
            from_column = attrs['one_relation'].split('.')[-1]
            manyrelation = not attrs.get('one_one', False)
        target_sqlschema = target_tbl.sqlschema
        target_sqltable = target_tbl.sqlname
        target_sqlcolumn = target_tbl.sqlnamemapper[target_column]
        from_sqlcolumn = from_tbl.sqlnamemapper[from_column]
        
        if (attrs.get('case_insensitive', False) == 'Y'):
            cnd = 'lower(%s.%s) = lower(%s.%s)' % (alias, target_sqlcolumn, basealias, from_sqlcolumn)
        else:
            cnd = '%s.%s = %s.%s' % (alias, target_sqlcolumn, basealias, from_sqlcolumn)
            
        if self.joinConditions:
            from_fld, target_fld = self._tablesFromRelation(attrs)
            extracnd, one_one = self.getJoinCondition(target_fld, from_fld, alias)
            if extracnd:
                cnd = '(%s AND %s)' % (cnd, extracnd)
                if one_one:
                    manyrelation = False # if in the model a relation is defined as one_one 
                    # it is used like a one relation in both ways

        #ENV
        #env_conditions = dictExtract(self.db.currentEnv,'env_%s_condition_' %target_tbl.fullname.replace('.','_'))
        #if env_conditions:
        #    pass
        #    #print x
        #    wherelist = [where] if where else []
        #    for condition in env_conditions.values():
        #        wherelist.append('( %s )' %condition)
        #    where = ' AND '.join(wherelist)

        self.cpl.joins.append('LEFT JOIN %s.%s AS %s ON %s' %
                              (target_sqlschema, target_sqltable, alias, cnd))
        #raise str('LEFT JOIN %s.%s AS %s ON %s' % (target_sqlschema, target_sqltable, alias, cnd))
        
        # if a relation many is traversed the number of returned rows are more of the rows in the main table.
        # the columns causing the increment of rows number are saved for use by SqlSelection._aggregateRows
        if manyrelation:
            if not self._currColKey in self.cpl.explodingColumns:
                self.cpl.explodingColumns.append(self._currColKey)
            self._explodingTables.append(pw)
            self._explodingRows = True
            
        return alias, newpath
        
    def getJoinCondition(self, target_fld, from_fld, alias):
        """Internal method:  get optional condition for a join clause from the joinConditions dict.
        
        A joinCondition is a dict containing:
        
        * *condition*: the condition as a WHERE clause, the columns of the target table are referenced as $tbl.colname
        * *params*: a dict of params used in the condition clause
        * *one_one*: ``True`` if a many relation becomes a one relation due to the condition
        
        :param target_fld: TODO
        :param from_fld: TODO
        :param alias: TODO"""
        extracnd = None
        one_one = None
        joinExtra = self.joinConditions.get('%s_%s' % (target_fld.replace('.', '_'), from_fld.replace('.', '_')))
        if joinExtra:
            extracnd = joinExtra['condition'].replace('$tbl', alias)
            params = joinExtra.get('params')
            self.sqlparams.update(params)
            #raise str(self.sqlparams)
            one_one = joinExtra.get('one_one')
        return extracnd, one_one
        
    def updateFieldDict(self, teststring, reldict=None):
        """Internal method: search for columns or related columns in a string, add found columns to
        the relationDict (reldict) and replace related columns (``@rel.colname``) with a symbolic name
        like ``$_rel_colname``. Return a string containing only columns expressed in the form ``$colname``,
        so the found relations can be converted in sql strings (see :meth:`getFieldAlias()` method) and
        replaced into the returned string with templateReplace (see :meth:`compiledQuery()`).
        
        :param teststring: TODO
        :param reldict: a dict of custom names for db columns: {'asname':'@relation_name.colname'}"""
        if reldict is None: reldict = self.cpl.relationDict
        for col in COLFINDER.finditer(teststring):
            colname = col.group(2)
            if not colname in reldict:
                reldict[colname] = colname
        for col in RELFINDER.finditer(teststring):
            colname = col.group(2)
            asname = self.db.colToAs(colname)
            reldict[asname] = colname
            teststring = teststring.replace(colname, '$%s' % asname,1)
        return teststring
        
    def expandMultipleColumns(self, flt, bagFields):
        """Internal method: return a list of columns from a fake column starting with ``*``
        
        :param flt: it can be:
        
                    * ``*``: returns all columns of the current table
                    * ``*prefix_``: returns all columns of the current table starting with ``prefix_``
                    * ``*@rel1.@rel2``: returns all columns of rel2 target table
                    * ``*@rel1.@rel2.prefix_``: returns all columns of rel2 target table starting with ``prefix_``
            
        :param bagFields: boolean. If ``True``, include fields of type Bag (``X``) when columns is ``*`` or contains
                          ``*@relname.filter``."""
        subfield_name = None
        if flt in self.tblobj.virtual_columns:
            subfield_name = flt
            vc = self.tblobj.virtual_columns[flt]
            flt = vc.sql_formula
        if flt.startswith('@'):
            path = gnrstring.split(flt)
            if path[-1].startswith('@'):
                flt = ''
            else:
                flt = path.pop(-1)
            flt = flt.strip('*')
            path = '.'.join(path)
            relflds = self.relations[path]
            rowkey = None
            if flt.startswith('('):
                flt = flt[1:-1]
                flt = flt.split(',')
                rowkey = flt[0].replace('.','_').replace('@','_')
                r = []
                flatten_path = path.replace('.','_').replace('@','_')
                for f in flt:
                    fldpath = '%s.%s' % (path, f)
                    r.append(fldpath)
                    flatten_fldpath=fldpath.replace('.','_').replace('@','_')
                    subfield_name = subfield_name or flatten_path
                    self.cpl.aggregateDict[flatten_fldpath] = [subfield_name,f, '%s_%s' %(flatten_path,rowkey)]
                return r
            else:
                return ['%s.%s' % (path, k) for k in relflds.keys() if k.startswith(flt) and not k.startswith('@')]
        else:
            return ['$%s' % k for k, dtype in self.relations.digest('#k,#a.dtype') if
                    k.startswith(flt) and not k.startswith('@') and (dtype != 'X' or bagFields)]
                    
    def compiledQuery(self, columns='', where='', order_by='',
                      distinct='', limit='', offset='',
                      group_by='', having='', for_update=False,
                      relationDict=None,
                      bagFields=False,
                      count=False, excludeLogicalDeleted=True,excludeDraft=True,
                      ignorePartition=False,ignoreTableOrderBy=False,
                      addPkeyColumn=True):
        """Prepare the SqlCompiledQuery to get the sql query for a selection.
        
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        :param where: the sql "WHERE" clause. For more information check the :ref:`sql_where` section
        :param order_by: corresponding to the sql "ORDER BY" operator. For more information check the
                         :ref:`sql_order_by` section
        :param distinct: boolean, ``True`` for getting a "SELECT DISTINCT"
        :param limit: number of result's rows. Corresponding to the sql "LIMIT" operator. For more
                      information, check the :ref:`sql_limit` section
        :param offset: the same of the sql "OFFSET"
        :param group_by: the sql "GROUP BY" clause. For more information check the :ref:`sql_group_by` section
        :param having: the sql "HAVING" clause. For more information check the :ref:`sql_having`
        :param for_update: boolean. If ``True``, lock the selected records of the main table (SELECT ... FOR UPDATE OF ...)
        :param relationDict: a dict to assign a symbolic name to a :ref:`relation`. For more information
                             check the :ref:`relationdict` documentation section
        :param bagFields: boolean. If ``True``, include fields of Bag type (``X``) when the ``columns``
                          parameter is ``*`` or contains ``*@relname.filter``
        :param count: boolean. If ``True``, optimize the sql query to get the number of resulting rows
                      (like count(*))
        :param excludeLogicalDeleted: boolean. If ``True``, exclude from the query all the records that are
                                      "logical deleted"
        :param excludeDraft: TODO
        :param addPkeyColumn: boolean. If ``True``, add a column with the pkey attribute"""
        # get the SqlCompiledQuery: an object that mantains all the informations to build the sql text
        self.cpl = SqlCompiledQuery(self.tblobj.sqlfullname,relationDict=relationDict,maintable_as=self.aliasCode(0))
        distinct = distinct or '' # distinct is a text to be inserted in the sql query string
        
        # aggregate: test if the result will aggregate db rows
        aggregate = bool(distinct or group_by)
        
        # group_by == '*': if all columns are aggregate functions, there will be no GROUP BY columns, 
        #                  but SqlQueryCompiler need to know that result will aggregate db rows
        if group_by == '*':
            group_by = None

        if not ignoreTableOrderBy and not aggregate:
            order_by = order_by or self.tblobj.attributes.get('order_by')
        self.init()
        if not 'pkey' in self.cpl.relationDict:
            self.cpl.relationDict['pkey'] = self.tblobj.pkey
            
        # normalize the columns string
        columns = columns or ''
        columns = columns.replace('  ', ' ')
        columns = columns.replace('\n', '')
        columns = columns.replace(' as ', ' AS ')
        columns = columns.replace(' ,', ',')
        if columns and not columns.endswith(','):
            columns = columns + ','
            
        # expand * and *filters: see self.expandMultipleColumns
        if '*' in columns:
            col_list = [col for col in gnrstring.split(columns, ',') if col]
            new_col_list = []
            for col in col_list:
                col = col.strip()
                if col.startswith('*'):
                    new_col_list = new_col_list + self.expandMultipleColumns(col[1:], bagFields)
                else:
                    new_col_list.append(col)
            columns = ','.join(new_col_list)
            
        # translate @relname.fldname in $_relname_fldname and add them to the relationDict
        if where:
            where = PERIODFINDER.sub(self.expandPeriod, where)
            
        currentEnv = self.db.currentEnv
        env_conditions = dictExtract(currentEnv,'env_%s_condition_' %self.tblobj.fullname.replace('.','_'))
        if env_conditions:
            wherelist = [where] if where else []
            for condition in env_conditions.values():
                wherelist.append('( %s )' %condition)
            where = ' AND '.join(wherelist)

        partition_kwargs = dictExtract(self.tblobj.attributes,'partition_')

        if not ignorePartition and partition_kwargs:
            wherelist = [where] if where else []
            for k,v in partition_kwargs.items():
                if currentEnv.get('current_%s' %v):
                    wherelist.append('( $%s=:env_current_%s )' % (k,v))
            where = ' AND '.join(wherelist)
        columns = self.updateFieldDict(columns)
        where = self.updateFieldDict(where or '')
        order_by = self.updateFieldDict(order_by or '')
        group_by = self.updateFieldDict(group_by or '')
        having = self.updateFieldDict(having or '')
        
        col_list = uniquify([col for col in gnrstring.split(columns, ',') if col])
        new_col_list = []
        for col in col_list:
            col = col.strip()
            if col.startswith('SUM'):
                aggregate = True
            if not ' AS ' in col:
                if col.startswith('$') and col[1:].replace('_', '').isalnum():
                    as_ = col[1:]
                else:
                    # replace non word char with _ and check for numbers
                    as_ = self.db.colToAs(col)
                col = '%s AS "%s"' % (col, as_)
            else:
                colbody, as_ = col.split(' AS ', 1)
                # leave the col as is, but save the AS name to recover the db column original name from selection result
                self.cpl.aliasDict[as_.strip()] = colbody.strip()
            new_col_list.append(col)
            
        # build the clean and complete sql string for the columns, but still all fields are expressed as $fieldname
        columns = ',\n'.join(new_col_list)
        
        # translate all fields and related fields from $fldname to t0.fldname, t1.fldname... and prepare the JOINs
        colPars = {}
        for key, value in self.cpl.relationDict.items():
            # self._currColKey manage exploding columns in recursive getFieldAlias without add too much parameters
            self._currColKey = key
            colPars[key] = self.getFieldAlias(value)
        if count:               # if the query is executed in count mode...
            order_by = ''       # sort has no meaning
            if group_by:        # the number of rows is defined only from GROUP BY cols, so clean aggregate functions from columns.
                columns = group_by # was 't0.%s' % self.tblobj.pkey        # ???? 
            elif distinct:
                pass            # leave columns as is to calculate distinct values
            else:
                columns = 'count(*) AS gnr_row_count'  # use the sql count function istead of load all data
        elif addPkeyColumn and self.tblobj.pkey and not aggregate:
            columns = columns + ',\n' + '%s.%s AS pkey' % (self.aliasCode(0),self.tblobj.pkey)  # when possible add pkey to all selections
            columns = columns.lstrip(',')                                   # if columns was '', now it starts with ','
        else:
            columns = columns.strip('\n').strip(',')
            
        # replace $fldname with tn.fldname: finally the real SQL columns!
        columns = gnrstring.templateReplace(columns, colPars, safeMode=True)
        
        # replace $fldname with tn.fldname: finally the real SQL where!
        
        where = gnrstring.templateReplace(where, colPars)
        #if excludeLogicalDeleted==True we have additional conditions in the where clause
        logicalDeletionField = self.tblobj.logicalDeletionField
        draftField = self.tblobj.draftField
        if logicalDeletionField:
            if excludeLogicalDeleted is True:
                extracnd = '%s.%s IS NULL' % (self.aliasCode(0),logicalDeletionField)
                if where:
                    where = '%s AND %s' % (extracnd, where)
                else:
                    where = extracnd
            elif excludeLogicalDeleted == 'mark':
                if not (aggregate or count):
                    columns = '%s, %s.%s AS _isdeleted' % (columns, self.aliasCode(0),logicalDeletionField) #add logicalDeletionField
        if draftField:
            if excludeDraft is True:
                extracnd = '%s.%s IS NOT TRUE' %(self.aliasCode(0),draftField)
                if where:
                    where = '%s AND %s' % (extracnd, where)
                else:
                    where = extracnd
        # add a special joinCondition for the main selection, not for JOINs
        if self.joinConditions:
            extracnd, one_one = self.getJoinCondition('*', '*', self.aliasCode(0))
            if extracnd:
                if where:
                    where = '(%s) AND (%s)' % (where, extracnd)
                else:
                    where = extracnd
        order_by = gnrstring.templateReplace(order_by, colPars)
        having = gnrstring.templateReplace(having, colPars)
        group_by = gnrstring.templateReplace(group_by, colPars)
        
        if distinct:
            distinct = 'DISTINCT '
        elif distinct is None or distinct == '':
            if self._explodingRows:
                if not aggregate:              # if there is not yet a group_by
                    distinct = 'DISTINCT '     # add a DISTINCT to remove unusefull rows: eg. a JOIN used only for a where, not for columns
                    if order_by:
                        xorderby=(('%s '%order_by.lower()).replace(' ascending ','').replace(' descending ','').replace(' asc ','').replace(' desc','')).split(',')
                        lowercol=columns.lower()
                        for xrd in xorderby:
                            if not xrd.strip() in lowercol:
                                columns = '%s, \n%s' % (columns, xrd)
                    #order_by=None
                    if count:
                        columns = '%s.%s' % (self.aliasCode(0),self.tblobj.pkey)
                        # Count the DISTINCT maintable pkeys, instead of count(*) which will give the number of JOIN rows.
                        # That gives the count of rows on the main table: the result is different from the actual number
                        # of rows returned by the query, but it is correct in terms of main table records.
                        # It is the right behaviour ???? Yes in some cases: see SqlSelection._aggregateRows
                        
        self.cpl.distinct = distinct
        self.cpl.columns = columns
        self.cpl.where = where
        self.cpl.group_by = group_by
        self.cpl.having = having
        self.cpl.order_by = order_by
        self.cpl.limit = limit
        self.cpl.offset = offset
        self.cpl.for_update = for_update
        #raise str(self.cpl.get_sqltext(self.db))  # uncomment it for hard debug
        return self.cpl
        
    def compiledRecordQuery(self, lazy=None, eager=None, where=None,
                            bagFields=True, for_update=False, relationDict=None, virtual_columns=None):
        """Prepare the :class:`SqlCompiledQuery` class to get the sql query for a selection.
        
        :param lazy: TODO. 
        :param eager: TODO. 
        :param where: the sql "WHERE" clause. For more information check the :ref:`sql_where` section.
                      
        :param bagFields: boolean, True to include fields of type Bag (``X``) when columns is * or contains *@relname.filter
        :param for_update: TODO
        :param relationDict: a dict to assign a symbolic name to a :ref:`relation`. For more information
                             check the :ref:`relationdict` documentation section
        :param virtual_columns: TODO."""
        self.cpl = SqlCompiledQuery(self.tblobj.sqlfullname, relationDict=relationDict)
        if not 'pkey' in self.cpl.relationDict:
            self.cpl.relationDict['pkey'] = self.tblobj.pkey
        self.init(lazy=lazy, eager=eager)
        for fieldname, value, attrs in self.relations.digest('#k,#v,#a'):
            xattrs = dict([(k, v) for k, v in attrs.items() if not k in ['tag', 'comment', 'table', 'pkg']])
            if not (bagFields or (attrs.get('dtype') != 'X')):
                continue
            if 'joiner' in attrs:
                xattrs['_relmode'] = self._getRelationMode(attrs['joiner'])
            else:
                self.fieldlist.append('%s.%s AS %s_%s' % (self.aliasCode(0),fieldname, self.aliasCode(0),fieldname))
                xattrs['as'] = '%s_%s' %(self.aliasCode(0),fieldname)
            self.cpl.resultmap.setItem(fieldname,None,xattrs)

        if virtual_columns:
            self._handle_virtual_columns(virtual_columns)
        self.cpl.where = self._recordWhere(where=where)
        
        self.cpl.columns = ',\n       '.join(self.fieldlist)
        #self.cpl.limit = 2
        self.cpl.for_update = for_update
        return self.cpl
            
    
    def _getRelationMode(self,joiner):
        if joiner['mode'] == 'O':
            return 'DynItemOne'
        isOneOne=joiner.get('one_one')
        if not isOneOne and self.joinConditions:
            from_fld, target_fld = self._tablesFromRelation(joiner)
            extracnd, isOneOne = self.getJoinCondition(target_fld, from_fld, '%s0' %self.aliasPrefix)
        return 'DynItemOneOne' if isOneOne else 'DynItemMany'

    
    def _handle_virtual_columns(self, virtual_columns):
        if isinstance(virtual_columns, basestring):
            virtual_columns = gnrstring.splitAndStrip(virtual_columns, ',')
        tbl_virtual_columns = self.tblobj.virtual_columns
        for col_name in virtual_columns:
            if col_name.startswith('$'):
                col_name = col_name[1:]
            column = tbl_virtual_columns[col_name]
            if column is None:
                # print 'not existing col:%s' % col_name  # jbe commenting out the print
                continue
            self._currColKey = col_name
            field = self.getFieldAlias(column.name)
            xattrs = dict([(k, v) for k, v in column.attributes.items() if not k in ['tag', 'comment', 'table', 'pkg']])
            
            if column.attributes['tag'] == 'virtual_column':
                as_name = '%s_%s' % (self.aliasCode(0), column.name)
                path_name = column.name
            else:
                pass
            xattrs['as'] = as_name
            self.fieldlist.append('%s AS %s' % (field, as_name))
            self.cpl.resultmap.setItem(path_name, None, xattrs)
            #self.cpl.dicttemplate[path_name] = as_name
            
    def expandPeriod(self, m):
        """TODO
        
        :param m: TODO"""
        fld = m.group(1)
        period_param = m.group(2)
        date_from, date_to = decodeDatePeriod(self.sqlparams[period_param],
                                              workdate=self.db.workdate,
                                              returnDate=True, locale=self.db.locale)
        from_param = '%s_from' % period_param
        to_param = '%s_to' % period_param
        if date_from is None and date_to is None:
            return ' true'
        elif date_from and date_to:
            if date_from == date_to:
                self.sqlparams[from_param] = date_from
                return ' %s = :%s ' % (fld, from_param)
                
            self.sqlparams[from_param] = date_from
            self.sqlparams[to_param] = date_to
            result = ' (%s BETWEEN :%s AND :%s) ' % (fld, from_param, to_param)
            return result
            
        elif date_from:
            self.sqlparams[from_param] = date_from
            return ' %s >= :%s ' % (fld, from_param)
        else:
            self.sqlparams[to_param] = date_to
            return ' %s <= :%s ' % (fld, to_param)
            
    def _recordWhere(self, where=None): # usato da record resolver e record getter
        if where:
            self.updateFieldDict(where)
            colPars = {}
            for key, value in self.cpl.relationDict.items():
                colPars[key] = self.getFieldAlias(value)
            where = gnrstring.templateReplace(where, colPars)
        return where
        
    def _tablesFromRelation(self, attrs):
        if attrs['mode'] == 'O':
            target_fld = attrs['one_relation']
            from_fld = attrs['many_relation']
        else:
            target_fld = attrs['many_relation']
            from_fld = attrs['one_relation']
        return from_fld, target_fld



class SqlDataResolver(BagResolver):
    """TODO"""
    classKwargs = {'cacheTime': 0,
                   'readOnly': True,
                   'db': None}
    classArgs = ['tablename']
        
    def resolverSerialize(self):
        """TODO"""
        attr = {}
        attr['resolvermodule'] = self.__class__.__module__
        attr['resolverclass'] = self.__class__.__name__
        attr['args'] = list(self._initArgs)
        attr['kwargs'] = dict(self._initKwargs)
        attr['kwargs'].pop('db')
        attr['kwargs']['_serialized_app_db'] = 'maindb'
        return attr
        
    def init(self):
        """TODO"""
    ##raise str(self._initKwargs)
    #if 'get_app' in self._initKwargs:
    #self.db = self._initKwargs['get_app'].db
        #if '.' in self.table:
        #    self.package, self.table = self.table.split('.')
        #self.tblstruct = self.dbroot.package(self.package).table(self.table)
        self.dbtable = self.db.table(self.tablename)
        self.onCreate()
        
    def onCreate(self):
        """TODO"""
        pass
        
class SqlRelatedRecordResolver(BagResolver):
    """TODO"""
    classKwargs = {'cacheTime': 0,
                   'readOnly': True,
                   'db': None,
                   'mode': None,
                   'joinConditions': None,
                   'sqlContextName': None,
                   'virtual_columns': None,
                   'ignoreMissing': False,
                   'ignoreDuplicate': False,
                   'bagFields': True,
                   'target_fld': None,
                   'relation_value': None}
                   
    def resolverSerialize(self):
        """TODO"""
        attr = {}
        attr['resolvermodule'] = self.__class__.__module__
        attr['resolverclass'] = self.__class__.__name__
        attr['args'] = list(self._initArgs)
        attr['kwargs'] = dict(self._initKwargs)
        attr['kwargs'].pop('db')
        attr['kwargs']['_serialized_app_db'] = 'maindb'
        return attr
        
    def load(self):
        """TODO"""
        pkg, tbl, related_field = self.target_fld.split('.')
        dbtable = '%s.%s' % (pkg, tbl)
        recordpars = dict()
        recordpars[str(related_field)] = self.relation_value
        if self.parentNode.attr.get('_storefield'):
            recordpars['_storename'] = self.parentNode.parentbag[self.parentNode.attr.get('_storefield')]
        record = SqlRecord(self.db.table(dbtable), joinConditions=self.joinConditions,
                           sqlContextName=self.sqlContextName,
                           ignoreMissing=self.ignoreMissing, ignoreDuplicate=self.ignoreDuplicate,
                           virtual_columns=self.virtual_columns,
                           bagFields=self.bagFields, **recordpars)
        return record.output(self.mode)
        
class SqlQuery(object):
    """The SqlQuery class represents the way in which data can be extracted from a db.
    You can get data with these SqlQuery methods:
    
    * the :meth:`~gnr.sql.gnrsqldata.SqlQuery.count` method
    * the :meth:`~gnr.sql.gnrsqldata.SqlQuery.cursor` method
    * the :meth:`~gnr.sql.gnrsqldata.SqlQuery.fetch` method
    * the :meth:`~gnr.sql.gnrsqldata.SqlQuery.selection` method (return a :class:`~gnr.sql.gnrsqldata.SqlSelection` class)
    * the :meth:`~gnr.sql.gnrsqldata.SqlQuery.servercursor` method
    
    The ``__init__`` method passes:
    
    :param dbtable: specify the :ref:`database table <table>`. More information in the
                    :ref:`dbtable` section (:ref:`dbselect_examples_simple`)
    :param columns: it represents the :ref:`table columns <columns>` to be returned by the "SELECT"
                    clause in the traditional sql query. For more information, check the
                    :ref:`sql_columns` section
    :param where: the sql "WHERE" clause. For more information check the :ref:`sql_where` section.
    :param order_by: corresponding to the sql "ORDER BY" operator. For more information check the
                     :ref:`sql_order_by` section
    :param distinct: boolean, ``True`` for getting a "SELECT DISTINCT"
    :param limit: number of result's rows. Corresponding to the sql "LIMIT" operator. For more
                  information, check the :ref:`sql_limit` section
    :param offset: the same of the sql "OFFSET"
    :param group_by: the sql "GROUP BY" clause. For more information check the :ref:`sql_group_by` section
    :param having: the sql "HAVING" clause. For more information check the :ref:`sql_having`
    :param for_update: boolean. TODO
    :param relationDict: a dict to assign a symbolic name to a :ref:`relation`. For more information
                         check the :ref:`relationdict` documentation section
    :param sqlparams: a dictionary which associates sqlparams to their values
    :param bagFields: boolean. If ``True`` include fields of type Bag (``X``) when columns is ``*`` or
                      contains ``*@relname.filter``
    :param joinConditions: special conditions for joining related tables. See the
                           :meth:`setJoinCondition() <gnr.sql.gnrsqldata.SqlQuery.setJoinCondition()>`
                           method
    :param sqlContextName: the name of the sqlContext to be reported for subsequent related selection.
                            (see the
                           :meth:`setJoinCondition() <gnr.web.gnrwebpage.GnrWebPage.setJoinCondition>` method)
    :param excludeLogicalDeleted: boolean. If ``True``, exclude from the query all the records that are
                                  "logical deleted"
    :param addPkeyColumn: boolean. If ``True``, add a column with the :ref:`pkey` attribute
    :param locale: the current locale (e.g: en, en_us, it)"""
    def __init__(self, dbtable, columns=None, where=None, order_by=None,
                 distinct=None, limit=None, offset=None,
                 group_by=None, having=None, for_update=False,
                 relationDict=None, sqlparams=None, bagFields=False,
                 joinConditions=None, sqlContextName=None,
                 excludeLogicalDeleted=True,excludeDraft=True,
                 ignorePartition=False,
                 addPkeyColumn=True, ignoreTableOrderBy=False,
                 locale=None,_storename=None,
                 aliasPrefix=None,
                 **kwargs):
        self.dbtable = dbtable
        self.sqlparams = sqlparams or {}
        self.querypars = dict(columns=columns, where=where, order_by=order_by,
                              distinct=distinct, group_by=group_by,
                              limit=limit, offset=offset,
                              having=having)
        self.joinConditions = joinConditions or {}
        self.sqlContextName = sqlContextName
        self.relationDict = relationDict or {}
        self.sqlparams.update(kwargs)
        self.excludeLogicalDeleted = excludeLogicalDeleted
        self.excludeDraft = excludeDraft
        self.ignorePartition = ignorePartition
        self.addPkeyColumn = addPkeyColumn
        self.ignoreTableOrderBy = ignoreTableOrderBy
        self.locale = locale
        self.storename = _storename
        self.aliasPrefix = aliasPrefix
        
        test = " ".join([v for v in (columns, where, order_by, group_by, having) if v])
        rels = set(re.findall('\$(\w*)', test))
        params = set(re.findall('\:(\w*)', test))
        for r in rels:                             # for each $name in the query
            if not r in params:                    # if name is also present as :name skip
                if r in self.sqlparams:            # if name is present in kwargs
                    if not r in self.relationDict: # if name is not yet defined in relationDict
                        self.relationDict[r] = self.sqlparams.pop(r)
                        
        self.bagFields = bagFields
        self.db = self.dbtable.db
        self._compiled = None
        
    def setJoinCondition(self, target_fld, from_fld, condition, one_one=False, **kwargs):
        """TODO
        
        :param target_fld: TODO
        :param from_fld: TODO
        :param condition: set a :ref:`sql_condition` for the join
        :param one_one: boolean. TODO
        """
        cond = dict(condition=condition, one_one=one_one, params=kwargs)
        self.joinConditions['%s_%s' % (target_fld.replace('.', '_'), from_fld.replace('.', '_'))] = cond
        
        #def resolver(self, mode='bag'):
        #return SqlSelectionResolver(self.dbtable.fullname,  db=self.db, mode=mode,
        #relationDict=self.relationDict, sqlparams=self.sqlparams,
        #joinConditions=self.joinConditions, bagFields=self.bagFields, **self.querypars)
        
    def _get_sqltext(self):
        return self.compiled.get_sqltext(self.db)
        
    sqltext = property(_get_sqltext)
        
    def _get_compiled(self):
        if self._compiled is None:
            self._compiled = self.compileQuery()
        return self._compiled
        
    compiled = property(_get_compiled)
        
    def compileQuery(self, count=False):
        """Return the :meth:`compiledQuery() <SqlQueryCompiler.compiledQuery()>` method.
        
        :param count: boolean. If ``True``, optimize the sql query to get the number of resulting rows (like count(*))"""
        return SqlQueryCompiler(self.dbtable.model,
                                joinConditions=self.joinConditions,
                                sqlContextName=self.sqlContextName,
                                sqlparams=self.sqlparams,
                                aliasPrefix=self.aliasPrefix,
                                locale=self.locale).compiledQuery(relationDict=self.relationDict,
                                                                  count=count,
                                                                  bagFields=self.bagFields,
                                                                  excludeLogicalDeleted=self.excludeLogicalDeleted,
                                                                  excludeDraft=self.excludeDraft,
                                                                  addPkeyColumn=self.addPkeyColumn,
                                                                  ignorePartition=self.ignorePartition,
                                                                  ignoreTableOrderBy=self.ignoreTableOrderBy,
                                                                  **self.querypars)
                                                                  
    def cursor(self):
        """Get a cursor of the current selection."""
        
        return self.db.execute(self.sqltext, self.sqlparams, dbtable=self.dbtable.fullname,storename=self.storename)
        
    def fetch(self):
        """Get a cursor of the current selection and fetch it"""
        cursor = self.cursor()
        if isinstance(cursor, list):
            result = []
            for c in cursor:
                result.extend(c.fetchall())
                c.close()
            return result
        result = cursor.fetchall()
        cursor.close()
        self.handlePyColumns(result)
        return result

    def handlePyColumns(self,data):
        if not self.compiled.pyColumns:
            return
        for field,handler in self.compiled.pyColumns:
            if handler:
                for d in data:
                    d[field] = handler(d,field=field)

        
    def fetchAsDict(self, key=None, ordered=False):
        """Return the :meth:`~gnr.sql.gnrsqldata.SqlQuery.fetch` method as a dict with as key
        the parameter key you gave (or the pkey if you don't specify any key) and as value the
        record you get from the query
        
        :param key: the key you give (if ``None``, it takes the pkey). 
        :param ordered: boolean. if ``True``, return the fetch using a :class:`GnrDict <gnr.core.gnrdict.GnrDict>`,
                        otherwise (``False``) return the fetch using a normal dict."""
        fetch = self.fetch()
        key = key or self.dbtable.pkey
        if ordered:
            factory = GnrDict
        else:
            factory = dict
        return factory([(r[key], r) for r in fetch])
        
    def fetchAsBag(self, key=None):
        """Return the :meth:`~gnr.sql.gnrsqldata.SqlQuery.fetch` method as a Bag of the given key
        
        :param key: the key you give (if ``None``, it takes the pkey). """
        fetch = self.fetch()
        key = key or self.dbtable.pkey
        return Bag(sorted([(r[key], None, dict(r)) for r in fetch]))
        
    def fetchGrouped(self, key=None, asBag=False):
        """Return the :meth:`~gnr.sql.gnrsqldata.SqlQuery.fetch` method as a dict of the given key
        
        :param key: the key you give (if ``None``, it takes the pkey). 
        :param asBag: boolean. If ``True``, return the result as a Bag. If False, return the
                      result as a dict"""
        fetch = self.fetch()
        key = key or self.dbtable.pkey
        if asBag:
            result = Bag()
        else:
            result = {}
        for r in fetch:
            k = r[key]
            if not k in result:
                result[k] = [r]
            else:
                result[k].append(r)
        return result
        
    def test(self):
        return (self.sqltext, self.sqlparams)
        
    def _dofetch(self, pyWhere=None):
        """private: called by _get_selection"""
        if pyWhere:
            cursor, rowset = self.serverfetch(arraysize=100)
            index = cursor.index
            data = []
            for rows in rowset:
                data.extend([r for r in rows if pyWhere(r)])
        else:
            cursor = self.cursor()
            if isinstance(cursor, list):
                data = []
                for c in cursor:
                    data.extend(cursor.fetchall() or [])
                    index = cursor.index
                    c.close()
                return index, data            
            data = cursor.fetchall() or []
            index = cursor.index
        self.handlePyColumns(data)

        return index, data

    def selection(self, pyWhere=None, key=None, sortedBy=None, _aggregateRows=False):
        """Execute the query and return a SqlSelection
        
        :param pyWhere: a callback that can be used to reduce the selection during the fetch
        :param key: TODO
        :param sortedBy: TODO
        :param _aggregateRows: boolean. TODO"""
        index, data = self._dofetch(pyWhere=pyWhere)
        return SqlSelection(self.dbtable, data,
                            index=index,
                            colAttrs=self._prepColAttrs(index),
                            joinConditions=self.joinConditions,
                            sqlContextName=self.sqlContextName,
                            key=key,
                            sortedBy=sortedBy,
                            explodingColumns=self.compiled.explodingColumns,
                            _aggregateRows=_aggregateRows,
                            _aggregateDict = self.compiled.aggregateDict
                            )
                            
    def _prepColAttrs(self, index):
        colAttrs = {}
        for k in index.keys():
            if k == 'pkey':
                fld = self.dbtable.pkey
            else:
                f = self.compiled.aliasDict.get(k, k)
                f = f.strip()
                f = f.strip('$')
                fld = self.compiled.relationDict.get(f, f)
            col = self.dbtable.column(fld)
            if col is not None:
                attrs = dict(col.attributes)
                attrs.pop('comment', None)
                attrs['dataType'] = attrs.pop('dtype', 'T')
                attrs['label'] = attrs.pop('name_long', k)
                attrs['print_width'] = col.print_width
                colAttrs[k] = attrs
        return colAttrs
        
    def servercursor(self):
        """Get a cursor on dbserver"""
        return self.db.execute(self.sqltext, self.sqlparams, cursorname='*',storename=self.storename)
        
    def serverfetch(self, arraysize=30):
        """Get fetch of the :meth:`servercursor()` method.
        
        :param arraysize: TODO"""
        cursor = self.servercursor()
        cursor.arraysize = arraysize
        rows = cursor.fetchmany()
        return cursor, self._cursorGenerator(cursor, rows)
        
    def iterfetch(self, arraysize=30):
        """TODO
        
        :param arraysize: TODO"""
        for r in self.serverfetch(arraysize=arraysize)[1]:
            yield r
            
    def _cursorGenerator(self, cursor, firstRows=None):
        if firstRows:
            yield firstRows
        rows = True
        while rows:
            rows = cursor.fetchmany()
            yield rows
        cursor.close()
        
    def count(self):
        """Return rowcount. It does not save a selection"""
        compiledQuery = self.compileQuery(count=True)
        cursor = self.db.execute(compiledQuery.get_sqltext(self.db), self.sqlparams, dbtable=self.dbtable.fullname,storename=self.storename)
        if isinstance(cursor, list):
            n = 0
            for c in cursor:
                l = c.fetchall()
                partial = len(l) # for group or distinct query select -1 for each group 
                if partial == 1 and c.description[0][0] == 'gnr_row_count': # for plain query select count(*)
                    partial = l[0][0]
                c.close()
                n+=partial
        else:
            l = cursor.fetchall()
            n = len(l) # for group or distinct query select -1 for each group 
            if n == 1 and cursor.description[0][0] == 'gnr_row_count': # for plain query select count(*)
                n = l[0][0]
            cursor.close()
        return n
        
class SqlSelection(object):
    """It is the resulting data from the execution of an istance of the :class:`SqlQuery`. Through the
    SqlSelection you can get data into differents modes: you can use the :meth:`output()` method or you
    can :meth:`freeze()` it into a file. You can also use the :meth:`sort()` and the :meth:`filter()` methods
    on a SqlSelection."""
    def __init__(self, dbtable, data, index=None, colAttrs=None, key=None, sortedBy=None,
                 joinConditions=None, sqlContextName=None, explodingColumns=None, _aggregateRows=False,_aggregateDict=None):
        self._frz_data = None
        self._frz_filtered_data = None
        self.dbtable = dbtable
        self.tablename = dbtable.fullname
        self.colAttrs = colAttrs or {}
        self.explodingColumns = explodingColumns
        self.aggregateDict = _aggregateDict
        if _aggregateRows == True:
            data = self._aggregateRows(data, index, explodingColumns,aggregateDict=_aggregateDict)
        self._data = data
        if key:
            self.setKey(key)
        elif 'pkey' in index:
            self.key = 'pkey'
        else:
            self.key = None
        self.sortedBy = sortedBy
        if sortedBy:
            self.sort(sortedBy)
        self._keyDict = None
        self._filtered_data = None
        self._index = index
        self.columns = self.allColumns
        self.freezepath = None
        self.analyzeBag = None
        self.isChangedSelection = True
        self.isChangedData = True
        self.isChangedFiltered = True
        self.joinConditions = joinConditions
        self.sqlContextName = sqlContextName
        
    def _aggregateRows(self, data, index, explodingColumns,aggregateDict=None):
        if self.explodingColumns:
            newdata = []
            datadict = {}
            mixColumns = [c for c in explodingColumns if c in index and not self.colAttrs[c].get('one_one') and not( aggregateDict and (c in aggregateDict))]
            for d in data:
                if not d['pkey'] in datadict:
                    for col in mixColumns:
                        d[col] = [d[col]]
                    if aggregateDict:
                        for k,v in aggregateDict.items():
                            subfld = v[0]
                            d[subfld] = d.get(subfld) or {}
                            sr = d[subfld].setdefault(d[v[2]],{})
                            sr[v[1]] = d[k]
                    newdata.append(d)
                    datadict[d['pkey']] = d
                else:
                    masterRow = datadict[d['pkey']]
                    for col in mixColumns:
                        if d[col] not in masterRow[col]:
                            masterRow[col].append(d[col])
                            masterRow[col].sort()
                    if aggregateDict:
                        for k,v in aggregateDict.items():
                            subfld = v[0]
                            sr = masterRow[subfld].setdefault(d[v[2]],{})
                            sr[v[1]] = d[k]
            data = newdata
            for d in data:
                for col in mixColumns:
                    d[col] = self.dbtable.fieldAggregate(col,d[col],fieldattr= self.colAttrs[col],onSelection=True)
        return data
        
    def setKey(self, key):
        """Internal method. Set the data of a SqlQuery in a dict 
        
        :param key: the key.
        """
        self.key = key
        for i, r in enumerate(self._data):
            r[key] = i
            
    def _get_allColumns(self):
        items = self._index.items()
        result = [None] * len(items)
        for k, v in items:
            result[v] = k
        return result
        
    allColumns = property(_get_allColumns)
        
    def _get_db(self):
        return self.dbtable.db
        
    db = property(_get_db)
        
    def _get_keyDict(self):
        if not self._keyDict:
            self._keyDict = dict([(r[self.key], r) for r in self.data])
        return self._keyDict
        
    keyDict = property(_get_keyDict)
    
    def output(self, mode, columns=None, offset=0, limit=None,
               filterCb=None, subtotal_rows=None, formats=None, locale=None, dfltFormats=None,
               asIterator=False, asText=False, **kwargs):
        """Return the selection into differents format
        
        :param mode: There are different options you can set:
                     
                     * `mode='pkeylist'`: TODO
                     * `mode='records'`: TODO
                     * `mode='data'`: TODO
                     * `mode='tabtext'`: TODO
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        :param offset: the same of the sql "OFFSET"
        :param limit: number of result's rows. Corresponding to the sql "LIMIT" operator. For more
                      information, check the :ref:`sql_limit` section
        :param filterCb: TODO
        :param subtotal_rows: TODO
        :param formats: TODO
        :param locale: the current locale (e.g: en, en_us, it)
        :param dfltFormats: TODO
        :param asIterator: boolean. TODO
        :param asText: boolean. TODO"""
        if subtotal_rows :
            subtotalNode = self.analyzeBag.getNode(subtotal_rows) if self.analyzeBag else None
            if subtotalNode and subtotalNode.attr:
                filterCb = lambda r: r[self.key] in subtotalNode.attr['idx']
        if mode == 'pkeylist' or mode == 'records':
            columns = 'pkey'
        if isinstance(columns, basestring):
            columns = gnrstring.splitAndStrip(columns, ',')
        if not columns:
            columns = self.allColumns
            if self.aggregateDict:
                columns = [c for c in columns if c not in self.aggregateDict]
        self.columns = columns
        if mode == 'data':
            columns = ['**rawdata**']
            
        if asIterator:
            prefix = 'iter'
        else:
            prefix = 'out'
            
        if mode == 'tabtext':
            asText = True
        if asText and not formats:
            formats = dict([(k, self.colAttrs.get(k, dict()).get('format')) for k in self.columns])
            
        outmethod = '%s_%s' % (prefix, mode)
        if hasattr(self, outmethod):
            outgen = self._out(columns=columns, offset=offset, limit=limit, filterCb=filterCb)
            if formats:
                outgen = self.toTextGen(outgen, formats=formats, locale=locale, dfltFormats=dfltFormats or {})
            return getattr(self, outmethod)(outgen, **kwargs) #calls the output method
        else:
            raise SelectionExecutionError('Not existing mode: %s' % outmethod)
            
    def __len__(self):
        return len(self.data)
        
    def _get_data(self):
        if self._filtered_data is not None:
            return self._filtered_data
        else:
            return self._data
            
    data = property(_get_data)
        
    def _get_filtered_data(self):
        if self._frz_filtered_data == 'frozen':
            self._freeze_filtered('r')
        return self._frz_filtered_data
        
    def _set_filtered_data(self, value):
        self._frz_filtered_data = value
        
    _filtered_data = property(_get_filtered_data, _set_filtered_data)
        
    def _get_full_data(self):
        if self._frz_data == 'frozen':
            self._freeze_data('r')
        return self._frz_data
        
    def _set_full_data(self, value):
        self._frz_data = value
        
    _data = property(_get_full_data, _set_full_data)
        
    def _freezeme(self):
        if self.analyzeBag != None:
            self.analyzeBag.makePicklable()
        saved = self.dbtable, self._data, self._filtered_data
        self.dbtable, self._data, self._filtered_data = None, 'frozen', 'frozen' * bool(self._filtered_data) or None
        selection_path = '%s.pik' % self.freezepath
        dumpfile_handle, dumpfile_path = tempfile.mkstemp(prefix='gnrselection',suffix='.pik')
        with os.fdopen(dumpfile_handle, "w") as f:
            cPickle.dump(self, f)
        shutil.move(dumpfile_path, selection_path)
        self.dbtable, self._data, self._filtered_data = saved
        
    def _freeze_data(self, readwrite):
        pik_path = '%s_data.pik' % self.freezepath
        if readwrite == 'w':
            dumpfile_handle, dumpfile_path = tempfile.mkstemp(prefix='gnrselection_data',suffix='.pik')
            with os.fdopen(dumpfile_handle, "w") as f:
                cPickle.dump(self._data, f)
            shutil.move(dumpfile_path, pik_path)
        else:
            with open(pik_path) as f:
                self._data = cPickle.load(f)
        f.close()
        
    def _freeze_filtered(self, readwrite):
        fpath = '%s_filtered.pik' % self.freezepath
        if readwrite == 'w' and self._filtered_data is None:
            if os.path.isfile(fpath):
                os.remove(fpath)
        else:
            if readwrite == 'w':
                dumpfile_handle, dumpfile_path = tempfile.mkstemp(prefix='gnrselection_filtered',suffix='.pik')
                with os.fdopen(dumpfile_handle, "w") as f:
                    cPickle.dump(self._filtered_data, f)
                shutil.move(dumpfile_path, fpath)
            else:
                with open(fpath) as f:
                    self._filtered_data = cPickle.load(f)
            
    def freeze(self, fpath, autocreate=False):
        """TODO
        
        :param fpath: the freeze path
        :param autocreate: boolean. if ``True``, TODO"""
        self.freezepath = fpath
        self.isChangedSelection = False
        self.isChangedData = False
        self.isChangedFiltered = False
        if autocreate:
            dirname = os.path.dirname(fpath)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
        self._freezeme()
        self._freeze_data('w')
        self._freeze_filtered('w')
        
    def freezeUpdate(self):
        """TODO"""
        if self.isChangedData:
            self._freeze_data('w')
        if self.isChangedFiltered:
            self._freeze_filtered('w')
            
        isChangedSelection = self.isChangedSelection
        self.isChangedSelection = False # clear all changes flag before freeze self
        self.isChangedData = False
        self.isChangedFiltered = False
        if isChangedSelection:
            self._freezeme()
            
    def getByKey(self, k):
        """TODO
        
        :param k: TODO"""
        return self.keyDict[k]
        
    def sort(self, *args):
        """TODO"""
        args = list(args)
        args = [x.replace('.','_').replace('@','_') for x in args]
        if len(args) == 1 and (',' in args[0]):
            args = gnrstring.splitAndStrip(args[0], ',')
        if args != self.sortedBy:
            if self.explodingColumns:
                for k, arg in enumerate(args):
                    if arg.split(':')[0] in self.explodingColumns:
                        args[k] = arg.replace('*', '')
            self.sortedBy = args
            gnrlist.sortByItem(self.data, *args)
            if self.key == 'rowidx':
                self.setKey('rowidx')
            self.isChangedSelection = True #prova
            if not self._filtered_data:
                self.isChangedData = True
            else:
                self.isChangedFiltered = True

                
    def filter(self, filterCb=None):
        """TODO
        
        :param filterCb: TODO. 
        """
        if filterCb:
            self._filtered_data = filter(filterCb, self._data)
        else:
            self._filtered_data = None
        self.isChangedFiltered = True
        
    def extend(self, selection, merge=True):
        """TODO
        
        :param selection: TODO
        :param merge: boolean. TODO
        """
        if not merge:
            if self._index != selection._index:
                raise GnrSqlException("Selections columns mismatch")
            else:
                l = [self.newRow(r) for r in selection.data]
        else:
            l = [self.newRow(r) for r in selection.data]
        self.data.extend(l)
        
    def apply(self, cb):
        """TODO
        
        :param cb: TODO
        """
        rowsToChange = []
        for i, r in enumerate(self._data):
            result = cb(r)
            if isinstance(result, dict):
                r.update(result)
            else:
                rowsToChange.append((i, result))
                
        if rowsToChange:
            rowsToChange.reverse()
            for i, change in rowsToChange:
                if change is None:
                    self._data.pop(i)
                else:
                    self._data.pop(i)
                    change.reverse()
                    for r in change:
                        self.insert(i, r)
                        
        self.isChangedData = True
        
    def insert(self, i, values):
        """TODO
        
        :param i: TODO
        :param values: TODO
        """
        self._data.insert(i, self.newRow(values))

    def append(self, values):
        """TODO
        
        :param i: TODO
        :param values: TODO
        """
        self._data.append(self.newRow(values))

    def newRow(self, values):
        """Add a new row and return it
        
        :param values: TODO"""
        r = GnrNamedList(self._index)
        r.update(values)
        return r
        
    def remove(self, cb):
        """TODO
        
        :param cb: TODO"""
        self._data = filter(not(cb), self._data)
        self.isChangedData = True
        
    def totalize(self, group_by=None, sum=None, collect=None, distinct=None,
                 keep=None, key=None, captionCb=None, **kwargs):
        """TODO
        
        :param group_by: the sql "GROUP BY" clause. For more information check the :ref:`sql_group_by` section
        :param sum: TODO
        :param collect: TODO
        :param distinct: boolean, ``True`` for getting a "SELECT DISTINCT"
        :param keep: TODO
        :param key: TODO
        :param captionCb: TODO"""
        if group_by is None:
            self.analyzeBag = None
        else:
            self.analyzeBag = self.analyzeBag or AnalyzingBag()
            if key is None:
                key = self.key
            elif key == '#':
                key = None
            if group_by:
                group_by = [x.replace('@', '_').replace('.', '_').replace('$', '') if isinstance(x, basestring) else x
                            for x in group_by]
            if keep:
                keep = [x.replace('@', '_').replace('.', '_').replace('$', '') if isinstance(x, basestring) else x for x
                        in keep]
            self.analyzeKey = key
            self.analyzeBag.analyze(self, group_by=group_by, sum=sum, collect=collect,
                                    distinct=distinct, keep=keep, key=key, captionCb=captionCb, **kwargs)
        return self.analyzeBag
        
    @deprecated
    def analyze(self, group_by=None, sum=None, collect=None, distinct=None, keep=None, key=None, **kwargs):
        """.. warning:: deprecated since version 0.7"""
        self.totalize(group_by=group_by, sum=sum, collect=collect, distinct=distinct, keep=keep, key=key, **kwargs)
        
    def totalizer(self, path=None):
        """TODO
        
        :param path: TODO. """
        if path and self.analyzeBag:
            return self.analyzeBag[path]
        else:
            return self.analyzeBag
            
    def totalizerSort(self, path=None, pars=None):
        """TODO
        
        :param path: TODO. 
        :param pars: TODO. 
        """
        tbag = self.totalizer(path)
        if pars:
            tbag.sort(pars)
        else:
            tbag.sort()
        
    def totals(self, path=None, columns=None):
        """TODO
           
        :param path: TODO
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section. """
        if isinstance(columns, basestring):
            columns = gnrstring.splitAndStrip(columns, ',')
            
        tbag = self.totalizer(path)
        
        result = []
        for tnode in tbag:
            tattr = tnode.getAttr()
            result.append(dict([(k, tattr[k]) for k in columns]))
            
        return result


    def sum(self,columns=None):            
        if isinstance(columns,basestring):
            columns = columns.split(',')
        result  = list()
        if not columns or not self.data:
            return result
        data = zip(*[[r[c] for c in columns] for r in self.data])
        for k,c in enumerate(columns):
            result.append(sum(filter(lambda r: r is not None, data[k])))
        return result

        
    def _out(self, columns=None, offset=0, limit=None, filterCb=None):
        if filterCb:
            source = itertools.ifilter(filterCb, self.data)
        else:
            source = self.data
        if limit:
            stop = offset + limit
        else:
            stop = None
        if columns != ['**rawdata**']:
            for r in itertools.islice(source, offset, stop):
                yield r.extractItems(columns)
        else:
            for r in itertools.islice(source, offset, stop):
                yield r
                
    def toTextGen(self, outgen, formats, locale, dfltFormats):
        """TODO
        
        :param outgen: TODO
        :param formats: TODO
        :param locale: the current locale (e.g: en, en_us, it)
        :param dfltFormats: TODO"""
        def _toText(cell):
            k, v = cell
            v = gnrstring.toText(v, format=formats.get(k) or dfltFormats.get(type(v)), locale=locale)
            return (k, v)
            
        for r in outgen:
            yield map(_toText, r)
            
    def __iter__(self):
        return self.data.__iter__()
            
    def out_listItems(self, outsource):
        """Return the outsource.
        
        :param outsource: TODO"""
        return outsource
        
    def out_count(self, outsource):
        """Return the number of rows in the outsource.
        
        :param outsource: TODO"""
        #dubbio secondo me non dovrebbe esserci
        n = 0
        for r in outsource:
            n += 1
        return n
        
    def out_distinctColumns(self, outsource):
        """TODO
        
        :param outsource: TODO"""
        return [uniquify(x) for x in zip(*[[v for k, v in r] for r in outsource])]
        
    def out_distinct(self, outsource):
        """TODO
        
        :param outsource: TODO"""
        return set([tuple([col[1] for col in r]) for r in outsource])
        
    def out_generator(self, outsource):
        """Return the outsource
        
        :param outsource: TODO"""
        return outsource
        
    def iter_data(self, outsource):
        """Return the outsource
        
        :param outsource: TODO"""
        return outsource
        
    def out_data(self, outsource):
        """Return a list of the outsource's rows.
        
        :param outsource: TODO"""
        return [r for r in outsource]
        
    def iter_dictlist(self, outsource):
        """A generator function that returns a dict of the outsource's rows.
        
        :param outsource: TODO"""
        for r in outsource:
            yield dict(r)
            
    def out_dictlist(self, outsource):
        """TODO
        
        :param outsource: TODO"""
        return [dict(r) for r in outsource]
        
    def out_json(self, outsource):
        """TODO
        
        :param outsource: TODO"""
        return gnrstring.toJson(self.out_dictlist(outsource))
        
    def out_list(self, outsource):
        """TODO
        
        :param outsource: TODO"""
        return [[v for k, v in r] for r in outsource]
        
    def out_pkeylist(self, outsource):
        """TODO
        
        :param outsource: TODO"""
        return [r[0][1] for r in outsource]
        
    def iter_pkeylist(self, outsource):
        """TODO
        
        :param outsource: TODO"""
        for r in outsource:
            yield r[0][1]

    def out_template(self,outsource,rowtemplate=None,joiner=''):
        result = []
        for r in outsource:
            result.append(gnrstring.templateReplace(rowtemplate,dict(r),safeMode=True))
        return joiner.join(result)

    def out_records(self, outsource,virtual_columns=None):
        """TODO
        
        :param outsource: TODO"""
        return [self.dbtable.record(r[0][1], mode='bag',virtual_columns=virtual_columns) for r in outsource]
        
    def iter_records(self, outsource):
        """TODO
        
        :param outsource: TODO"""
        for r in outsource:
            yield self.dbtable.record(r[0][1], mode='bag')
            
    def out_bag(self, outsource, recordResolver=False):
        """TODO
        
        :param outsource: TODO
        :param recordResolver: boolean. TODO"""
        b = Bag()
        headers = Bag()
        for k in self.columns:
            headers.setItem(k, None, _attributes=self.colAttrs.get(k, {}))
        b['headers'] = headers
        b['rows'] = self.buildAsBag(outsource, recordResolver)
        return b
            
    def buildAsBag(self, outsource, recordResolver):
        """TODO
        
        :param outsource: TODO
        :param recordResolver: boolean. TODO"""
        result = Bag()
        defaultTable = self.dbtable.fullname
        for j, row in enumerate(outsource):
            row = Bag(row)
            pkey = row.pop('pkey')
            if not pkey:
                spkey = 'r_%i' % j
            else:
                spkey = gnrstring.toText(pkey)
                    
            nodecaption = self.dbtable.recordCaption(row)
            #fields, mask = self.dbtable.rowcaptionDecode()
            #cols = [(c, gnrstring.toText(row[c])) for c in fields]
            #if '$' in mask:
            #nodecaption = gnrstring.templateReplace(mask, dict(cols))
            #else:
            #nodecaption = mask % tuple([v for k,v in cols])
            
            result.setItem('%s' % spkey, row, nodecaption=nodecaption)
            if pkey and recordResolver:
                result['%s._' % spkey] = SqlRelatedRecordResolver(db=self.db, cacheTime=-1, mode='bag',
                                                                  target_fld='%s.%s' % (defaultTable, self.dbtable.pkey),
                                                                  relation_value=pkey,
                                                                  joinConditions=self.joinConditions,
                                                                  sqlContextName=self.sqlContextName)
                                                                  
        return result
            
    def out_recordlist(self, outsource, recordResolver=True):
        """TODO
        
        :param outsource: TODO
        :param recordResolver: boolean. TODO"""
        result = Bag()
        content = None
        for j, row in enumerate(outsource):
            row = dict(row)
            content = self.dbtable.buildrecord(row)
            result.setItem('r_%i' % j, content, _pkey=row.get('pkey'))
        return result
        
    def out_baglist(self, outsource, recordResolver=False, labelIsPkey=False):
        """TODO
        
        :param outsource: TODO
        :param recordResolver: boolean. TODO
        :param caption: boolean. TODO"""
        result = Bag()
        for j, row in enumerate(outsource):
            row = dict(row)
            pkey = row.pop('pkey', None)
            if labelIsPkey:
                label = pkey
            else:
                label = 'r_%i' % j
            result.setItem(label, Bag(row), _pkey=pkey)
        return result
        
    def out_selection(self, outsource, recordResolver=False, caption=False):
        """TODO
        
        :param outsource: TODO
        :param recordResolver: boolean. TODO
        :param caption: boolean. TODO"""
        result = Bag()
        content = ''
        for j, row in enumerate(outsource):
            row = dict(row)
            pkey = row.pop('pkey', None)
            if not pkey:
                spkey = 'r_%i' % j
            else:
                spkey = gnrstring.toText(pkey).replace('.', '_')
            if pkey and recordResolver:
                content = SqlRelatedRecordResolver(db=self.db, cacheTime=-1, mode='bag',
                                                   target_fld='%s.%s' % (self.dbtable.fullname, self.dbtable.pkey),
                                                   relation_value=pkey,
                                                   joinConditions=self.joinConditions,
                                                   sqlContextName=self.sqlContextName)
            if caption:
                if isinstance(caption, basestring):
                    rowcaption = caption
                else:
                    rowcaption = None
                row['caption'] = self.dbtable.recordCaption(row, rowcaption=rowcaption)
            result.setItem('%s' % spkey, content,
                           _pkey=pkey, _attributes=row, _removeNullAttributes=False)
        return result
            
    def out_grid(self, outsource, recordResolver=True,**kwargs):
        """TODO
           
        :param outsource: TODO
        :param recordResolver: boolean. TODO"""
        return self.buildAsGrid(outsource, recordResolver,**kwargs)
        
    def buildAsGrid(self, outsource, recordResolver,virtual_columns=None,**kwargs):
        """TODO
           
        :param outsource: TODO
        :param recordResolver: boolean. TODO"""
        result = Bag()
        content = None
        for j, row in enumerate(outsource):
            row = Bag(row)
            pkey = row.pop('pkey')
            if not pkey:
                spkey = 'r_%i' % j
            else:
                spkey = gnrstring.toText(pkey)
            if pkey and recordResolver:
                content = SqlRelatedRecordResolver(db=self.db, cacheTime=-1, mode='bag',
                                                   target_fld='%s.%s' % (self.dbtable.fullname, self.dbtable.pkey),
                                                   relation_value=pkey, joinConditions=self.joinConditions,
                                                   virtual_columns=virtual_columns,
                                                   sqlContextName=self.sqlContextName)

            result.addItem('%s' % spkey, content, _pkey=spkey, _attributes=dict(row), _removeNullAttributes=False)
        return result
        
    def out_fullgrid(self, outsource, recordResolver=True):
        """TODO
           
        :param outsource: TODO
        :param recordResolver: boolean. TODO"""
        result = Bag()
        result['structure'] = self._buildGridStruct()
        result['data'] = self.buildAsGrid(outsource, recordResolver)
        return result
        
    def _buildGridStruct(self, examplerow=None):
        structure = Bag()
        r = structure.child('view').child('row')
        for colname in self.columns:
            if colname not in ('pkey', 'rowidx'):
                r.child('cell', childname=colname, **self._cellStructFromCol(colname, examplerow=examplerow))
        return structure
        
    def _cellStructFromCol(self, colname, examplerow=None):
        kwargs = dict(self.colAttrs.get(colname, {}))
        kwargs.pop('tag', None)
        kwargs['name'] = kwargs.pop('label', None)
        kwargs['field'] = colname
        size = kwargs.pop('size', None)
        size = kwargs.pop('print_width', size)
        kwargs['width'] = None
        kwargs['dtype'] = kwargs.pop('dataType', None)
        if not kwargs['dtype']:
            kwargs['dtype'] = GnrClassCatalog.convert().asTypedText(45)[-1]
        if size:
            if isinstance(size, basestring):
                if ':' in size:
                    size = size.split(':')[1]
            kwargs['width'] = '%iem' % int(int(size) * .7)
        return kwargs
        
    def out_xmlgrid(self, outsource):
        """Return a Bag
           
        :param outsource: TODO"""
        result = Bag()
        
        dataXml = []
        catalog = gnrclasses.GnrClassCatalog()
        #xmlheader = "<?xml version='1.0' encoding='UTF-8'?>\n"
        #structCellTmpl='<%(field)s  name="%(name)s" field="%(field)s" dataType="%(dataType)s" width="%(width)s" tag="cell"/>'
        dataCellTmpl = '<r_%i  %s/>'
        columns = [c for c in self.columns if not c in ('pkey', 'rowidx')]
        #structXml = '\n'.join([structCellTmpl % self._cellStructFromCol(colname) for colname in columns])
        #structure = '<structure><view_0 tag="view"><row_0 tag="row">%s</row_0></view_0></structure>' % structXml
        for row in outsource:
            row = dict(row)
            rowstring = ' '.join(
                    ['%s=%s' % (colname, saxutils.quoteattr(catalog.asTypedText(row[colname]))) for colname in columns])
            dataXml.append(dataCellTmpl % (row['rowidx'], rowstring))
        result['data'] = BagAsXml('\n'.join(dataXml))
        result['structure'] = self._buildGridStruct(row)
        #dataXml='<data>%s</data>' %
        # result = '%s\n<GenRoBag><result>%s\n%s</result></GenRoBag>' % (xmlheader,structure,dataXml)
        #result = BagAsXml('%s\n%s' % (structure,dataXml))
        return result
        
    @property
    def colHeaders(self):
        """TODO"""
        def translate(txt):
            if txt.startswith('!!'):
                txt = txt[2:]
                
                #app = getattr(self.dbtable.db, 'application', None)
                #if app:
                #    txt = app.localization.get(txt, txt)
            return txt
                
        columns = [c for c in self.columns if not c in ('pkey', 'rowidx')]
        headers = []
        for colname in columns:
            colattr = self.colAttrs.get(colname, dict())
            headers.append(translate(colattr.get('label', colname)))
        return headers
            
    def out_tabtext(self, outsource):
        """TODO
        
        :param outsource: TODO"""
        def translate(txt):
            if txt.startswith('!!'):
                txt = txt[2:]
                
                #app = getattr(self.dbtable.db, 'application', None)
                #if app:
                #    txt = app.localization.get(txt, txt)
            return txt
            
        columns = [c for c in self.columns if not c in ('pkey', 'rowidx')]
        headers = []
        for colname in columns:
            colattr = self.colAttrs.get(colname, dict())
            headers.append(translate(colattr.get('label', colname)))
        result = ['\t'.join(headers)]
        for row in outsource:
            r = dict(row)
            result.append(
                    '\t'.join([r[col].replace('\n', ' ').replace('\r', ' ').replace('\t', ' ') for col in columns]))
        return '\n'.join(result)
        
    def out_xls(self, outsource, filepath=None):
        """TODO
        
        :param outsource: TODO
        :param filePath: boolean. TODO. """
        from gnr.core.gnrxls import XlsWriter
        
        columns = [c for c in self.columns if not c in ('pkey', 'rowidx')]
        coltypes = dict([(k, v['dataType']) for k, v in self.colAttrs.items()])
        writer = XlsWriter(columns=columns, coltypes=coltypes, headers=self.colHeaders, filepath=filepath,
                           font='Times New Roman',
                           format_float='#,##0.00', format_int='#,##0')
        writer(data=outsource)
        
class SqlRelatedSelectionResolver(BagResolver):
    """TODO"""
    classKwargs = {'cacheTime': 0, 'readOnly': True, 'db': None,
                   'columns': None, 'mode': None, 'sqlparams': None, 'joinConditions': None, 'sqlContextName': None,
                   'target_fld': None, 'relation_value': None, 'condition': None, 'bagFields': None,'virtual_columns':None}
                   
    def resolverSerialize(self):
        """TODO"""
        attr = {}
        attr['resolvermodule'] = self.__class__.__module__
        attr['resolverclass'] = self.__class__.__name__
        attr['args'] = list(self._initArgs)
        attr['kwargs'] = dict(self._initKwargs)
        attr['kwargs'].pop('db')
        attr['kwargs']['_serialized_app_db'] = 'maindb'
        return attr
        
    def load(self):
        """TODO"""
        pkg, tbl, related_field = self.target_fld.split('.')
        dbtable = '%s.%s' % (pkg, tbl)
        
        where = "$%s = :val_%s" % (related_field, related_field)
        
        self.sqlparams = self.sqlparams or {}
        self.sqlparams[str('val_%s' % related_field)] = self.relation_value
        if self.condition:
            where = '(%s) AND (%s)' % (where, self.condition)
            
        query = SqlQuery(self.db.table(dbtable), columns=self.columns, where=where,
                         joinConditions=self.joinConditions, sqlContextName=self.sqlContextName,
                         bagFields=self.bagFields, **self.sqlparams)
        return query.selection().output(self.mode, recordResolver=(self.mode == 'grid'),virtual_columns=self.virtual_columns)
        
class SqlRecord(object):
    """TODO"""
    def __init__(self, dbtable, pkey=None, where=None,
                 lazy=None, eager=None, relationDict=None,
                 sqlparams=None,
                 ignoreMissing=False, ignoreDuplicate=False,
                 bagFields=True, for_update=False,
                 joinConditions=None, sqlContextName=None,
                 virtual_columns=None,_storename=None,
                 aliasPrefix=None,
                 **kwargs):
        self.dbtable = dbtable
        self.pkey = pkey
        self.where = where
        self.relmodes = dict(lazy=lazy, eager=eager)
        self.relationDict = relationDict
        self.sqlparams = sqlparams or {}
        self.sqlparams.update(kwargs)
        self.joinConditions = joinConditions or {}
        self.sqlContextName = sqlContextName
        self.db = self.dbtable.db
        self._compiled = None
        self._result = None
        self.ignoreMissing = ignoreMissing
        self.ignoreDuplicate = ignoreDuplicate
        self.bagFields = bagFields
        self.for_update = for_update
        self.virtual_columns = virtual_columns
        self.storename = _storename
        self.aliasPrefix = aliasPrefix or 't'

        
    def setJoinCondition(self, target_fld, from_fld, condition, one_one=False, **kwargs):
        """TODO
        
        :param target_fld: TODO
        :param from_fld: TODO
        :param condition: set a :ref:`sql_condition` for the join
        :param one_one: boolean. TODO"""
        cond = dict(condition=condition, one_one=one_one, params=kwargs)
        self.joinConditions['%s_%s' % (target_fld.replace('.', '_'), from_fld.replace('.', '_'))] = cond
        
    def output(self, mode, **kwargs):
        """TODO
        
        :param mode: TODO"""
        if hasattr(self, 'out_%s' % mode):
            return getattr(self, 'out_%s' % mode)(**kwargs) #calls the output method
        else:
            raise SelectionExecutionError('Not existing mode: %s' % mode)
            
    def _get_compiled(self):
        if self._compiled is None:
            self._compiled = self.compileQuery()
        return self._compiled
        
    compiled = property(_get_compiled)
    
    def compileQuery(self):
        """TODO"""
        if self.where:
            where = self.where
        elif self.pkey is not None:
            where = '$pkey = :pkey'
        else:
            where = ' AND '.join(['%s0.%s=:%s' % (self.aliasPrefix,k, k) for k in self.sqlparams.keys()])
        compiler = SqlQueryCompiler(self.dbtable.model, sqlparams=self.sqlparams,
                                  joinConditions=self.joinConditions,
                                  sqlContextName=self.sqlContextName,aliasPrefix=self.aliasPrefix)
        return compiler.compiledRecordQuery(where=where,relationDict=self.relationDict,bagFields=self.bagFields,
                                                for_update=self.for_update,virtual_columns=self.virtual_columns,
                                                **self.relmodes)
        
    def _get_result(self):
        if self._result is None:
            if not self.compiled.where:
                raise RecordSelectionError(
                        "Insufficient parameters for selecting a record: %s" % (self.dbtable.fullname, ))
            params = self.sqlparams
            if self.pkey is not None:
                params['pkey'] = self.pkey
                #raise '%s \n\n%s' % (str(params), str(self.compiled.get_sqltext(self.db)))
            cursor = self.db.execute(self.compiled.get_sqltext(self.db), params, dbtable=self.dbtable.fullname,storename=self.storename)
            data = cursor.fetchall()
            index = cursor.index
            cursor.close()
            if self.compiled.explodingColumns and len(data)>1:
                data = self.aggregateRecords(data,index)
            if len(data) == 1:
                self._result = data[0]
            elif len(data) == 0:
                if self.ignoreMissing:
                    self._result = Bag()
                else:
                    raise RecordNotExistingError(
                            "No record found in table %s for selection %s %s" % (self.dbtable.fullname,
                                                                                 self.compiled.get_sqltext(self.db),
                                                                                 params))
            else:
                if self.ignoreDuplicate:
                    print
                    self._result = data[0]
                else:
                    raise RecordDuplicateError(
                            "Found more than one record in table %s for selection %s %s" % (self.dbtable.fullname,
                                                                                            self.compiled.get_sqltext(
                                                                                                    self.db), params))
        return self._result


    def aggregateRecords(self,data,index):
        resultmap = self.compiled.resultmap
        mapdict = dict(resultmap.digest('#k,#a.as'))
        explodingColumns = [(mapdict[k],k) for k in self.compiled.explodingColumns]
        result = dict(data[0])
        for col,fld in explodingColumns:
            result[col] = [result[col]]
        for d in data[1:]:
            for col,fld in explodingColumns:
                result[col].append(d[col])
        for col,fld in explodingColumns:
            result[col] = self.dbtable.fieldAggregate(fld,result[col],fieldattr=resultmap.getAttr(fld))
        return [result]

    def _set_result(self,result):
        self._result = Bag()

    result = property(_get_result,_set_result)
    
    def out_newrecord(self, resolver_one=True, resolver_many=True):
        """TODO
        
        :param resolver_one: boolean. TODO
        :param resolver_many: boolean. TODO"""
        result = SqlRecordBag(self.db, self.dbtable.fullname)
        self.result = Bag()
        self.loadRecord(result, resolver_many=resolver_many, resolver_one=resolver_one)
        
        newdefaults = self.dbtable.defaultValues()
        for k, v in newdefaults.items():
            result[k] = v
        
        return result


    def out_sample(self, resolver_one=True, resolver_many=True,sample_kwargs=None):
        """TODO
        
        :param resolver_one: boolean. TODO
        :param resolver_many: boolean. TODO"""
        result = SqlRecordBag(self.db, self.dbtable.fullname)
        self.result = Bag(self.dbtable.sampleValues())
        self.loadRecord(result, resolver_many=resolver_many, resolver_one=resolver_one)
        if sample_kwargs:
            result.update(sample_kwargs)
        return result
        
    def out_bag(self, resolver_one=True, resolver_many=True):
        """TODO
        
        :param resolver_one: boolean. TODO
        :param resolver_many: boolean. TODO"""
        result = SqlRecordBag(self.db, self.dbtable.fullname)
        if self.result is not None:
            self.loadRecord(result, resolver_many=resolver_many,resolver_one=resolver_one)
        return result
        
    
    def out_template(self,recordtemplate=None):
        record=Bag()
        self.loadRecord(record,resolver_many=True, resolver_one=True)
        return gnrstring.templateReplace(recordtemplate,record,safeMode=True)
        
    def out_record(self):
        """TODO"""
        result = Bag()
        if self.result:
            self.loadRecord(result,resolver_many=False, resolver_one=False)
        return result
        
    def out_json(self):
        """TODO"""
        return gnrstring.toJson(self.out_dict())
        
    def out_dict(self):
        """TODO"""
        return dict([(str(k)[3:], self.result[k]) for k in self.result.keys()])
    

    def loadRecord(self,result,resolver_one=None,resolver_many=None):
        self._loadRecord(result,self.result,self.compiled.resultmap,resolver_one=resolver_one,resolver_many=resolver_many)
        if self.compiled.pyColumns:
            for field,handler in self.compiled.pyColumns:
                if handler:
                    result[field] = handler(result,field=field)
   

    def _loadRecord_DynItemMany(self,joiner,info,sqlresult,resolver_one,resolver_many,virtual_columns):
        opkg, otbl, ofld = joiner['one_relation'].split('.')

        info['_from_fld'] = joiner['one_relation']
        info['_target_fld'] = joiner['many_relation']
        info['_relation_value'] = sqlresult['%s0_%s' %(self.aliasPrefix,ofld)]
        target_fld = info['_target_fld']
        mpkg, mtbl, mrelated_field = target_fld.split('.')
        many_table = self.db.table('%s.%s' % (mpkg, mtbl))
        order_by = joiner.get('many_order_by') or many_table.attributes.get('order_by')
        sqlparams = dict()
        if order_by:
            sqlparams['order_by'] = order_by

        #if True or resolver_many is True:
        value = SqlRelatedSelectionResolver(
                columns='*', db=self.db, cacheTime=-1,
                target_fld=target_fld,
                relation_value=info['_relation_value'],
                mode='grid', joinConditions=self.joinConditions,
                sqlContextName=self.sqlContextName,
                virtual_columns=virtual_columns,
                sqlparams = sqlparams,
                )
        #else:
        info['_many_order_by'] = order_by
        info['_sqlContextName'] = self.sqlContextName
        info['_resolver_name'] = resolver_many
        info['_virtual_columns'] = virtual_columns
        return value,info

    def _loadRecord_DynItemOneOne(self,joiner,info,sqlresult,resolver_one,resolver_many,virtual_columns):
        opkg, otbl, ofld = joiner['one_relation'].split('.')
        info['_from_fld'] = joiner['one_relation']
        info['_target_fld'] = joiner['many_relation']
        info['one_one'] = joiner['one_one']
        relation_value = sqlresult['%s0_%s' %(self.aliasPrefix,ofld)]
        #if True or resolver_one is True:
        value = SqlRelatedRecordResolver(db=self.db, cacheTime=-1,
                                         target_fld=info['_target_fld'],
                                         relation_value=relation_value,
                                         mode='bag',
                                         bagFields=True,
                                         ignoreMissing=True,
                                         virtual_columns=virtual_columns,
                                         joinConditions=self.joinConditions,
                                         sqlContextName=self.sqlContextName)
        #else:
        info['_resolver_name'] = resolver_one
        info['_sqlContextName'] = self.sqlContextName
        info['_relation_value'] = relation_value
        info['_virtual_columns'] = virtual_columns

        return value,info
                         

    def _loadRecord_DynItemOne(self,joiner,info,sqlresult,resolver_one,resolver_many,virtual_columns):
        if joiner.get('eager_one'):
            info['_eager_one']=joiner['eager_one']
        mpkg, mtbl, mfld = joiner['many_relation'].split('.')
        info['_from_fld'] = joiner['many_relation']
        info['_target_fld'] = joiner['one_relation']
        relation_value = sqlresult['%s0_%s' %(self.aliasPrefix,mfld)]                       
        #if True or resolver_one is True:
        value=SqlRelatedRecordResolver(db=self.db, cacheTime=-1,
                                             target_fld=info['_target_fld'],
                                             relation_value=relation_value,
                                             mode='bag', virtual_columns=virtual_columns,
                                             bagFields=True,
                                             ignoreMissing=True,
                                             joinConditions=self.joinConditions,
                                             sqlContextName=self.sqlContextName
                                             )
        #else:
        if 'storefield' in joiner:
            info['_storefield'] = joiner['storefield']
        if 'resolver_kwargs' in joiner:
            info['_resolver_kwargs'] = joiner['resolver_kwargs']
        info['_resolver_name'] = resolver_one
        info['_sqlContextName'] = self.sqlContextName
        info['_auto_relation_value'] = mfld
        info['_virtual_columns'] = virtual_columns
        info['_storename'] = joiner.get('_storename') or self.storename
        return value,info
        
    def _onChangedValueCb(self,node=None,evt=None,info=None,**kwargs):
        if evt=='upd_value':
            rnode = node.parentbag.getNode('@%s' %node.label)
            if rnode and rnode.resolver:
                rnode.resolver(relation_value=node.value)

    def _loadRecord(self, result, sqlresult,fields, resolver_one=None, resolver_many=None):
        for fieldname, args in fields.digest('#k,#a'):
            dtype = args.get('dtype')
            info = dict(args)
            joiner = info.pop('joiner',None)
            relmode = info.pop('_relmode',None)            
            if relmode:
                info['mode'] = joiner['mode']
                if (relmode=='DynItemMany' and resolver_many) or (resolver_one and relmode in ('DynItemOneOne','DynItemOne')):
                    virtual_columns = self.virtual_columns
                    if virtual_columns:
                        virtual_columns = ','.join(
                            [vc.split('.', 1)[1] for vc in virtual_columns.split(',') if vc.startswith(fieldname)])
                    value, info = getattr(self,'_loadRecord_%s' %relmode)(joiner,info,sqlresult,resolver_one,resolver_many,virtual_columns)
                    result.setItem(fieldname, value, info)               
                    if resolver_one and relmode =='DynItemOne':
                        result.getNode(fieldname[1:]).subscribe('resolverChanged',self._onChangedValueCb)
            else:
                value = sqlresult['%s0_%s' %(self.aliasPrefix,fieldname)]

                if dtype == 'X':
                    if self.bagFields:
                        value = Bag(value)
                    else:
                        continue
               #if dtype == 'X':
               #    try:
               #        #md5value = value or ''
               #        #md5value = md5value.encode('utf8')
               #        #info['_bag_md5'] = hashlib.md5(md5value).hexdigest()
               #        value = Bag(value)
               #    except:
               #        pass
                result.setItem(fieldname, value, info)

    
class SqlRecordBag(Bag):
    """TODO"""
    def __init__(self, db=None, tablename=None):
        Bag.__init__(self)
        self.db = db
        self.tablename = tablename
        self.isNew = True
        
    def save(self, **kwargs):
        """TODO"""
        for k, v in kwargs.items():
            self[k] = v
        if self.isNew:
            self.db.table(self.tablename).insert(self)
            self.isNew = False
        else:
            self.db.table(self.tablename).update(self)
        
    def _set_db(self, db):
        if db is None:
            self._db = db
        else:
            #self._db = weakref.ref(db)
            self._db = db
        
    def _get_db(self):
        if self._db:
            #return self._db()
            return self._db
        
    db = property(_get_db, _set_db)