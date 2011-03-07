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
import re
#import weakref
import cPickle
import itertools
import hashlib
from xml.sax import saxutils
from gnr.core.gnrdict import GnrDict
from gnr.core.gnrlang import deprecated, uniquify
from gnr.core.gnrdate import decodeDatePeriod
from gnr.core.gnrlist import GnrNamedList
from gnr.core import gnrclasses
from gnr.core import gnrstring
from gnr.core import gnrlist
from gnr.core.gnrclasses import GnrClassCatalog
from gnr.core.gnrbag import Bag, BagResolver, BagAsXml
from gnr.core.gnranalyzingbag import AnalyzingBag
from gnr.sql.gnrsql_exceptions import SelectionExecutionError, RecordDuplicateError,\
    RecordNotExistingError, RecordSelectionError,\
    GnrSqlMissingField, GnrSqlMissingColumn

COLFINDER = re.compile(r"(\W|^)\$(\w+)")
RELFINDER = re.compile(r"(\W|^)(\@([\w.@:]+))")
PERIODFINDER = re.compile(r"#PERIOD\s*\(\s*((?:\$|@)?[\w\.\@]+)\s*,\s*(\w*)\)")
ENVFINDER = re.compile(r"#ENV\(([^,)]+)(,[^),]+)?\)")
PREFFINDER = re.compile(r"#PREF\(([^,)]+)(,[^),]+)?\)")
STOREFINDER = re.compile(r"#STORE\(([^,)]+)(,[^),]+)?\)")


class SqlCompiledQuery(object):
    """SqlCompiledQuery is a private class used by SqlQueryCompiler. 
       It is used to store all parameters needed to compile a query string."""
       
    def __init__(self, maintable, relationDict=None):
        """:param maintable: the name of the main table to query.
        :param relationDict: a dict of custom names for db columns: {'asname':'@relation_name.colname'}.
                             Default value is ``None``
        """
        self.maintable = maintable
        self.relationDict = relationDict or {}
        self.aliasDict = {}
        self.template = Bag()
        self.dicttemplate = {}
        
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
        
    def get_sqltext(self, db):
        """Compile the SQL query string based on current query parameters and the specific db adapter for the current db in use.
        
        :param db: a GnrSqlDb instance
        :returns: an SQL string
        """
        kwargs = {}
        for k in (
        'maintable', 'distinct', 'columns', 'joins', 'where', 'group_by', 'having', 'order_by', 'limit', 'offset',
        'for_update'):
            kwargs[k] = getattr(self, k)
        return db.adapter.compileSql(**kwargs)
            
