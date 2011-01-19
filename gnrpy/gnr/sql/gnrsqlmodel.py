# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package            : GenroPy sql - see LICENSE for details
# module gnrsqlmodel : an advanced data storage system
# Copyright (c)      : 2004 - 2007 Softwell sas - Milano 
# Written by         : Giovanni Porcari, Francesco Cavazzana
#                      Saverio Porcari, Francesco Porcari
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
import logging

from gnr.core.gnrstring import boolean
from gnr.core.gnrbag import Bag, BagResolver
from gnr.core.gnrlang import moduleDict
from gnr.core.gnrstructures import GnrStructObj, GnrStructData
from gnr.sql.gnrsqlutils import SqlModelChecker, ModelExtractor
from gnr.sql.gnrsqltable import SqlTable
from gnr.sql.gnrsql_exceptions import GnrSqlMissingField, GnrSqlMissingTable,\
    GnrSqlMissingColumn, GnrSqlRelationError

import threading

logger = logging.getLogger('gnr.sql.gnrsql')

class NotExistingTableError(Exception):
    pass

class DbModel(object):
    def __init__(self, db):
        #self._db = weakref.ref(db)
        self.db = db
        self.src = DbModelSrc.makeRoot()
        self.obj = None
        self.relations = Bag()
        self._columnsWithRelations = {}
        self.mixins = Bag()


    def build(self):
        """Db startup operations:
        - prepares the GnrStructObj root
        - loads all relations from Db structure
        """

        def _doObjMixinConfig(objmix, pkgsrc):
            if hasattr(objmix, 'config_db'):
                objmix.config_db(pkgsrc)
            if hasattr(objmix, 'config_db_custom'):
                objmix.config_db_custom(pkgsrc)

        if 'tbl' in self.mixins:
            for pkg in self.mixins['tbl'].keys():
                pkgsrc = self.src['packages.%s' % pkg]
                for tblmix in self.mixins['tbl.%s' % pkg].values():
                    tblmix.db = self.db
                    _doObjMixinConfig(tblmix, pkgsrc)

        if 'pkg' in self.mixins:
            for pkg, pkgmix in self.mixins['pkg'].items():
                pkgsrc = self.src['packages.%s' % pkg]
                pkgmix.db = self.db
                _doObjMixinConfig(pkgmix, pkgsrc)

        sqldict = moduleDict('gnr.sql.gnrsqlmodel', 'sqlclass,sqlresolver')
        self.obj = DbModelObj.makeRoot(self, self.src, sqldict)

        for many_relation_tuple, relation in self._columnsWithRelations.items():
            oneCol = relation.pop('related_column')
            self.addRelation(many_relation_tuple, oneCol, **relation)
        self._columnsWithRelations.clear()

    def resolveAlias(self, name):
        pkg, tbl, col = name.split('.')
        pkg = self.obj[pkg]
        tbl = pkg.table(tbl)
        col = tbl.columns[col]
        return (pkg.name, tbl.name, col.name)

    def addRelation(self, many_relation_tuple, oneColumn, mode=None, one_one=None, onDelete=None, onDelete_sql=None,
                    onUpdate=None, onUpdate_sql=None, deferred=None, eager_one=None, eager_many=None, relation_name=None,
                    one_name=None, many_name=None, one_group=None, many_group=None, many_order_by=None):
        """ This method adds a relation in the current model.
            @param many_relation_tuple: the column of the "many table" as tuple. Eg. ('video','movie','director_id')
            @param oneColumn: the column of the "one table" as string. Eg. 'video.director.id'
            @param  one_name: the one_to_many relation's name. Eg. 'movies'
            @param  many_name: the many_to_one relation's name. Eg. 'director'
            @param mode: relation (dflt), insensitive, foreignkey
            @param eager_one: if True ('Y') the one_to_many relation is eager
            @param eager_many: if True ('Y') the many_to_one relation is eager
            @param onDelete: 'C:cascade' | 'I:ignore' | 'R:raise'
        """
        try:
            many_pkg, many_table, many_field = many_relation_tuple
            many_relation = '.'.join(many_relation_tuple)

            one_pkg, one_table, one_field = self.resolveAlias(oneColumn)
            one_relation = '.'.join((one_pkg, one_table, one_field))
            if not (many_field and one_field):
                logger.warning("pkg, table or field involved in the relation %s -> %s doesn't exist" % (
                many_relation, one_relation))
                return
            link_many_name = many_field
            relation_name = relation_name or '_'.join(many_relation_tuple)
            #if not  many_name:
            #     many_name = link_one_name
            #if not  one_name:
            #     one_name = link_many_name
            case_insensitive = (mode == 'insensitive')
            foreignkey = (mode == 'foreignkey')
            self.relations.setItem('%s.%s.@%s' % (many_pkg, many_table, link_many_name), None, mode='O',
                                   many_relation=many_relation, many_rel_name=many_name, foreignkey=foreignkey,
                                   many_order_by=many_order_by,
                                   one_relation=one_relation, one_rel_name=one_name, one_one=one_one, onDelete=onDelete,
                                   onDelete_sql=onDelete_sql,
                                   onUpdate=onUpdate, onUpdate_sql=onUpdate_sql, deferred=deferred,
                                   case_insensitive=case_insensitive, eager_one=eager_one, eager_many=eager_many,
                                   one_group=one_group, many_group=many_group)
            self.relations.setItem('%s.%s.@%s' % (one_pkg, one_table, relation_name), None, mode='M',
                                   many_relation=many_relation, many_rel_name=many_name, many_order_by=many_order_by,
                                   one_relation=one_relation, one_rel_name=one_name, one_one=one_one, onDelete=onDelete,
                                   onDelete_sql=onDelete_sql,
                                   onUpdate=onUpdate, onUpdate_sql=onUpdate_sql, deferred=deferred,
                                   case_insensitive=case_insensitive, eager_one=eager_one, eager_many=eager_many,
                                   one_group=one_group, many_group=many_group)
            #print 'The relation %s - %s was added'%(str('.'.join(many_relation_tuple)), str(oneColumn))
            self.checkRelationIndex(many_pkg, many_table, many_field)
            self.checkRelationIndex(one_pkg, one_table, one_field)
        except:
            logger.warning('The relation %s - %s cannot be added', str('.'.join(many_relation_tuple)), str(oneColumn))
            #print 'The relation %s - %s cannot be added'%(str('.'.join(many_relation_tuple)), str(oneColumn))

    def checkRelationIndex(self, pkg, table, column):
        tblobj = self.table(table, pkg=pkg)
        indexname = '%s_%s_key' % (table, column)
        if column != tblobj.pkey and not indexname in tblobj.indexes:
            tblobj.indexes.children[indexname] = DbIndexObj(parent=tblobj.indexes, attrs=dict(columns=column))

    def load(self, source=None):
        """Load the modelsrc from a xml source
        @param source: xml model (diskfile or text or url)
        """
        self.src.update(source)

    def importFromDb(self):
        exporter = ModelExtractor(self.db)
        root = DbModelSrc.makeRoot()
        exporter.extractModelSrc(root=root)
        self.src.update(root)

    def save(self, path):
        """save the current modelsrc as xml file at path
        @param path: the file path
        """
        self.src.save(path)


    def check(self, applyChanges=False):
        """This method verifies the compatibility between the database and the model.
        It saves sql statements that makes the database compatible with the model.
        @param applyChanges: if True applies the changes.
        """
        checker = SqlModelChecker(self.db)
        self.modelChanges = checker.checkDb()
        self.modelBagChanges = checker.bagChanges
        if applyChanges:
            self.applyModelChanges()
        return bool(self.modelChanges)

    def applyModelChanges(self):
        if self.modelChanges[0].startswith('CREATE DATABASE'):
            self.db.adapter.createDb()
            self.modelChanges.pop(0)
        for x in self.modelChanges:
            self.db.execute(x)
        self.db.commit()

    def _doMixin(self, path, obj):
        if self.db.started:
            raise ConfigureAfterStartError(path)
        self.mixins[path] = obj

    def packageMixin(self, pkg, obj):
        self._doMixin('pkg.%s' % pkg, obj)

    def tableMixin(self, tblpath, obj):
        self._doMixin('tbl.%s' % tblpath, obj)

    def package(self, pkg):
        """Returns a package object
        @param pkw: package name"""
        return self.obj[pkg]

    def table(self, tblname, pkg=None):
        """returns a table object
        @param table: table name
        @param pkg: package name"""
        if '.' in tblname:
            pkg, tblname = tblname.split('.')[:2]
        if pkg is None:
            raise ValueError(
                    "table() called with '%(tblname)s' instead of '<packagename>.%(tblname)s'" % {'tblname': tblname})
            #if pkg is None:
        #    pkg = self.obj.keys()[0]
        return self.obj[pkg].table(tblname)

    def column(self, colname):
        """returns a column object
        @param colname: colname name"""
        colpath = colname.split('.')
        if len(colpath) == 2:
            pkg = None
            tblname, colname = colpath
        else:
            pkg, tblname, colname = colpath
        return self.table(tblname, pkg=pkg).column(colname)


