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
from gnr.core.gnrdecorator import extract_kwargs
from gnr.core.gnrbag import Bag, BagResolver
from gnr.core.gnrlang import moduleDict
from gnr.core.gnrstructures import GnrStructObj, GnrStructData
from gnr.sql.gnrsqlutils import SqlModelChecker, ModelExtractor
from gnr.sql.gnrsqltable import SqlTable
from gnr.sql.gnrsql_exceptions import GnrSqlMissingField, GnrSqlMissingTable,\
    GnrSqlMissingColumn, GnrSqlRelationError

import threading

logger = logging.getLogger(__name__)

class NotExistingTableError(Exception):
    pass
    
class DbModel(object):
    """TODO"""
    def __init__(self, db):
        #self._db = weakref.ref(db)
        self.db = db
        self.src = DbModelSrc.makeRoot()
        self.obj = None
        self.relations = Bag()
        self._columnsWithRelations = {}
        self.mixins = Bag()
        
    @property
    def debug(self):
        """TODO"""
        return self.db.debug
        
    def build(self):
        """Database startup operations:
        
        * prepare the GnrStructObj root
        * load all relations from Db structure
        """
        
        def _doObjMixinConfig(objmix, pkgsrc):
            if hasattr(objmix, 'config_db'):
                objmix.config_db(pkgsrc)
            for pkg_id in self.db.application.packages.keys():
                config_from_pkg = getattr(objmix,'config_db_%s'%pkg_id,None)
                if config_from_pkg:
                    config_from_pkg(pkgsrc)
            if hasattr(objmix, 'config_db_custom'):
                objmix.config_db_custom(pkgsrc)
                
        if 'tbl' in self.mixins:
            for pkg in self.mixins['tbl'].keys():
                pkgsrc = self.src['packages.%s' % pkg]
                tables=self.mixins['tbl.%s' % pkg]
                tablenames=tables.keys()
                tablenames.sort()
                for tblname in tablenames:
                    tblmix=tables[tblname]
                    tblmix.db = self.db
                    tblmix._tblname = tblname
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
        """TODO
        
        :param name: TODO
        :returns: TODO
        """
        pkg, tbl, col = name.split('.')
        pkg = self.obj[pkg]
        tbl = pkg.table(tbl)
        col = tbl.columns[col]
        return (pkg.name, tbl.name, col.name)
       
    @extract_kwargs(resolver=True) 
    def addRelation(self, many_relation_tuple, oneColumn, mode=None,storename=None, one_one=None, onDelete=None, onDelete_sql=None,
                    onUpdate=None, onUpdate_sql=None, deferred=None, eager_one=None, eager_many=None, relation_name=None,
                    one_name=None, many_name=None, one_group=None, many_group=None, many_order_by=None,storefield=None,
                    resolver_kwargs=None):
        """Add a relation in the current model.
        
        :param many_relation_tuple: tuple. The column of the "many table". e.g: ('video','movie','director_id')
        :param oneColumn: string. The column of the "one table". e.g: 'video.director.id'
        :param mode: string. The method's mode. You can choose between:
                     
                     * 'relation': default mode. It defines a purely logical and case-sensitive relation:
                       there is no referential integrity check
                     * 'foreignkey': the relation becomes a SQL relation
                     * 'insensitive': same features of the ``mode='relation'`` but the relation
                       is *case-insensitive*
                       
        :param one_one: TODO
        :param onDelete: 'C:cascade' | 'I:ignore' | 'R:raise'
        :param onDelete_sql: TODO
        :param onUpdate: TODO
        :param onUpdate_sql: TODO
        :param deferred: the same of the sql "DEFERRED". For more information, check the
                         :ref:`sql_deferred` section
        :param eager_one: boolean. If ``True`` ('Y') the one_to_many relation is eager
        :param eager_many: boolean. If ``True`` ('Y') the many_to_one relation is eager
        :param relation_name: string. An attribute of the :ref:`table_relation`. It allows
                              to estabilish an alternative string for the :ref:`inverse_relation`.
                              For more information, check the :ref:`relation_name` section
        :param one_name: the one_to_many relation's name. e.g: 'movies'
        :param many_name: the many_to_one relation's name. e.g: 'director'
        :param one_group: TODO
        :param many_group: TODO
        :param many_order_by: TODO"""
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
            default_relation_name = many_table if one_one=='*' else '_'.join(many_relation_tuple)
            relation_name = relation_name or default_relation_name
            #if not  many_name:
            #     many_name = link_one_name
            #if not  one_name:
            #     one_name = link_many_name
            case_insensitive = (mode == 'insensitive')
            foreignkey = (mode == 'foreignkey')
            self.relations.setItem('%s.%s.@%s' % (many_pkg, many_table, link_many_name), None, mode='O',
                                   many_relation=many_relation, many_rel_name=many_name, foreignkey=foreignkey,
                                   many_order_by=many_order_by,relation_name=relation_name,
                                   one_relation=one_relation, one_rel_name=one_name, one_one=one_one, onDelete=onDelete,
                                   onDelete_sql=onDelete_sql,
                                   onUpdate=onUpdate, onUpdate_sql=onUpdate_sql, deferred=deferred,
                                   case_insensitive=case_insensitive, eager_one=eager_one, eager_many=eager_many,
                                   one_group=one_group, many_group=many_group,storefield=storefield,_storename=storename,
                                   resolver_kwargs=resolver_kwargs)
            self.relations.setItem('%s.%s.@%s' % (one_pkg, one_table, relation_name), None, mode='M',
                                   many_relation=many_relation, many_rel_name=many_name, many_order_by=many_order_by,
                                   one_relation=one_relation, one_rel_name=one_name, one_one=one_one, onDelete=onDelete,
                                   onDelete_sql=onDelete_sql,
                                   onUpdate=onUpdate, onUpdate_sql=onUpdate_sql, deferred=deferred,
                                   case_insensitive=case_insensitive, eager_one=eager_one, eager_many=eager_many,
                                   one_group=one_group, many_group=many_group,storefield=storefield,_storename=storename)
            #print 'The relation %s - %s was added'%(str('.'.join(many_relation_tuple)), str(oneColumn))
            self.checkRelationIndex(many_pkg, many_table, many_field)
            self.checkRelationIndex(one_pkg, one_table, one_field)
        except Exception,e:
            if self.debug:
                raise
            print e
            logger.warning('The relation %s - %s cannot be added', str('.'.join(many_relation_tuple)), str(oneColumn))
            #print 'The relation %s - %s cannot be added'%(str('.'.join(many_relation_tuple)), str(oneColumn))
            
    def checkRelationIndex(self, pkg, table, column):
        """TODO
        
        :param pkg: the :ref:`package <packages>` object
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param column: the table :ref:`column`"""
        tblobj = self.table(table, pkg=pkg)
        indexname = '%s_%s_key' % (table, column)
        if column != tblobj.pkey and not indexname in tblobj.indexes:
            tblobj.indexes.children[indexname] = DbIndexObj(parent=tblobj.indexes, attrs=dict(columns=column))
            
    def load(self, source=None):
        """Load the modelsrc from a XML source
        
        :param source: XML model (diskfile or text or url). """
        self.src.update(source)
        
    def importFromDb(self):
        exporter = ModelExtractor(self.db)
        root = DbModelSrc.makeRoot()
        exporter.extractModelSrc(root=root)
        self.src.update(root)
        
    def save(self, path):
        """save the current modelsrc as XML file at path
        
        :param path: the file path"""
        self.src.save(path)
        
    def check(self, applyChanges=False):
        """Verify the compatibility between the database and the model.
        
        Save the sql statements that makes the database compatible with the model.
        
        :param applyChanges: boolean. If ``True``, apply the changes. Default value is ``False``"""
        checker = SqlModelChecker(self.db)
        self.modelChanges = checker.checkDb()
        self.modelBagChanges = checker.bagChanges
        if applyChanges:
            self.applyModelChanges()
        return bool(self.modelChanges)
        
    @property
    def checker(self):
        return SqlModelChecker(self.db)

    def applyModelChanges(self):
        """TODO"""
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
        """TODO
        
        :param pkg: the :ref:`package <packages>` object
        :param obj: TODO"""
        self._doMixin('pkg.%s' % pkg, obj)
        
    def tableMixin(self, tblpath, obj):
        self._doMixin('tbl.%s' % tblpath, obj)
        
    def package(self, pkg):
        """Return a package object
        
        :param pkg: the :ref:`package <packages>` object"""

        return self.obj[pkg]
        
    def table(self, tblname, pkg=None):
        """Return a table object
        
        :param tblname: the :ref:`database table <table>` name
        :param pkg: the :ref:`package <packages>` object"""
        if '.' in tblname:
            pkg, tblname = tblname.split('.')[:2]
        if pkg is None:
            raise ValueError(
                    "table() called with '%(tblname)s' instead of '<packagename>.%(tblname)s'" % {'tblname': tblname})
            #if pkg is None:
        #    pkg = self.obj.keys()[0]
        if not self.obj[pkg]:
            return
        return self.obj[pkg].table(tblname)

    def column(self, colname):
        """Return a column object
        
        :param colname: the column name"""
        colpath = colname.split('.')
        if len(colpath) == 2:
            pkg = None
            tblname, colname = colpath
        else:
            pkg, tblname, colname = colpath
        return self.table(tblname, pkg=pkg).column(colname)
        