class SqlQueryCompiler(object):
    """SqlQueryCompiler is a private class used by SqlQuery and SqlRecord to build an SqlCompiledQuery instance."""
            
    def __init__(self, tblobj, joinConditions=None, sqlContextName=None, sqlparams=None, locale=None):
        """:param tblobj: the main table to query: an instance of SqlTable, you can get it using db.table('pkgname.tablename')
        :param joinConditions: special conditions for joining related tables. See SqlQuery.setJoinCondition.
                               Default value is ``None``
        :param sqlContextName: the name of the sqlContext to be reported for subsequent related selection. 
                               Default value is ``None`` (see GnrBaseWebPage.setJoinCondition)
        :param sqlparams: a dict of parameters used in where clause.
                          Default value is ``None``
        :param locale: add???. Default value is ``None``
        """
        self.tblobj = tblobj
        self.db = tblobj.db
        self.dbmodel = tblobj.db.model
        self.relations = tblobj.newRelationResolver(cacheTime=-1)
        self.sqlparams = sqlparams
        self.joinConditions = joinConditions
        self.sqlContextName = sqlContextName
        self.cpl = None
        self._currColKey = None
        self.locale = locale
        
    def init (self, lazy=None, eager=None):
        """add???
        
        :param lazy: add???. Default value is ``None``
        :param eager: add???. Default value is ``None``
        """
        self._explodingRows = False
        self._explodingTables = []
        self.lazy = lazy or []
        self.eager = eager or []
        self.aliases = {self.tblobj.sqlfullname: 't0'}
        self.fieldlist = []
        
    def getFieldAlias(self, fieldpath, curr=None, basealias=None):
        """Internal method. Translate fields path and related fields path in a valid sql string for the column.
           
        It translates ``@relname.@rel2name.colname`` to ``t4.colname``.
           
        It has nothing to do with the AS operator, nor the name of the output columns.
           
        It automatically adds the join tables as needed.
           
        It can be recursive to resolve virtualcolumns
           
        :param fieldpath: a path to a field, like '$colname' or '@relname.@rel2name.colname'
        :param curr: add???. Default value is ``None``
        :param basealias: add???. Default value is ``None``
        :returns: add???
        """
        def expandPref(m):
            """#PREF(myprefpath,default)"""
            prefpath = m.group(1)
            dflt=m.group(2)[1:] if m.group(2) else None
            return str(curr_tblobj.pkg.getPreference(prefpath,dflt))
        
        def expandStore(m):
            """#STORE(mystorepath,default)"""
            storepath = m.group(1)
            dflt=m.group(2)[1:] if m.group(2) else None
            return self.db.getFromStore(storepath,dflt)

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
        basealias = basealias or 't0'
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
            elif fldalias.sql_formula:
                subreldict = {}
                sql_formula = self.updateFieldDict(fldalias.sql_formula, reldict=subreldict)
                sql_formula = ENVFINDER.sub(expandEnv, sql_formula)
                sql_formula = PREFFINDER.sub(expandPref, sql_formula)
                sql_formula = STOREFINDER.sub(expandStore, sql_formula)
                sql_formula = sql_formula.replace('#THIS', alias)
                subColPars = {}
                for key, value in subreldict.items():
                    subColPars[key] = self.getFieldAlias(value, curr=curr, basealias=alias)
                sql_formula = gnrstring.templateReplace(sql_formula, subColPars, safeMode=True)

                return sql_formula
            else:
                raise GnrSqlMissingColumn('Invalid column %s in table %s.%s (requested field %s)' % (
                fld, curr.pkg_name, curr.tbl_name, '.'.join(newpath)))
        return '%s.%s' % (alias, fld)
            
    def _findRelationAlias(self, pathlist, curr, basealias, newpath):
        """Internal method: called by getFieldAlias to get the alias (t1, t2...) for the join table.
        It is recursive to resolve paths like @rel.@rel2.@rel3.column.
        """
        p = pathlist.pop(0)
        steps = curr['%s?joiner' % p]
        if steps == None:
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
            for step in steps:
                alias, newpath = self.getAlias(step, newpath, basealias)
                basealias = alias
            curr = curr[p]
        if pathlist:
            alias, curr = self._findRelationAlias(pathlist, curr, basealias, newpath)
        return alias, curr
            
    def getAlias(self, attrs, path, basealias):
        """Internal method: returns the alias (t1, t2...) for the join table of the current relation.
        If the relation is traversed for the first time, it builds the join clause.
        Here case_insensitive relations and joinConditions are addressed.
        
        :param attrs: add???
        :param path: add???
        :param basealias: add???
        :returns: add???
        """
        #ref = attrs['many_relation'].split('.')[-1]
        ref = attrs['many_relation'].split('.', 1)[-1] #fix 25-11-09
        newpath = path + [ref]
        pw = tuple(newpath)
        if pw in self.aliases: # if the requested join table is yet added by previous columns
            if pw in self._explodingTables:
                self.cpl.explodingColumns.append(self._currColKey)
            return self.aliases[pw], newpath # return the joint table alias
        alias = 't%i' % len(self.aliases)    # else add it to the join clauses
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
        from_sqltable = from_tbl.sqlname
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
        self.cpl.joins.append('LEFT JOIN %s.%s AS %s ON %s' %
                              (target_sqlschema, target_sqltable, alias, cnd))
        #raise str('LEFT JOIN %s.%s AS %s ON %s' % (target_sqlschema, target_sqltable, alias, cnd))
        
        # if a relation many is traversed the number of returned rows are more of the rows in the main table.
        # the columns causing the increment of rows number are saved for use by SqlSelection._aggregateRows
        if manyrelation:
            self.cpl.explodingColumns.append(self._currColKey)
            self._explodingTables.append(pw)
            self._explodingRows = True
            
        return alias, newpath
        
    def getJoinCondition(self, target_fld, from_fld, alias):
        """Internal method:  get optional condition for a join clause from the joinConditions dict.
        
        A joinCondition is a dict containing:
        
        * `condition`: the condition as a where clause, the columns of the target table are referenced as $tbl.colname
        * `params`: a dict of params used in the condition clause
        * `one_one`: True if a many relation becomes a one relation because of the condition
        
        :param target_fld: add???
        :param from_fld: add???
        :param alias: add???
        :returns: add???
        """
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
        """Internal method: search for columns or related columns in a string, add found columns to the relationDict
        and replace related columns (@rel.colname) with a symbolic name like $_rel_colname.
        Return a string containing only columns expressed in the form $colname, so the relations found
        can be converted in sql strings (see getFieldAlias) and replaced into the returned string with templateReplace
        (see compiledQuery)
        
        :param teststring: add???
        :param reldict: add???. Default value is ``None``
        :returns: add???
        """
        if reldict is None: reldict = self.cpl.relationDict
        for col in COLFINDER.finditer(teststring):
            colname = col.group(2)
            if not colname in reldict:
                reldict[colname] = colname
        for col in RELFINDER.finditer(teststring):
            colname = col.group(2)
            asname = self.db.colToAs(colname)
            reldict[asname] = colname
            teststring = teststring.replace(colname, '$%s' % asname)
        return teststring
        
    def expandMultipleColumns(self, flt, bagFields):
        """Internal method: returns a list of columns from a fake column starting with *
        
        :param flt: can be::
        
            *                    --> returns all columns of the current table
            *prefix_             --> returns all columns of the current table starting with prefix_
            *@rel1.@rel2         --> returns all columns of rel2 target table
            *@rel1.@rel2.prefix_ --> returns all columns of rel2 target table starting with prefix_
        
        :param bagFields: boolean, True to include fields of type Bag ('X') when columns is * or contains *@relname.filter
                          Default value is ``False``
        :returns: a list of columns
        """
        if flt.startswith('@'):
            path = flt.split('.')
            if path[-1].startswith('@'):
                flt = ''
            else:
                flt = path.pop(-1)
            flt = flt.strip('*')
            path = '.'.join(path)
            relflds = self.relations[path]
            return ['%s.%s' % (path, k) for k in relflds.keys() if k.startswith(flt) and not k.startswith('@')]
        else:
            return ['$%s' % k for k, dtype in self.relations.digest('#k,#a.dtype') if
                    k.startswith(flt) and not k.startswith('@') and (dtype != 'X' or bagFields)]
                    
    def compiledQuery(self, columns='', where='', order_by='',
                      distinct='', limit='', offset='',
                      group_by='', having='', for_update=False,
                      relationDict=None,
                      bagFields=False,
                      count=False, excludeLogicalDeleted=True,
                      addPkeyColumn=True):
        """Prepare the SqlCompiledQuery to get the sql query for a selection.
        
        :param columns: the columns to be returned by the sql select. It is a string of comma-separated columns.
                        It is a standard sql column clause and may contain sql functions and AS operators.
                        In addition to sql expressions, a column can be:
                        
                        * `$colname`: a column of the main table or a key of the relationDict
                        * `@relname.colname`: a related column
                        * `sqlfunction($colname, @relname.colname)`: $ and @ syntax can be used inside sql functions too 
                        * `*` : all the columns of the main table (with or without the bagFields)
                        * `*filter`: all columns of the main table filtered (see expandMultipleColumns)
                        * `*@relname.filter`: all columns of a related table filtered (see expandMultipleColumns)
                        Default value is ``''``
        
        :param where: the sql WHERE clause. Database columns can be use the syntax ``$colname`` and ``@relname.colname``.
                      Parameters for the query starts with ``:``, like ``@relname.colname = :param1``
                      Default value is ``''``
        :param order_by: the sql ORDER BY clause. Database columns can be use the syntax ``$colname``
                         and ``@relname.colname``. Default value is ``''``
        :param distinct: boolean, True for getting a SELECT DISTINCT. Default value is ``''``
        :param limit: number, the sql LIMIT clause. Default value is ``''``
        :param offset: number, the sql LIMIT clause. Default value is ``''``
        :param group_by: the sql GROUP BY clause. Database columns can be use the syntax ``$colname`` and ``@relname.colname``.
                         Use group_by='*' when all columns are aggregate functions in order to avoid the automatic insertion 
                         of the pkey field in the columns.
                         Default value is ``''``
        :param having: the sql HAVING clause. Database columns can be use the syntax ``$colname``
                       and ``@relname.colname``. Default value is ``''``
        :param for_update: boolean, True to lock the selected records of the main table (SELECT ... FOR UPDATE OF ...).
                           Default value is ``False``
        :param relationDict: a dict to assign a symbolic name to related fields. ``dict(myname='@relname.colname')``
                             ``myname`` can be used as ``$myname`` in all clauses to refer to the related column ``@relname.colname``.
                             ``myname`` is also the name of the related column in the result of the select (relatedcol AS myname).
                             Default value is ``None``
        :param bagFields: boolean, True to include fields of type Bag ('X') when columns is ``*`` or contains ``*@relname.filter``.
                          Default value is ``False``
        :param count: boolean, True to optimyze the sql query to get just the number of resulting rows (like count(*)).
                      Default value is ``False``
        :param excludeLogicalDeleted: boolean, True to exclude from the query all the records that are "logical deleted".
                                      Default value is ``True``
        :param addPkeyColumn: boolean, True to add a column pkey. Default value is ``True``
        :returns: add???
        """
        # get the SqlCompiledQuery: an object that mantains all the informations to build the sql text
        self.cpl = SqlCompiledQuery(self.tblobj.sqlfullname, relationDict=relationDict)
        distinct = distinct or '' # distinct is a text to be inserted in the sql query string
        
        # aggregate: test if the result will aggregate db rows
        aggregate = bool(distinct or group_by)
        
        # group_by == '*': if all columns are aggregate functions, there will be no GROUP BY columns, 
        #                  but SqlQueryCompiler need to know that result will aggregate db rows
        if group_by == '*':
            group_by = None
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
        columns = self.updateFieldDict(columns)
        where = self.updateFieldDict(where or '')
        order_by = self.updateFieldDict(order_by or '')
        group_by = self.updateFieldDict(group_by or '')
        having = self.updateFieldDict(having or '')
        
        col_list = uniquify([col for col in gnrstring.split(columns, ',') if col])
        new_col_list = []
        for col in col_list:
            col = col.strip()
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
            columns = columns + ',\n' + 't0.%s AS pkey' % self.tblobj.pkey  # when possible add pkey to all selections
            columns = columns.lstrip(',')                                   # if columns was '', now it starts with ','
        else:
            columns = columns.strip('\n').strip(',')
            
        # replace $fldname with tn.fldname: finally the real SQL columns!
        columns = gnrstring.templateReplace(columns, colPars, safeMode=True)
        
        # replace $fldname with tn.fldname: finally the real SQL where!
        where = gnrstring.templateReplace(where, colPars)
        #if excludeLogicalDeleted==True we have additional conditions in the where clause
        logicalDeletionField = self.tblobj.logicalDeletionField
        if logicalDeletionField:
            if excludeLogicalDeleted == True:
                extracnd = 't0.%s IS NULL' % logicalDeletionField
                if where:
                    where = '%s AND %s' % (extracnd, where)
                else:
                    where = extracnd
            elif excludeLogicalDeleted == 'mark':
                if not (aggregate or count):
                    columns = '%s, t0.%s AS _isdeleted' % (columns, logicalDeletionField)
                    
        # add a special joinCondition for the main selection, not for JOINs
        if self.joinConditions:
            extracnd, one_one = self.getJoinCondition('*', '*', 't0')
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
                    if count:
                        columns = 't0.%s' % self.tblobj.pkey
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
        """Prepare the SqlCompiledQuery to get the sql query for a selection.
        
        :param lazy: add???. Default value is ``None``
        :param eager: add???. Default value is ``None``
        :param where: add???. Default value is ``None``
        :param bagFields: boolean, True to include fields of type Bag ('X') when columns is * or contains *@relname.filter
                          Default value is ``True``
        :param for_update: add???. Default value is ``False``
        :param relationDict: add???. Default value is ``None``
        :param virtual_columns: add???. Default value is ``None``
        :returns: add???
        """
        self.cpl = SqlCompiledQuery(self.tblobj.sqlfullname, relationDict=relationDict)
        if not 'pkey' in self.cpl.relationDict:
            self.cpl.relationDict['pkey'] = self.tblobj.pkey
        self.init(lazy=lazy, eager=eager)
        self.recordFields(self.relations, [], [], 't0', bagFields)
        if virtual_columns:
            self._handle_virtual_columns(virtual_columns)
        self.cpl.where = self._recordWhere(where=where)
        
        self.cpl.columns = ',\n       '.join(self.fieldlist)
        self.cpl.limit = 2
        self.cpl.for_update = for_update
        return self.cpl
        
    def _handle_virtual_columns(self, virtual_columns):
        if isinstance(virtual_columns, basestring):
            virtual_columns = gnrstring.splitAndStrip(virtual_columns, ',')
        tbl_virtual_columns = self.tblobj.virtual_columns
        for col_name in virtual_columns:
            if col_name.startswith('$'):
                col_name = col_name[1:]
            column = tbl_virtual_columns[col_name]
            if column is None:
                print 'not existing col:%s' % col_name
                continue
            field = self.getFieldAlias(column.name)
            xattrs = dict([(k, v) for k, v in column.attributes.items() if not k in ['tag', 'comment', 'table', 'pkg']])
            
            if column.attributes['tag'] == 'virtual_column':
                as_name = '%s_%s' % ('t0', column.name)
                path_name = column.name
            else:
                pass
            xattrs['as'] = as_name
            self.fieldlist.append('%s AS %s' % (field, as_name))
            self.cpl.template.setItem(path_name, None, xattrs)
            self.cpl.dicttemplate[path_name] = as_name
            
    def expandPeriod(self, m):
        """add???
        
        :param m: add???
        :returns: add???
        """
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
                as_ = self.cpl.template['%s#as' % value]
                if as_:
                    colPars[key] = '.'.join(as_.split('_', 1))
                else:
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
        
    def recordFields(self, fields, path, bagpath, basealias, bagFields): # usato da recordBuilder
        """add???
        
        :param fields: add???
        :param path: add???
        :param bagpath: add???
        :param basealias: add???
        :param bagFields: boolean, True to include fields of type Bag ('X') when columns is * or contains *@relname.filter
        """
        for field, value, attrs in fields.digest('#k,#v,#a'):
            #alias = None
            joinlist = attrs.get('joiner', None)
            dtype = attrs.get('dtype', None)
            attrs = dict([(k, v) for k, v in attrs.items() if not k in ['tag', 'comment', 'table', 'pkg']])
            newbase = basealias
            newpath = list(path)
            if (dtype != 'X') or bagFields:
                if not joinlist:
                    self.fieldlist.append('%s.%s AS %s_%s' % (basealias, field, basealias, field))
                    as_name = '%s_%s' % (basealias, field)
                    path_name = '.'.join(bagpath + [field])
                    xattrs = dict(attrs)
                    xattrs['as'] = as_name
                    self.cpl.template.setItem(path_name, None, xattrs)
                    self.cpl.dicttemplate[path_name] = as_name
                else:
                    joinlist = list(joinlist)
                    attrs = joinlist.pop()
                    extra_one_one = None
                    if self.joinConditions:
                        from_fld, target_fld = self._tablesFromRelation(attrs)
                        extracnd, extra_one_one = self.getJoinCondition(target_fld, from_fld, basealias)
                        
                    else:
                        joinExtra = {}
                    if attrs['mode'] == 'O' or attrs.get('one_one') or extra_one_one:
                        for at in joinlist: # solo se joinlist ha piu di 1 elemento: ramo morto?
                            raise
                            #newbase, newpath = self.getAlias(at, newpath, newbase)
                        if isinstance(value, Bag): #  è un relation one, perché non dovrebbe essere una bag?
                            fieldpath = '.'.join(bagpath + [field])
                            testallpath = '.'.join(bagpath + ['*'])
                            # if joinExtra.get('one_one') we had to eager load the relation in order to use the joinExtra conditions
                            is_eager_one = attrs.get('eager_one') and self.db.allow_eager_one
                            if extra_one_one\
                               or (fieldpath in self.eager)\
                               or (testallpath in self.eager)\
                            or (is_eager_one and not fieldpath in self.lazy):
                                #call recordFields recoursively for related records to be loaded in one query
                                alias, newpath = self.getAlias(attrs, newpath, newbase)
                                self.cpl.template.setItem('.'.join(bagpath + [field]), None, _attributes=attrs,
                                                          basealias=newbase)
                                self.recordFields(value, newpath, bagpath + [field], alias, bagFields)
                            elif attrs['mode'] == 'M': # a one to many relation with one_one attribute
                                self.cpl.template.setItem(fieldpath, 'DynItemOneOne', _attributes=attrs,
                                                          basealias=newbase)
                            else: # a simple many to one relation 
                                self.cpl.template.setItem(fieldpath, 'DynItemOne', _attributes=attrs, basealias=newbase)
                        else: #  ramo morto?
                            raise
                            #alias, newpath = self.getAlias(attrs, newpath, newbase)
                            #self.fieldlist.append('%s.%s AS %s_%s' % (alias, field, alias, field))                        
                            #as_name = '%s_%s' % (alias, field)
                            #path_name = '.'.join(bagpath + [field])
                            #self.cpl.template.setItem(path_name, None, as=as_name)
                            #self.cpl.dicttemplate[path_name] = as_name
                    else:
                        self.cpl.template.setItem('.'.join(bagpath + [field]), 'DynItemMany', _attributes=attrs,
                                                  basealias=newbase)
                                                  