class DbModelSrc(GnrStructData):
    """
       this is a GnrStructData subclass of definition for the elements of a GenroDb
       TESTED in a_structure_load_test.py
    """

    def package(self, name, sqlschema=None,
                comment=None,
                name_short=None, name_long=None, name_full=None,
                **kwargs):
        """Add a package to the structure. Child of root.
        @param name: package name,
        @param comment: comment about package,
        @param name_short: name_short,
        @param name_long: name_long,
        @param name_full: name_full"""

        if not 'packages' in self: #if it is the first package it prepares the package_list packages
            self.child('package_list', 'packages')

        return self.child('package', 'packages.%s' % name,
                          comment=comment, sqlschema=sqlschema,
                          name_short=name_short, name_long=name_long,
                          name_full=name_full, **kwargs)

    def externalPackage(self, name):
        return self.root('packages.%s' % name)

    def table(self, name, pkey=None, lastTS=None, rowcaption=None,
              sqlname=None, sqlschema=None,
              comment=None,
              name_short=None, name_long=None, name_full=None,
              **kwargs):
        """Add a table to the structure. Child of package.
           @param name: table name,
           @param sqlschema
           @param comment: comment about table,
           @param name_short: name_short,
           @param name_long: name_long,
           @param name_full: name_full
           @param pkey
           """

        if not 'tables' in self:
            #if it is the first table it prepares the table_list tables
            self.child('table_list', 'tables')
        return self.child('table', 'tables.%s' % name, comment=comment,
                          name_short=name_short, name_long=name_long, name_full=name_full,
                          pkey=pkey, lastTS=lastTS, rowcaption=rowcaption, pkg=self.parentNode.label,
                          **kwargs)

    def column(self, name, dtype=None, size=None,
               default=None, notnull=None, unique=None, indexed=None,
               sqlname=None, comment=None,
               name_short=None, name_long=None, name_full=None,
               group=None, onInserting=None, onUpdating=None, onDeleting=None,
               **kwargs):
        """ insert a column into a table. Child of table.
         @param name: column name,
         @param dtype
         @param size: string, 'min:max' or fixed lenght 'len'
         @param comment: comment about column,
         @param sqlname
         @param name_short: name_short,
         @param name_long: name_long,
         @param name_full: name_full
         @param default
         @param notnull
         @param unique
         @param indexed
         @param group: group is a hierarchical path of logical categories and subacategories the columns belongs to.
                       If the group path starts with '_' the group is "reserved" (invisible).
                       If it starts with '*' it can be seen only from aministration tools.
         @param oninserting
         @param onupdating
         @param ondeleting
        """

        if '::' in name:
            name, dtype = name.split('::')
        if not 'columns' in self:
            self.child('column_list', 'columns')
        return self.child('column', 'columns.%s' % name, dtype=dtype, size=size,
                          comment=comment, sqlname=sqlname,
                          name_short=name_short, name_long=name_long, name_full=name_full,
                          default=default, notnull=notnull, unique=unique, indexed=indexed,
                          group=group, onInserting=onInserting, onUpdating=onUpdating, onDeleting=onDeleting,
                          **kwargs)

    def virtual_column(self, name, relation_path=None, sql_formula=None, py_method=None, **kwargs):
        """ insert a related column alias into a table. Child of table.
            @param name: alias name,
            @param alias: path of related column
        """
        if '::' in name: name, dtype = name.split('::')
        if not 'virtual_columns' in self:
            self.child('virtual_columns_list', 'virtual_columns')
        return self.child('virtual_column', 'virtual_columns.%s' % name,
                          relation_path=relation_path,
                          sql_formula=sql_formula, py_method=py_method,
                          virtual_column=True, **kwargs)

    def aliasColumn(self, name, relation_path, **kwargs):
        return self.virtual_column(name, relation_path=relation_path, **kwargs)

    def formulaColumn(self, name, sql_formula, dtype='A', **kwargs):
        return self.virtual_column(name, sql_formula=sql_formula, dtype=dtype, **kwargs)

    def pyColumn(self, name, py_method, **kwargs):
        return self.virtual_column(name, py_method=py_method, **kwargs)

    def aliasTable(self, name, relation_path, **kwargs):
        """ insert a related table alias into a table. Child of table.
            @param name: alias name,
            @param alias: path of related table
        """
        if '::' in name: name, dtype = name.split('::')
        if not 'table_aliases' in self:
            self.child('tblalias_list', 'table_aliases')
        return self.child('table_alias', 'table_aliases.@%s' % name, relation_path=relation_path, **kwargs)

    table_alias = aliasTable

    def index(self, columns=None, name=None, unique=None):
        """Add an index to a column. self must be a column src or an index_list
        @param columns: list, or tuple, or string separated by commas
        @param name: index name
        @unique param: unicity bound"""
        if isinstance(columns, list) or isinstance(columns, tuple):
            columns = ','.join(columns)
        if not name:
            name = "%s_%s_key" % (self.parentNode.label, columns.replace(',', '_'))
        if not 'indexes' in self:
            self.child('index_list', 'indexes')

        child = self.child('index', 'indexes.%s' % name, columns=columns, unique=unique)
        return child

    def relation(self, related_column, mode='relation', one_name=None,
                 many_name=None, eager_one=None, eager_many=None, one_one=None, child=None,
                 one_group=None, many_group=None, onUpdate=None, onUpdate_sql=None, onDelete=None,
                 onDelete_sql=None, deferred=None, relation_name=None, **kwargs):
        """ This method adds a relation in the current model.
            @param many_relation_tuple: the column of the "many table" as tuple. Eg. ('video','movie','director_id')
            @param oneColumn: the column of the "one table" as string. Eg. 'video.director.id'
            @param  one_name: the one_to_many relation's name. Eg. 'movies'
            @param  many_name: the many_to_one relation's name. Eg. 'director'
            @param mode: relation (dflt), insensitive, foreignkey
            @param eager_one: if True ('Y') the one_to_many relation is eager
            @param eager_many: if True ('Y') the many_to_one relation is eager
            @param onDelete: 'C:cascade' | 'I:ignore' | 'R:raise'
            @param onUpdate:
            @param onUpdate_sql:
            @param onDelete:
            @param onDelete_sql:
            @param deferred:
            @param relation_name:
        """
        if one_one and isinstance(one_one,basestring):
            rc = related_column.split('.')
            fromTableNode = self.parent.parent.parentNode
            fromTableName = fromTableNode.label
            fromPkg = fromTableNode.getAttr('pkg')
            if len(rc)==2:
                table,externalKey = rc
                pkg = fromPkg
            else:
                pkg,table,externalKey = rc
            fromColumn = self.parentNode.label
            fromColumnNameLong = self.parentNode.attr.get('name_long')
            relation_path='@%s_%s_%s.%s' %(fromPkg,fromTableName,fromColumn,externalKey)
            self.externalPackage(pkg).table(table).aliasColumn(one_one,relation_path=relation_path,name_long=fromColumnNameLong)
            one_one=True
        return self.setItem('relation', self.__class__(), related_column=related_column, mode=mode,
                            one_name=one_name, many_name=many_name, one_one=one_one, child=child,
                            one_group=one_group, many_group=many_group, deferred=deferred, onUpdate=onUpdate,
                            onDelete=onDelete,
                            eager_one=eager_one, eager_many=eager_many, onUpdate_sql=onUpdate_sql,
                            onDelete_sql=onDelete_sql, relation_name=relation_name,
                            **kwargs)