class DbModelSrc(GnrStructData):
    """A GnrStructData subclass. It is used for the elements of a GenroDb
    TESTED in a_structure_load_test.py"""
    
    def package(self, name, sqlschema=None,
                comment=None,
                name_short=None, name_long=None, name_full=None,
                **kwargs):
        """Add a package to the structure.
        
        :param name: the package name
        :param sqlschema: actual sql name of the schema. For more information check the :ref:`about_schema`
                          documentation section
        :param comment: the package's comment. 
        :param name_short: the :ref:`name_short` of the package
        :param name_long: the :ref:`name_long` of the package
        :param name_full: the :ref:`name_full` of the package"""
        if not 'packages' in self: #if it is the first package it prepares the package_list packages
            self.child('package_list', 'packages')
        
        return self.child('package', 'packages.%s' % name,
                          comment=comment, sqlschema=sqlschema,
                          name_short=name_short, name_long=name_long,
                          name_full=name_full, **kwargs)
                          
    def externalPackage(self, name):
        """TODO
        
        :param name: the package name"""
        return self.root('packages.%s' % name)
        
    def table(self, name, pkey=None, lastTS=None, rowcaption=None,
              sqlname=None, sqlschema=None,
              comment=None,
              name_short=None, name_long=None, name_full=None,
              **kwargs):
        """Add a :ref:`database table <table>` to the structure and returns it
        
        :param name: the name of the table
        :param pkey: the record :ref:`primary key <pkey>`
        :param lastTS: the date of the last modification (TS = timestamp)
        :param rowcaption: the textual representation of a record in a user query.
                           For more information, check the :ref:`rowcaption` section
        :param sqlname: TODO
        :param sqlschema: actual sql name of the schema. For more information check
                          the :ref:`about_schema` documentation section
        :param comment: the table's comment
        :param name_short: the :ref:`name_short` of the table
        :param name_long: the :ref:`name_long` of the table
        :param name_full: the :ref:`name_full` of the table
        :param \*\*kwargs: 
            
            * **name_plural** - the :ref:`name_plural` of the table"""
        if not 'tables' in self:
            #if it is the first table it prepares the table_list tables
            self.child('table_list', 'tables')
        pkg=self.parentNode.label
        return self.child('table', 'tables.%s' % name, comment=comment,
                          name_short=name_short, name_long=name_long, name_full=name_full,
                          pkey=pkey, lastTS=lastTS, rowcaption=rowcaption, pkg=pkg,
                          fullname='%s.%s' %(pkg,name),
                          **kwargs)
                          
    def column(self, name, dtype=None, size=None,
               default=None, notnull=None, unique=None, indexed=None,
               sqlname=None, comment=None,
               name_short=None, name_long=None, name_full=None,
               group=None, onInserting=None, onUpdating=None, onDeleting=None,
               **kwargs):
        """Insert a :ref:`column` into a :ref:`table`
        
        :param name: the column name. You can specify both the name and the :ref:`datatype`
                     using the following syntax: ``'name::datatype'``
        :param dtype: the :ref:`datatype`
        :param size: string. ``'min:max'`` or fixed lenght ``'len'``
        :param default: the default value of the column
        :param notnull: This sets the 'Mandatory. attribute in the database
        :param unique: boolean. Same of the sql UNIQUE
        :param indexed: boolean. If ``True``, allow to create an index for the column data
                        (speed up the queries on the indexed column)
        :param sqlname: You can set a different sqlname that the one in the model if required.  Only use if you know what you are doing.
        :param comment: The column's comment
        :param name_short: the :ref:`name_short` of the column
        :param name_long: the :ref:`name_long` of the column
        :param name_full: the :ref:`name_full` of the column
        :param group: a hierarchical path of logical categories and subacategories
                      the columns belongs to. For more information, check the :ref:`group` section
        :param onInserting: This sets the method name which is triggered when a record is inserted.  useful for adding a code for example
        :param onUpdating: This sets the method name which is triggered when a record is updated
        :param onDeleting: This sets the method name which is triggered when a record is deleted"""
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
                          
    def virtual_column(self, name, relation_path=None, sql_formula=None,select=None,exists=None, py_method=None, **kwargs):
        """Insert a related alias column into a :ref:`table`. The virtual_column is
        a child of the table created with the :meth:`table()` method
        
        :param name: the column name. You can specify both the name and the :ref:`datatype`
                     using the following syntax: ``'name::datatype'``
        :param relation_path: the column's related path. For more information,
                              check the :ref:`relation_path` section
        :param sql_formula: TODO
        :param py_method: TODO"""
        if '::' in name: name, dtype = name.split('::')
        if not 'virtual_columns' in self:
            self.child('virtual_columns_list', 'virtual_columns')
        return self.child('virtual_column', 'virtual_columns.%s' % name,
                          relation_path=relation_path,select=select,exists=exists,
                          sql_formula=sql_formula, py_method=py_method,
                          virtual_column=True, **kwargs)
                          
    def aliasColumn(self, name, relation_path, **kwargs):
        """Insert an aliasColumn into a :ref:`table`, that is a column with a relation path.
        The aliasColumn is a child of the table created with the :meth:`table()` method
        
        :param name: the column name
        :param relation_path: the column's related path. For more information,
                              check the :ref:`relation_path` section
        :returns: an aliasColumn
        """
        return self.virtual_column(name, relation_path=relation_path, **kwargs)
        
    def formulaColumn(self, name, sql_formula=None,select=None, exists=None,dtype='A', **kwargs):
        """Insert a formulaColumn into a table, that is TODO. The aliasColumn is a child of the table
        created with the :meth:`table()` method
        
        :param name: the column name
        :param sql_formula: TODO
        :param dtype: the :ref:`datatype`. Default value is ``A``
        :returns: a formulaColumn
        """
        return self.virtual_column(name, sql_formula=sql_formula,select=select,exists=exists, dtype=dtype, **kwargs)
        
    def pyColumn(self, name, py_method=None,**kwargs):
        """Insert a pyColumn into a table, that is TODO. The aliasColumn is a child of the table
        created with the :meth:`table()` method
        
        :param name: the column name
        :param sql_formula: TODO
        :param dtype: the :ref:`datatype`. Default value is ``A``
        :returns: a formulaColumn"""
        py_method = py_method or 'pyColumn_%s' %name
        return self.virtual_column(name, py_method=py_method, **kwargs)
        
    def aliasTable(self, name, relation_path, **kwargs):
        """Insert a related table alias into a table. The aliasTable is a child of the table
        created with the :meth:`table()` method
        
        :param name: the aliasTable name. You can specify both the name and the :ref:`datatype`
                     using the following syntax: ``'name::datatype'``
        :param relation_path: the column's related path. For more information,
                              check the :ref:`relation_path` section"""
        if '::' in name: name, dtype = name.split('::')
        if not 'table_aliases' in self:
            self.child('tblalias_list', 'table_aliases')
        return self.child('table_alias', 'table_aliases.@%s' % name, relation_path=relation_path, **kwargs)
        
    table_alias = aliasTable
        
    def index(self, columns=None, name=None, unique=None):
        """Add an index to a column. ``self`` must be a column src or an index_list
        
        :param columns: list, or tuple, or string separated by commas
        :param name: the index name
        :param unique: boolean. Same of the sql UNIQUE"""
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
        """Add a relation between two :ref:`tables <table>`. This relation can be traveled in the
        direct direction (check the :ref:`relation` section) or in the inverse direction
        (check the :ref:`inverse_relation` section)
        
        :param related_column: string. The path of the related column. Syntax:
                               ``packageName.tableName.pkeyColumnName``, where:
                               
                               * ``packageName`` is the name of the :ref:`package <packages>` folder
                                 (you can omit it if the tables to link live in the same package folder)
                               * ``tableName`` is the name of the :ref:`table` to be related
                               * ``pkeyColumnName`` is the name of the :ref:`pkey` of the table to be related
                               
        :param mode: string. The method's mode. You can choose between:
                     
                     * 'relation': default mode. It defines a purely logical and case-sensitive
                       relation: there is no referential integrity check
                     * 'foreignkey': the relation becomes a SQL relation
                     * 'insensitive': same features of the ``mode='relation'`` but the relation
                       is *case-insensitive*
                       
        :param one_name: the one_to_many relation's name. e.g: 'movies'
        :param many_name: the many_to_one relation's name. e.g: 'director'
        :param eager_one: boolean. If ``True`` the one_to_many relation is eager as much as possible. If False then not even the first relation is eager. If Lazy, then only the first related record is loaded in the first rpc.
        :param eager_many: boolean. If ``True`` the many_to_one relation is eager ** DOES NOT CURRENTLY WORK **
        :param one_one: instead of a bag of rows, you get directly the bag of the record. This means that you do not have to deal with the related many path, but have an easier path to deal with in both directions.
        :param child: TODO ** Have forgotten **
        :param one_group: In the query hpopup and view hTree, this is the label given for group that the columns will be displayed
        :param many_group: In the query hpopup and view hTree, this is the label given for group that the columns will be displayed
        :param onUpdate: cascade.  If you change the pkey, then all fkeys will receive new pkey value. If you have triggers in python then this will inform the triggers
        :param onUpdate_sql: cascade. If you change the pkey, then all fkeys will receive new pkey value. No python triggers are informed. 
        :param onDelete: 'C:cascade' | 'I:ignore' | 'R:raise' | 'SetNull  Triggers are informed
        :param onDelete_sql: 'C:cascade' | 'I:ignore' | 'R:raise' | 'SetNull  Triggers are not informed
        :param deferred: the same of the sql "DEFERRED". This means that relational integrity is not checked until commit.
        :param relation_name: string. An attribute of the :ref:`table_relation`. It allows
                              to estabilish an alternative string for the :ref:`inverse_relation`.
                              For more information, check the :ref:`relation_name` section"""
        
        return self.setItem('relation', self.__class__(), related_column=related_column, mode=mode,
                            one_name=one_name, many_name=many_name, one_one=one_one, child=child,
                            one_group=one_group, many_group=many_group, deferred=deferred,
                            onUpdate=onUpdate, onDelete=onDelete,
                            eager_one=eager_one, eager_many=eager_many,
                            onUpdate_sql=onUpdate_sql, onDelete_sql=onDelete_sql,
                            relation_name=relation_name, **kwargs)
                            