class SqlDataResolver(BagResolver):
    """add???"""
    classKwargs = {'cacheTime': 0,
                   'readOnly': True,
                   'db': None}
    classArgs = ['tablename']
        
    def resolverSerialize(self):
        """add???
        
        :returns: add???
        """
        attr = {}
        attr['resolvermodule'] = self.__class__.__module__
        attr['resolverclass'] = self.__class__.__name__
        attr['args'] = list(self._initArgs)
        attr['kwargs'] = dict(self._initKwargs)
        attr['kwargs'].pop('db')
        attr['kwargs']['_serialized_app_db'] = 'maindb'
        return attr
        
    def init(self):
        """add???"""
    ##raise str(self._initKwargs)
    #if 'get_app' in self._initKwargs:
    #self.db = self._initKwargs['get_app'].db
        #if '.' in self.table:
        #    self.package, self.table = self.table.split('.')
        #self.tblstruct = self.dbroot.package(self.package).table(self.table)
        self.dbtable = self.db.table(self.tablename)
        self.onCreate()
        
    def onCreate(self):
        """add???"""
        pass
        
class SqlRelatedRecordResolver(BagResolver):
    """add???"""
    classKwargs = {'cacheTime': 0, 'readOnly': True, 'db': None,
                   'mode': None, 'joinConditions': None, 'sqlContextName': None, 'virtual_columns': None,
                   'ignoreMissing': False, 'ignoreDuplicate': False, 'bagFields': True,
                   'target_fld': None, 'relation_value': None}
                   
    def resolverSerialize(self):
        """add???"""
        attr = {}
        attr['resolvermodule'] = self.__class__.__module__
        attr['resolverclass'] = self.__class__.__name__
        attr['args'] = list(self._initArgs)
        attr['kwargs'] = dict(self._initKwargs)
        attr['kwargs'].pop('db')
        attr['kwargs']['_serialized_app_db'] = 'maindb'
        return attr
        
    def load(self):
        """add???"""
        pkg, tbl, related_field = self.target_fld.split('.')
        dbtable = '%s.%s' % (pkg, tbl)
        recordpars = dict()
        recordpars[str(related_field)] = self.relation_value
        record = SqlRecord(self.db.table(dbtable), joinConditions=self.joinConditions,
                           sqlContextName=self.sqlContextName,
                           ignoreMissing=self.ignoreMissing, ignoreDuplicate=self.ignoreDuplicate,
                           virtual_columns=self.virtual_columns,
                           bagFields=self.bagFields, **recordpars)
        return record.output(self.mode)
        