class DbModelObj(GnrStructObj):
    """Base class for all the StructObj in this module"""

    def init(self):
        self._dbroot = self.root.rootparent.db

        mixpath = self._getMixinPath()
        mixobj = self._getMixinObj()
        if mixpath:
            mixobj.mixin(self.db.model.mixins[mixpath], attributes='_plugins')
        mixin = self.attributes.get('mixin')
        if mixin:
            if not ':' in mixin:
                mixin = '%s:%s' % (self.module.__module__, mixin)
            mixobj.mixin(mixin)
        self.doInit()

    def _getMixinPath(self):
        return None

    def _getMixinObj(self):
        return self

    def doInit(self):
        pass

    def _get_dbroot(self):
        return self._dbroot

    dbroot = property(_get_dbroot)
    db = dbroot

    def _get_adapter(self):
        return self.dbroot.adapter

    adapter = property(_get_adapter)

    def _get_sqlname(self):
        return self.attributes.get('sqlname', self.name)

    sqlname = property(_get_sqlname)

    def _set_name_short(self, name):
        self.attributes['name_short'] = name

    def _get_name_short(self):
        return self.attributes.get('name_short', self.attributes.get('name_long', self.name))

    name_short = property(_get_name_short, _set_name_short)

    def _set_name_long(self, name):
        self.attributes['name_long'] = name

    def _get_name_long(self):
        return self.attributes.get('name_long', self.name_short)

    name_long = property(_get_name_long, _set_name_long)

    def _set_name_full(self, name):
        self.attributes['name_full'] = name

    def _get_name_full(self):
        return self.attributes.get('name_full', self.name_long)

    name_full = property(_get_name_full, _set_name_full)

    def getTag(self):
        return self.sqlclass or self._sqlclass

    def getAttr(self, attr=None, dflt=None):
        if attr:
            return self.attributes.get(attr, dflt)
        else:
            return self.attributes