class DbModelObj(GnrStructObj):
    """Base class for all the StructObj in this module"""
        
    def init(self):
        self._dbroot = self.root.rootparent.db
        
        mixpath = self._getMixinPath()
        mixobj = self._getMixinObj()
        if mixpath:
            mixobj.mixin(self.db.model.mixins[mixpath], attributes='_plugins,_pluginId')
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
        """TODO"""
        return self.sqlclass or self._sqlclass
        
    def getAttr(self, attr=None, dflt=None):
        """
        :param attr: the attribute. 
        :param dflt: the default. 
        """
        if attr:
            return self.attributes.get(attr, dflt)
        else:
            return self.attributes
            
class DbPackageObj(DbModelObj):
    """TODO"""
    sqlclass = "package"
        
    def _getMixinPath(self):
        return 'pkg.%s' % self.name
        
    def _get_tables(self):
        """property. Returns a SqlTableList"""
        return self['tables'] or {} #temporary FIX
        
    tables = property(_get_tables)
        
    def dbtable(self, name):
        """Return a table
        
        :param name: the database table's name
        :returns: a database table"""
        return self.table(name).dbtable
            
    def table(self, name):
        """Return a table
        
        :param name: the table's name
        :returns: a table
        """
        table = self['tables.%s' % name]
        if table is None:
            raise GnrSqlMissingTable("Table '%s' undefined in package: '%s'" % (name, self.name))
        return table
        
    def tableSqlName(self, tblobj):
        """Return the name of the given SqlTable
        
        :param tblobj: an instance of SqlTable
        :returns: the name of the given SqlTable
        """
        sqlprefix = self.attributes.get('sqlprefix')
        if sqlprefix == '':
            return tblobj.name
        else:
            return '%s_%s' % (sqlprefix or self.name, tblobj.name)
            
    def _get_sqlschema(self):
        return self.attributes.get('sqlschema', self.dbroot.main_schema)
            
    sqlschema = property(_get_sqlschema)
            
