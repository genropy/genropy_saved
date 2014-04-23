#-*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy sql - see LICENSE for details
# module gnrsqltable : Genro sql table object.
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

__version__ = '1.0b'

#import weakref
import os

from gnr.core import gnrstring
from gnr.core.gnrlang import GnrObject,getUuid,uniquify
from gnr.core.gnrdecorator import deprecated
from gnr.core.gnrbag import Bag, BagCbResolver
from gnr.core.gnrdict import dictExtract
#from gnr.sql.gnrsql_exceptions import GnrSqlException,GnrSqlSaveException, GnrSqlApplicationException
from gnr.sql.gnrsqldata import SqlRecord, SqlQuery
from gnr.sql.gnrsql import GnrSqlException
from datetime import datetime
import logging

gnrlogger = logging.getLogger(__name__)


class RecordUpdater(object):
    """TODO
    
    Example::
    
        with self.recordToUpdate(pkey) as record:
            # do something
            pass"""
    
    def __init__(self, tblobj,pkey=None,mode=None,raw=False,insertMissing=False,**kwargs):
        self.tblobj = tblobj
        self.pkey = pkey
        self.mode = mode or 'dict'
        self.kwargs = kwargs
        self.raw = raw
        self.insertMissing = insertMissing
        self.insertMode = False

    def __enter__(self):
        self.record = self.tblobj.record(pkey=self.pkey,for_update=True,ignoreMissing=self.insertMissing,**self.kwargs).output(self.mode)
        self.insertMode = self.record.get(self.tblobj.pkey) is None
        self.oldrecord = None if self.insertMode else dict(self.record)
        return self.record
        
        
    def __exit__(self, exception_type, value, traceback):
        if not exception_type:
            if self.raw:
                if self.insertMode:
                    self.tblobj.raw_insert(self.record)
                else:
                    self.tblobj.raw_update(self.record,self.oldrecord)
            else:
                if self.insertMode:
                    self.tblobj.insert(self.record)
                else:
                    self.tblobj.update(self.record,self.oldrecord)
        

class GnrSqlSaveException(GnrSqlException):
    """Standard Genro SQL Save Exception
    
    * **code**: GNRSQL-003
    * **description**: Genro SQL Save Exception
    """
    code = 'GNRSQL-003'
    description = '!!Genro SQL Save Exception'
    caption = "!!The record %(rowcaption)s in table %(tablename)s cannot be saved:%(msg)s"

class GnrSqlDeleteException(GnrSqlException):
    """Standard Genro SQL Delete Exception
    
    * **code**: GNRSQL-004
    * **description**: Genro SQL Delete Exception
    """
    code = 'GNRSQL-004'
    description = '!!Genro SQL Delete Exception'
    caption = "!!The record %(rowcaption)s in table %(tablename)s cannot be deleted:%(msg)s"

class GnrSqlProtectUpdateException(GnrSqlException):
    """Standard Genro SQL Save Exception
    
    * **code**: GNRSQL-011
    * **description**: Genro SQL Save Exception
    """
    code = 'GNRSQL-011'
    description = '!!Genro SQL Protect Update Exception'
    caption = "!!The record %(rowcaption)s in table %(tablename)s is not updatable:%(msg)s"

class GnrSqlProtectDeleteException(GnrSqlException):
    """Standard Genro SQL Protect Delete Exception
    
    * **code**: GNRSQL-012
    * **description**: Genro SQL Protect Delete Exception
    """
    code = 'GNRSQL-012'
    description = '!!Genro SQL Protect Delete Exception'
    caption = "!!The record %(rowcaption)s in table %(tablename)s is not deletable:%(msg)s"

class GnrSqlProtectValidateException(GnrSqlException):
    """Standard Genro SQL Protect Validate Exception
    
    * **code**: GNRSQL-013
    * **description**: Genro SQL Protect Validate Exception
    """
    code = 'GNRSQL-013'
    description = '!!Genro SQL Protect Validate Exception'
    caption = "!!The record %(rowcaption)s in table %(tablename)s contains invalid data:%(msg)s"

class GnrSqlBusinessLogicException(GnrSqlException):
    """Standard Genro SQL Business Logic Exception
    
    * **code**: GNRSQL-021
    * **description**: Genro SQL Business Logic Exception
    """
    code = 'GNRSQL-021'
    description = '!!Genro SQL Business Logic Exception'
    caption = '!!The requested operation violates the internal business logic: %(msg)s'


class GnrSqlStandardException(GnrSqlException):
    """Standard Genro SQL Business Logic Exception
    
    * **code**: GNRSQL-021
    * **description**: Genro SQL Business Logic Exception
    """
    code = 'GNRSQL-023'
    description = '!!%(description)s'
    caption = '!!%(msg)s'

class GnrSqlNotExistingColumnException(GnrSqlException):
    """Standard Genro SQL Business Logic Exception
    
    * **code**: GNRSQL-022
    * **description**: Genro SQL Business Logic Exception
    """
    code = 'GNRSQL-081'
    description = '!!Genro SQL Not Existing Column Exception'
    caption = "!!Column %(column)s not existing in table %(tablename)s "

    
EXCEPTIONS = {'save': GnrSqlSaveException,
              'delete': GnrSqlDeleteException,
              'protect_update': GnrSqlProtectUpdateException,
              'protect_delete': GnrSqlProtectDeleteException,
              'protect_validate': GnrSqlProtectValidateException,
              'business_logic':GnrSqlBusinessLogicException,
              'standard':GnrSqlStandardException,
              'not_existing_column':GnrSqlNotExistingColumnException}
              