class DbPackageObj(DbModelObj):
    sqlclass = "package"

    def _getMixinPath(self):
        return 'pkg.%s' % self.name

    def _get_tables(self):
        """property. Returns a SqlTableList"""
        return self['tables'] or {} #temporary FIX

    tables = property(_get_tables)

    def dbtable(self, name):
        """returns a table
        @params name: table's name"""
        return self.table(name).dbtable

    def table(self, name):
        """returns a table
        @params name: table's name"""
        table = self['tables.%s' % name]
        if table is None:
            raise GnrSqlMissingTable("Table '%s' undefined in package: '%s'" % (name, self.name))
        return table

    def tableSqlName(self, tblobj):
        """return the name of the given SqlTable
        @param tblobj: an instance of SqlTable"""
        sqlprefix = self.attributes.get('sqlprefix')
        if sqlprefix == '':
            return tblobj.name
        else:
            return '%s_%s' % (sqlprefix or self.name, tblobj.name)


    def _get_sqlschema(self):
        return self.attributes.get('sqlschema', self.dbroot.main_schema)

    sqlschema = property(_get_sqlschema)


class DbTableObj(DbModelObj):
    sqlclass = 'table'

    def doInit(self):
        self.dbtable.onIniting()
        self._sqlnamemapper = {}
        self._indexedColumn = {}
        self._fieldTriggers = {}
        self.allcolumns = []
        self.dbtable.onInited()

    def afterChildrenCreation(self):
        objclassdict = self.root.objclassdict
        if not self.columns:
            self.children['columns'] = objclassdict['column_list'](parent=self)
        if not self.indexes:
            self.children['indexes'] = objclassdict['index_list'](parent=self)
        if not self.virtual_columns:
            self.children['virtual_columns'] = objclassdict['virtual_columns_list'](parent=self)
        if not self.table_aliases:
            self.children['table_aliases'] = objclassdict['tblalias_list'](parent=self)
        indexesobj = self.indexes
        for colname, indexargs in self._indexedColumn.items():
            indexname = "%s_%s_key" % (self.name, indexargs['columns'].replace(',', '_'))
            indexesobj.children[indexname] = objclassdict['index'](parent=self.indexes, attrs=indexargs)

        if not self.relations:
            self.children['relations'] = self.newRelationResolver()

    def newRelationResolver(self, **kwargs):
        child_kwargs = {'main_tbl': '%s.%s' % (self.pkg.name, self.name),
                        'tbl_name': self.name,
                        'pkg_name': self.pkg.name}
        child_kwargs.update(kwargs)
        relationTree = RelationTreeResolver(**child_kwargs)
        relationTree.setDbroot(self.dbroot)
        return relationTree


    def _getMixinPath(self):
        return 'tbl.%s.%s' % (self.pkg.name, self.name)

    def _getMixinObj(self):
        self.dbtable = SqlTable(self)
        return self.dbtable

    def _get_pkg(self):
        """property. Returns the SqlPackage that contains the current table"""
        return self.parent.parent

    pkg = property(_get_pkg)


    def _get_fullname(self):
        """property. Returns the absolute table's name"""
        return '%s.%s' % (self.pkg.name, self.name)

    fullname = property(_get_fullname)

    def _get_name_plural(self):
        """property. Returns the absolute table's name"""
        return self.attributes.get('name_plural') or self.name_long

    name_plural = property(_get_name_plural)

    def _get_sqlschema(self):
        """property. Returns the sqlschema"""
        return self.attributes.get('sqlschema', self.pkg.sqlschema)

    sqlschema = property(_get_sqlschema)

    def _get_sqlname(self):
        """property. Returns the table's sqlname"""
        sqlname = self.attributes.get('sqlname')
        if not sqlname:
            sqlname = self.pkg.tableSqlName(self)
        return sqlname

    sqlname = property(_get_sqlname)

    def _get_sqlfullname(self):
        """property. Returns the table's sqlfullname"""
        return '%s.%s' % (self.sqlschema, self.sqlname)

    sqlfullname = property(_get_sqlfullname)

    def _get_sqlnamemapper(self):
        return self._sqlnamemapper

    sqlnamemapper = property(_get_sqlnamemapper)

    def _get_pkey(self):
        """property. Returns the table's pkey"""
        return self.attributes.get('pkey', '')

    pkey = property(_get_pkey)

    def _get_lastTS(self):
        """property. Returns the table's pkey"""
        return self.attributes.get('lastTS', '')

    lastTS = property(_get_lastTS)

    def _get_logicalDeletionField(self):
        """property. Returns the table's logicalDeletionField"""
        return self.attributes.get('logicalDeletionField', '')

    logicalDeletionField = property(_get_logicalDeletionField)

    def _get_noChangeMerge(self):
        """property. set noChangeMerge to True to avoid automatic merge of concurrent non conflicting changes"""
        return self.attributes.get('noChangeMerge', '')

    noChangeMerge = property(_get_noChangeMerge)


    def _get_rowcaption(self):
        """property. Returns the table's rowcaption"""
        return self.attributes.get('rowcaption', self.pkey)

    rowcaption = property(_get_rowcaption)

    def _get_queryfields(self):
        """property. Returns the table's queryfields"""
        return self.attributes.get('queryfields', None)

    queryfields = property(_get_queryfields)

    def _get_columns(self):
        """Returns an SqlColumnList"""
        return self['columns']

    columns = property(_get_columns)

    def _get_indexes(self):
        """Returns an SqlIndexedList"""
        return self['indexes']

    indexes = property(_get_indexes)

    def _get_relations(self):
        return self['relations']

    relations = property(_get_relations)

    def _get_virtual_columns(self):
        """Returns a DbColAliasListObj"""
        return self['virtual_columns']

    virtual_columns = property(_get_virtual_columns)

    def _get_table_aliases(self):
        """Returns an DbTblAliasListObj"""
        return self['table_aliases']

    table_aliases = property(_get_table_aliases)

    def column(self, name):
        """Returns a column object or None if it doesn't exists.
        @param name: A column's name or a relation path starting from the current table.
        Eg:@director_id.name
        """
        col = None
        colalias = None
        if name.startswith('$'):
            name = name[1:]
        if not name.startswith('@'):
            col = self['columns.%s' % name]
            if col == None:
                colalias = self['virtual_columns.%s' % name]
                if colalias != None:
                    if colalias.relation_path:
                        name = colalias.relation_path
                    elif colalias.sql_formula:
                        col = colalias
                    elif colalias.py_method:
                        col = colalias
                    else:
                        raise GnrSqlMissingColumn('Invalid column %s in table %s' % (name, self.name_full))
        if name.startswith('@'):
            relcol = self._relatedColumn(name)
            if colalias is not None and 'virtual_column' in relcol.attributes:
                mixedattributes = dict(relcol.attributes)
                colalias_attributes = dict(colalias.attributes)
                colalias_attributes.pop('tag')
                colalias_attributes.pop('relation_path')
                mixedattributes.update(colalias_attributes)
                col = relcol
                col.attributes = mixedattributes
            else:
                col = relcol
            #if col == None:
        #    raise 'Missing column %s' % name
        return col

    def _relatedColumn(self, fieldpath):
        """Returns a column object corresponding to the relation path
        @param fieldpath: ex "@member_id.name"
        """
        relpath = fieldpath.split('.')
        firstrel = relpath.pop(0)
        attrs = self.relations.getAttr(firstrel)
        if not attrs:
            tblalias = self['table_aliases.%s' % firstrel]
            if tblalias == None:
                #from gnr.sql.gnrsql import GnrSqlBadRequest
                #raise GnrSqlBadRequest('Missing field %s' % fieldpath )
                raise GnrSqlMissingField('Missing field %s' % fieldpath)
            else:
                relpath = tblalias.relation_path.split(
                        '.') + relpath # set the alias table relation_path in the current path
                reltbl = self
        else:
            joiner = attrs['joiner'][0]
            if joiner['mode'] == 'O':
                relpkg, reltbl, relfld = joiner['one_relation'].split('.')
            else:
                relpkg, reltbl, relfld = joiner['many_relation'].split('.')
            reltbl = self.dbroot.package(relpkg).table(reltbl)

        return reltbl.column('.'.join(relpath))

    def fullRelationPath(self, name):
        """Returns the full relation path to the given column
        @param fieldpath: ex "@member_id.name"
        """
        if name.startswith('$'):
            name = name[1:]
        if not name.startswith('@') and not name in self['columns'].keys():
            colalias = self['virtual_columns.%s' % name]
            if colalias != None:
                if colalias.relation_path:
                    name = colalias.relation_path
        if name.startswith('@'):
            rel, pathlist = name.split('.', 1)
            if 'table_aliases' in self and rel in self['table_aliases']:
                relpath = self['table_aliases.%s' % rel].relation_path
                rel, pathlist = ('%s.%s' % (relpath, pathlist)).split('.', 1)

            reltbl = self.column(rel[1:]).relatedTable()
            return '%s.%s' % (rel, reltbl.fullRelationPath(pathlist))
        else:
            return name


    def resolveRelationPath(self, relpath):
        if relpath in self.relations:
            return relpath # it is a real relation path with no aliases

        relpath = relpath.split('.')
        firstrel = relpath.pop(0)

        attrs = self.relations.getAttr(firstrel)
        if not attrs:
            tblalias = self['table_aliases.%s' % firstrel]
            if tblalias == None:
                raise GnrSqlRelationError('Cannot find %s in %s' % (tblalias, self.name))
            else:
                relpath = tblalias.relation_path.split(
                        '.') + relpath # set the alias table relation_path in the current path
                return self.resolveRelationPath('.'.join(relpath))
        else:
            joiner = attrs['joiner'][0]
            if joiner['mode'] == 'O':
                relpkg, reltbl, relfld = joiner['one_relation'].split('.')
            else:
                relpkg, reltbl, relfld = joiner['many_relation'].split('.')
            reltbl = self.dbroot.package(relpkg).table(reltbl)
            return '%s.%s' % (firstrel, reltbl.resolveRelationPath('.'.join(relpath)))


    def _get_relations_one(self):
        """This method returns a bag containing all the ManyToOne relations that point to the current table"""
        result = Bag()
        for k, joiner in self.relations.digest('#k,#a.joiner'):
            if joiner and joiner[0]['mode'] == 'O':
                r = joiner[0]
                result[r['many_relation'].split('.')[-1]] = r['one_relation']
        return result

    relations_one = property(_get_relations_one)

    def _get_relations_many(self):
        """This method returns a bag containing all the OneToMany relations that starts from to the current table"""
        result = Bag()
        for k, joiner in self.relations.digest('#k,#a.joiner'):
            if joiner and joiner[0]['mode'] == 'M':
                rel = joiner[0]
                result.setItem(rel['many_relation'].replace('.', '_'), rel['one_relation'].split('.')[-1], rel)
        return result

    relations_many = property(_get_relations_many)

    def _get_relatingColumns(self):
        """This method returns a list of columns that joins to the primary key of the table"""
        return self.relations_many.digest('#a.many_relation')

    relatingColumns = property(_get_relatingColumns)

    def getRelation(self, relpath):
        joiner = self.relations.getAttr(relpath, 'joiner')
        if joiner:
            joiner = joiner[0]
            return {'many': joiner['many_relation'], 'one': joiner['one_relation']}

    def getRelationBlock(self, relpath):
        joiner = self.relations.getAttr(relpath, 'joiner')[0]
        mpkg, mtbl, mfld = joiner['many_relation'].split('.')
        opkg, otbl, ofld = joiner['one_relation'].split('.')
        return dict(mode=joiner['mode'], mpkg=mpkg, mtbl=mtbl, mfld=mfld, opkg=opkg, otbl=otbl, ofld=ofld)

