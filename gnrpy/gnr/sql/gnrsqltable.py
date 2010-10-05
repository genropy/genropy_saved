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

__version__='1.0b'

#import weakref
import os

from gnr.core import gnrstring
from gnr.core.gnrlang import GnrObject
from gnr.core.gnrbag import Bag, BagCbResolver
#from gnr.sql.gnrsql_exceptions import GnrSqlException,GnrSqlSaveException, GnrSqlApplicationException
from gnr.sql.gnrsqldata import SqlRecord, SqlQuery
from gnr.sql.gnrsql import GnrSqlException
from gnr.core.gnrlang import getUuid
import logging
gnrlogger = logging.getLogger('gnr.sql.gnrsqltable')

class GnrSqlSaveException(GnrSqlException): 
    code='GNRSQL-03'
    description='!!Genro SQL Save Exception'
    caption="!!The record %(rowcaption)s in table %(tablename)s cannot be saved:%(msg)s" 
    
class GnrSqlDeleteException(GnrSqlException): 
    code='GNRSQL-04'
    description='!!Genro SQL Delete Exception'
    caption="!!The record %(rowcaption)s in table %(tablename)s cannot be deleted:%(msg)s" 

class GnrSqlProtectUpdateException(GnrSqlException):
    code='GNRSQL-11'
    description='!!Genro SQL Protect Update Exception'
    caption="!!The record %(rowcaption)s in table %(tablename)s is not updatable:%(msg)s" 

class GnrSqlProtectDeleteException(GnrSqlException):
    code='GNRSQL-12'
    description='!!Genro SQL Protect Update Exception'
    caption="!!The record %(rowcaption)s in table %(tablename)s is not deletable:%(msg)s"  

class GnrSqlProtectValidateException(GnrSqlException):
    code='GNRSQL-13'
    description='!!Genro SQL Protect Validate Exception'
    caption="!!The record %(rowcaption)s in table %(tablename)s contains invalid data:%(msg)s"
    
EXCEPTIONS= {'save': GnrSqlSaveException,
             'delete': GnrSqlDeleteException,
             'protect_update':GnrSqlProtectUpdateException,
             'protect_delete':GnrSqlProtectDeleteException,
             'protect_validate':GnrSqlProtectValidateException}
     