class SqlQuery(object):
    """The SqlQuery represents the way in which data can be extracted from a db.
    You can get data with these SqlQuery methods:
    
    * the :meth:`count` method
    * the :meth:`cursor` method
    * the :meth:`fetch` method
    * the :meth:`selection` method: return a SqlSelection
    * the :meth:`servercursor` method
    
    :param dbtable: the table on which the query is focused on
    :param columns: add???. Default value in ``__init__`` is ``None``
    :param where: the same of the sql WHERE. Default value in ``__init__`` is ``None``
    :param order_by: the same of the sql ORDER BY. Default value in ``__init__`` is ``None``
    :param distinct: the same of the sql DISTINCT. Default value in ``__init__`` is ``None``
    :param limit: the same of the sql LIMIT. Default value in ``__init__`` is ``None``
    :param offset: add???. Default value in ``__init__`` is ``None``
    :param group_by: the same of the sql GROUP BY. Default value in ``__init__`` is ``None``
    :param having: the same of the sql HAVING. Default value in ``__init__`` is ``None``
    :param for_update: boolean. add???. Default value in ``__init__`` is ``False``
    :param relationDict: a dictionary which associates relationPath names 
                         with an alias name. e.g: ``{'$member_name':'@member_id.name'}``.
                         Default value in ``__init__`` is ``None``
    :param sqlparams: a dictionary which associates sqlparams to their value.
                      Default value in ``__init__`` is ``None``
    :param bagFields: boolean, True to include fields of type Bag ('X') when columns is * or
                      contains *@relname.filter. Default value in ``__init__`` is ``False``
    :param joinConditions: add???. Default value in ``__init__`` is ``None``
    :param sqlContextName: add???. Default value in ``__init__`` is ``None``
    :param excludeLogicalDeleted: boolean. add???. Default value in ``__init__`` is ``True``
    :param addPkeyColumn: boolean. add???. Default value in ``__init__`` is ``True``
    :param locale: add???. Default value in ``__init__`` is ``None``
    """
    
    def __init__(self, dbtable, columns=None, where=None, order_by=None,
                 distinct=None, limit=None, offset=None,
                 group_by=None, having=None, for_update=False,
                 relationDict=None, sqlparams=None, bagFields=False,
                 joinConditions=None, sqlContextName=None,
                 excludeLogicalDeleted=True,
                 addPkeyColumn=True, locale=None,
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
        self.addPkeyColumn = addPkeyColumn
        self.locale = locale
        
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
        """add???
        
        :param target_fld: add???
        :param from_fld: add???
        :param condition: add???
        :param one_one: boolean. add???. Default value is ``False``
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
        """add???
        
        :param count: boolean. add???. Default value is ``False``
        """
        return SqlQueryCompiler(self.dbtable.model,
                                joinConditions=self.joinConditions,
                                sqlContextName=self.sqlContextName,
                                sqlparams=self.sqlparams,
                                locale=self.locale).compiledQuery(relationDict=self.relationDict,
                                                                  count=count,
                                                                  bagFields=self.bagFields,
                                                                  excludeLogicalDeleted=self.excludeLogicalDeleted,
                                                                  addPkeyColumn=self.addPkeyColumn,
                                                                  **self.querypars)
                                                                  
    def cursor(self):
        """get a cursor of current selection
        
        :returns: add???
        """
        return self.db.execute(self.sqltext, self.sqlparams, dbtable=self.dbtable.fullname)
        
    def fetch(self):
        """Get a cursor of the current selection and fetch it"""
        cursor = self.cursor()
        result = cursor.fetchall()
        cursor.close()
        return result
        
    def fetchAsDict(self, key=None, ordered=False):
        """Return the fetch as a dict of the given key
        
        :param key: the key you give (if None, it takes the pkey). Default value is ``None``
        :param ordered: boolean. add???. Default value is ``False``
        :returns: the fetch as a dict of the given key
        """
        fetch = self.fetch()
        key = key or self.dbtable.pkey
        if ordered:
            factory = GnrDict
        else:
            factory = dict
        return factory([(r[key], r) for r in fetch])
        
    def fetchAsBag(self, key=None):
        """Return the fetch as a bag of the given key
        
        :param key: the key you give (if None, it takes the pkey). Default value is ``None``
        :returns: the fetch as a bag of the given key
        """
        fetch = self.fetch()
        key = key or self.dbtable.pkey
        return Bag(sorted([(r[key], None, dict(r)) for r in fetch]))
        
    def fetchGrouped(self, key=None, asBag=False):
        """Return the fetch as a dict of the given key
        
        :param key: the key you give (if None, it takes the pkey). Default value is ``None``
        :param asBag: boolean. If ``True``, return the result as a Bag. If False, return the
                      result as a dict. Default value is ``False``
        :returns:
        """
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
        """add???"""
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
            data = cursor.fetchall() or []
            index = cursor.index
        return index, data
        
    def selection(self, pyWhere=None, key=None, sortedBy=None, _aggregateRows=False):
        """Execute the query and return a SqlSelection
        
        :param pyWhere: a callback that can be used to reduce the selection during the fetch.
                        Default value is ``None``
        :param key: add???.
                    Default value is ``None``
        :param sortedBy: add???.
                    Default value is ``None``
        :param _aggregateRows: boolean. add???.
                    Default value is ``False``
        :returns: a SqlSelection
        """
        index, data = self._dofetch(pyWhere=pyWhere)
        return SqlSelection(self.dbtable, data,
                            index=index,
                            colAttrs=self._prepColAttrs(index),
                            joinConditions=self.joinConditions,
                            sqlContextName=self.sqlContextName,
                            key=key,
                            sortedBy=sortedBy,
                            explodingColumns=self.compiled.explodingColumns,
                            _aggregateRows=_aggregateRows
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
        return self.db.execute(self.sqltext, self.sqlparams, cursorname='*')
        
    def serverfetch(self, arraysize=30):
        """Get fetch of servercursor
        
        :param arraysize: add???. Default value is ``30``
        """
        cursor = self.servercursor()
        cursor.arraysize = arraysize
        rows = cursor.fetchmany()
        return cursor, self._cursorGenerator(cursor, rows)
        
    def iterfetch(self, arraysize=30):
        """add???
        
        :param arraysize: add???. Default value is ``30``
        """
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
        cursor = self.db.execute(compiledQuery.get_sqltext(self.db), self.sqlparams, dbtable=self.dbtable.fullname)
        l = cursor.fetchall()
        n = len(l) # for group or distinct query select -1 for each group 
        if n == 1 and cursor.description[0][0] == 'gnr_row_count': # for plain query select count(*)
            n = l[0][0]
        cursor.close()
        return n
        
class SqlSelection(object):
    """It is the resulting data from the execution of a SqlQuery. Through SqlSelection you can get
    data into differents modes, using output method or freeze it into a file. You can sort and
    filter a SqlSelection.
    """
        
    def __init__(self, dbtable, data, index=None, colAttrs=None, key=None, sortedBy=None,
                 joinConditions=None, sqlContextName=None, explodingColumns=None, _aggregateRows=False):
        self._frz_data = None
        self._frz_filtered_data = None
        self.dbtable = dbtable
        self.tablename = dbtable.fullname
        self.explodingColumns = explodingColumns
        if _aggregateRows == True:
            data = self._aggregateRows(data, index, explodingColumns)
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
        self.colAttrs = colAttrs or {}
        self.columns = self.allColumns
        self.freezepath = None
        self.analyzeBag = None
        self.isChangedSelection = True
        self.isChangedData = True
        self.isChangedFiltered = True
        self.joinConditions = joinConditions
        self.sqlContextName = sqlContextName
        
    def _aggregateRows(self, data, index, explodingColumns):
        if self.explodingColumns:
            newdata = []
            datadict = {}
            mixColumns = [c for c in explodingColumns if c in index]
            for d in data:
                if not d['pkey'] in datadict:
                    for col in mixColumns:
                        d[col] = [d[col]]
                    newdata.append(d)
                    datadict[d['pkey']] = d
                else:
                    masterRow = datadict[d['pkey']]
                    for col in mixColumns:
                        if d[col] not in masterRow[col]:
                            masterRow[col].append(d[col])
            data = newdata
        return data
        
    def setKey(self, key):
        """add???
        
        :param key: add???
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
        
        :param mode: (optional) There are different options you can set.
        
            * `mode='pkeylist'`: add???
            * `mode='records'`: add???
            * `mode='data'`: add???
            * `mode='tabtext'`: add???
            
        :param columns: add???. Default value is ``None``
        :param offset: add???. Default value is ``0``
        :param limit: add???. Default value is ``None``
        :param filterCb: add???. Default value is ``None``
        :param subtotal_rows: add???. Default value is ``None``
        :param formats: add???. Default value is ``None``
        :param locale: add???. Default value is ``None``
        :param dfltFormats: add???. Default value is ``None``
        :param asIterator: boolean. add???. Default value is ``False``
        :param asText: boolean. add???. Default value is ``False``
        :returns: the selection
        """
        if subtotal_rows:
            attr = self.analyzeBag.getAttr(subtotal_rows)
            if attr:
                filterCb = lambda r: r[self.key] in attr['idx']
        if mode == 'pkeylist' or mode == 'records':
            columns = 'pkey'
        if isinstance(columns, basestring):
            columns = gnrstring.splitAndStrip(columns, ',')
            
        self.columns = columns or self.allColumns
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
        f = file('%s.pik' % self.freezepath, 'w')
        cPickle.dump(self, f)
        f.close()
        self.dbtable, self._data, self._filtered_data = saved
        
    def _freeze_data(self, readwrite):
        f = file('%s_data.pik' % self.freezepath, readwrite)
        if readwrite == 'w':
            cPickle.dump(self._data, f)
        else:
            self._data = cPickle.load(f)
        f.close()
        
    def _freeze_filtered(self, readwrite):
        fpath = '%s_filtered.pik' % self.freezepath
        if readwrite == 'w' and self._filtered_data is None:
            if os.path.isfile(fpath):
                os.remove(fpath)
        else:
            f = file(fpath, readwrite)
            if readwrite == 'w':
                cPickle.dump(self._filtered_data, f)
            else:
                self._filtered_data = cPickle.load(f)
            f.close()
            
    def freeze(self, fpath, autocreate=False):
        """add???
        
        :param fpath: add???
        :param autocreate: boolean. add???. Default value is ``False``
        """
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
        """add???"""
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
        """add???
        
        :param k: add???
        :returns: add???
        """
        return self.keyDict[k]
        
    def sort(self, *args):
        """add???"""
        args = list(args)
        if len(args) == 1 and (',' in args[0]):
            args = gnrstring.splitAndStrip(args[0], ',')
        if args != self.sortedBy:
            if self.explodingColumns:
                newargs = []
                for k, arg in enumerate(args):
                    if arg.split(':')[0] in self.explodingColumns:
                        args[k] = arg.replace('*', '')
            self.sortedBy = args
            gnrlist.sortByItem(self.data, *args)
            self.isChangedSelection = True #prova
            if not self._filtered_data:
                self.isChangedData = True
            else:
                self.isChangedFiltered = True
                
    def filter(self, filterCb=None):
        """add???
        
        :param filterCb: add???. Default value is ``None``
        """
        if filterCb:
            self._filtered_data = filter(filterCb, self._data)
        else:
            self._filtered_data = None
        self.isChangedFiltered = True
        
    def extend(self, selection, merge=True):
        """add???
        
        :param selection: add???
        :param merge: boolean. add???. Default value is ``True``
        """
        if not merge:
            if self._index != selection._index:
                raise "Selections' columns mismatch"
            else:
                l = [self.newRow(r) for r in selection.data]
        else:
            l = [self.newRow(r) for r in selection.data]
        self.data.extend(l)
        
    def apply(self, cb):
        """add???
        
        :param cb: add???
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
        """add???
        
        :param i: add???
        :param values: add???
        """
        self._data.insert(i, self.newRow(values))
        
    def newRow(self, values):
        """add a new row
        
        :param values: add???
        :returns: the new row
        """
        r = GnrNamedList(self._index)
        r.update(values)
        return r
        
    def remove(self, cb):
        """add???
        
        :param cb: add???
        """
        self._data = filter(not(cb), self._data)
        self.isChangedData = True
        
    def totalize(self, group_by=None, sum=None, collect=None, distinct=None,
                 keep=None, key=None, captionCb=None, **kwargs):
        """add???
        
        :param group_by: add???. Default value is ``None``
        :param sum: add???. Default value is ``None``
        :param collect: add???. Default value is ``None``
        :param distinct: add???. Default value is ``None``
        :param keep: add???. Default value is ``None``
        :param key: add???. Default value is ``None``
        :param captionCb: add???. Default value is ``None``
        """
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
        """add???
        
        :param group_by: add???. Default value is ``None``
        :param sum: add???. Default value is ``None``
        :param collect: add???. Default value is ``None``
        :param distinct: add???. Default value is ``None``
        :param keep: add???. Default value is ``None``
        :param key: add???. Default value is ``None``
        """
        self.totalize(group_by=group_by, sum=sum, collect=collect, distinct=distinct, keep=keep, key=key, **kwargs)
        
    def totalizer(self, path=None):
        """add???
        
        :param path: add???. Default value is ``None``
        :returns: add???
        """
        if path and self.analyzeBag:
            return self.analyzeBag[path]
        else:
            return self.analyzeBag
            
    def totalizerSort(self, path=None, pars=None):
        """add???
        
        :param path: add???. Default value is ``None``
        :param pars: add???. Default value is ``None``
        """
        tbag = self.totalizer(path)
        if pars:
            tbag.sort(pars)
        else:
            tbag.sort()
            
    def outputTEST(self, mode, columns=None, offset=0, limit=None,
                   filterCb=None, subtotal_rows=None, formats=None, locale=None, dfltFormats=None, recordResolver=None,
                   asIterator=False):
        """add???
        
        :param mode: add???
        :param columns: add???. Default value is ``None``
        :param offset: add???. Default value is ``0``
        :param limit: add???. Default value is ``None``
        :param filterCb: add???. Default value is ``None``
        :param subtotal_rows: add???. Default value is ``None``
        :param formats: add???. Default value is ``None``
        :param locale: add???. Default value is ``None``
        :param dfltFormats: add???. Default value is ``None``
        :param recordResolver: add???. Default value is ``None``
        :param asIterator: boolean. add???. Default value is ``False``
        """
        pass
        
    def totals(self, path=None, columns=None):
        """add???
           
        :param path: add???
        :param columns: add???. Default value is ``None``
        """
        if isinstance(columns, basestring):
            columns = gnrstring.splitAndStrip(columns, ',')
            
        tbag = self.totalizer(path)
        
        result = []
        for tnode in tbag:
            tattr = tnode.getAttr()
            result.append(dict([(k, tattr[k]) for k in columns]))
            
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
        """add???
           
        :param outgen: add???
        :param formats: add???
        :param locale: add???
        :param dfltFormats: add???
        """
        def _toText(cell):
            k, v = cell
            v = gnrstring.toText(v, format=formats.get(k) or dfltFormats.get(type(v)), locale=locale)
            return (k, v)
            
        for r in outgen:
            yield map(_toText, r)
            
    def __iter__(self):
        return self.data.__iter__()
            
    def out_listItems(self, outsource):
        """add???
           
        :param outsource: add???
        :returns: add???
        """
        return outsource
            
    def out_count(self, outsource):
        """add???
           
        :param outsource: add???
        :returns: add???
        """
        #dubbio secondo me non dovrebbe esserci
        n = 0
        for r in outsource:
            n += 1
        return n
            
    def out_distinctColumns(self, outsource):
        """add???
           
        :param outsource: add???
        :returns: add???
        """
        return [uniquify(x) for x in zip(*[[v for k, v in r] for r in outsource])]
            
    def out_distinct(self, outsource):
        """add???
           
        :param outsource: add???
        :returns: add???
        """
        return set([tuple([col[1] for col in r]) for r in outsource])
            
    def out_generator(self, outsource):
        """add???
           
        :param outsource: add???
        :returns: add???
        """
        return outsource
            
    def iter_data(self, outsource):
        """add???
           
        :param outsource: add???
        :returns: add???
        """
        return outsource
            
    def out_data(self, outsource):
        """add???
           
        :param outsource: add???
        :returns: add???
        """
        return [r for r in outsource]
            
    def iter_dictlist(self, outsource):
        """add???
           
        :param outsource: add???
        :returns: add???
        """
        for r in outsource:
            yield dict(r)
            
    def out_dictlist(self, outsource):
        """add???
           
        :param outsource: add???
        :returns: add???
        """
        return [dict(r) for r in outsource]
            
    def out_json(self, outsource):
        """add???
           
        :param outsource: add???
        :returns: add???
        """
        return gnrstring.toJson(self.out_dictlist(outsource))
            
    def out_list(self, outsource):
        """add???
           
        :param outsource: add???
        :returns: add???
        """
        return [[v for k, v in r] for r in outsource]
            
    def out_pkeylist(self, outsource):
        """add???
           
        :param outsource: add???
        :returns: add???
        """
        return [r[0][1] for r in outsource]
            
    def iter_pkeylist(self, outsource):
        """add???
           
        :param outsource: add???
        :returns: add???
        """
        for r in outsource:
            yield r[0][1]
            
    def out_records(self, outsource):
        """add???
           
        :param outsource: add???
        :returns: add???
        """
        return [self.dbtable.record(r[0][1], mode='bag') for r in outsource]
            
    def iter_records(self, outsource):
        """add???
           
        :param outsource: add???
        :returns: add???
        """
        for r in outsource:
            yield self.dbtable.record(r[0][1], mode='bag')
            
    def out_bag(self, outsource, recordResolver=False):
        """add???
           
        :param outsource: add???
        :param recordResolver: boolean. add???. Default value is ``False``
        :returns: add???
        """
        b = Bag()
        headers = Bag()
        for k in self.columns:
            headers.setItem(k, None, _attributes=self.colAttrs.get(k, {}))
        b['headers'] = headers
        b['rows'] = self.buildAsBag(outsource, recordResolver)
        return b
            
    def buildAsBag(self, outsource, recordResolver):
        """add???
           
        :param outsource: add???
        :param recordResolver: boolean. add???
        :returns: add???
        """
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
        """add???
           
        :param outsource: add???
        :param recordResolver: boolean. add???. Default value is ``True``
        :returns: add???
        """
        result = Bag()
        content = None
        for j, row in enumerate(outsource):
            row = dict(row)
            content = self.dbtable.buildrecord(row)
            result.setItem('r_%i' % j, content, _pkey=row.get('pkey'))
        return result
            
    def out_baglist(self, outsource, recordResolver=False, caption=False):
        """add???
           
        :param outsource: add???
        :param recordResolver: boolean. add???. Default value is ``False``
        :param caption: boolean. add???. Default value is ``False``
        :returns: add???
        """
        result = Bag()
        for j, row in enumerate(outsource):
            row = dict(row)
            pkey = row.pop('pkey', None)
            spkey = 'r_%i' % j
            result.setItem(spkey, Bag(row), _pkey=pkey)
        return result
            
    def out_selection(self, outsource, recordResolver=False, caption=False):
        """add???
           
        :param outsource: add???
        :param recordResolver: boolean. add???. Default value is ``False``
        :param caption: boolean. add???. Default value is ``False``
        :returns: add???
        """
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
            
    def out_grid(self, outsource, recordResolver=True):
        """add???
           
        :param outsource: add???
        :param recordResolver: boolean. add???. Default value is ``True``
        :returns: add???
        """
        return self.buildAsGrid(outsource, recordResolver)
        
    def buildAsGrid(self, outsource, recordResolver):
        """add???
           
        :param outsource: add???
        :param recordResolver: boolean. add???
        :returns: add???
        """
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
                                                   sqlContextName=self.sqlContextName)

            result.addItem('%s' % spkey, content, _pkey=spkey, _attributes=dict(row), _removeNullAttributes=False)
        return result

    def out_fullgrid(self, outsource, recordResolver=True):
        """add???
           
        :param outsource: add???
        :param recordResolver: boolean. add???. Default value is ``True``
        :returns: add???
        """
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
        """add???
           
        :param outsource: add???
        :returns: add???
        """
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
        """add???"""
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
        """add???
           
        :param outsource: add???
        :returns: add???
        """
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
        """add???
           
        :param outsource: add???
        :param filePath: boolean. add???. Default value is ``None``
        """
        from gnr.core.gnrxls import XlsWriter

        columns = [c for c in self.columns if not c in ('pkey', 'rowidx')]
        coltypes = dict([(k, v['dataType']) for k, v in self.colAttrs.items()])
        writer = XlsWriter(columns=columns, coltypes=coltypes, headers=self.colHeaders, filepath=filepath,
                           font='Times New Roman',
                           format_float='#,##0.00', format_int='#,##0')
        writer(data=outsource)