class DbBaseColumnObj(DbModelObj):
    def _get_dtype(self):
        """property. Returns the data type"""
        return self.attributes.get('dtype', 'T')

    dtype = property(_get_dtype)

    def _get_isReserved(self):
        #DUBBIO qui nome cammello
        """property. Returns the attribute reserved"""
        return self.attributes.get('group', '').startswith('_')

    isReserved = property(_get_isReserved)

    def _get_readonly(self):
        """property. Returns the attribute readonly"""
        return (self.attributes.get('readonly', 'N').upper() == 'Y')

    readonly = property(_get_readonly)

    def _get_pkg(self):
        """property. Returns the SqlPackage"""
        return self.parent.parent.pkg

    pkg = property(_get_pkg)

    def _get_table(self):
        """property. Returns the SqlTable"""
        return self.parent.parent

    table = property(_get_table)

    def _get_sqlschema(self):
        """property. Returns the sqlschema"""
        return 'sqlschema', self.table.sqlschema

    sqlschema = property(_get_sqlschema)

    def _get_sqlfullname(self):
        """property. Returns the sqlfullname"""
        return '%s.%s' % (self.table.sqlfullname, self.sqlname)

    sqlfullname = property(_get_sqlfullname)

    def _get_fullname(self):
        """property. Returns the fullname"""
        return '%s.%s' % (self.table.fullname, self.name)

    fullname = property(_get_fullname)

    def _set_print_width(self, size):
        self.attributes['print_width'] = size

    def _get_print_width(self):
        if not 'print_width' in self.attributes:
            self.attributes['print_width'] = self.table.dbtable.getColumnPrintWidth(self)
        return self.attributes['print_width']

    print_width = property(_get_print_width, _set_print_width)