class SqlTable(GnrObject):
    """This is the base classe for database tables.
    
    Your tables will inherit from it (altough it won't be explicit in your code, since it's done by GenroPy mixin machinery).
    
    In your webpage, package or table methods, you can get a reference to a table by name in this way::

        self.db.table('packagename.tablename')
    
    You can also get them from the application instance::
    
        app = GnrApp('instancename')
        app.db.table('packagename.tablename')
    
    """
        
    def __init__(self, tblobj):
        self._model = tblobj
        self.name = tblobj.name
        self.fullname = tblobj.fullname
        self.name_long = tblobj.name_long
        self.name_plural = tblobj.name_plural
        
    def use_dbstores(self):
        return False
        
    def exception(self,exception,record=None,msg=None,**kwargs):
        if exception in EXCEPTIONS:
            rowcaption=''
            if record:  
                rowcaption=self.recordCaption(record)
            e= EXCEPTIONS[exception](tablename=self.fullname,
                                         rowcaption=rowcaption,
                                         msg=msg,**kwargs)
            if self.db.application and self.db.application.site and self.db.application.site.currentPage:
                e.setLocalizer(self.db.application.site.currentPage.localizer)
            return e
        raise
         
    def __repr__(self):
        return "<SqlTable %s>" % repr(self.fullname)

    @property
    def model(self):
        """property model.

        Return the corresponding DbTableObj object"""
        return self._model

    @property
    def pkg(self):
        """property pkg.

        Return the DbPackageObj object that contains the current table"""
        return self.model.pkg
    
    @property
    def db(self):
        """property db

        Return the GnrSqlDb object"""
        return self.model.db
    dbroot = db
    
    def column(self,name):
        """Returns a column object.

        :param name: A column's name or a relation path starting from the current table. (eg. ``@director_id.name``)
        """
        return self.model.column(name)
        
    def fullRelationPath(self,name):
        return self.model.fullRelationPath(name)
    
    def getColumnPrintWidth(self, column):
        if column.dtype in ['A','C','T','X','P']:
            size = column.attributes.get('size',None)
            if not size:
                if column.dtype == 'T':
                    result=35
                else:
                    result=12
            elif isinstance(size,basestring):
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
                 result=size
        else:
            result=gnrstring.guessLen(column.dtype,
                                      format=column.attributes.get('print_format',None),
                                      mask=column.attributes.get('print_mask',None))
        
        namelong=column.attributes.get('name_long','untitled')
        if '\n' in namelong:
            namelong=namelong.split('\n')
            nl=[len(x) for x in namelong]
            headerlen=max[nl]
        else:
            headerlen= len(namelong)
        return max(result, headerlen)

    
    @property
    def attributes(self):
        return self.model.attributes
    
    @property
    def pkey(self):
        """property db

        Return the DbColumnObj object"""
        return self.model.pkey

    @property
    def lastTS(self):
        """property db

        Return the DbColumnObj object"""
        return self.model.lastTS
    
    @property
    def logicalDeletionField(self):
        """property db

        Return the DbColumnObj object"""
        return self.model.logicalDeletionField

    @property
    def noChangeMerge(self):
           """property db

           Return the DbColumnObj object"""
           return self.model.noChangeMerge
    
    @property
    def rowcaption(self):
        """property rowcaption.

        Returns the table's rowcaption"""
        return self.model.rowcaption
    
    @property
    def columns(self):
        """property columns

        Returns the DbColumnListObj object"""
        return self.model.columns
    
    @property
    def relations(self):
        """property columns
        
        Returns the DbColumnListObj object"""
        return self.model.relations
    
    @property
    def indexes(self):
        """property indexes
        
        Returns the DbIndexListObj object"""
        return self.model.indexes

    @property
    def relations_one(self):
        """property relations_one
        
        Return a bag of relations that start from the current table"""
        return self.model.relations_one
    
    @property
    def relations_many(self):
        """property relations_many
        
        Return a bag of relations that point to the current table"""
        return self.model.relations_many
    
    def recordCoerceTypes(self,record,null='NULL'):
        """Check and coerce types in record.
        
        :param record: an object implementing dict interface as colname, colvalue
        """
        converter=self.db.typeConverter
        for k in record.keys():
            if not k.startswith('@'):
                colattr=self.column(k).attributes
                dtype=self.column(k).dtype
                v=record[k]
                if (v is None) or (v == null):
                    record[k]=None
                elif dtype=='B' and not isinstance(v,basestring):
                    record[k] = bool(v)
                else:
                    if dtype and isinstance(v,basestring):
                        if not dtype in ['T','A','C']:
                            v=converter.fromText(record[k],dtype)
                    if 'rjust' in colattr:
                        v=v.rjust(int(colattr['size']),colattr['rjust'])
                    
                    elif 'ljust' in  colattr:
                        v=v.ljust(int(colattr['size']),colattr['ljust'])
                    record[k]=v
    
    def buildrecord(self, fields, resolver_one=None, resolver_many=None):
        newrecord = Bag()
        for fld_node in self.model.relations:
            fld=fld_node.label
            if fld.startswith('@'):
                info = dict(fld_node.getAttr())
                attrs=info.pop('joiner')[0]
                if attrs['mode'] == 'O': # or extra_one_one:
                    #print 'many_one: %s'%str(attrs)
                    if resolver_one:
                        mpkg, mtbl, mfld = attrs['many_relation'].split('.')
                        info.pop('many_relation',None)
                        info['_from_fld'] = attrs['many_relation']
                        info['_target_fld'] = attrs['one_relation']
                        info['mode']=attrs['mode']
                        
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
                if dtype=='X':
                    try:
                        v = Bag(v)
                    except:
                        pass
            
            newrecord.setItem(fld, v, info)
        return newrecord
    
    def buildrecord_(self, fields):
        newrecord = Bag()
        for fld in self.columns.keys():
            v = fields.get(fld)
            info = dict(self.columns[fld].attributes)
            dtype = info.get('dtype')
            if dtype=='X':
                try:
                    v = Bag(v)
                except:
                    pass
            
            newrecord.setItem(fld, v, info)
        return newrecord
    
    def newrecord(self, assignId=False, resolver_one=None, resolver_many=None, **kwargs):
        newrecord = self.buildrecord(kwargs, resolver_one=resolver_one, resolver_many=resolver_many)
        if assignId:
            newrecord[self.pkey] = self.newPkeyValue()
        return newrecord
        
    def record(self, pkey=None, where=None,
               lazy=None, eager=None, mode=None, relationDict=None, ignoreMissing=False,virtual_columns=None,
               ignoreDuplicate=False, bagFields=True, joinConditions=None, sqlContextName=None,
               for_update=False, **kwargs):
        """
        This method is used to get a single record of the table. It returns a SqlRecordResolver.
        The record can be identified by
        - its primary key
        - one or more conditions passed as kwargs (e.g. username='foo')
        - a where condition
         
        :param pkey: record primary key.
        :param where: (optional) This is the sql "WHERE" clause. We suggest not to use hardcoded values into the where clause, but
            refer to variables passed to the selection method as kwargs
            e.g. where="$date BETWEEN :mybirthday AND :christmas", mybirthday=mbd, christmas=xmas
        :param lazy:
        :param eager:
        :param mode: bag, dict, json
        :param relationDict: (optional) this is a dictionary that contains couples composed by fieldName and relationPath
            e.g. {'$member_name':'@member_id.name'}
        
        """
        record = SqlRecord(self, pkey=pkey, where=where,
                           lazy=lazy, eager=eager,
                           relationDict=relationDict,
                           ignoreMissing=ignoreMissing,
                           virtual_columns=virtual_columns,
                           ignoreDuplicate=ignoreDuplicate,
                           joinConditions=joinConditions, sqlContextName=sqlContextName,
                           bagFields=bagFields,for_update=for_update, **kwargs)
        
        if mode:
            return record.output(mode)
        else:
            return record
        
    def recordAs(self, record, mode='bag'):
        """Returns a record in the specified mode.
        
        It accepts and return a record as a bag, dict or primary pkey (as a string).
        
        :param record:      a bag, a dict or a string (i.e. the record's pkey)
        :param mode:        'dict' or 'bag' or 'pkey'
        :returns:           a bag, a dict or a string (i.e. the record's pkey)
        """
        if isinstance(record, basestring):
            if mode == 'pkey':
                return record
            else:
                return self.record(pkey = record, mode=mode)
        if mode=='pkey':
            # The record is either a dict or a bag, so it accepts indexing operations
            return record.get('pkey', None) or record.get(self.pkey)
        if mode=='dict' and not isinstance(record, dict):
            return dict([(k, v) for k,v in record.items() if not k.startswith('@')])
        if mode=='bag' and not isinstance(record, Bag):
            return self.record(pkey = record.get('pkey', None) or record.get(self.pkey), mode=mode)
        return record
            
        
    def defaultValues (self):
        """Override this to assign defaults to new record.
           return a dictionary: fill it with defaults
        """
        return dict( [(x.name, x.attributes['default'])for x in self.columns.values() if 'default' in x.attributes])

    
    def query(self, columns='*', where=None, order_by=None,
              distinct=None, limit=None, offset=None,
              group_by=None, having=None, for_update=False,
              relationDict=None, sqlparams=None,excludeLogicalDeleted=True,
              addPkeyColumn=True,locale=None,
              mode=None, **kwargs):
        """This method return an object SqlQuery object which represents a query that
        can be executed with different modes.
           
       :param columns:  it represents what the 'SELECT' clause in the traditional SQL query.
          
                        It is a string of column names and related fields separated by comma.
                        Each column's name is prefixed with '$'. Related fields uses a syntax based on the char '@'
                        and 'dot notation'.
                        e.g. "@member_id.name".For selecting all columns use the char '*'.
                        columns parameter accepts also special statements such as 'COUNT','DISTINCT' and 'SUM'.
       
       :param where:    (optional) This is the sql "WHERE" clause. We suggest not
                        to use hardcoded values into the where clause, but
                        refer to variables passed to the query method as kwargs
                        because using this way will look after all data conversion and string quoting automatically
                        e.g. where="$date BETWEEN :mybirthday AND :christmas", mybirthday=mbd, christmas=xmas
       
       :param order_by: (optional)  this param corresponds to sql ORDER BY operator
       :param distinct: (optional)  this param corresponds to sql DISTINCT operator
       :param limit: (optional)  number of result's rows.
       :param offset: (optional)  this param corresponds to sql OFFSET operator
       :param group_by: (optional)  this param corresponds to sql GROUP BY operator
       :param having: (optional)  this param corresponds to sql HAVING operator
       :param relationDict: (optional) a dictionary which associates relationPath names
                                    with an alias name. eg: {'$member_name':'@member_id.name'}
       :param sqlparams: (optional)  an optional dictionary for sql query parameters.
       
       :param kwargs: another way to pass sql query parameters
        """
        query = SqlQuery(self, columns=columns, where=where, order_by=order_by,
                         distinct=distinct, limit=limit, offset=offset,
                         group_by=group_by, having=having, for_update=for_update,
                         relationDict=relationDict, sqlparams=sqlparams,
                         excludeLogicalDeleted=excludeLogicalDeleted,
                         addPkeyColumn=addPkeyColumn,locale=locale,
                         **kwargs)
        
        return query
    
    def batchUpdate(self,updater=None,**kwargs):
        fetch = self.query(addPkeyColumn=False,for_update=True,**kwargs).fetch()
        for row in fetch:
            new_row = dict(row)
            if callable(updater):
                updater(new_row)
            elif isinstance(updater,dict):
                new_row.update(updater)
            self.update(new_row,row)
            
    def readColumns(self,pkey=None,columns=None, where=None, **kwargs):
        where = where or '$%s=:pkey' %self.pkey
        kwargs.pop('limit',None)
        fetch = self.query(columns=columns,limit=1,where=where,
                           pkey=pkey,addPkeyColumn=False, **kwargs).fetch()
        if not fetch:
            row = [None for x in columns.split(',')]
        else:
            row = fetch[0]
        if len(row)==1:
            row = row[0]
        return row
    
    def sqlWhereFromBag(self, wherebag, sqlArgs=None,**kwargs):
        """**TODO:** Documentation?

        Not sure what this is, but here is the existing docstring in all its glory::
        
            <c_0 column="invoice_num" op="ISNULL" rem='without invoice' />
            <c_1 column="@anagrafica.provincia" op="IN" jc='AND'>MI,FI,TO</condition>
            <c_2 not="true::B" jc='AND'>
                    <condition column="" op=""/>
                    <condition column="" op="" jc='OR'/>
            </c_2>
        """
        if sqlArgs is None:
            sqlArgs = {}
        result = self.db.whereTranslator(self, wherebag, sqlArgs,**kwargs)
        return result, sqlArgs
    
    def frozenSelection(self, fpath):
        """it gets a pickled selection"""
        selection = self.db.unfreezeSelection(fpath)
        assert selection.dbtable == self,'the frozen selection does not belong to this table'
        return selection
    
    def checkPkey(self,record):
        pkeyValue = record.get(self.pkey)
        newkey = False
        if pkeyValue in (None,''):
            newkey = True
            record[self.pkey] = self.newPkeyValue()
        return newkey
    
    def empty(self):
        self.db.adapter.emptyTable(self)
    
    
    def sql_deleteSelection(self, where,**kwargs):
        """Delete a selection from the table. It works only in SQL so
        no python trigger is executed.
        :param tblobj: the table object
        :param where: the where condition
        :param kwargs : arguments for where
        """
        todelete=self.query('$%s'%self.pkey, where=where,addPkeyColumn=False,for_update=True, **kwargs).fetch()
        if todelete:
            self.db.adapter.sql_deleteSelection(self, pkeyList=[x[0] for x in todelete])
        
    #Jeff added the support to deleteSelection for passing no condition so that all records would be deleted
    def deleteSelection(self, condition_field=None, condition_value=None, excludeLogicalDeleted=False,condition_op='='):
        # if self.trigger_onDeleting:
        if(condition_field and condition_value):
            where = '%s %s :value' % (condition_field,condition_op)
        else:
            where = ''
        q= self.query(where=where,
                        excludeLogicalDeleted=excludeLogicalDeleted,
                         value=condition_value,
                         addPkeyColumn=False,
                         for_update=True)
        sel = q.fetch()
        for r in sel:
            self.delete(r)
        # if not self.trigger_onDeleting:
        #  sql delete where
    
    def touchRecords(self, where=None,**kwargs):
        sel = self.query(where=where, addPkeyColumn=False,for_update=True,**kwargs).fetch()
        for row in sel:
            row._notUserChange = True
            self.update(row)
        
    def existsRecord(self, record):
        """This method check if a record already exists in the table"""
        if not hasattr(record, 'keys'):
            record = {self.pkey: record}
        return self.db.adapter.existsRecord(self, record)
    
    def insertOrUpdate(self, record):
        """This method inserts or updates a single record.
        If the record doesn't exist it inserts, else it updates.
        :param record_data: a dictionary that represent the record that must be updated
        """
        pkey = record.get(self.pkey)
        if (not pkey in (None,'')) and self.existsRecord(record):
            return self.update(record)
        else:
            return self.insert(record)
    
    def lock(self, mode='ACCESS EXCLUSIVE', nowait=False):
        self.db.adapter.lockTable(self, mode, nowait)
        
        
    def insert(self, record):
        """This method inserts a single record.
        :param record_data: a dictionary that represent the record that must be inserted
        """
        self.db.insert(self, record)
    
    def delete(self, record):
        """Delete a single record from this table.
        
        :param record: a dictionary, bag or pkey (string)
        """
        if isinstance(record, basestring):
            record = self.recordAs(record,'dict')
        self.db.delete(self, record)
    
    def deleteRelated(self, record):
        for rel in self.relations_many:
            onDelete=rel.getAttr('onDelete','').lower()
            if onDelete and not (onDelete in ('i' ,'ignore')):
                mpkg, mtbl, mfld = rel.attr['many_relation'].split('.')
                opkg, otbl, ofld = rel.attr['one_relation'].split('.')
                relatedTable = self.db.table(mtbl,pkg=mpkg)
                sel = relatedTable.query(columns='*', where='%s = :pid' % mfld,
                                            pid=record[ofld], for_update=True).fetch()
                if sel:
                    if onDelete in ('r' ,'raise'):
                        raise self.exception('delete',record=record,msg='!!Record referenced in table %(reltable)s',reltable=relatedTable.fullname)
                    elif onDelete in ('c' ,'cascade') :
                        for row in sel:
                            relatedTable.delete(relatedTable.record(row['pkey'], mode='bag'))
        
    def update(self, record, old_record=None, pkey=None):
        """This method updates a single record.
        :param record_data: a dictionary that represent the record that must be updated
        """
        self.db.update(self, record, old_record=old_record, pkey=pkey)

    def writeRecordCluster(self, recordCluster,recordClusterAttr, debugPath=None):
        """This method receives a changeSet and executes insert, delete or update
        :param record_data: a dictionary that represent the record that must be updated
        """
        main_changeSet, relatedOne, relatedMany = self._splitRecordCluster(recordCluster, debugPath=debugPath)
        isNew = recordClusterAttr.get('_newrecord')
        toDelete = recordClusterAttr.get('_deleterecord')
        pkey = recordClusterAttr.get('_pkey')
        noTestForMerge=self.pkg.attributes.get('noTestForMerge')
        if isNew and toDelete:
            return # the record doesn't exists in DB, there's no need to delete it
        
        if isNew:
            main_record = main_changeSet
        else:
            old_record = self.record(pkey, for_update=True, mode='bag')
            main_record = old_record.deepcopy()
            lastTs = recordClusterAttr.get('lastTS')
            changed_TS = lastTs and (lastTs != str(main_record[self.lastTS]))
            if changed_TS and (self.noChangeMerge or toDelete):
                raise self.exception ("save",record=main_record,msg="Another user modified the record.Operation aborted")
            if toDelete:
                self.delete(old_record)
                return
            testForMerge = (not noTestForMerge ) and (changed_TS or (not lastTs) )# the record is modified by another user OR there's no lastTS field to check for modifications
            for fnode in main_changeSet:
                fname = fnode.label
                if testForMerge:
                    incompatible = False
                    if fnode.getAttr('_gnrbag'):
                        incompatible = (fnode.getAttr('_bag_md5') != main_record.getAttr(fname, '_bag_md5'))
                    elif fnode.value != main_record[fname]:  # new value is different from value in db
                        incompatible = (fnode.getAttr('oldValue') != main_record[fname]) # value in db is different from oldvalue --> other user changed it
                    if incompatible:
                        raise self.exception("save",record=main_record,
                                      msg="Incompatible changes: another user modified field %(fldname)s from %(oldValue)s to %(newValue)s",
                                      fldname=fname, 
                                      oldValue=fnode.getAttr('oldValue'),
                                      newValue= main_record[fname])
                main_record[fname] = fnode.value
        for rel_name, rel_recordClusterNode in relatedOne.items():
            rel_recordCluster = rel_recordClusterNode.value
            rel_recordClusterAttr = rel_recordClusterNode.getAttr()
            rel_column = self.model.column(rel_name)
            rel_tblobj = rel_column.relatedTable().dbtable
            joiner = rel_column.relatedColumnJoiner()
            rel_record = rel_tblobj.writeRecordCluster(rel_recordCluster,rel_recordClusterAttr)
            from_fld = joiner['many_relation'].split('.')[2]
            to_fld = joiner['one_relation'].split('.')[2]
            main_record[from_fld] = rel_record[to_fld]
            
        if isNew:
            self.insert(main_record)
        else:
            self.update(main_record, old_record=old_record ,pkey=pkey)
        for rel_name, rel_recordClusterNode in relatedMany.items():
            rel_recordCluster = rel_recordClusterNode.value
            rel_recordClusterAttr = rel_recordClusterNode.getAttr()
            if rel_name.endswith('_removed'):
                rel_name = rel_name[:-8]
            relblock = self.model.getRelationBlock(rel_name)
            many_tblobj = self.db.table(relblock['mtbl'] , pkg=relblock['mpkg'])
            many_key = relblock['mfld']
            relKey = main_record[relblock['ofld']]
            for sub_recordClusterNode in rel_recordCluster:
                if sub_recordClusterNode.attr.get('_newrecord') and not(sub_recordClusterNode.attr.get('_deleterecord')):
                    sub_recordClusterNode.value[many_key] = relKey
                many_tblobj.writeRecordCluster(sub_recordClusterNode.value,sub_recordClusterNode.getAttr())
        return main_record
    
    def xmlDebug(self, data, debugPath, name=None):
        name= name or self.name
        filepath=os.path.join(debugPath,'%s.xml' %name)
        data.toXml(filepath,autocreate=True)
    
    def _splitRecordCluster(self, recordCluster, mainRecord=None, debugPath=None):
        relatedOne={}
        relatedMany={}
        if recordCluster:
            nodes = recordCluster.nodes
            revnodes=list(enumerate(nodes))
            revnodes.reverse()
            for j,n in revnodes:
                if n.label.startswith('@'):
                    if n.getAttr('mode') == 'O':
                        relatedOne[n.label[1:]]=nodes.pop(j)
                    else:
                        relatedMany[n.label]=nodes.pop(j)
        if debugPath:
            self.xmlDebug(recordCluster, debugPath)
            for k,v in relatedOne.items():
                self.xmlDebug(v, debugPath, k)
            for k,v in relatedMany.items():
                self.xmlDebug(v, debugPath, k)
        return recordCluster, relatedOne, relatedMany
    
    def _doFieldTriggers(self, triggerEvent, record):
        trgFields = self.model._fieldTriggers.get(triggerEvent)
        if trgFields:
            for fldname, trgFunc in trgFields:
                getattr(self, 'trigger_%s' % trgFunc)(record, fldname)
    
    def newPkeyValue(self):
        """This method get a new unique id to use as primary key on the current table"""
        pkey = self.model.pkey
        if self.model.column(pkey).dtype in ('L','I','R'):
            lastid = self.query(columns='max($%s)' % pkey, group_by='*').fetch()[0] or [0]
            return lastid[0] + 1
        else:
            return getUuid()
    
    def baseViewColumns(self):
        allcolumns = self.model.columns
        result = [k for k,to_add in allcolumns.digest('#k,#a.base_view') if to_add]
        if not result:
            result = [col for col,colobj in allcolumns.items() if not colobj.isReserved]
        return ','.join('result')

    def getResource(self,path):
        return self.db.getResource(self,path)
    #---------- method to implement via mixin
    def onIniting(self):
        pass
    
    def onInited(self):
        pass

    
    def trigger_onInserting(self,record):
        #self.trigger_onUpdating(record) Commented out Miki 2009/02/24
        pass 
        
    def trigger_onInserted(self, record):
        #self.trigger_onUpdated(record) Commented out Miki 2009/02/24
        pass
    
    def trigger_onUpdating(self, record, old_record=None):
        pass
    
    def trigger_onUpdated(self, record, old_record=None):
        pass
    
    def trigger_onDeleting(self, record):
        pass
    
    def trigger_onDeleted(self, record):
        pass
        
    def protect_update(self,record, old_record=None):
        pass
        
    def protect_delete(self,record):
        pass
        
    def protect_validate(self,record, old_record=None):
        pass
            
    def check_updatable(self,record):
        try :
            self.protect_update(record)
            return True
        except EXCEPTIONS['protect_update'],e:
            return False

    def check_deletable(self,record):
        try :
            self.protect_delete(record)
            return True
        except EXCEPTIONS['protect_delete'],e:
            return False
        
    def columnsFromString(self, columns):
        result = []
        if not columns:
            return result
        if isinstance(columns, basestring):
            columns = gnrstring.splitAndStrip(columns)
        for col in columns:
            if not col.startswith('@') and not col.startswith('$'):
                col = '$%s' % col
                #FIX 
            result.append(col)
        return result
    
    def getQueryFields(self, columns=None,captioncolumns=None):
        columns = columns or self.model.queryfields or captioncolumns
        return self.columnsFromString(columns)
    
    def rowcaptionDecode(self, rowcaption=None):
        rowcaption = rowcaption or self.rowcaption
        if not rowcaption:
            return [],''
        
        if ':' in rowcaption:
            fields, mask = rowcaption.split(':',1)
        else:
            fields, mask = rowcaption, None
        fields = fields.replace('*', self.pkey)
        fields = self.columnsFromString(fields)
        if not mask:
            mask = ' - '.join(['%s' for k in fields])
        return fields, mask
    
    def recordCaption(self, record, newrecord=False, rowcaption=None):
        if newrecord:
            return '!!New %s' %self.name_long.replace('!!','')
        else:
            fields, mask = self.rowcaptionDecode(rowcaption)
            if not fields:
                return ''
            fields = [f.lstrip('$') for f in fields]
            if not isinstance(record, Bag):
                fields = [self.db.colToAs(f) for f in fields]
            cols = [(c, gnrstring.toText(record[c])) for c in fields]
            if '$' in mask:
                caption = gnrstring.templateReplace(mask, dict(cols))
            else:
                caption = mask % tuple([v for k,v in cols])
            return caption
    
    def colToAs(self, col):
        return self.db.colToAs(col)
    
    def relationName(self, relpath):
        relpath = self.model.resolveRelationPath(relpath)
        attributes = self.model.relations.getAttr(relpath)
        joiner = attributes['joiner'][0]
        if joiner['mode']=='M':
            relpkg, reltbl, relfld = joiner['many_relation'].split('.')
            targettbl = '%s.%s' % (relpkg, reltbl)
            result = joiner.get('many_rel_name') or self.db.table(targettbl).name_plural
        else:
            relpkg, reltbl, relfld = joiner['one_relation'].split('.')
            targettbl = '%s.%s' % (relpkg, reltbl)
            result = joiner.get('one_rel_name') or self.db.table(targettbl).name_long
        return result
    
    def xmlDump(self, path):
        filepath=os.path.join(path,'%s_dump.xml' %self.name)
        records = self.query(excludeLogicalDeleted=False).fetch()
        result = Bag()
        
        for r in records:
            r=dict(r)
            pkey=  r.pop('pkey')
            result['records.%s' % pkey.replace('.','_')] = Bag(r)
        result.toXml(filepath, autocreate=True)
    
    def importFromXmlDump(self, path):
        if '.xml' in path:
            filepath = path
        else:
            filepath=os.path.join(path,'%s_dump.xml' %self.name)
        data = Bag(filepath)
        if data:
            for record in data['records'].values():
                record.pop('_isdeleted')
                self.insert(record)
                
    def importFromAuxInstance(self, instance_name, tbl_name=None, empty_before=False, excludeLogicalDeleted=True):
        aux_db = self.db.application.getAuxInstance(instance_name).db
        source_tbl = aux_db.table(tbl_name or self.fullname)
        source_records = source_tbl.query(addPkeyColumn=False, excludeLogicalDeleted=excludeLogicalDeleted).fetch()
        if empty_before:
            self.empty()
        for record in source_records:
            if empty_before:
                self.insert(record)
            else:
                self.insertOrUpdate(record)

    
    def relationExplorer(self, omit='', prevRelation='', dosort=True, pyresolver=False, **kwargs):
        def xvalue(attributes):
            if not pyresolver:
                return
            if attributes.get('one_relation'):
                if attributes['mode']=='O':
                    relpkg, reltbl, relfld = attributes['one_relation'].split('.')
                else:
                    relpkg, reltbl, relfld = attributes['many_relation'].split('.')
                targettbl = self.db.table('%s.%s' % (relpkg, reltbl))
                return BagCbResolver(targettbl.relationExplorer, omit=omit,
                                     prevRelation=attributes['fieldpath'], dosort=dosort,
                                     pyresolver=pyresolver, **kwargs)
        
        def resultAppend(result, label, attributes, omit):
            gr = attributes.get('group') or ' '
            grin = gr[0]
            if grin == '*' or grin == '_':
                attributes['group'] = gr[1:]
            if grin not in omit:
                result.setItem(label, xvalue(attributes), attributes)
            
        
        def convertAttributes(result, relnode, prevRelation, omit):
            attributes = dict(relnode.getAttr())
            attributes['fieldpath'] = gnrstring.concat(prevRelation, relnode.label)
            if 'joiner' in attributes:
                joiner=attributes.pop('joiner')
                attributes.update(joiner[0])
                attributes['name_long'] = self.relationName(relnode.label)
                if attributes['mode']=='M':
                    attributes['group'] = attributes.get('many_group') or 'zz'
                    attributes['dtype'] = 'RM'
                else:
                    attributes['group'] = attributes.get('one_group')
                    attributes['dtype'] = 'RO'
            else:
                attributes['name_long'] = attributes.get('name_long') or relnode.label
            resultAppend(result, relnode.label, attributes, omit)
        
        tblmodel = self.model
        result=Bag()
        for relnode in tblmodel.relations: # add columns relations
            convertAttributes(result, relnode, prevRelation, omit)
        
        for vcolname, vcol in tblmodel.virtual_columns.items():
            targetcol = self.column(vcolname)
            attributes = dict(targetcol.attributes)
            attributes.update(vcol.attributes)
            attributes['fieldpath'] = gnrstring.concat(prevRelation, vcolname)
            attributes['name_long'] = attributes.get('name_long') or vcolname
            if 'sql_formula' in attributes:
                attributes['dtype'] = attributes.get('dtype') or 'T'
            resultAppend(result, vcolname, attributes, omit)
        
        for aliastbl in tblmodel.table_aliases.values():
            relpath = tblmodel.resolveRelationPath(aliastbl.relation_path)
            attributes = dict(tblmodel.relations.getAttr(relpath))
            attributes['name_long'] = aliastbl.attributes.get('name_long') or self.relationName(relpath)
            attributes['group'] = aliastbl.attributes.get('group')
            attributes['fieldpath'] = gnrstring.concat(prevRelation, aliastbl.name)
            joiner=attributes.pop('joiner')
            attributes.update(joiner[0])
            mode=attributes.get('mode')
            if mode=='O':
                attributes['dtype'] = 'RO'
            elif mode=='M':
                attributes['dtype'] = 'RM'
            resultAppend(result, aliastbl.name, attributes, omit)
        
        if dosort:
            result.sort(lambda a, b: cmp(a.getAttr('group','').split('.'), b.getAttr('group','').split('.')))
            grdict = dict([(k[6:],v) for k,v in self.attributes.items() if k.startswith('group_')])
            if not grdict:
                return result
            newresult = Bag()
            for node in result:
                grk = (node.getAttr('group') or '').split('.')[0]
                if grk and grdict.get(grk):
                    if not grk in newresult:
                        newresult.setItem(grk, None, name_long=grdict.get(grk))
                    newresult.setItem('%s.%s' % (grk, node.label), node.getValue(), node.getAttr())
                else:
                    newresult.setItem(node.label, node.getValue(), node.getAttr())
            return newresult
        else:
            return result
    
    def getPlugin(self, name=None, **kwargs):
        if name == 'batch':
            return SqlTableBatch(self, **kwargs)
        
        return self.plugins[name](self, **kwargs)
    
    def _get_plugins(self):
        return self._plugins
        #return self.db.application.packages.getItem(self.pkg.name).tablePlugins.get(self.name, {})
    plugins = property(_get_plugins)