class DbTableObj(DbModelObj):
    """TODO"""
    sqlclass = 'table'
            
    def doInit(self):
        """TODO"""
        self.dbtable.onIniting()
        self._sqlnamemapper = {}
        self._indexedColumn = {}
        self._fieldTriggers = {}
        self.allcolumns = []
        self.dbtable.onInited()
            
    def afterChildrenCreation(self):
        """TODO"""
        objclassdict = self.root.objclassdict
        if not self.columns:
            self.children['columns'] = objclassdict['column_list'](parent=self)
        if not self.indexes:
            self.children['indexes'] = objclassdict['index_list'](parent=self)
        if not 'virtual_columns' in self.children:
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
        """TODO"""
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

    def _get_draftField(self):
        """property. Returns the table's logicalDeletionField"""
        return self.attributes.get('draftField', '')
        
    draftField = property(_get_draftField)
        
    def _get_noChangeMerge(self):
        """property. set noChangeMerge to True to avoid automatic merge of concurrent non conflicting changes"""
        return self.attributes.get('noChangeMerge', '')
        
    noChangeMerge = property(_get_noChangeMerge)
        
    def _get_rowcaption(self):
        """property. Returns the table's rowcaption"""
        attr = self.attributes
        rowcaption = attr.get('rowcaption')
        if not rowcaption and attr.get('caption_field'):
            rowcaption = '$%(caption_field)s' %attr
        rowcaption = rowcaption or '$%(pkey)s' %attr
        return rowcaption      
    rowcaption = property(_get_rowcaption)
    
    @property
    def newrecord_caption(self):
        """property. Returns the table's rowcaption"""
        return self.attributes.get('newrecord_caption', self.name_long)
        
        
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
      
    @property  
    def virtual_columns(self):
        """Returns a DbColAliasListObj"""
        virtual_columns = self['virtual_columns']
        local_virtual_columns = self.db.localVirtualColumns(self.fullname) #to remove use dynamic_virtual_columns
        if local_virtual_columns:
            for node in local_virtual_columns:
                obj = DbVirtualColumnObj(structnode=node,parent=virtual_columns)
                virtual_columns.children[obj.name.lower()] = obj

        for node in self.dynamic_columns:
            obj = DbVirtualColumnObj(structnode=node,parent=virtual_columns)
            virtual_columns.children[obj.name.lower()] = obj
        return virtual_columns

    @property
    def dynamic_columns(self):
        result = Bag()
        dbtable = self.dbtable
        fmethods = [v for v in [getattr(dbtable,k) for k in dir(dbtable) if k.startswith('formulaColumn_')]]
        for f in fmethods:
            r = f()
            if not isinstance(r,list):
                r = [r]
            for c in r:
                kw = dict(c)
                result.setItem(kw.pop('name'),None,**kw)
        return result

    @property
    def full_virtual_columns(self):
        """Returns a DbColAliasListObj"""
        virtual_columns = self.virtual_columns
        custom_virtual_columns = self.db.customVirtualColumns(self.fullname)
        if custom_virtual_columns:
            for node in custom_virtual_columns:
                obj = DbVirtualColumnObj(structnode=node,parent=virtual_columns)
                virtual_columns.children[obj.name.lower()] = obj
        return virtual_columns
    
        
    def _get_table_aliases(self):
        """Returns an DbTblAliasListObj"""
        return self['table_aliases']
        
    table_aliases = property(_get_table_aliases)
        
    def column(self, name):
        """Return a column object or None if it doesn't exists.
        
        :param name: A column's name or a :ref:`relation_path` starting from the current table.
                     e.g: ``@director_id.name``"""
        col = None
        colalias = None
        if name.startswith('$'):
            name = name[1:]
        if not name.startswith('@'):
            col = self['columns.%s' % name]
            if col is not None:
                return col
            
            colalias = self['virtual_columns.%s' % name]
            if colalias is not None:
                if colalias.relation_path:
                    name = colalias.relation_path
                elif colalias.sql_formula or colalias.select or colalias.exists:
                    return colalias
                elif colalias.py_method:
                    return colalias
                else:
                    raise GnrSqlMissingColumn('Invalid column %s in table %s' % (name, self.name_full))
        if name.startswith('@'):
            relcol = self._relatedColumn(name)
            assert relcol is not None, 'relation %s does not exist in table %s' %(relcol,name)
            if colalias is None:
                return relcol
                
            if not 'virtual_column' in colalias.attributes:
                raise             
            return AliasColumnWrapper(relcol,colalias.attributes)
     
    def _relatedColumn(self, fieldpath):
        """Return a column object corresponding to the relation path
        
        :param fieldpath: e.g: ``@member_id.name``
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
            joiner = attrs['joiner']
            if joiner['mode'] == 'O':
                relpkg, reltbl, relfld = joiner['one_relation'].split('.')
            else:
                relpkg, reltbl, relfld = joiner['many_relation'].split('.')
            reltbl = self.dbroot.package(relpkg).table(reltbl)
            
        return reltbl.column('.'.join(relpath))
        
    def fullRelationPath(self, name):
        """Return the full relation path to the given column
        
        :param name: the name of the relation path. e.g: ``@member_id.name``
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
            colobj = self.column(rel[1:])
            if colobj is not None:
                reltbl = colobj.relatedTable()
            else:
                reltbl = '.'.join(self.relations.getNode(rel).attr['joiner']['many_relation'].split('.')[0:2])
                reltbl = self.db.table(reltbl)
            return '%s.%s' % (rel, reltbl.fullRelationPath(pathlist))
        else:
            return name
            
    def resolveRelationPath(self, relpath):
        """TODO
        
        :param relpath: TODO
        """
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
            joiner = attrs['joiner']
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
            if joiner and joiner['mode'] == 'O':
                result.setItem(joiner['many_relation'].split('.')[-1],joiner['one_relation'],joiner)
        return result
        
    relations_one = property(_get_relations_one)
    
        
    def _get_relations_many(self):
        """This method returns a bag containing all the OneToMany relations that starts from to the current table"""
        result = Bag()
        for k, joiner in self.relations.digest('#k,#a.joiner'):
            if joiner and joiner['mode'] == 'M':
                result.setItem(joiner['many_relation'].replace('.', '_'), joiner['one_relation'].split('.')[-1], joiner)
        return result
        
    relations_many = property(_get_relations_many)
        
    def _get_relatingColumns(self):
        """This method returns a list of columns that joins to the primary key of the table"""
        return self.relations_many.digest('#a.many_relation')
        
    relatingColumns = property(_get_relatingColumns)
        
    def getRelation(self, relpath):
        """TODO
        
        :param relpath: TODO
        :returns: TODO
        """
        joiner = self.relations.getAttr(relpath, 'joiner')
        if joiner:
            return {'many': joiner['many_relation'], 'one': joiner['one_relation']}
            
    def getRelationBlock(self, relpath):
        """TODO
        
        :param relpath: TODO
        :returns: TODO
        """
        joiner = self.relations.getAttr(relpath, 'joiner')
        mpkg, mtbl, mfld = joiner['many_relation'].split('.')
        opkg, otbl, ofld = joiner['one_relation'].split('.')
        return dict(mode=joiner['mode'], mpkg=mpkg, mtbl=mtbl, mfld=mfld, opkg=opkg, otbl=otbl, ofld=ofld)
    
    def getJoiner(self,related_table):
        reltableobj = self.db.table(related_table)
        related_field = reltableobj.column(reltableobj.pkey).fullname
        for n in self.relations:
            joiner = n.attr.get('joiner')
            if joiner:
                if joiner.get('one_relation')==related_field:
                    return joiner
        relating_field = self.column(self.pkey).fullname
        for n in reltableobj.relations:
            joiner = n.attr.get('joiner')
            if joiner:
                if joiner.get('one_relation')==relating_field:
                    return joiner
                
                
    def manyRelationsList(self,cascadeOnly=False):
        result = list()
        relations = self.relations.keys()
        for k in relations:
            n = self.relations.getNode(k)
            joiner =  n.attr.get('joiner')
            if joiner and joiner['mode'] == 'M' and (not cascadeOnly or  (joiner.get('onDelete')=='cascade' or joiner.get('onDelete_sql')=='cascade')):
                fldlist = joiner['many_relation'].split('.')
                tblname = '.'.join(fldlist[0:2])
                fkey = fldlist[-1]
                result.append((tblname,fkey))
        return result

    def oneRelationsList(self,foreignkeyOnly=False):
        result = list()
        for n in self.relations_one:
            attr =  n.attr
            if not foreignkeyOnly or attr.get('foreignkey'):
                fldlist = attr['one_relation'].split('.')
                tblname = '.'.join(fldlist[0:2])
                fkey = attr['many_relation'].split('.')[-1]
                pkey = fldlist[-1]
                result.append((tblname,pkey,fkey))
        return result
        
        
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
    """TODO"""
    sqlclass = 'column'
        
    def _captureChildren(self, children):
        self.column_relation = children['relation']
        return False
        
    def doInit(self):
        """TODO"""
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
            
        for trigType in ('onInserting', 'onUpdating', 'onDeleting','onInserted', 'onUpdated', 'onDeleted'):
            trigFunc = self.attributes.get(trigType)
            if trigFunc:
                self.table._fieldTriggers.setdefault(trigType, []).append((self.name, trigFunc))
                    
    def relatedTable(self):
        """Get the SqlTable that is related by the current column"""
        r = self.table.relations.getAttr('@%s' % self.name)
        if r:
            return self.dbroot.model.table(r['joiner']['one_relation'])
            
    def relatedColumn(self):
        """Get the SqlColumn that is related by the current column"""
        r = self.table.relations.getAttr('@%s' % self.name)
        if r:
            return self.dbroot.model.column(r['joiner']['one_relation'])
            
    def relatedColumnJoiner(self):
        """Get the SqlTable that is related by the current column"""
        r = self.table.relations.getAttr('@%s' % self.name)
        if r:
            return r['joiner']

    def rename(self,newname):
        self.db.adapter.renameColumn(self.table.sqlname,self.sqlname,newname)
            