class DbColumnObj(DbBaseColumnObj):
    sqlclass = 'column'

    def _captureChildren(self, children):
        self.column_relation = children['relation']
        return False

    def doInit(self):
        if not self.attributes.get('dtype'):
            if self.attributes.get('size'):
                self.attributes['dtype'] = 'A'
            else:
                self.attributes['dtype'] = 'T'
        attributes_mixin_handler = getattr(self.pkg, 'custom_type_%s' % self.attributes['dtype'], None)
        if attributes_mixin_handler:
            attributes_mixin = dict(attributes_mixin_handler())
            self.attributes['dtype'] = attributes_mixin.pop('dtype')
            attributes_mixin.update(self.attributes)
            self.attributes = attributes_mixin
        self.table.sqlnamemapper[self.name] = self.sqlname
        column_relation = self.structnode.value['relation']
        if column_relation is not None:
            reldict = dict(column_relation.attributes)
            related_column = reldict['related_column'].split('.')
            if len(related_column) == 2:
                reldict['related_column'] = '.'.join([self.pkg.name] + related_column)
            self.dbroot.model._columnsWithRelations[(self.pkg.name, self.table.name, self.name)] = reldict
        indexed = boolean(self.attributes.get('indexed'))
        unique = boolean(self.attributes.get('unique'))
        if indexed or unique:
            self.table._indexedColumn[self.name] = {'columns': self.name, 'unique': unique}

        for trigType in ('onInserting', 'onUpdating', 'onDeleting'):
            trigFunc = self.attributes.get(trigType)
            if trigFunc:
                self.table._fieldTriggers.setdefault(trigType, []).append((self.name, trigFunc))

    def relatedTable(self):
        """Get the SqlTable that is related by the current column"""
        r = self.table.relations.getAttr('@%s' % self.name)
        if r:
            r = r['joiner'][0]
            return self.dbroot.model.table(r['one_relation'])


    def relatedColumn(self):
        """Get the SqlColumn that is related by the current column"""
        r = self.table.relations.getAttr('@%s' % self.name)
        if r:
            r = r['joiner'][0]
            return self.dbroot.model.column(r['one_relation'])

    def relatedColumnJoiner(self):
        """Get the SqlTable that is related by the current column"""
        r = self.table.relations.getAttr('@%s' % self.name)
        if r:
            return r['joiner'][0]