class SqlTablePlugin(object):
    pass

class SqlTableBatch(SqlTablePlugin):
    stopOnError = True
    forUpdate = False
    thermofield = None
    def __init__(self, tblobj, thermoCb=None, thermoId=None, thermofield=None,
                            stopOnError=False, forUpdate=False, onRow=None, **kwargs):
        self.db = tblobj.db
        self.tblobj = tblobj
        self.thermoCb = thermoCb
        self.thermoId = thermoId
        if thermofield:
            self.thermofield = thermofield
        if stopOnError:
            self.stopOnError = stopOnError
        if forUpdate:
            self.forUpdate = forUpdate
        self._onRow = None
        if onRow:
            self._onRow = getattr(tblobj, onRow)
        self.kwargs = kwargs
        self.stopped = None
    
    def run(self, pkeyList=None, **kwargs):
        self.stopped = False
        self.pkeyList = pkeyList
        self.result = []
        self.errors = []
        
        if self.thermoId:
            self.thermoCb(self.thermoId, None, '', len(pkeyList), command='init')
        
        self.onStart()
        self.loop()
        self.onEnd()
        if self.thermoId: self.thermoCb(self.thermoId, command='end')
        return self.prepareResult()
    
    def prepareResult(self):
        result = Bag()
        for i, pkey, caption, r in self.result:
            result.setItem('result.r_%i' % i, None, result=r, pkey=pkey, caption=caption)
        for i, pkey, caption, e in self.errors:
            result.setItem('errors.r_%i' % i, None, error=str(e), pkey=pkey, caption=caption)
        return result
    
    def loop(self):
        for i, record in enumerate(self.dataProvider()):
            if self.setThermo(i, record) == 'stop':
                self.stopped = True
                break
            try:
                result = self.onRow(record)
                if self.forUpdate:
                    self.tblobj.update(record)
                if result:
                    self.result.append((i, record[self.tblobj.pkey], self.tblobj.recordCaption(record), result))
            except Exception, e:
                if self.stopOnError:
                    raise e
                else:
                    self.errors.append((i, record[self.tblobj.pkey], self.tblobj.recordCaption(record), e))
    
    def setThermo(self, i, record):
        if self.thermoId:
            if self.thermofield=='*':
                msg = self.tblobj.recordCaption(record[0])
            else:
                msg = record[0][self.thermofield]
            result = self.thermoCb(self.thermoId, i+1, msg)
            if result=='stop':
                self.thermoCb(self.thermoId, command='stopped')
            return result
    
    def onStart(self, **kwargs):
        #override this
        pass
    
    def onRow(self, record, **kwargs):
        #override this
        self._onRow(record, **kwargs)
    
    def onEnd(self, **kwargs):
        if self.forUpdate and (not self.stopped):
            self.db.commit()
    
    def dataProvider(self,):
        #override this
        return self.recordProvider()
    
    def recordProvider(self):
        for pk in self.pkeyList:
            yield self.tblobj.record(pk, forUpdate=self.forUpdate, mode='bag')
    
    def selectionProvider(self):
        for r in self.selection.output('data', asIterator=True):
            yield r
    
    def columns(self):
        return '*'
        
   #unused method: to be deleted
   #def createSelection(self,**kwargs):
   #    self.tblobj.query(columns=self.columns(), pkeyList=self.pkeyList, forUpdate=self.forUpdate, **kwargs).selection()
   #            

if __name__=='__main__':
    pass