class DbVirtualColumnObj(DbBaseColumnObj):
    sqlclass = 'virtual_column'
        
    def _get_relation_path(self):
        """property. Returns the :ref:`relation_path`"""
        return self.attributes.get('relation_path')
        
    relation_path = property(_get_relation_path)
        
    def _get_sql_formula(self):
        """property. Returns the sql_formula"""
        return self.attributes.get('sql_formula')
        
    sql_formula = property(_get_sql_formula)
    
    def _get_select(self):
        """property. Returns the sql_formula"""
        return self.attributes.get('select')
        
    select = property(_get_select)

    def _get_exists(self):
        """property. Returns the sql_formula"""
        return self.attributes.get('exists')
        
    exists = property(_get_exists)

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

class AliasColumnWrapper(DbModelObj):
    def __init__(self,originalColumn=None,aliasAttributes=None):
        mixedattributes = dict(originalColumn.attributes)
        colalias_attributes = dict(aliasAttributes)
        colalias_attributes.pop('tag')
        colalias_attributes.pop('relation_path')
        mixedattributes.update(colalias_attributes)
        virtual_column = mixedattributes.pop('virtual_column', None)
        if virtual_column:
            self.sqlclass = 'virtual_column'
        self.originalColumn = originalColumn
        self.attributes = mixedattributes

    def __getattr__(self,name):
        return getattr(self.originalColumn,name)
        
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
        """TODO"""
        args = list(self._initArgs)
        kwargs = dict(self._initKwargs)
        #kwargs.pop('dbroot')
        kwargs['_serialized_app_handler'] = 'maindb'
        #lbl = kwargs.pop('autoRelate', None)
        #if lbl:
        #kwargs[lbl] = '@'+lbl
        
        return BagResolver.resolverSerialize(self, args=args, kwargs=kwargs)
        
    def setDbroot(self, dbroot):
        """Set the database root
        
        :param dbroot: the database root
        """
        self.dbroot = dbroot
        
    def load(self):
        """TODO"""
        self.main_table_obj = self.dbroot.model.table(self.main_tbl)
        if not self.__fields:
            self._lock.acquire()
            if not self.__fields: #repeat test after lock_acquire
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
                               joiner=relpars) #relpars deve essere una lista???? gardare in getalias sqldata
                               
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
            result.setItem(label, child, joiner=relpars)
        return result
        
class ModelSrcResolver(BagResolver):
    """TODO"""
    classKwargs = {'cacheTime': 300, 'readOnly': False, 'dbroot': None}
    classArgs = ['dbId']
        
    def load(self):
        """TODO"""
        return self.dbroot.model.src
        
    def resolverSerialize(self):
        """TODO"""
        args = list(self._initArgs)
        kwargs = dict(self._initKwargs)
        kwargs.pop('dbroot')
        return BagResolver.resolverSerialize(self, args=args, kwargs=kwargs)
        
class ConfigureAfterStartError(Exception):
    pass
        
if __name__ == '__main__':
    pass
        