class SqlTable(GnrObject):
    """The base class for database :ref:`tables <table>`.
    
    Your tables will inherit from it (altough it won't be explicit in your code, since it's
    done by GenroPy mixin machinery).
    
    In your webpage, package or table methods, you can get a reference to a table by name it
    in this way::
    
        self.db.table('packagename.tablename')
    
    You can also get them from the application instance::
    
        app = GnrApp('instancename')
        app.db.table('packagename.tablename')"""
    def __init__(self, tblobj):
        self._model = tblobj
        self.name = tblobj.name
        self.fullname = tblobj.fullname
        self.name_long = tblobj.name_long
        self.name_plural = tblobj.name_plural
        
    def use_dbstores(self,**kwargs):
        pass

    def exception(self, exception, record=None, msg=None, **kwargs):
        """TODO
        
        :param exception: the exception raised.
        :param record: TODO.
        :param msg: TODO."""
        if isinstance(exception,basestring):
            exception = EXCEPTIONS.get(exception)
            if not exception:
                raise exception
        rowcaption = ''
        if record:
            try:
                rowcaption = self.recordCaption(record)
            except:
                rowcaption = 'Current Record'
        e = exception(tablename=self.fullname,rowcaption=rowcaption,msg=msg, **kwargs)
        
        if self.db.application and hasattr(self.db.application,'site') and self.db.application.site.currentPage:
            e.setLocalizer(self.db.application.site.currentPage.localizer)
        return e
        
    def __repr__(self):
        return "<SqlTable %s>" % repr(self.fullname)
        
    @property
    def model(self):
        """Return the corresponding DbTableObj object"""
        return self._model
        
    @property
    def pkg(self):
        """Return the DbPackageObj object that contains the current table"""
        return self.model.pkg
        
    @property
    def db(self):
        """Return the GnrSqlDb object"""
        return self.model.db
        
    dbroot = db
        
    def column(self, name):
        """Returns a :ref:`column` object.
        
        :param name: A column's name or a :ref:`relation <relations>` starting from
                     the current :ref:`table`. (eg. ``@director_id.name``)"""
        return self.model.column(name)
        
    def fullRelationPath(self, name):
        """TODO
        
        :param name: TODO"""
        return self.model.fullRelationPath(name)

    @property
    def partitionParameters(self):
        kw = dictExtract(self.attributes,'partition_')
        if not kw:
            return
        result = dict()
        result['field'] = kw.keys()[0]
        result['path'] = kw[result['field']]
        result['table'] = self.column(result['field']).relatedColumn().table.fullname
        return result

    def getColumnPrintWidth(self, column):
        """Allow to find the correct width for printing and return it
        
        :param column: the column to print"""
        if column.dtype in ['A', 'C', 'T', 'X', 'P']:
            size = column.attributes.get('size', None)
            values =  column.attributes.get('values', None)
            if values or not size:
                if column.dtype == 'T':
                    result = 20
                else:
                    result = 12
            elif isinstance(size, basestring):
                if ':' in size:
                    size = size.split(':')[1]
                size = float(size)
                if size < 3:
                    result = 2
                elif size < 10:
                    result = size * 0.8
                elif size < 30:
                    result = size * 0.7
                else:
                    result = 30
            else:
                result = size
        else:
            result = gnrstring.guessLen(column.dtype,
                                        format=column.attributes.get('print_format', None),
                                        mask=column.attributes.get('print_mask', None))
                                        
        namelong = column.attributes.get('name_short') or column.attributes.get('name_long', 'untitled')
        namelong = namelong.replace('!!','')
        if '\n' in namelong:
            namelong = namelong.split('\n')
            nl = [len(x) for x in namelong]
            headerlen = max[nl]
        else:
            headerlen = len(namelong)
        return max(result, headerlen)
        
    @property
    def attributes(self):
        """TODO"""
        return self.model.attributes
        
    @property
    def pkey(self):
        """Return the pkey DbColumnObj object"""
        return self.model.pkey
        
    @property
    def lastTS(self):
        """Return the lastTS DbColumnObj object"""
        return self.model.lastTS
        
    @property
    def logicalDeletionField(self):
        """Return the logicalDeletionField DbColumnObj object"""
        return self.model.logicalDeletionField

    @property
    def draftField(self):
        """Return the draftField DbColumnObj object"""
        return self.model.draftField
        
    @property
    def noChangeMerge(self):
        """Return the noChangeMerge DbColumnObj object"""
        return self.model.noChangeMerge
        
    @property
    def rowcaption(self):
        """Return the table's :ref:`rowcaption`"""
        return self.model.rowcaption
    

    @property
    def newrecord_caption(self):
        """Return the table's :ref:`rowcaption`"""
        return self.model.newrecord_caption
             
    @property
    def columns(self):
        """Returns the columns DbColumnListObj object"""
        return self.model.columns
        
    @property
    def relations(self):
        """Returns the relations DbColumnListObj object"""
        return self.model.relations
        
    @property
    def indexes(self):
        """Returns the indexes DbIndexListObj object"""
        return self.model.indexes
        
    @property
    def relations_one(self):
        """Return a Bag of relations that start from the current table"""
        return self.model.relations_one
        
    @property
    def relations_many(self):
        """Return a bag of relations that point to the current table"""
        return self.model.relations_many
        
    def counterColumns(self):
        return

    def recordCoerceTypes(self, record, null='NULL'):
        """Check and coerce types in record.
        
        :param record: an object implementing dict interface as colname, colvalue
        :param null: TODO"""
        converter = self.db.typeConverter
        for k in record.keys():
            if not k.startswith('@'):
                colattr = self.column(k).attributes
                dtype = self.column(k).dtype
                v = record[k]
                if (v is None) or (v == null):
                    record[k] = None
                elif dtype == 'B' and not isinstance(v, basestring):
                    record[k] = bool(v)
                else:
                    if dtype and isinstance(v, basestring):
                        if not dtype in ['T', 'A', 'C']:
                            v = converter.fromText(record[k], dtype)
                    if 'rjust' in colattr:
                        v = v.rjust(int(colattr['size']), colattr['rjust'])
                        
                    elif 'ljust' in  colattr:
                        v = v.ljust(int(colattr['size']), colattr['ljust'])
                    record[k] = v
                    
    def buildrecord(self, fields, resolver_one=None, resolver_many=None):
        """Build a new record and return it
        
        :param fields: TODO
        :param resolver_one: TODO
        :param resolver_many: TODO"""
        newrecord = Bag()
        for fld_node in self.model.relations:
            fld = fld_node.label
            if fld.startswith('@'):
                info = dict(fld_node.getAttr())
                attrs = info.pop('joiner')
                if attrs['mode'] == 'O': # or extra_one_one:
                    #print 'many_one: %s'%str(attrs)
                    if resolver_one:
                        mpkg, mtbl, mfld = attrs['many_relation'].split('.')
                        info.pop('many_relation', None)
                        info['_from_fld'] = attrs['many_relation']
                        info['_target_fld'] = attrs['one_relation']
                        info['mode'] = attrs['mode']
                        
                        if resolver_one is True:
                            pass # non posso fare il resolver python, il valore di link non c'è ancora
                        else:
                            v = None
                            info['_resolver_name'] = resolver_one
                            #info['_sqlContextName'] = self.sqlContextName # non ho il contesto, ma comunque serve?
                            #if attrs.get('one_one'): # one_one
                            #print 'one_one: %s'%str(attrs)
                            #pass # one_one relation to a non saved record did make sense ???
                else: # one_many
                    #print 'one_many: %s'%str(attrs)
                    pass # many relation to a non saved record didn't make sense
            else:
                v = fields.get(fld)
                info = dict(self.columns[fld].attributes)
                dtype = info.get('dtype')
                if dtype == 'X':
                    try:
                        v = Bag(v)
                    except:
                        pass
                        
            newrecord.setItem(fld, v, info)
        return newrecord
        
    def buildrecord_(self, fields):
        """TODO
        
        :param fields: TODO"""
        newrecord = Bag()
        for fld in self.columns.keys():
            v = fields.get(fld)
            info = dict(self.columns[fld].attributes)
            dtype = info.get('dtype')
            if dtype == 'X':
                try:
                    v = Bag(v)
                except:
                    pass
                    
            newrecord.setItem(fld, v, info)
        return newrecord
        
    def newrecord(self, assignId=False, resolver_one=None, resolver_many=None, **kwargs):
        """TODO
        
        :param assignId: TODO
        :param resolver_one: TODO
        :param resolver_many: TODO"""
        newrecord = self.buildrecord(kwargs, resolver_one=resolver_one, resolver_many=resolver_many)
        if assignId:
            newrecord[self.pkey] = self.newPkeyValue(record=newrecord)
        return newrecord
        
    def record(self, pkey=None, where=None,
               lazy=None, eager=None, mode=None, relationDict=None, ignoreMissing=False, virtual_columns=None,
               ignoreDuplicate=False, bagFields=True, joinConditions=None, sqlContextName=None,
               for_update=False, _storename=None,aliasPrefix=None,**kwargs):
        """Get a single record of the table. It returns a SqlRecordResolver.
        
        The record can be identified by:
        
        * its primary key
        * one or more conditions passed as kwargs (e.g. username='foo')
        * a "where" condition
         
        :param pkey: the record :ref:`primary key <pkey>`
        :param where: the sql "WHERE" clause. For more information check the :ref:`sql_where` section
        :param lazy: TODO
        :param eager: TODO
        :param mode: bag, dict, json
        :param relationDict: a dict to assign a symbolic name to a :ref:`relation_path`. For more information
                             check the :ref:`relationdict` documentation section
        :param ignoreMissing: TODO
        :param virtual_columns: TODO
        :param ignoreDuplicate: TODO
        :param bagFields: boolean. If ``True``, include fields of type Bag (``X``) when columns is ``*``
                          or contains ``*@relname.filter``
        :param joinConditions: special conditions for joining related tables. See the
                               :meth:`setJoinCondition() <gnr.sql.gnrsqldata.SqlQuery.setJoinCondition()>` method
        :param sqlContextName: TODO
        :param for_update: TODO"""
        record = SqlRecord(self, pkey=pkey, where=where,
                           lazy=lazy, eager=eager,
                           relationDict=relationDict,
                           ignoreMissing=ignoreMissing,
                           virtual_columns=virtual_columns,
                           ignoreDuplicate=ignoreDuplicate,
                           joinConditions=joinConditions, sqlContextName=sqlContextName,
                           bagFields=bagFields, for_update=for_update, _storename=_storename,
                           aliasPrefix=aliasPrefix,**kwargs)

        if mode:
            return record.output(mode)
        else:
            return record

    def restoreUnifiedRecord(self,record=None):
        r = Bag(record['__moved_related'])
        if not r:
            return
        relations = r.getItem('relations')
        if hasattr(self,'onRestoring'):
            self.onRestoring(record=record)
        if relations:
            for n in relations:
                tblobj = self.db.table(n.attr['tblname'])
                updater = dict()
                updater[n.attr['fkey']] = record['id']
                tblobj.batchUpdate(updater,_pkeys=n.value.split(','))
        record['__moved_related'] = None

    def _onUnifying(self,destRecord=None,sourceRecord=None,moved_relations=None,relations=None):
        pass

    def unifyRecords(self,sourcePkey=None,destPkey=None):
        moved_relations = Bag()
        sourceRecord = self.record(pkey=sourcePkey,for_update=True).output('dict')
        destRecord = self.record(pkey=destPkey,for_update=True).output('dict')
        relations = self.model.relations.keys()
        self._onUnifying(sourceRecord=sourceRecord,destRecord=destRecord,moved_relations=moved_relations,relations=relations)
        if hasattr(self,'onUnifying'):
            self.onUnifying(sourceRecord=sourceRecord,destRecord=destRecord,moved_relations=moved_relations)
        for k in relations:
            n = self.relations.getNode(k)
            joiner =  n.attr.get('joiner')
            if joiner and joiner['mode'] == 'M':
                fldlist = joiner['many_relation'].split('.')
                tblname = '.'.join(fldlist[0:2])
                tblobj = self.db.table(tblname)
                fkey = fldlist[-1]
                joinkey = joiner['one_relation'].split('.')[-1]
                updater = dict()
                updater[fkey] = destRecord[joinkey]
                updatedpkeys = tblobj.batchUpdate(updater,where='$%s=:spkey' %fkey,spkey=sourceRecord[joinkey],_raw_update=True)
                moved_relations.setItem('relations.%s' %tblname.replace('.','_'), ','.join(updatedpkeys),tblname=tblname,fkey=fkey)
        if self.model.column('__moved_related') is not None:
            old_record = dict(sourceRecord)
            moved_relations.setItem('destPkey',destPkey)
            moved_relations = moved_relations.toXml()
            sourceRecord.update(__del_ts=datetime.now(),__moved_related=moved_relations)
            self.raw_update(sourceRecord,old_record=old_record)
        else:
            self.delete(sourcePkey)
            

    def itemsAsText(self,caption_field=None,cols=None,**kwargs):
        caption_field = caption_field or self.attributes['caption_field']
        f = self.query(columns='$%s,$%s' %(self.pkey,caption_field),**kwargs).fetch()
        l = []
        for i,r in enumerate(f):
            if cols and i and not i%cols:
                l.append('/')
            l.append('%s:%s' %(r[self.pkey],r[caption_field].replace(',',' ').replace(':',' ')))

        return ','.join(l)

    def duplicateRecord(self,recordOrKey=None, howmany=None,destination_store=None,**kwargs):
        duplicatedRecords=[]
        howmany = howmany or 1
        record = self.recordAs(recordOrKey,mode='dict')
        pkey = record.pop(self.pkey,None)
        for colname,obj in self.model.columns.items():
            if colname == self.draftField or colname == 'parent_id':
                continue
            if obj.attributes.get('unique') or obj.attributes.get('_sysfield'):
                record.pop(colname,None)
        if hasattr(self,'onDuplicating'):
            self.onDuplicating(record)
        for i in range(howmany):
            r=dict(record)
            r.update(kwargs)
            if destination_store:
                with self.db.tempEnv(storename=destination_store):
                    self.insert(r)
            else:
                self.insert(r)
            duplicatedRecords.append(r)
        for n in self.model.relations:
            joiner =  n.attr.get('joiner')
            if joiner and joiner['mode'] == 'M' and (joiner.get('onDelete')=='cascade' or joiner.get('onDelete_sql')=='cascade'):
                rellist = joiner['many_relation'].split('.')
                fkey = rellist[-1]
                subtable ='.'.join(rellist[:-1])
                manytable = self.db.table(subtable)
                rows = manytable.query(where="$%s=:p" %fkey,p=pkey,addPkeyColumn=False,bagFields=True).fetch()
                for dupRec in duplicatedRecords:
                    for r in rows:
                        r = dict(r)
                        r[fkey] = dupRec[self.pkey]
                        manytable.duplicateRecord(r,destination_store=destination_store)
        return duplicatedRecords[0]
            
    def recordAs(self, record, mode='bag', virtual_columns=None,ignoreMissing=True):
        """Accept and return a record as a bag, dict or primary pkey (as a string)
        
        :param record: a bag, a dict or a string (i.e. the record's pkey)
        :param mode: 'dict' or 'bag' or 'pkey'
        :param virtual_columns: TODO"""
        if isinstance(record, basestring):
            if mode == 'pkey':
                return record
            else:
                return self.record(pkey=record, mode=mode, virtual_columns=virtual_columns,ignoreMissing=ignoreMissing)
        if mode == 'pkey':
            # The record is either a dict or a bag, so it accepts indexing operations
            return record.get('pkey', None) or record.get(self.pkey)
        if mode == 'dict' and not isinstance(record, dict):
            return dict([(k, v) for k, v in record.items() if not k.startswith('@')])
        if mode == 'bag' and (virtual_columns or not isinstance(record, Bag)):
            pkey=record.get('pkey', None) or record.get(self.pkey)
            if pkey:
                record = self.record(pkey=pkey, mode=mode,virtual_columns=virtual_columns)
        return record
            

    def defaultValues (self):
        """Override this method to assign defaults to new record. Return a dictionary - fill
        it with defaults"""
        return dict([(x.name, x.attributes['default'])for x in self.columns.values() if 'default' in x.attributes])
        

    def sampleValues (self):
        """Override this method to assign defaults to new record. Return a dictionary - fill
        it with defaults"""
        return dict([(x.name, x.attributes['sample'])for x in self.columns.values() if 'sample' in x.attributes])

    def query(self, columns='*', where=None, order_by=None,
              distinct=None, limit=None, offset=None,
              group_by=None, having=None, for_update=False,
              relationDict=None, sqlparams=None, excludeLogicalDeleted=True,
              excludeDraft=True,
              addPkeyColumn=True,
              ignoreTableOrderBy=False,ignorePartition=False, locale=None,
              mode=None,_storename=None,aliasPrefix=None, **kwargs):
        """Return a SqlQuery (a method of ``gnr/sql/gnrsqldata``) object representing a query.
        This query is executable with different modes.
        
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        :param where: the sql "WHERE" clause. For more information check the :ref:`sql_where` section
        :param order_by: corresponding to the sql "ORDER BY" operator. For more information check the
                         :ref:`sql_order_by` section
        :param distinct: boolean, ``True`` for getting a "SELECT DISTINCT"
        :param limit: number of result's rows. Corresponding to the sql "LIMIT" operator. For more
                      information, check the :ref:`sql_limit` section
        :param offset: corresponding to the sql "OFFSET" operator
        :param group_by: the sql "GROUP BY" clause. For more information check the :ref:`sql_group_by` section
        :param having: the sql "HAVING" clause. For more information check the :ref:`sql_having`
        :param for_update: boolean. TODO
        :param relationDict: a dict to assign a symbolic name to a :ref:`relation_path`. For more information
                             check the :ref:`relationdict` documentation section
        :param sqlparams: an optional dictionary for sql query parameters
        :param excludeLogicalDeleted: boolean. If ``True``, exclude from the query all the records that are
                                      "logical deleted"
        :param excludeDraft: TODO
        :param addPkeyColumn: boolean. If ``True``, add a column with the pkey attribute
        :param locale: the current locale (e.g: en, en_us, it)
        :param mode: TODO
        :param \*\*kwargs: another way to pass sql query parameters"""
        query = SqlQuery(self, columns=columns, where=where, order_by=order_by,
                         distinct=distinct, limit=limit, offset=offset,
                         group_by=group_by, having=having, for_update=for_update,
                         relationDict=relationDict, sqlparams=sqlparams,
                         excludeLogicalDeleted=excludeLogicalDeleted,excludeDraft=excludeDraft,
                         ignorePartition=ignorePartition,
                         addPkeyColumn=addPkeyColumn,ignoreTableOrderBy=ignoreTableOrderBy,
                        locale=locale,_storename=_storename,
                         aliasPrefix=aliasPrefix,**kwargs)
        return query


    def recordToUpdate(self, pkey=None,updater=None,**kwargs):
        """Return a TempEnv class"""
        return RecordUpdater(self, pkey=pkey,**kwargs)
            
    def batchUpdate(self, updater=None, _wrapper=None, _wrapperKwargs=None, autocommit=False,_pkeys=None,pkey=None,_raw_update=None,**kwargs):
        """A :ref:`batch` used to update a database. For more information, check the :ref:`batchupdate` section
        
        :param updater: MANDATORY. It can be a dict() (if the batch is a :ref:`simple substitution
                        <batchupdate>`) or a method
        :param autocommit: boolan. If ``True``, perform the commit of the database (``self.db.commit()``)
        :param **kwargs: insert all the :ref:`query` parameters, like the :ref:`sql_where` parameter
        """
        if not 'where' in kwargs:
            if pkey:
                _pkeys = [pkey]
            if not _pkeys:
                return
            kwargs['where'] = '$%s IN :_pkeys' %self.pkey
            if isinstance(_pkeys,basestring):
                _pkeys = _pkeys.strip(',').split(',')
            kwargs['_pkeys'] = _pkeys
            kwargs.setdefault('excludeDraft',False)
            kwargs.setdefault('ignorePartition',True)
            kwargs.setdefault('excludeLogicalDeleted',False)
        elif pkey:
            kwargs['pkey'] = pkey

        fetch = self.query(addPkeyColumn=False, for_update=True, **kwargs).fetch()
        if _wrapper:
            _wrapperKwargs = _wrapperKwargs or dict()
            fetch = _wrapper(fetch, **(_wrapperKwargs or dict()))
        pkeycol = self.pkey
        updatedKeys = []
        for row in fetch:
            new_row = dict(row)
            if callable(updater):
                updater(new_row)
            elif isinstance(updater, dict):
                new_row.update(updater)
            record_pkey = row[pkeycol]
            updatedKeys.append(record_pkey)
            if not _raw_update:
                self.update(new_row, row,pkey=record_pkey)
            else:
                self.raw_update(new_row,old_record=row,pkey=record_pkey)
        if autocommit:
            self.db.commit()
        return updatedKeys
        
    def toXml(self,pkeys=None,path=None,where=None,rowcaption=None,columns=None,related_one_dict=None,**kwargs):
        where = '$%s IN :pkeys' %self.pkey if pkeys else where
        columns = columns or '*'
        if rowcaption:
            rowcaption = self.rowcaption if rowcaption is True else rowcaption
            fields,mask = self.rowcaptionDecode(rowcaption)
            columns = '%s,%s' %(columns,','.join(fields))        
        f = self.query(where=where,pkeys=pkeys,columns=columns,bagFields=True,**kwargs).fetch()
        result = Bag()
        for r in f:
            caption = self.recordCaption(record=r,rowcaption=rowcaption) if rowcaption else None
            result.setItem(r[self.pkey],self.recordToXml(r),caption=caption,pkey=r[self.pkey])
        if path:
            result.toXml(path,autocreate=True)
        return result
            
    
    def recordToXml(self,record,path=None):
        result = Bag()
        for col in self.columns:
            result[col] = record[col]
        if path:
            result.toXml(path,autocreate=True)
        return result
            
    def fieldsChanged(self,fieldNames,record,old_record):
        if isinstance(fieldNames,basestring):
            fieldNames = fieldNames.split(',')
        for field in fieldNames:
            if record.get(field) != old_record.get(field):
                return True
        return False

    def fieldAggregate(self,field,data,fieldattr=None,onSelection=False):
        handler = getattr(self,'aggregate_%s' %field,None)
        if handler:
            return handler(data)
        dtype = fieldattr.get('dataType',None) or fieldattr.get('dtype','A') 
        aggregator = fieldattr.get('aggregator')
        aggregator = fieldattr.get('aggregator_record',aggregator) if not onSelection else fieldattr.get('aggregator_selection',aggregator)
        if aggregator==False:
            return data
        if dtype=='B':
            dd = [d or False for d in data]
            data = not (False in dd) if (aggregator or 'AND')=='AND' else (True in dd)
        elif dtype in ('R','L','N'):
            aggregator = aggregator or 'SUM'
            dd = filter(lambda r: r is not None, data)
            if not dd:
                data = None
            elif aggregator=='SUM':
                data = sum(dd)
            elif aggregator=='MAX':
                data = max(dd)
            elif aggregator=='MIN':
                data = min(dd)
            elif aggregator=='AVG':
                data = sum(dd)/len(dd) if len(dd) else 0
            elif aggregator=='CNT':
                data = len(data) if data else 0
        else:
            data.sort()
            data = (aggregator or ',').join(uniquify([gnrstring.toText(d) for d in data]))
        return data


    def readColumns(self, pkey=None, columns=None, where=None, **kwargs):
        """TODO
        
        :param pkey: the record :ref:`primary key <pkey>`
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        :param where: the sql "WHERE" clause. For more information check the :ref:`sql_where` section"""
        where = where or '$%s=:pkey' % self.pkey
        kwargs.pop('limit', None)
        fetch = self.query(columns=columns, limit=1, where=where,
                           pkey=pkey, addPkeyColumn=False,excludeDraft=False,
                           ignorePartition=True,excludeLogicalDeleted=False, **kwargs).fetch()
        if not fetch:
            row = [None for x in columns.split(',')]
        else:
            row = fetch[0]
        if len(row) == 1:
            row = row[0]
        return row
        
    def sqlWhereFromBag(self, wherebag, sqlArgs=None, **kwargs):
        """TODO
        
        :param wherebag: TODO
        :param sqlArgs: TODO
        
        Not sure what this is, but here is the previous existing docstrings in all their glory::
        
            <c_0 column="invoice_num" op="ISNULL" rem='without invoice' />
            <c_1 column="@anagrafica.provincia" op="IN" jc='AND'>MI,FI,TO</condition>
            <c_2 not="true::B" jc='AND'>
                    <condition column="" op=""/>
                    <condition column="" op="" jc='OR'/>
            </c_2>"""
        if sqlArgs is None:
            sqlArgs = {}
        self.model.virtual_columns
        result = self.db.whereTranslator(self, wherebag, sqlArgs, **kwargs)
        return result, sqlArgs
        
    def frozenSelection(self, fpath):
        """Get a pickled selection and return it
        
        :param fpath: TODO"""
        selection = self.db.unfreezeSelection(fpath)
        assert selection.dbtable == self, 'the frozen selection does not belong to this table'
        return selection
        
    def checkPkey(self, record):
        """TODO
        
        :param record: TODO"""
        pkeyValue = record.get(self.pkey)
        newkey = False
        if pkeyValue in (None, ''):
            newkey = True
            record[self.pkey] = self.newPkeyValue(record=record)
        return newkey
        
    def empty(self):
        """TODO"""
        self.db.adapter.emptyTable(self)
        
    def sql_deleteSelection(self, where, **kwargs):
        """Delete a selection from the table. It works only in SQL so no python trigger is executed
        
        :param where: the sql "WHERE" clause. For more information check the :ref:`sql_where` section
        :param \*\*kwargs: optional arguments for the "where" attribute"""
        todelete = self.query('$%s' % self.pkey, where=where, addPkeyColumn=False, for_update=True,excludeDraft=False ,**kwargs).fetch()
        if todelete:
            self.db.adapter.sql_deleteSelection(self, pkeyList=[x[0] for x in todelete])
            
    #Jeff added the support to deleteSelection for passing no condition so that all records would be deleted
    def deleteSelection(self, condition_field=None, condition_value=None, excludeLogicalDeleted=False, excludeDraft=False,condition_op='=',
                        where=None, **kwargs):
        """TODO
        
        :param condition_field: TODO
        :param condition_value: TODO
        :param excludeLogicalDeleted: boolean. If ``True``, exclude from the query all the records that are
                                      "logical deleted"
        :param excludeDraft: TODO
        :param condition_op: TODO"""
        # if self.trigger_onDeleting:
        if(condition_field and condition_value):
            where = '%s %s :condition_value' % (condition_field, condition_op)
            kwargs['condition_value'] = condition_value
            
        q = self.query(where=where,
                       excludeLogicalDeleted=excludeLogicalDeleted,
                       addPkeyColumn=False,excludeDraft=excludeDraft,
                       for_update=True, **kwargs)
        sel = q.fetch()
        for r in sel:
            self.delete(r)
            # if not self.trigger_onDeleting:
            #  sql delete where

    def notifyDbUpdate(self,record):
        self.db.notifyDbUpdate(self,record)
            
    def touchRecords(self,_pkeys=None,_wrapper=None,_wrapperKwargs=None,_notifyOnly=False,pkey=None,method=None, **kwargs):
        """TODO
        
        :param where: the sql "WHERE" clause. For more information check the :ref:`sql_where` section"""
        if not 'where' in kwargs:
            if pkey:
                _pkeys = [pkey]
            if not _pkeys:
                return
            kwargs['where'] = '$%s IN :_pkeys' %self.pkey
            if isinstance(_pkeys,basestring):
                _pkeys = _pkeys.strip(',').split(',')
            kwargs['_pkeys'] = _pkeys
            kwargs.setdefault('excludeDraft',False)
            kwargs.setdefault('ignorePartition',True)
            kwargs.setdefault('excludeLogicalDeleted',False)
        method = method or 'update'
        sel = self.query(addPkeyColumn=False, for_update=(method=='update'), **kwargs).fetch()
        if _wrapper:
            _wrapperKwargs = _wrapperKwargs or dict()
            sel = _wrapper(sel, **(_wrapperKwargs or dict()))
        if _notifyOnly:
            self.notifyDbUpdate(sel)
            return
        handler = getattr(self,method) if isinstance(method,basestring) else method
        for row in sel:
            row._notUserChange = True
            handler(row, old_record=dict(row))
            
    def existsRecord(self, record):
        """Check if a record already exists in the table and return it (if it is not already in the keys)
        :param record: the record to be checked"""
        if not hasattr(record, 'keys'):
            record = {self.pkey: record}
        return self.db.adapter.existsRecord(self, record)
    
    def checkDuplicate(self,**kwargs):
        """TODO"""
        where = ' AND '.join(['$%s=:%s' % (k, k) for k in kwargs.keys()])
        return self.query(where=where,**kwargs).count()>0
    
    def insertOrUpdate(self, record):
        """Insert a single record if it doesn't exist, else update it
        
        :param record: a dictionary that represent the record that must be updated"""
        pkey = record.get(self.pkey)
        if (not pkey in (None, '')) and self.existsRecord(record):
            return self.update(record)
        else:
            return self.insert(record)

    def countRecords(self):
        return self.query(excludeLogicalDeleted=False,excludeDraft=False).count()
            
    def lock(self, mode='ACCESS EXCLUSIVE', nowait=False):
        """TODO
        
        :param mode: TODO
        :param nowait: boolean. TODO"""
        self.db.adapter.lockTable(self, mode, nowait)

        
    def insert(self, record, **kwargs):
        """Insert a single record
        
        :param record: a dictionary representing the record that must be inserted"""
        self.db.insert(self, record, **kwargs)
        
    def raw_insert(self, record, **kwargs):
        """Insert a single record without triggers
        
        :param record: a dictionary representing the record that must be inserted"""
        self.db.raw_insert(self, record, **kwargs)
            
    def insertMany(self, records, **kwargs):
        self.db.insertMany(self, records, **kwargs)

    def raw_update(self,record=None,old_record=None,pkey=None,**kwargs):
        self.db.raw_update(self, record, pkey=pkey,old_record=old_record,**kwargs)

    def delete(self, record, **kwargs):
        """Delete a single record from this table.
        
        :param record: a dictionary, bag or pkey (string)"""
        if isinstance(record, basestring):
            record = self.recordAs(record, 'dict')
        self.db.delete(self, record, **kwargs)
    
    def updateRelated(self, record,old_record=None):

        for rel in self.relations_many:
            onUpdate = rel.getAttr('onUpdate', '').lower()
            if onUpdate and not (onUpdate in ('i', 'ignore')):
                mpkg, mtbl, mfld = rel.attr['many_relation'].split('.')
                opkg, otbl, ofld = rel.attr['one_relation'].split('.')
                if record.get(ofld) == old_record.get(ofld):
                    return
                relatedTable = self.db.table(mtbl, pkg=mpkg)
                sel = relatedTable.query(columns='*', where='%s = :pid' % mfld,
                                         pid=old_record[ofld], for_update=True).fetch()
                if sel:
                    if onUpdate in ('r', 'raise'):
                        raise self.exception('update', record=record, msg='!!Record referenced in table %(reltable)s',
                                             reltable=relatedTable.fullname)
                    if onUpdate in ('c', 'cascade'):
                        for row in sel:
                            rel_rec = dict(row)
                            rel_rec[mfld] = record[ofld]
                            relatedTable.update(rel_rec,old_record=dict(row))    
                                        
    def deleteRelated(self, record):
        """TODO
        
        :param record: a dictionary, bag or pkey (string)"""
        for rel in self.relations_many:
            onDelete = rel.getAttr('onDelete', '').lower()
            if onDelete and not (onDelete in ('i', 'ignore')):
                mpkg, mtbl, mfld = rel.attr['many_relation'].split('.')
                opkg, otbl, ofld = rel.attr['one_relation'].split('.')
                relatedTable = self.db.table(mtbl, pkg=mpkg)
                sel = relatedTable.query(columns='*', where='%s = :pid' % mfld,
                                         pid=record[ofld], for_update=True,excludeDraft=False).fetch()
                if sel:
                    if onDelete in ('r', 'raise'):
                        raise self.exception('delete', record=record, msg='!!Record referenced in table %(reltable)s',
                                             reltable=relatedTable.fullname)
                    elif onDelete in ('c', 'cascade'):
                        for row in sel:
                            relatedTable.delete(relatedTable.record(row['pkey'], mode='bag'))
                    elif onDelete in ('n','setnull'):
                        for row in sel:
                            rel_rec = dict(row)
                            rel_rec.pop('pkey',None)
                            oldrec = dict(rel_rec)
                            rel_rec[mfld] = None
                            relatedTable.update(rel_rec,oldrec)
                            
    def update(self, record, old_record=None, pkey=None,**kwargs):
        """Update a single record
        
        :param record: TODO
        :param old_record: TODO
        :param pkey: the record :ref:`primary key <pkey>`"""
        self.db.update(self, record, old_record=old_record, pkey=pkey,**kwargs)
        
    def writeRecordCluster(self, recordCluster, recordClusterAttr, debugPath=None):
        """Receive a changeSet and execute insert, delete or update
        
        :param recordCluster: TODO
        :param recordClusterAttr: TODO
        :param debugPath: TODO"""
        def onBagColumns(attributes=None,**kwargs):
            if attributes and '__old' in attributes:
                attributes.pop('__old')
        main_changeSet, relatedOne, relatedMany = self._splitRecordCluster(recordCluster, debugPath=debugPath)
        isNew = recordClusterAttr.get('_newrecord')
        toDelete = recordClusterAttr.get('_deleterecord')
        pkey = recordClusterAttr.get('_pkey')
        invalidFields = recordClusterAttr.get('_invalidFields')
        noTestForMerge = self.attributes.get('noTestForMerge') or self.pkg.attributes.get('noTestForMerge')
        if isNew and toDelete:
            return # the record doesn't exists in DB, there's no need to delete it
        if isNew:
            main_record = main_changeSet
        else:
            old_record = self.record(pkey, for_update=True,bagFields=True).output('bag', resolver_one=False, resolver_many=False)
            main_record = old_record.deepcopy()
            if main_changeSet or toDelete:
                lastTs = recordClusterAttr.get('lastTS')
                changed_TS = lastTs and (lastTs != str(main_record[self.lastTS]))
                if changed_TS and (self.noChangeMerge or toDelete):
                    raise self.exception("save", record=main_record,
                                         msg="Another user modified the record.Operation aborted changed_TS %s  lastTs %s " %(changed_TS,lastTs))
                if toDelete:
                    self.delete(old_record)
                    return
                testForMerge = not noTestForMerge and (changed_TS or (not lastTs) )# the record is modified by another user OR there's no lastTS field to check for modifications
                for fnode in main_changeSet:
                    fname = fnode.label
                    if testForMerge:
                        incompatible = False
                        if fnode.getAttr('_gnrbag'):
                            pass
                            #incompatible = (fnode.getAttr('_bag_md5') != main_record.getAttr(fname, '_bag_md5'))
                        elif fnode.value != main_record[fname]:  # new value is different from value in db
                            incompatible = (fnode.getAttr('oldValue') != main_record[
                                                                         fname]) # value in db is different from oldvalue --> other user changed it
                        if incompatible:
                            raise self.exception("save", record=main_record,
                                                 msg="Incompatible changes: another user modified field %(fldname)s from %(oldValue)s to %(newValue)s"
                                                 ,
                                                 fldname=fname,
                                                 oldValue=fnode.getAttr('oldValue'),
                                                 newValue=main_record[fname])
                    main_record[fname] = fnode.value
        for rel_name, rel_recordClusterNode in relatedOne.items():
            rel_recordCluster = rel_recordClusterNode.value
            rel_recordClusterAttr = rel_recordClusterNode.getAttr()
            rel_column = self.model.column(rel_name)
            rel_tblobj = rel_column.relatedTable().dbtable
            joiner = rel_column.relatedColumnJoiner()
            rel_record = rel_tblobj.writeRecordCluster(rel_recordCluster, rel_recordClusterAttr)
            from_fld = joiner['many_relation'].split('.')[2]
            to_fld = joiner['one_relation'].split('.')[2]
            main_record[from_fld] = rel_record[to_fld]  
            recordClusterAttr['lastTS_%s' %rel_name] = str(rel_record[rel_tblobj.lastTS]) if rel_tblobj.lastTS else None
          
        if self.attributes.get('invalidFields'):
            invalidFields_fld = self.attributes.get('invalidFields')
            main_record[invalidFields_fld] = gnrstring.toJsonJS(invalidFields) if invalidFields else None
            
        if isNew:
            self.insert(main_record,onBagColumns=onBagColumns)
        elif main_changeSet:
            self.update(main_record, old_record=old_record, pkey=pkey,onBagColumns=onBagColumns)
        for rel_name, rel_recordClusterNode in relatedMany.items():
            rel_recordCluster = rel_recordClusterNode.value
            rel_recordClusterAttr = rel_recordClusterNode.getAttr()
            if rel_name.endswith('_removed'):
                rel_name = rel_name[:-8]
            relblock = self.model.getRelationBlock(rel_name)
            many_tblobj = self.db.table(relblock['mtbl'], pkg=relblock['mpkg'])
            many_key = relblock['mfld']
            relKey = main_record[relblock['ofld']]
            if rel_recordClusterAttr.get('one_one',None):
                rel_recordCluster[many_key]=relKey
                many_tblobj.writeRecordCluster(rel_recordCluster, rel_recordClusterAttr)
            else:
                for sub_recordClusterNode in rel_recordCluster:
                    if sub_recordClusterNode.attr.get('_newrecord') and not(
                    sub_recordClusterNode.attr.get('_deleterecord')):
                        sub_recordClusterNode.value[many_key] = relKey
                    many_tblobj.writeRecordCluster(sub_recordClusterNode.value, sub_recordClusterNode.getAttr())
        return main_record
            
    def xmlDebug(self, data, debugPath, name=None):
        """TODO
        
        :param data: TODO
        :param debugPath: TODO
        :param name: TODO"""
        name = name or self.name
        filepath = os.path.join(debugPath, '%s.xml' % name)
        data.toXml(filepath, autocreate=True)
        
    def _splitRecordCluster(self, recordCluster, mainRecord=None, debugPath=None):
        relatedOne = {}
        relatedMany = {}
        if recordCluster:
            nodes = recordCluster.nodes
            revnodes = list(enumerate(nodes))
            revnodes.reverse()
            for j, n in revnodes:
                if n.label.startswith('@'):
                    if n.getAttr('mode') == 'O' :
                        relatedOne[n.label[1:]] = nodes.pop(j)
                    else:
                        relatedMany[n.label] = nodes.pop(j)
        if debugPath:
            self.xmlDebug(recordCluster, debugPath)
            for k, v in relatedOne.items():
                self.xmlDebug(v, debugPath, k)
            for k, v in relatedMany.items():
                self.xmlDebug(v, debugPath, k)
        return recordCluster, relatedOne, relatedMany
        
    def _doFieldTriggers(self, triggerEvent, record,**kwargs):
        trgFields = self.model._fieldTriggers.get(triggerEvent)
        if trgFields:
            for fldname, trgFunc in trgFields:
                if callable(trgFunc):
                    trgFunc(record, fldname)
                else:
                    getattr(self, 'trigger_%s' % trgFunc)(record, fldname=fldname,**kwargs)
                
    def _doExternalPkgTriggers(self, triggerEvent, record,**kwargs):
        for pkg_id in self.db.application.packages.keys():
            trgFunc = getattr(self, 'trigger_%s_%s'%(triggerEvent, pkg_id), None)
            if callable(trgFunc):
                trgFunc(record, **kwargs)


    def newPkeyValue(self,record=None):
        """Get a new unique id to use as :ref:`primary key <pkey>`
        on the current :ref:`database table <table>`"""
        return self.pkeyValue(record=record)


    def pkeyValue(self,record=None):
        pkey = self.model.pkey
        if self.model.column(pkey).dtype in ('L', 'I', 'R'):
            lastid = self.query(columns='max($%s)' % pkey, group_by='*').fetch()[0] or [0]
            return lastid[0] + 1
        elif self.attributes.get('pkey_columns'):
            return '_'.join([record.get(col) for col in self.attributes.get('pkey_columns').split(',') if record.get(col) is not None])
        else:
            return getUuid()
            
    def baseViewColumns(self):
        """TODO"""
        allcolumns = self.model.columns
        result = [k for k, v in allcolumns.items() if v.attributes.get('base_view')]
        if not result:
            result = [col for col, colobj in allcolumns.items() if not colobj.isReserved]
        return ','.join(result)
        
    def getResource(self, path):
        """TODO
        
        :param path: TODO"""
        return self.db.getResource(self, path)
        
        #---------- method to implement via mixin
    def onIniting(self):
        """Hook method called on... TODO"""
        pass
        
    def onInited(self):
        """Hook method called on... TODO"""
        pass

    @property
    def currentTrigger(self):
        trigger_stack =  self.db.currentEnv.get('_trigger_stack')
        if trigger_stack:
            return trigger_stack.parentItem
        
    def trigger_onInserting(self, record):
        """Hook method. Allow to act on *record* during the record insertion
        
        :param record: the record"""
        #self.trigger_onUpdating(record) Commented out Miki 2009/02/24
        pass
        
    def trigger_onInserted(self, record):
        """Hook method. Allow to act on *record* after the record insertion
        
        :param record: the record"""
        #self.trigger_onUpdated(record) Commented out Miki 2009/02/24
        pass
        
    def trigger_onUpdating(self, record, old_record=None):
        """Hook method. Allow to act on *record* and *old_record*
        during the record update
        
        :param record: the new record
        :param old_record: the old record to be substituted by the new one"""
        pass
        
    def trigger_onUpdated(self, record, old_record=None):
        """Hook method. Allow to act on *record* and *old_record*
        after the record update
        
        :param record: the new record
        :param old_record: the old record to be substituted by the new one"""
        pass
        
    def trigger_onDeleting(self, record):
        """Hook method. Allow to act on *record* during the record delete
        
        :param record: the new record"""
        pass
        
    def trigger_onDeleted(self, record):
        """Hook method. Allow to act on *record* after the record delete
        
        :param record: the new record"""
        pass
        
    def protect_update(self, record, old_record=None):
        """TODO
        
        :param record: TODO
        :param old_record: TODO"""
        pass
        
    def protect_delete(self, record):
        """TODO
        
        :param record: TODO"""
        pass
        
    def protect_validate(self, record, old_record=None):
        """TODO
        
        :param record: TODO
        :param old_record: TODO"""
        pass
        
    def diagnostic_errors(self, record, old_record=None):
        """TODO
        
        :param record: TODO
        :param old_record: TODO"""
        print 'You should override for diagnostic'
        return
    
    def diagnostic_warnings(self, record, old_record=None):
        """TODO
        
        :param record: TODO
        :param old_record: TODO"""
        print 'You should override for diagnostic'
        return


    def trigger_assignCounters(self,record=None,old_record=None):
        "Inside dbo. You can override"
        pass

    def trigger_releaseCounters(self,record=None):
        "Inside dbo"
        pass

    def _isReadOnly(self,record):
        if self.attributes.get('readOnly'):
            return True
        if record.get('__protection_tag'):
            return not (record['__protection_tag'] in self.db.currentEnv['userTags'].split(','))

    def _islocked_write(self,record):
        return self._isReadOnly(record) or self.islocked_write(record)
    
    def islocked_write(self,record):
        #OVERRIDE THIS
        pass

    def _islocked_delete(self,record):
        return self._isReadOnly(record) or self.attributes.get('readOnly') or self.islocked_delete(record)

    def islocked_delete(self,record):
        #OVERRIDE THIS
        pass

    def isDraft(self,record):
        if self.draftField:
            return record[self.draftField]
        return False


    def check_updatable(self, record,ignoreReadOnly=None):
        """TODO
        
        :param record: TODO"""
        try:
            self.protect_update(record,record)
            return True
        except EXCEPTIONS['protect_update'], e:
            return False
            
    def check_deletable(self, record):
        """TODO
        
        :param record: TODO"""
        try:
            self.protect_delete(record)
            return True
        except EXCEPTIONS['protect_delete'], e:
            return False
            
    def columnsFromString(self, columns=None):
        """TODO
        
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section"""
        result = []
        if not columns:
            return result
        if isinstance(columns, basestring):
            columns = gnrstring.splitAndStrip(columns)
        for col in columns:
            if not col[0] in ('@','$','('):
                col = '$%s' % col
                #FIX 
            result.append(col)
        return result
        
    def getQueryFields(self, columns=None, captioncolumns=None):
        """TODO
        
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        :param captioncolumns: TODO"""
        columns = columns or self.model.queryfields or captioncolumns
        return self.columnsFromString(columns)
        
    def rowcaptionDecode(self, rowcaption=None):
        """TODO
        
        :param rowcaption: the textual representation of a record in a user query.
                           For more information, check the :ref:`rowcaption` section
        """
        rowcaption = rowcaption or self.rowcaption
        if not rowcaption:
            return [], ''
            
        if ':' in rowcaption:
            fields, mask = rowcaption.split(':', 1)
        else:
            fields, mask = rowcaption, None
        fields = fields.replace('*', self.pkey)
        fields = self.columnsFromString(fields)
        if not mask:
            mask = ' - '.join(['%s' for k in fields])
        return fields, mask
        
    def recordCaption(self, record, newrecord=False, rowcaption=None):
        """TODO
        
        :param record: TODO
        :param newrecord: boolean. TODO
        :param rowcaption: the textual representation of a record in a user query.
                           For more information, check the :ref:`rowcaption` section
        """
        if newrecord:
            return self.newrecord_caption
        else:
            fields, mask = self.rowcaptionDecode(rowcaption)
            if not fields:
                return ''
            fields = [f.lstrip('$') for f in fields]
            if not isinstance(record, Bag):
                fields = [self.db.colToAs(f) for f in fields]
            cols = [(c, gnrstring.toText(record[c], locale=self.db.locale)) for c in fields]
            if '$' in mask:
                caption = gnrstring.templateReplace(mask, dict(cols))
            else:
                caption = mask % tuple([v for k, v in cols])
            return caption
            
    def colToAs(self, col):
        """TODO
        
        :param col: TODO"""
        return self.db.colToAs(col)
        
    def relationName(self, relpath):
        """TODO
        
        :param relpath: TODO"""
        relpath = self.model.resolveRelationPath(relpath)
        attributes = self.model.relations.getAttr(relpath)
        joiner = attributes['joiner']
        if joiner['mode'] == 'M':
            relpkg, reltbl, relfld = joiner['many_relation'].split('.')
            targettbl = '%s.%s' % (relpkg, reltbl)
            result = joiner.get('many_rel_name') or self.db.table(targettbl).name_plural
        else:
            relpkg, reltbl, relfld = joiner['one_relation'].split('.')
            targettbl = '%s.%s' % (relpkg, reltbl)
            result = joiner.get('one_rel_name') or self.db.table(targettbl).name_long
        return result
        
    
    @deprecated
    def xmlDump(self, path):
        """TODO
        
        :param path: TODO"""
        filepath = os.path.join(path, '%s_dump.xml' % self.name)
        records = self.query(excludeLogicalDeleted=False,excludeDraft=False).fetch()
        result = Bag()
        
        for r in records:
            r = dict(r)
            pkey = r.pop('pkey')
            result['records.%s' % pkey.replace('.', '_')] = Bag(r)
        result.toXml(filepath, autocreate=True)
    
    @deprecated
    def importFromXmlDump(self, path):
        """TODO
        
        :param path: TODO"""
        if '.xml' in path:
            filepath = path
        else:
            filepath = os.path.join(path, '%s_dump.xml' % self.name)
        data = Bag(filepath)
        if data:
            for record in data['records'].values():
                record.pop('_isdeleted')
                self.insert(record)
             
    def copyToDb(self, dbsource, dbdest, empty_before=False, excludeLogicalDeleted=False, excludeDraft=False,
                 source_records=None, bagFields=True,source_tbl_name=None, raw_insert=None,_converters=None, **querykwargs):
        """TODO
        
        :param dbsource: sourcedb
        :param dbdest: destdb
        :param empty_before: boolean. TODO
        :param excludeLogicalDeleted: boolean. If ``True``, exclude from the query all the records that are
                                      "logical deleted"
        :param excludeDraft: TODO
        :param source_records: TODO"""
        tbl_name = self.fullname
        source_tbl = dbsource.table(source_tbl_name or tbl_name)
        dest_tbl = dbdest.table(tbl_name)
        querykwargs['addPkeyColumn'] = False
        querykwargs['excludeLogicalDeleted'] = excludeLogicalDeleted
        querykwargs['excludeDraft'] = excludeDraft
        source_records = source_records or source_tbl.query(bagFields=bagFields,**querykwargs).fetch()
        insertOnly= False
        if empty_before:
            insertOnly = True
            dest_tbl.empty()
        elif raw_insert and dest_tbl.countRecords()==0:
            insertOnly = True
        for record in source_records:
            record = dict(record)
            if _converters:
                for c in _converters:
                    record = getattr(self,c)(record)
            if insertOnly:
                if raw_insert:
                    dest_tbl.raw_insert(record)
                else:
                    dest_tbl.insert(record)
            else:
                dest_tbl.insertOrUpdate(record)
    
    def copyToDbstore(self,pkey=None,dbstore=None,bagFields=True,**kwargs):
        """TODO
        
        :param pkey: the record :ref:`primary key <pkey>`
        :param dbstore: TODO
        :param bagFields: TODO"""
        queryargs = kwargs
        if pkey:
            queryargs = dict(where='$pkey=:pkey',pkey=pkey)
        records = self.query(addPkeyColumn=False,bagFields=bagFields,**queryargs).fetch()
        with self.db.tempEnv(storename=dbstore):
            for rec in records:
                self.insertOrUpdate(rec)
            self.db.deferredCommit()
                
    def exportToAuxInstance(self, instance, empty_before=False, excludeLogicalDeleted=True,
                            excludeDraft=True, source_records=None, **querykwargs):
        """TODO
        
        :param instance: the name of the instance
        :param empty_before: boolean. TODO
        :param excludeLogicalDeleted: boolean. If ``True``, exclude from the query all the records that are
                                      "logical deleted"
        :param excludeDraft: TODO
        :param source_records: TODO"""
        if isinstance(instance,basestring):
            instance = self.db.application.getAuxInstance(instance)
        dest_db = instance.db
        self.copyToDb(self.db,dest_db,empty_before=empty_before,excludeLogicalDeleted=excludeLogicalDeleted,
                        excludeDraft=True,source_records=source_records,**querykwargs)
                        
    def importFromAuxInstance(self, instance, empty_before=False, excludeLogicalDeleted=False,
                              excludeDraft=False, source_records=None,source_tbl_name=None, raw_insert=None, **querykwargs):
        """TODO
        
        :param instance: the name of the instance
        :param empty_before: boolean. TODO
        :param excludeLogicalDeleted: boolean. If ``True``, exclude from the query all the records that are
                                      "logical deleted"
        :param excludeDraft: TODO
        :param source_records: TODO"""
        if isinstance(instance,basestring):
            instance = self.db.application.getAuxInstance(instance)

        source_db = instance.db
        src_version = int(source_db.table(source_tbl_name or self.fullname).attributes.get('version') or 0)
        dest_version = int(self.attributes.get('version') or 0)
        converters = None
        if src_version!=dest_version:
            assert dest_version > src_version, 'table %s version conflict from %i to %i' %(self.fullname,src_version,dest_version)
            converters = ['_convert_%i_%i' %(x,x+1) for x in range(src_version,dest_version)]
            if filter(lambda m: not hasattr(self,m), converters):
                print 'missing converter',self.fullname
                return 
        self.copyToDb(source_db,self.db,empty_before=empty_before,excludeLogicalDeleted=excludeLogicalDeleted,
                      source_records=source_records,excludeDraft=excludeDraft,
                      raw_insert=raw_insert,
                      source_tbl_name=source_tbl_name,_converters=converters,**querykwargs)
                      
    def relationExplorer(self, omit='', prevRelation='', dosort=True, pyresolver=False, **kwargs):
        """TODO
        
        :param omit: TODO
        :param prevRelation: TODO
        :param dosort: boolean. TODO
        :param pyresolver: boolean. TODO"""
        def xvalue(attributes):
            if not pyresolver:
                return
            if attributes.get('one_relation'):
                if attributes['mode'] == 'O':
                    relpkg, reltbl, relfld = attributes['one_relation'].split('.')
                else:
                    relpkg, reltbl, relfld = attributes['many_relation'].split('.')
                targettbl = self.db.table('%s.%s' % (relpkg, reltbl))
                return BagCbResolver(targettbl.relationExplorer, omit=omit,
                                     prevRelation=attributes['fieldpath'], dosort=dosort,
                                     pyresolver=pyresolver, **kwargs)
                                     
        def resultAppend(result, label, attributes, omit):
            gr = attributes.get('group') or ' '
            if '%' in gr:
                subgroups = dictExtract(attributes,'subgroup_')
                gr = gr %subgroups
                attributes['group'] = gr
            grin = gr[0]
            if grin == '*' or grin == '_':
                attributes['group'] = gr[1:]
            if grin not in omit:
                result.setItem(label, xvalue(attributes), attributes)
                
        def convertAttributes(result, relnode, prevRelation, omit):
            attributes = dict(relnode.getAttr())
            attributes['fieldpath'] = gnrstring.concat(prevRelation, relnode.label)
            if 'joiner' in attributes:
                joiner = attributes.pop('joiner')
                attributes.update(joiner)
                attributes['name_long'] = self.relationName(relnode.label)
                if attributes['mode'] == 'M':
                    attributes['group'] = attributes.get('many_group') or 'zz'
                    attributes['dtype'] = 'RM'
                else:
                    attributes['group'] = attributes.get('one_group')
                    attributes['dtype'] = 'RO'
            else:
                attributes['name_long'] = attributes.get('name_long') or relnode.label
            resultAppend(result, relnode.label, attributes, omit)
            
        tblmodel = self.model
        result = Bag()
        for relnode in tblmodel.relations: # add columns relations
            convertAttributes(result, relnode, prevRelation, omit)
            
        for vcolname, vcol in tblmodel.virtual_columns.items():
            targetcol = self.column(vcolname)
            attributes = dict(targetcol.attributes)
            attributes.update(vcol.attributes)
            attributes['fieldpath'] = gnrstring.concat(prevRelation, vcolname)
            attributes['name_long'] = attributes.get('name_long') or vcolname
            attributes['dtype'] = attributes.get('dtype') or 'T'
            resultAppend(result, vcolname, attributes, omit)
            
        for aliastbl in tblmodel.table_aliases.values():
            relpath = tblmodel.resolveRelationPath(aliastbl.relation_path)
            attributes = dict(tblmodel.relations.getAttr(relpath))
            attributes['name_long'] = aliastbl.attributes.get('name_long') or self.relationName(relpath)
            attributes['group'] = aliastbl.attributes.get('group')
            attributes['fieldpath'] = gnrstring.concat(prevRelation, aliastbl.name)
            joiner = attributes.pop('joiner')
            attributes.update(joiner)
            mode = attributes.get('mode')
            if mode == 'O':
                attributes['dtype'] = 'RO'
            elif mode == 'M':
                attributes['dtype'] = 'RM'
            resultAppend(result, aliastbl.name, attributes, omit)
        if dosort:
            result.sort(lambda a, b: cmp(a.getAttr('group', '').split('.'), b.getAttr('group', '').split('.')))
            grdict = dict([(k[6:], v) for k, v in self.attributes.items() if k.startswith('group_')])
            if not grdict:
                return result
            newresult = Bag()
            for node in result:
                nodeattr = node.attr
                grplist=(nodeattr.get('group') or '').split('.')
                if grplist[-1] and grplist[-1].isdigit():
                    grplist.pop()
                if grplist and grplist[0] in grdict:
                    for j,kg in enumerate(grplist):
                        grplevel='.'.join(grplist[0:j+1])
                        if not grplevel in newresult:
                            newresult.setItem(grplevel, None, name_long=grdict.get(grplevel,grplevel.split('.')[-1]))
                    newresult.setItem('%s.%s' % ('.'.join(grplist), node.label), node.getValue(), node.getAttr())

                else:
                    newresult.setItem(node.label, node.getValue(), node.getAttr())
            return newresult
        else:
            return result

    def setQueryCondition(self,condition_name,condition):
        self.db.currentEnv['env_%s_condition_%s' %(self.fullname.replace('.','_'),condition_name)] = condition
                    
if __name__ == '__main__':
    pass