class SqlRelatedSelectionResolver(BagResolver):
    """add???"""
    classKwargs = {'cacheTime': 0, 'readOnly': True, 'db': None,
                   'columns': None, 'mode': None, 'sqlparams': None, 'joinConditions': None, 'sqlContextName': None,
                   'target_fld': None, 'relation_value': None, 'condition': None, 'bagFields': None}
                   
    def resolverSerialize(self):
        """add???"""
        attr = {}
        attr['resolvermodule'] = self.__class__.__module__
        attr['resolverclass'] = self.__class__.__name__
        attr['args'] = list(self._initArgs)
        attr['kwargs'] = dict(self._initKwargs)
        attr['kwargs'].pop('db')
        attr['kwargs']['_serialized_app_db'] = 'maindb'
        return attr

    def load(self):
        """add???"""
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
        return query.selection().output(self.mode, recordResolver=(self.mode == 'grid'))

class SqlRecord(object):
    """add???"""
    def __init__(self, dbtable, pkey=None, where=None,
                 lazy=None, eager=None, relationDict=None,
                 sqlparams=None,
                 ignoreMissing=False, ignoreDuplicate=False,
                 bagFields=True, for_update=False,
                 joinConditions=None, sqlContextName=None,
                 virtual_columns=None,
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

    def setJoinCondition(self, target_fld, from_fld, condition, one_one=False, **kwargs):
        """add???
        
        :param target_fld: add???
        :param from_fld: add???
        :param condition: add???
        :param one_one: boolean. add???. Default value is ``False``
        """
        cond = dict(condition=condition, one_one=one_one, params=kwargs)
        self.joinConditions['%s_%s' % (target_fld.replace('.', '_'), from_fld.replace('.', '_'))] = cond

    def output(self, mode, **kwargs):
        """add???
        
        :param mode: add???
        """
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
        """add???"""
        if self.where:
            where = self.where
        elif self.pkey is not None:
            where = '$pkey = :pkey'
        else:
            where = ' AND '.join(['t0.%s=:%s' % (k, k) for k in self.sqlparams.keys()])

        result = SqlQueryCompiler(self.dbtable.model, sqlparams=self.sqlparams,
                                  joinConditions=self.joinConditions,
                                  sqlContextName=self.sqlContextName).compiledRecordQuery(where=where,
                                                                                          relationDict=self.relationDict
                                                                                          ,
                                                                                          bagFields=self.bagFields,
                                                                                          for_update=self.for_update,
                                                                                          virtual_columns=self.virtual_columns
                                                                                          ,
                                                                                          **self.relmodes)
        return result

    def _get_result(self):
        if self._result is None:
            if not self.compiled.where:
                raise RecordSelectionError(
                        "Insufficient parameters for selecting a record: %s" % (self.dbtable.fullname, ))
            params = self.sqlparams
            if self.pkey is not None:
                params['pkey'] = self.pkey
                #raise '%s \n\n%s' % (str(params), str(self.compiled.get_sqltext(self.db)))
            cursor = self.db.execute(self.compiled.get_sqltext(self.db), params, dbtable=self.dbtable.fullname)
            data = cursor.fetchall()
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
                    self._result = data[0]
                else:
                    raise RecordDuplicateError(
                            "Found more than one record in table %s for selection %s %s" % (self.dbtable.fullname,
                                                                                            self.compiled.get_sqltext(
                                                                                                    self.db), params))
        return self._result

    result = property(_get_result)

    def out_newrecord(self, resolver_one=True, resolver_many=True):
        """add???
        
        :param resolver_one: boolean. add???. Default value is ``True``
        :param resolver_many: boolean. add???. Default value is ``True``
        """
        result = SqlRecordBag(self.db, self.dbtable.fullname)
        record = Bag()
        self._loadRecord(result, record, self.compiled.template, resolver_many=resolver_many, resolver_one=resolver_one)
        
        newdefaults = self.dbtable.defaultValues()
        for k, v in newdefaults.items():
            result[k] = v
        
        return result
        
    def out_bag(self, resolver_one=True, resolver_many=True):
        """add???
        
        :param resolver_one: boolean. add???. Default value is ``True``
        :param resolver_many: boolean. add???. Default value is ``True``
        """
        result = SqlRecordBag(self.db, self.dbtable.fullname)
        record = self.result
        if record != None:
            self._loadRecord(result, self.result, self.compiled.template, resolver_many=resolver_many,
                             resolver_one=resolver_one)
        return result
        
    def out_record(self):
        """add???"""
        result = Bag()
        record = self.result
        if record:
            self._loadRecord(result, record, self.compiled.template, resolver_many=False, resolver_one=False)
        return result
        
    def out_json(self):
        """add???"""
        return gnrstring.toJson(self.out_dict())
        
    def out_dict(self):
        """add???"""
        return dict([(str(k), self.result[v]) for k, v in self.compiled.dicttemplate.items()])
        
    def _loadRecord(self, result, sqlresult, template, resolver_one=None, resolver_many=None):
        for k, v, args in template.digest('#k,#v,#a'):
            dtype = args.get('dtype')
            info = dict(args)
            for lbl in ('as', 'foreignkey', 'default', 'basealias', 'case_insensitive', 'many_rel_name', 'one_rel_name',
                        'many_relation', 'one_relation'):
                info.pop(lbl, None)
            if isinstance(v, Bag):
                value = Bag()
                self._loadRecord(value, sqlresult, v, resolver_one=resolver_one, resolver_many=resolver_many)
                reltbl = self.db.table(args['one_relation'])
                nodecaption = self.dbtable.recordCaption(value)
                result.setItem(k, value, nodecaption=nodecaption, pkey=value[reltbl.pkey])
            elif v == 'DynItemMany':
                if resolver_many:
                    opkg, otbl, ofld = args['one_relation'].split('.')

                    info['_from_fld'] = args['one_relation']
                    info['_target_fld'] = args['many_relation']
                    info['_relation_value'] = sqlresult['%s_%s' % (args['basealias'], ofld)]

                    if resolver_many is True:
                        value = SqlRelatedSelectionResolver(
                                columns='*', db=self.db, cacheTime=-1,
                                target_fld=info['_target_fld'],
                                relation_value=info['_relation_value'],
                                mode='grid', joinConditions=self.joinConditions,
                                sqlContextName=self.sqlContextName
                                )
                    else:
                        value = None
                        info['_sqlContextName'] = self.sqlContextName
                        info['_resolver_name'] = resolver_many
                    result.setItem(k, value, info)

            elif v == 'DynItemOneOne':
                if resolver_one:
                    opkg, otbl, ofld = args['one_relation'].split('.')
                    info.pop('many_relation', None)
                    info['_from_fld'] = args['one_relation']
                    info['_target_fld'] = args['many_relation']
                    relation_value = sqlresult['%s_%s' % (args['basealias'], ofld)]

                    if resolver_one is True:
                        value = SqlRelatedRecordResolver(db=self.db, cacheTime=-1,
                                                         target_fld=info['_target_fld'],
                                                         relation_value=relation_value,
                                                         mode='bag',
                                                         bagFields=True,
                                                         ignoreMissing=True,
                                                         joinConditions=self.joinConditions,
                                                         sqlContextName=self.sqlContextName)
                    else:
                        value = None
                        info['_resolver_name'] = resolver_one
                        info['_sqlContextName'] = self.sqlContextName
                        info['_relation_value'] = relation_value
                    result.setItem(k, value, info)

            elif v == 'DynItemOne':
                if resolver_one:
                    mpkg, mtbl, mfld = args['many_relation'].split('.')

                    info.pop('many_relation', None)
                    info['_from_fld'] = args['many_relation']
                    info['_target_fld'] = args['one_relation']
                    relation_value = sqlresult['%s_%s' % (args['basealias'], mfld)]
                    rel_vc = None
                    if self.virtual_columns:
                        rel_vc = ','.join(
                                [vc.split('.', 1)[1] for vc in self.virtual_columns.split(',') if vc.startswith(k)])
                    if resolver_one is True:
                        value = SqlRelatedRecordResolver(db=self.db, cacheTime=-1,
                                                         target_fld=info['_target_fld'],
                                                         relation_value=relation_value,
                                                         mode='bag', virtual_columns=rel_vc,
                                                         bagFields=True,
                                                         ignoreMissing=True,
                                                         joinConditions=self.joinConditions,
                                                         sqlContextName=self.sqlContextName
                                                         )
                    else:
                        value = None
                        info['_resolver_name'] = resolver_one
                        info['_sqlContextName'] = self.sqlContextName
                        info['_auto_relation_value'] = mfld
                        info['_virtual_columns'] = rel_vc
                    result.setItem(k, value, info)
            else:
                if args.get('as'):
                #if args.get('as').startswith('t1'):
                #raise '%s \n\n%s' % (str(args), str(sqlresult))
                    value = sqlresult[args.get('as')]
                else:
                    value = v
                if dtype == 'X' and self.bagFields == True:
                    try:
                        md5value = value or ''
                        md5value = md5value.encode('utf8')
                        info['_bag_md5'] = hashlib.md5(md5value).hexdigest()
                        value = Bag(value)

                    except:
                        pass
                result.setItem(k, value, info)

class SqlRecordBag(Bag):
    """add???"""
    def __init__(self, db=None, tablename=None):
        Bag.__init__(self)
        self.db = db
        self.tablename = tablename
        self.isNew = True
        
    def save(self, **kwargs):
        """add???"""
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