class DbVirtualColumnObj(DbBaseColumnObj):
    sqlclass = 'virtual_column'

    def _get_relation_path(self):
        """property. Returns the relation_path"""
        return self.attributes.get('relation_path')

    relation_path = property(_get_relation_path)

    def _get_sql_formula(self):
        """property. Returns the sql_formula"""
        return self.attributes.get('sql_formula')

    sql_formula = property(_get_sql_formula)

    def _get_py_method(self):
        """property. Returns the py_method"""
        return self.attributes.get('py_method')

    py_method = property(_get_py_method)

    def _get_readonly(self):
        """property. Returns the attribute readonly"""
        return True

    readonly = property(_get_readonly)

    def relatedColumn(self):
        pass

class DbTableAliasObj(DbModelObj):
    sqlclass = 'table_alias'

    def _get_relation_path(self):
        """property. Returns the relation_path"""
        return self.attributes['relation_path']

    relation_path = property(_get_relation_path)

class DbTblAliasListObj(DbModelObj):
    sqlclass = "tblalias_list"

class DbColAliasListObj(DbModelObj):
    sqlclass = "virtual_columns_list"

class DbColumnListObj(DbModelObj):
    sqlclass = "column_list"

class DbIndexListObj(DbModelObj):
    sqlclass = "index_list"

class DbPackageListObj(DbModelObj):
    sqlclass = "package_list"

class DbTableListObj(DbModelObj):
    sqlclass = "table_list"


class DbIndexObj(DbModelObj):
    sqlclass = "index"

    def _get_sqlname(self):
        return self.attributes.get('sqlname',
                                   '%s_%s_idx' % (self.table.sqlname, self.getAttr('columns').replace(',', '_')))

    sqlname = property(_get_sqlname)

    def _get_table(self):
        return self.parent.parent

    table = property(_get_table)


class RelationTreeResolver(BagResolver):
    classKwargs = {'cacheTime': 0,
                   'readOnly': True,
                   'main_tbl': None,
                   'tbl_name': None,
                   'pkg_name': None,
                   'path': None,
                   'parentpath': None
    }

    def __init__(self, *args, **kwargs):
        self._lock = threading.RLock()
        self.__fields = None
        super(RelationTreeResolver, self).__init__(*args, **kwargs)

    def resolverSerialize(self):
        args = list(self._initArgs)
        kwargs = dict(self._initKwargs)
        #kwargs.pop('dbroot')
        kwargs['_serialized_app_handler'] = 'maindb'
        #lbl = kwargs.pop('autoRelate', None)
        #if lbl:
        #kwargs[lbl] = '@'+lbl

        return BagResolver.resolverSerialize(self, args=args, kwargs=kwargs)

    def setDbroot(self, dbroot):
        self.dbroot = dbroot

    def load(self):
        self.main_table_obj = self.dbroot.model.table(self.main_tbl)
        if not self.__fields:
            self._lock.acquire()
            self.__fields = self._fields(self.tbl_name, self.pkg_name, self.path, self.parentpath)
            self._lock.release()
        return self.__fields

    def _fields(self, table, pkg_name, path=None, parentpath=None):
        path = path or []
        parentpath = parentpath or []
        if parentpath:
            tbltuple = tuple(parentpath)
        else:
            tbltuple = ('%s_%s' % (pkg_name, table),)
        if path:
            prfx = []
            for p in path:
                if p == '*O':
                    pass
                elif p == '*M':
                    pass
                elif p == '*m':
                    pass
                else:
                    if p.startswith('%s_' % self.pkg_name):
                        p = p[len(self.pkg_name) + 1:]
                    prfx.append(p)
            prfx = '_'.join(prfx)
        else:
            prfx = None
        tableFullName = '%s_%s' % (pkg_name, table)
        result = Bag()
        result.tbl_name = table
        result.pkg_name = pkg_name

        cols = self.dbroot.package(pkg_name).table(table)['columns'].values()
        relations = self.dbroot.model.relations('%s.%s' % (pkg_name, table))
        onerels = []
        manyrels = []
        if relations:
            onerels = [(lbl, a, a['many_relation'].replace('.', '_'))
                       for lbl, a in relations.digest('#k,#a') if a['mode'] == 'O'
            ]
            manyrels = [(lbl, a, a['many_relation'].replace('.', '_'))
                        for lbl, a in relations.digest('#k,#a') if a['mode'] == 'M'
            ]
        for col in cols:
            fullname = '%s_%s_%s' % (pkg_name, table, col.name)
            result.setItem(col.name, None, col.attributes, prfx=prfx, table=table, pkg=pkg_name)
            relToExpand = (None, None)
            for lbl, relpars, relcol in onerels:
                if fullname == relcol:
                    relToExpand = (lbl, relpars)
                    break
            lbl, relpars = relToExpand
            if lbl:
                un_sch, un_tbl = relpars['one_relation'].split('.')[:2]
                un_schtbl = '%s_%s' % (un_sch, un_tbl)
                #if not un_schtbl in path:                    
                child_kwargs = {'main_tbl': self.main_tbl,
                                'tbl_name': un_tbl,
                                'pkg_name': un_sch,
                                'path': path + ['*O', un_schtbl],
                                'parentpath': parentpath + [col],
                                'cacheTime': self.cacheTime
                }
                child = RelationTreeResolver(**child_kwargs)
                child.setDbroot(self.dbroot)
                result.setItem(lbl, child, col.attributes,
                               joiner=[relpars]) #relpars deve essere una lista???? gardare in getalias sqldata

        for label, relpars, relcol in manyrels:
            sch, tbl, col = relpars['many_relation'].split('.')
            schtbl = '%s_%s' % (sch, tbl)
            if (len(cols) == 1 and cols[0].endswith('_id')):
                relmode = '*M'
            else:
                relmode = '*m'
            child_kwargs = {'main_tbl': self.main_tbl,
                            'tbl_name': tbl,
                            'pkg_name': sch,
                            'path': path + [relmode, schtbl],
                            'parentpath': parentpath + [col],
                            'cacheTime': self.cacheTime}
            child = RelationTreeResolver(**child_kwargs)
            child.setDbroot(self.dbroot)
            result.setItem(label, child, joiner=[relpars])
        return result


class ModelSrcResolver(BagResolver):
    classKwargs = {'cacheTime': 300, 'readOnly': False, 'dbroot': None}
    classArgs = ['dbId']

    def load(self):
        return self.dbroot.model.src

    def resolverSerialize(self):
        args = list(self._initArgs)
        kwargs = dict(self._initKwargs)
        kwargs.pop('dbroot')
        return BagResolver.resolverSerialize(self, args=args, kwargs=kwargs)

class ConfigureAfterStartError(Exception):
    pass

if __name__ == '__main__':
    main()

