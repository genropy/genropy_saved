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


#import weakref
import os
import re

from gnr.core import gnrstring
from gnr.core.gnrlang import GnrObject,getUuid,uniquify
from gnr.core.gnrdecorator import deprecated,extract_kwargs
from gnr.core.gnrbag import Bag, BagCbResolver
from gnr.core.gnrdict import dictExtract
#from gnr.sql.gnrsql_exceptions import GnrSqlException,GnrSqlSaveException, GnrSqlApplicationException
from gnr.sql.gnrsqldata import SqlRecord, SqlQuery
from gnr.sql.gnrsqltable_proxy.hierarchical import HierarchicalHandler
from gnr.sql.gnrsql import GnrSqlException
from datetime import datetime
import logging
import threading

__version__ = '1.0b'
gnrlogger = logging.getLogger(__name__)

class RecordUpdater(object):
    """TODO
    
    Example::
    
        with self.recordToUpdate(pkey) as record:
            # do something
            pass"""
    
    def __init__(self, tblobj,pkey=None,mode=None,raw=False,insertMissing=False,ignoreMissing=None,for_update=None,**kwargs):
        self.tblobj = tblobj
        self.pkey = pkey
        self.mode = mode or 'record'
        self.kwargs = kwargs
        self.raw = raw
        self.insertMissing = insertMissing
        self.ignoreMissing = ignoreMissing
        self.for_update = for_update or True
        self.insertMode = False

    def __enter__(self):
        self.record = self.tblobj.record(pkey=self.pkey,for_update=self.for_update,ignoreMissing=self.insertMissing or self.ignoreMissing,
                                                    **self.kwargs).output(self.mode)
        if self.record.get(self.tblobj.pkey) is None:
            oldrecord = None
            if self.insertMissing:
                self.record = self.tblobj.newrecord(resolver_one=False, resolver_many=False)
                for k,v in self.kwargs.items():
                    if k in self.tblobj.columns and v is not None:
                        self.record[k] = v
                self.insertMode = True
            else:
                self.record = None
        else:
            oldrecord = dict(self.record)
            for k,v in oldrecord.items():
                if v and isinstance(v,Bag):
                    oldrecord[k] = v.deepcopy()
        self.oldrecord = oldrecord
        self.pkey = oldrecord.get(self.tblobj.pkey) if oldrecord else self.pkey
        return self.record
        
        
    def __exit__(self, exception_type, value, traceback):
        if not exception_type:
            if not self.record:
                return
            if self.raw:
                if self.record.get(self.tblobj.pkey) is False:
                    self.tblobj.raw_delete(self.oldrecord)
                elif self.insertMode:
                    self.tblobj.raw_insert(self.record)
                else:
                    self.tblobj.raw_update(self.record,self.oldrecord,pkey=self.pkey)
            else:
                if self.record.get(self.tblobj.pkey) is False:
                    if not self.insertMode:
                        self.tblobj.delete(self.oldrecord)
                elif self.insertMode:
                    self.tblobj.insert(self.record)
                else:
                    self.tblobj.update(self.record,self.oldrecord,pkey=self.pkey)
        

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
        self._user_config = {}
        self._lock = threading.RLock()
        if tblobj.attributes.get('hierarchical'):
            self.hierarchicalHandler = HierarchicalHandler(self)
        
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
        return exception(tablename=self.fullname,rowcaption=rowcaption,msg=msg,localizer=self.db.localizer, **kwargs)
        
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
        
    def column(self, name,**kwargs):
        """Returns a :ref:`column` object.
        
        :param name: A column's name or a :ref:`relation <relations>` starting from
                     the current :ref:`table`. (eg. ``@director_id.name``)"""
        result = self.model.column(name,**kwargs)
        return result
        
    def subtable(self, name,**kwargs):
        """Returns a :ref:`column` object.
        
        :param name: A column's name or a :ref:`relation <relations>` starting from
                     the current :ref:`table`. (eg. ``@director_id.name``)"""
        result = self.model.subtable(name,**kwargs)
        return result

    def fullRelationPath(self, name):
        """TODO
        
        :param name: TODO"""
        return self.model.fullRelationPath(name)

    def getPartitionCondition(self,ignorePartition=None):
        if ignorePartition:
            return
        partitionParameters = self.partitionParameters
        if partitionParameters:
            env = self.db.currentEnv
            if env.get('current_%(path)s' %partitionParameters):
                return "$%(field)s =:env_current_%(path)s" %partitionParameters
            elif env.get('allowed_%(path)s' %partitionParameters):
                return "( $%(field)s IS NULL OR $%(field)s IN :env_allowed_%(path)s )" %partitionParameters

    @property
    def partitionParameters(self):
        kw = dictExtract(self.attributes,'partition_')
        if not kw:
            return
        result = dict()
        result['field'] = kw.keys()[0]
        result['path'] = kw[result['field']]
        col = self.column(result['field'])
        if col.relatedColumn() is None:
            result['table'] = self.fullname
        else:
            result['table'] = col.relatedColumn().table.fullname
        return result

    @property
    def user_config(self):
        uc = self._user_config
        if not uc:
            self._user_config = {'ts':datetime.now(),'config':{}}
        else:
            expirebag = self.db.currentEnv.get('_user_conf_expirebag')
            if expirebag:
                exp_ts = expirebag[self.fullname] or expirebag['%s.*' %self.pkg.name] or expirebag['*']
                if exp_ts and exp_ts> uc['ts']:
                    self._user_config = {'ts':datetime.now(),'config':{}}
        return self._user_config['config']
        

    def getUserConfiguration(self,user_group=None,user=None):
        user_config = self.user_config.get((user_group,user))
        if user_config is None:
            with self._lock:
                user_config = self.db._getUserConfiguration(table=self.fullname,user_group=user_group,user=user)
                self.user_config[(user_group,user)] = user_config or False
        return user_config


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
    def multidb(self):
        return self.attributes.get('multidb',None)

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
    def virtual_columns(self):
        """Returns the virtual columns DbColumnListObj object"""
        return self.model.virtual_columns

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

    def removeLocalizationFromText(self,text):
        return re.sub("(?:!!)(?:\\[\\w*\\])?(.*)", "\\1", text)
        
    def counterColumns(self):
        return



    def variantColumn_unaccent(self, field, **kwargs):
        sql_formula=self.db.adapter.unaccentFormula(field)
        return dict(name='{field}_unaccent'.format(field=field), 
                                            sql_formula=sql_formula,
                                            **kwargs)
    
    def variantColumn_fill(self, field, side='r', size=0, char='_', **kwargs):
        sql_formula = "{side}pad(${field},{size},'{char}')".format(side=side,
                                                                field=field,
                                                                size=size,
                                                                char=char)
        return dict(name='{field}_{side}filled'.format(field=field,side=side), 
                                            sql_formula=sql_formula,
                                            **kwargs)


    #def variantColumn_repaccent(self, field, **kwargs):
    #    sql_formula= u"""unaccent(REGEXP_REPLACE(   
    #                                REGEXP_REPLACE(
    #                                   REGEXP_REPLACE(
    #                                      REGEXP_REPLACE(
    #                                          REGEXP_REPLACE(
    #                                              REGEXP_REPLACE(${field},'ò$','o''')
    #                                          ,'ì','i''')
    #                                      ,'à','a''')
    #                                   ,'é','e''')
    #                                ,'è','e''')
    #                            ,'ù','u''')
    #                            )""".format(field=field)

    #    return dict(name='{field}_repaccent'.format(field=field), 
    #                                        sql_formula=sql_formula,
    #                                        **kwargs)


    def variantColumn_egvariant(self,field,**kwargs):
        #for documentation
        pass

    def variantColumn_age_day(self, field, dateArg=None, **kwargs):
        sql_formula=self.db.adapter.ageAtDate(field, dateArg=dateArg, timeUnit='day')
        return dict(name='{field}_age_day'.format(field=field), 
                                            sql_formula=sql_formula,
                                            dtype='L',
                                            **kwargs)

    def variantColumn_age(self, field, dateArg=None, **kwargs):
        dref = dateArg or ':env_workdate'
        return dict(name='{field}_age'.format(field=field), dtype='T',
                                            sql_formula='CAST(age(${field},{dref}) as TEXT)'.format(field=field, dref=dref),
                                            **kwargs)

    def variantColumn_sharevalue(self, field, sharefield=None, **kwargs):
        #dref = dateArg or ':env_workdate'
        result = []
        f = self.query(columns='{sharefield} AS _shval'.format(sharefield=sharefield),distinct=True).fetch()
        for r in f:
            shval = r['_shval'] 
            sql_formula = "(CASE WHEN {sharefield} ='{shval}' THEN ${field} ELSE 0 END)".format(sharefield=sharefield,shval=shval,field=field)
            print('sql_formula',sql_formula)
            result.append(dict(name='{field}_{shval}'.format(field=field,shval=shval),
                            sql_formula=sql_formula,
                            var_shval=shval,dtype='N'))
        return result
  

    @property
    def availablePermissions(self):
        default_table_permissions = ['ins','upd','del','archive','export','import','print','mail','action']
        if not hasattr(self,'_availablePermissions'):
            customPermissions = dict()
            for pkgid,pkgobj in self.db.packages.items():
                customPermissions.update(dictExtract(pkgobj.attributes,'permission_'))
            customPermissions.update(dictExtract(self.attributes,'permission_'))
            customPermissions = default_table_permissions+customPermissions.keys()
            for k,handler in self.__dict__.items():
                permissions = getattr(handler,'permissions',None)
                if permissions:
                    customPermissions = customPermissions + permissions.split(',')
            self._availablePermissions = ','.join(uniquify(customPermissions))
        return self._availablePermissions

    def recordCoerceTypes(self, record, null='NULL'):
        """Check and coerce types in record.
        
        :param record: an object implementing dict interface as colname, colvalue
        :param null: TODO"""
        converter = self.db.typeConverter
        for k in record.keys():
            if not k.startswith('@'):
                if self.column(k) is None:
                    continue
                colattr = self.column(k).attributes
                dtype = self.column(k).dtype
                v = record[k]
                if (v is None) or (v == null) or v=='':
                    record[k] = None
                elif dtype in ['T', 'A', 'C'] and not isinstance(v, basestring):
                    record[k] = str(v if not isinstance(v,float) else int(v))
                elif dtype == 'B' and not isinstance(v, basestring):
                    record[k] = bool(v)
                else:
                    if dtype and isinstance(v, basestring):
                        if dtype not in ['T', 'A', 'C']:
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
        
    def newrecord(self, assignId=False, resolver_one=None, resolver_many=None, _fromRecord=None, **kwargs):
        """TODO
        
        :param assignId: TODO
        :param resolver_one: TODO
        :param resolver_many: TODO"""
        
        defaultValues = dict()
        if _fromRecord:
            for colname,obj in self.model.columns.items():
                if  obj.attributes.get('unique'):
                    continue
                if obj.attributes.get('_sysfield') and colname not in (self.draftField, 'parent_id'):
                    continue
                defaultValues[colname] = _fromRecord[colname]
        else:
            defaultValues = self.defaultValues() or {}
        defaultValues.update(kwargs)

        newrecord = self.buildrecord(defaultValues, resolver_one=resolver_one, resolver_many=resolver_many)
        if assignId:
            newrecord[self.pkey] = self.newPkeyValue(record=newrecord)
        return newrecord

    def cachedRecord(self,pkey=None,virtual_columns=None,keyField=None,createCb=None):
        keyField = keyField or self.pkey
        ignoreMissing = createCb is not None
        def recordFromCache(cache=None,pkey=None,virtual_columns_set=None):
            cacheNode = cache.getNode(pkey)
            if cacheNode:
                result,cached_virtual_columns_set = cacheNode.value,cacheNode.getAttr('virtual_columns_set')
            else:
                result,cached_virtual_columns_set = None,None
            in_cache = bool(result)
            if in_cache and not virtual_columns_set.issubset(cached_virtual_columns_set):
                in_cache = False
                virtual_columns_set = virtual_columns_set.union(cached_virtual_columns_set)
            if not in_cache:
                result = self.record(virtual_columns=','.join(virtual_columns_set),ignoreMissing=ignoreMissing,**{keyField:pkey}).output('dict')
                if (not result) and createCb:
                    result = createCb(pkey)
                    if virtual_columns and result:
                        result = self.record(virtual_columns=','.join(virtual_columns_set),**{keyField:pkey}).output('dict')
                cache.setItem(pkey,result,virtual_columns_set=virtual_columns_set)
            return dict(result),in_cache
        virtual_columns_set = set(virtual_columns.split(',')) if virtual_columns else set()
        return self.tableCachedData('cachedRecord',recordFromCache,pkey=pkey,
                                virtual_columns_set=virtual_columns_set)

    def findDuplicates(self,allrecords=True):
        dup_records = self.query(where="($_duplicate_finder IS NOT NULL) AND ($_duplicate_finder!='')",
                                 columns='$_duplicate_finder,count(*)',having='count(*)>1',
                                 group_by='$_duplicate_finder').fetch()
        duplicated = [r[0] for r in dup_records]
        if not duplicated:
            return []
        q = self.query(where='$_duplicate_finder IN :dpf',dpf=duplicated,columns='$_duplicate_finder',
                        order_by='$_duplicate_finder,$__mod_ts desc')
        #if allrecords:
        return [r['pkey'] for r in q.fetch()]
        #else:
        #    return [l[0]['pkey'] for l in q.fetchGrouped('_duplicate_finder').values()]

    
    def opTranslate(self,column,op,value,dtype=None,sqlArgs=None):
        translator = self.db.adapter.getWhereTranslator()
        return translator.prepareCondition(column, op, value, dtype, sqlArgs,tblobj=self)

    def cachedKey(self,topic):
        if self.multidb=='*' or not self.use_dbstores() is False:
            storename = self.db.rootstore
        else:
            storename = self.db.currentStorename
        return '%s.%s.%s' %(storename,topic,self.fullname)

    def tableCachedData(self,topic,cb,**kwargs):
        currentPage = self.db.currentPage
        cacheKey = self.cachedKey(topic)
        if currentPage:
            cacheInPage = self.db.currentEnv.get('cacheInPage')
            if cacheInPage:
                store = getattr(currentPage,'_pageTableCache',None)
                if not store:
                    currentPage._pageTableCache = {}
                    store = currentPage._pageTableCache
                localcache = store.get(cacheKey) or Bag()
            else:
                store = currentPage.pageStore()
                localcache = store.getItem(cacheKey)
                localcache = localcache or Bag()
            data,in_cache = cb(cache=localcache,**kwargs)
            if store is not None and not in_cache:
                if cacheInPage:
                    store[cacheKey] = localcache
                else:
                    with currentPage.pageStore() as store:
                        store.setItem(cacheKey,localcache,_caching_table=self.fullname)
        else:
            localcache = self.db.currentEnv.setdefault(cacheKey,Bag())
            data,in_cache = cb(cache=localcache,**kwargs)
        return data


    def record(self, pkey=None, where=None,
               lazy=None, eager=None, mode=None, relationDict=None, ignoreMissing=False, virtual_columns=None,
               ignoreDuplicate=False, bagFields=True, joinConditions=None, sqlContextName=None,
               for_update=False, _storename=None,checkPermissions=False,aliasPrefix=None,**kwargs):
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
                           checkPermissions=checkPermissions,
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
                if n.value:
                    tblobj.batchUpdate(updater,_pkeys=n.value.split(','))
        record['__moved_related'] = None

    def _onUnifying(self,destRecord=None,sourceRecord=None,moved_relations=None,relations=None):
        pass

    def unifyRelatedRecords(self,sourceRecord=None,destRecord=None,moved_relations=None,relations=None):
        relations = self.model.relations.keys()
        old_destRecord = dict(destRecord)
        upd_destRec = False
        for k in relations:
            n = self.relations.getNode(k)
            joiner =  n.attr.get('joiner')
            if joiner and joiner['mode'] == 'M':
                if joiner.get('external_relation'):
                    continue
                fldlist = joiner['many_relation'].split('.')
                tblname = '.'.join(fldlist[0:2])
                tblobj = self.db.table(tblname)
                fkey = fldlist[-1]
                joinkey = joiner['one_relation'].split('.')[-1]
                updater = dict()
                if not destRecord[joinkey]:
                    destRecord[joinkey] = sourceRecord[joinkey]
                    upd_destRec = True
                updater[fkey] = destRecord[joinkey]
                updatedpkeys = tblobj.batchUpdate(updater,where='$%s=:spkey' %fkey,spkey=sourceRecord[joinkey],_raw_update=True)
                moved_relations.setItem('relations.%s' %tblname.replace('.','_'), ','.join(updatedpkeys),tblname=tblname,fkey=fkey)
        if upd_destRec:
            self.raw_update(destRecord,old_destRecord)
        return moved_relations

    def unifyRecords(self,sourcePkey=None,destPkey=None):
        sourceRecord = self.record(pkey=sourcePkey,for_update=True).output('dict')
        destRecord = self.record(pkey=destPkey,for_update=True).output('dict')
        self._unifyRecords_default(sourceRecord,destRecord)

    def _unifyRecords_default(self,sourceRecord=None,destRecord=None):
        moved_relations = Bag()
        with self.db.tempEnv(unifying='related'):
            self._onUnifying(sourceRecord=sourceRecord,destRecord=destRecord,moved_relations=moved_relations)
            if hasattr(self,'onUnifying'):
                self.onUnifying(sourceRecord=sourceRecord,destRecord=destRecord,moved_relations=moved_relations)
            moved_relations = self.unifyRelatedRecords(sourceRecord=sourceRecord,destRecord=destRecord,moved_relations=moved_relations)
        with self.db.tempEnv(unifying='main_record'):
            if self.model.column('__moved_related') is not None:
                old_record = dict(sourceRecord)
                moved_relations.setItem('destPkey',sourceRecord[self.pkey])
                moved_relations = moved_relations.toXml()
                sourceRecord.update(__del_ts=datetime.now(),__moved_related=moved_relations)
                self.raw_update(sourceRecord,old_record=old_record)
            else:
                self.delete(destRecord[self.pkey])
            

    def hasRelations(self,recordOrPkey):
        return bool(self.currentRelations(recordOrPkey,checkOnly=True))

    def currentRelations(self,recordOrPkey,checkOnly=False):
        result = Bag()
        i = 0
        if isinstance(recordOrPkey,basestring):
            record = self.record(pkey=recordOrPkey).output('dict')
        else:
            record = recordOrPkey
        for n in self.model.relations:
            joiner =  n.attr.get('joiner')
            if joiner and joiner['mode'] == 'M':
                rowdata = Bag()
                fldlist = joiner['many_relation'].split('.')
                tblname = fldlist[0:2]
                linktblobj = self.db.table('.'.join(tblname))
                fkey = fldlist[-1]
                joinkey = joiner['one_relation'].split('.')[-1]
                rel_count = linktblobj.query(where='$%s=:spkey' %fkey,spkey=record[joinkey]).count()
                linktblobj_name = linktblobj.fullname
                rowdata.setItem('linktbl',linktblobj_name)
                rowdata.setItem('count',rel_count)
                if rel_count:
                    if checkOnly:
                        return True
                    result.setItem('r_%i' %i,rowdata)
                i+=1
        return result

    def itemsAsText(self,caption_field=None,cols=None,**kwargs):
        caption_field = caption_field or self.attributes['caption_field']
        f = self.query(columns='$%s,$%s' %(self.pkey,caption_field),**kwargs).fetch()
        l = []
        for i,r in enumerate(f):
            if cols and i and not i%cols:
                l.append('/')
            l.append('%s:%s' %(r[self.pkey],r[caption_field].replace(',',' ').replace(':',' ')))

        return ','.join(l)
    
    def onArchivingRecord(self,record=None,archive_ts=None):
        self.archiveRelatedRecords(record=record,archive_ts=archive_ts)            

    def archiveRelatedRecords(self,record=None,archive_ts=None):
        usingRootstore = self.db.usingRootstore()
        for rel in self.relations_many:
            if rel.getAttr('onDelete', 'raise').lower() == 'cascade':
                mpkg, mtbl, mfld = rel.attr['many_relation'].split('.')
                opkg, otbl, ofld = rel.attr['one_relation'].split('.')
                relatedTable = self.db.table(mtbl, pkg=mpkg)
                if not usingRootstore and relatedTable.use_dbstores() is False:
                    continue
                if relatedTable.logicalDeletionField:
                    updater = {relatedTable.logicalDeletionField:archive_ts}
                    relatedTable.batchUpdate(updater, 
                                            where='$%s = :pid' % mfld,
                                            pid=record[ofld], 
                                            excludeDraft=False,
                                            excludeLogicalDeleted=False)
  

    def duplicateRecord(self,recordOrKey=None, howmany=None,destination_store=None,**kwargs):
        duplicatedRecords=[]
        howmany = howmany or 1
        original_record = self.recordAs(recordOrKey,mode='dict')
        record = dict(original_record)
        pkey = record.get(self.pkey,None)
        record[self.pkey] = None
        for colname,obj in self.model.columns.items():
            if colname == self.draftField or colname == 'parent_id':
                continue
            if obj.attributes.get('unique') or obj.attributes.get('_sysfield'):
                record[colname] = None
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
            joiner =  n.attr.get('joiner',{})
            onDuplicate =  joiner.get('onDuplicate')
            if onDuplicate is None and (joiner.get('onDelete')=='cascade' or joiner.get('onDelete_sql')=='cascade'):
                onDuplicate = 'recursive'
            if joiner and joiner['mode'] == 'M' and onDuplicate=='recursive':
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
        if hasattr(self,'onDuplicated'):
            self.onDuplicated(duplicated_records=duplicatedRecords,original_record=original_record)
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
            

    def defaultValues(self):
        """Override this method to assign defaults to new record. Return a dictionary - fill
        it with defaults"""
        return dict([(x.name, x.attributes['default'])for x in self.columns.values() if 'default' in x.attributes])
        

    def sampleValues(self):
        """Override this method to assign defaults to new record. Return a dictionary - fill
        it with defaults"""
        return dict([(x.name, x.attributes['sample'])for x in self.columns.values() if 'sample' in x.attributes])

    def createSysRecords(self):
        pass

    @extract_kwargs(jc=True)
    def query(self, columns=None, where=None, order_by=None,
              distinct=None, limit=None, offset=None,
              group_by=None, having=None, for_update=False,
              relationDict=None, sqlparams=None, excludeLogicalDeleted=True,
              excludeDraft=True,
              addPkeyColumn=True,
              subtable=None,
              ignoreTableOrderBy=False,ignorePartition=False, locale=None,
              mode=None,_storename=None,checkPermissions=False,aliasPrefix=None, 
              joinConditions=None,jc_kwargs=None,**kwargs):
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
        joinConditions = joinConditions or {}
        for v in jc_kwargs.values():
            rel,cond = v.split(':',1)
            one_one = None
            if rel.endswith('*'):
                one_one = True
                rel = rel[0:-1]
            joinConditions[rel] = dict(condition=cond,params=dict(),one_one=one_one)
        query = SqlQuery(self, columns=columns, where=where, order_by=order_by,
                         distinct=distinct, limit=limit, offset=offset,
                         group_by=group_by, having=having, for_update=for_update,
                         relationDict=relationDict, sqlparams=sqlparams,
                         excludeLogicalDeleted=excludeLogicalDeleted,excludeDraft=excludeDraft,
                         ignorePartition=ignorePartition,
                         addPkeyColumn=addPkeyColumn,ignoreTableOrderBy=ignoreTableOrderBy,
                        locale=locale,_storename=_storename,
                        checkPermissions=checkPermissions,jc_kwargs=jc_kwargs,
                         aliasPrefix=aliasPrefix,joinConditions=joinConditions,
                         subtable=subtable,**kwargs)
        return query


    def recordToUpdate(self, pkey=None,updater=None,**kwargs):
        """Return a TempEnv class"""
        return RecordUpdater(self, pkey=pkey,**kwargs)
            
    def batchUpdate(self, updater=None, _wrapper=None, _wrapperKwargs=None, 
                    autocommit=False,_pkeys=None,pkey=None,_raw_update=None,
                    _onUpdatedCb=None,updater_kwargs=None,for_update=None,**kwargs):
        """A :ref:`batch` used to update a database. For more information, check the :ref:`batchupdate` section
        
        :param updater: MANDATORY. It can be a dict() (if the batch is a :ref:`simple substitution
                        <batchupdate>`) or a method
        :param autocommit: boolan. If ``True``, perform the commit of the database (``self.db.commit()``)
        :param **kwargs: insert all the :ref:`query` parameters, like the :ref:`sql_where` parameter
        """
        if 'where' not in kwargs:
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

        fetch = self.query(addPkeyColumn=False, for_update=for_update or True, **kwargs).fetch()
        if _wrapper:
            _wrapperKwargs = _wrapperKwargs or dict()
            fetch = _wrapper(fetch, **(_wrapperKwargs or dict()))
        pkeycol = self.pkey
        updatedKeys = []
        updatercb,updaterdict = None,None
        commit_every = False 
        if autocommit and autocommit is not True:
            commit_every = autocommit
            autocommit = False
        if callable(updater):
            if updater_kwargs:
                def updatercb(row):
                    return updater(row,**updater_kwargs)
            else:
                updatercb = updater
        elif isinstance(updater,dict):
            updaterdict = updater
        for i,row in enumerate(fetch):
            new_row = dict(row)
            if not _raw_update:
                self.expandBagFields(row)
                self.expandBagFields(new_row)
            if updatercb:
                doUpdate = updatercb(new_row)
                if doUpdate is False:
                    continue
            elif updaterdict:
                new_row.update(updater)
            record_pkey = row[pkeycol]
            updatedKeys.append(record_pkey)
            if not _raw_update:
                self.update(new_row, row,pkey=record_pkey)
            else:
                self.raw_update(new_row,old_record=row,pkey=record_pkey)
            if _onUpdatedCb:
                _onUpdatedCb(record=new_row,old_record=row,pkey=record_pkey)
            if commit_every and i%commit_every==0:
                self.db.commit()
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
            
    def fieldsChanged(self,fieldNames,record,old_record=None):
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


    def setColumns(self, pkey,**kwargs):
        record = self.record(pkey,for_update=True).output('dict')
        old_record = dict(record)
        for k,v in kwargs.items():
            if record[k]!=v:
                record[k] = v
        if record != old_record:
            self.update(record,old_record)

    def readColumns(self, pkey=None, columns=None, where=None, **kwargs):
        """TODO
        
        :param pkey: the record :ref:`primary key <pkey>`
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        :param where: the sql "WHERE" clause. For more information check the :ref:`sql_where` section"""
        where = where or '$%s=:pkey' % self.pkey
        kwargs.pop('limit', None)
        kwargs.setdefault('ignoreTableOrderBy',True)
        fetch = self.query(columns=columns, limit=1, where=where,
                           pkey=pkey, addPkeyColumn=False,excludeDraft=False,
                           ignorePartition=True,excludeLogicalDeleted=False, 
                           **kwargs).fetch()
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
        
    def empty(self, truncate=None):
        """TODO"""
        self.db.adapter.emptyTable(self, truncate=None)

    def fillFromSqlTable(self, sqltablename):
        self.db.adapter.fillFromSqlTable(self, sqltablename)

    def sql_deleteSelection(self, where=None,_pkeys=None, **kwargs):
        """Delete a selection from the table. It works only in SQL so no python trigger is executed
        
        :param where: the sql "WHERE" clause. For more information check the :ref:`sql_where` section
        :param \*\*kwargs: optional arguments for the "where" attribute"""
        if where:
            todelete = self.query('$%s' % self.pkey, where=where, addPkeyColumn=False, for_update=True,excludeDraft=False ,_pkeys=_pkeys,**kwargs).fetch()
            _pkeys = [x[0] for x in todelete] if todelete else None
        if _pkeys:
            self.db.adapter.sql_deleteSelection(self, pkeyList=_pkeys)
            
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
        return sel
            # if not self.trigger_onDeleting:
            #  sql delete where


    @property
    def dbevents(self):
        return self.db.dbevents[self.fullname]


    def notifyDbUpdate(self,record):
        self.db.notifyDbUpdate(self,record)
            
    def touchRecords(self,_pkeys=None,_wrapper=None,_wrapperKwargs=None,
                    _notifyOnly=False,pkey=None,
                    order_by=None,method=None, columns=None,**kwargs):
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
        for_update = method=='update'
        handler = getattr(self,method) if isinstance(method,basestring) else method
        onUpdating = None
        if method != 'update':
            columns = columns or getattr(handler,'columns',None)
            for_update = getattr(handler,'for_update',False)
            doUpdate = getattr(handler,'doUpdate',False)
            order_by = getattr(handler,'order_by',None)

            for_update = doUpdate or for_update
            if doUpdate:
                onUpdating = handler
                handler = self.update
        sel = self.query(addPkeyColumn=False, 
                        for_update=for_update,
                        columns=columns or '*', 
                        order_by=order_by,**kwargs).fetch()
        if _wrapper:
            _wrapperKwargs = _wrapperKwargs or dict()
            sel = _wrapper(sel, **(_wrapperKwargs or dict()))
        if _notifyOnly:
            self.notifyDbUpdate(sel)
            return
        for row in sel:
            row._notUserChange = True
            old_record = dict(row)
            self.expandBagFields(row)
            self.expandBagFields(old_record)
            if onUpdating:
                onUpdating(row, old_record=old_record)
            handler(row, old_record=old_record)
        return sel

    def expandBagFields(self,record,columns=None):
        if not columns:
            columns = [k for k,v in self.model.columns.items() if v.dtype=='X']
        if isinstance(columns,basestring):
            columns = columns.split(',')
        for c in columns:
            record[c] = Bag(record.get(c))
            
    def existsRecord(self, record):
        """Check if a record already exists in the table and return it (if it is not already in the keys)
        :param record: the record to be checked"""
        if not hasattr(record, 'keys'):
            record = {self.pkey: record}
        return self.db.adapter.existsRecord(self, record)
    
    def checkDuplicate(self,excludeDraft=None,ignorePartition=None,**kwargs):
        """TODO"""
        where = ' AND '.join(['$%s=:%s' % (k, k) for k in kwargs.keys()])
        return self.query(where=where,excludeDraft=excludeDraft,
                        ignorePartition=ignorePartition,**kwargs).count()>0
    
    def insertOrUpdate(self, record):
        """Insert a single record if it doesn't exist, else update it
        
        :param record: a dictionary that represent the record that must be updated"""
        pkey = record.get(self.pkey)
        old_record = None
        if not (pkey in (None,'')):
            old_record = self.query(where="$%s=:pk" %self.pkey, pk=pkey,for_update=True).fetch()
        if not old_record:
            return self.insert(record)
        else:
            self.update(record,old_record=old_record[0])


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
            
        
    def raw_delete(self, record, **kwargs):
        """Delete a single record without triggers
        
        :param record: a dictionary representing the record that must be inserted"""
        self.db.raw_delete(self, record, **kwargs)

    def insertMany(self, records, **kwargs):
        self.db.insertMany(self, records, **kwargs)

    def raw_update(self,record=None,old_record=None,pkey=None,**kwargs):
        self.db.raw_update(self, record,old_record=old_record,pkey=pkey,**kwargs)
    
    def changePrimaryKeyValue(self, pkey=None,newpkey=None,**kwargs):
        self.db.adapter.changePrimaryKeyValue(self,pkey=pkey,newpkey=newpkey)

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
                sel = relatedTable.query(columns='*', where='%s = :pid' % mfld,subtable='*',
                                         excludeDraft=False,ignorePartition=True,
                                         excludeLogicalDeleted=False,
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
        usingRootstore = self.db.usingRootstore()
        for rel in self.relations_many:
            defaultOnDelete = 'raise' if rel.getAttr('mode')=='foreignkey' else 'ignore'
            onDelete = rel.getAttr('onDelete', defaultOnDelete).lower()
            if onDelete and not (onDelete in ('i', 'ignore')):
                mpkg, mtbl, mfld = rel.attr['many_relation'].split('.')
                opkg, otbl, ofld = rel.attr['one_relation'].split('.')
                relatedTable = self.db.table(mtbl, pkg=mpkg)
                if not usingRootstore and relatedTable.use_dbstores() is False:
                    continue
                sel = relatedTable.query(columns='*', where='$%s = :pid' % mfld,
                                         pid=record[ofld], for_update=True,
                                         subtable='*',ignorePartition=True,
                                         excludeDraft=False,
                                         excludeLogicalDeleted=False).fetch()
                if sel:
                    if onDelete in ('r', 'raise'):
                        raise self.exception('delete', record=record, msg='!!Record referenced in table %(reltable)s',
                                             reltable=relatedTable.fullname)
                    elif onDelete in ('c', 'cascade'):
                        for row in sel:
                            relatedTable.delete(row)
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
        if old_record and not pkey:
            pkey = old_record.get(self.pkey)
        if record.get(self.pkey) == pkey:
            pkey = None
        self.db.update(self, record, old_record=old_record, pkey=pkey,**kwargs)
        
    def writeRecordCluster(self, recordCluster, recordClusterAttr, debugPath=None):
        """Receive a changeSet and execute insert, delete or update
        
        :param recordCluster: TODO
        :param recordClusterAttr: TODO
        :param debugPath: TODO"""                
        main_changeSet, relatedOne, relatedMany = self._splitRecordCluster(recordCluster, debugPath=debugPath)
        isNew = recordClusterAttr.get('_newrecord')
        toDelete = recordClusterAttr.get('_deleterecord')
        pkey = recordClusterAttr.get('_pkey')
        invalidFields = recordClusterAttr.get('_invalidFields')
        noTestForMerge = self.attributes.get('noTestForMerge') or self.pkg.attributes.get('noTestForMerge')
        blackListAttributes = ('__old','_newrecord')
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
            self.insert(main_record,blackListAttributes=blackListAttributes)
        elif main_changeSet:
            self.update(main_record, old_record=old_record, pkey=pkey,blackListAttributes=blackListAttributes)
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
        if not self.db.application:
            return
        for pkg_id in self.db.application.packages.keys():
            trigger_name = 'trigger_%s_%s'%(triggerEvent, pkg_id)
            avoid_trigger_par = self.db.currentEnv.get('avoid_trigger_%s' %pkg_id)
            if avoid_trigger_par:
                if avoid_trigger_par=='*' or triggerEvent in avoid_trigger_par.split(','):
                    print 'avoiding trigger',triggerEvent
                    continue
            trgFunc = getattr(self, trigger_name, None)
            if callable(trgFunc):
                trgFunc(record, **kwargs)

    def hasProtectionColumns(self):
        #override
        return False

    def guessPkey(self,identifier):
        if identifier is None:
            return
        def cb(cache=None,identifier=None,**kwargs):
            if identifier in cache:
                return cache[identifier],True
            codeField = None
            result = None
            if ':' in identifier:
                wherelist = []
                wherekwargs = dict()
                for cond in identifier.split(','):
                    codeField,codeVal = cond.split(':')
                    wherelist.append('$%s=:v_%s' %(codeField,codeField))
                    wherekwargs['v_%s' %codeField] = codeVal
                result = self.readColumns(columns='$%s' %self.pkey,where=' AND '.join(wherelist),
                                        subtable='*',**wherekwargs)
            elif hasattr(self,'sysRecord_%s' %identifier):
                result = self.sysRecord(identifier)[self.pkey]
            elif self.pkey != 'id' or not codeField:
                result = identifier
            cache[identifier] = result
            return result,False
        return self.tableCachedData('guessedPkey',cb,identifier=identifier)


    def newPkeyValue(self,record=None):
        """Get a new unique id to use as :ref:`primary key <pkey>`
        on the current :ref:`database table <table>`"""
        return self.pkeyValue(record=record)


    def pkeyValue(self,record=None):
        pkey = self.model.pkey
        pkeycol = self.model.column(pkey)
        if pkeycol.dtype in ('L', 'I', 'R'):
            lastid = self.query(columns='max($%s)' % pkey, group_by='*').fetch()[0]
            return (lastid[0] or 0) + 1
        elif not record:
            return getUuid()
        elif self.attributes.get('pkey_columns'):
            joiner = self.attributes.get('pkey_columns_joiner') or '_'
            return joiner.join([str(record.get(col)) for col in self.attributes.get('pkey_columns').split(',') if record.get(col) is not None])
        elif record.get('__syscode'):
            size =  pkeycol.getAttr('size')
            if size and ':' not in size:
                return record['__syscode'].ljust(int(size),'_')
            else:
                return record['__syscode']
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

    def _islocked_write(self,record):
        return self._isReadOnly(record) or self.islocked_write(record)

    def islocked_write(self,record):
        #OVERRIDE THIS
        pass


    def _islocked_delete(self,record):
        return (self._isReadOnly(record) is not False) or self.islocked_delete(record)

    def islocked_delete(self,record):
        #OVERRIDE THIS
        pass

    def isDraft(self,record):
        if self.draftField:
            return record.get(self.draftField)
        return False


    def check_updatable(self, record,ignoreReadOnly=None):
        """TODO
        
        :param record: TODO"""
        try:
            self.protect_update(record,record)
            return True
        except EXCEPTIONS['protect_update']:
            return False
            
    def check_deletable(self, record):
        """TODO
        
        :param record: TODO"""
        try:
            self.protect_delete(record)
            return True
        except EXCEPTIONS['protect_delete']:
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

    def newRecordCaption(self,record=None):
        return self.newrecord_caption
        
    def recordCaption(self, record, newrecord=False, rowcaption=None):
        """TODO
        
        :param record: TODO
        :param newrecord: boolean. TODO
        :param rowcaption: the textual representation of a record in a user query.
                           For more information, check the :ref:`rowcaption` section
        """
        if newrecord:
            return self.newRecordCaption(record)
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

    def dependenciesTree(self,records=None,history=None,ascmode=False):
        history = history or dict() 
        for rel in self.relations_one:
            mpkg, mtbl, mfld = rel.attr['many_relation'].split('.')
            opkg, otbl, ofld = rel.attr['one_relation'].split('.')
            relatedTable = self.db.table(otbl, pkg=opkg)
            tablename = relatedTable.fullname
            if not tablename in history:
                history[tablename] = dict(one=set(),many=set())
            one_history_set = history[tablename]['one']
            sel = relatedTable.query(columns='*', where='$%s IN :pkeys' %ofld,
                                         pkeys=list(set([r[mfld] for r in records])-one_history_set),
                                         excludeDraft=False,excludeLogicalDeleted=False).fetch()
            if sel:
                one_history_set.update([r[relatedTable.pkey] for r in sel])
                relatedTable.dependenciesTree(sel,history=history,ascmode=True)
        #if ascmode:
        #    return history
 
        for rel in self.relations_many:
            mpkg, mtbl, mfld = rel.attr['many_relation'].split('.')
            opkg, otbl, ofld = rel.attr['one_relation'].split('.')
            relatedTable = self.db.table(mtbl, pkg=mpkg)
            tablename=relatedTable.fullname
            if not tablename in history:
                history[tablename] = dict(one=set(),many=set())
            if ascmode and not (len(relatedTable.relations_one) == 1 and len(relatedTable.relations_many)==0 \
                    and relatedTable.relations_one.getAttr('#0','onDelete')=="cascade"):
                continue
            many_history_set = history[tablename]['many']
            sel = relatedTable.query(columns='*', where='%s in :rkeys AND $%s NOT IN :pklist' % (mfld,relatedTable.pkey),
                                        pklist = list(many_history_set),
                                         rkeys=[r[ofld] for r in records],excludeDraft=False,excludeLogicalDeleted=False).fetch()
            if sel:
                many_history_set.update([r[relatedTable.pkey] for r in sel])
                relatedTable.dependenciesTree(sel,history=history,ascmode=False)

        return history                    
             
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
    
    def copyToDbstore(self,pkey=None,dbstore=None,bagFields=True,empty_before=False,**kwargs):
        """TODO
        
        :param pkey: the record :ref:`primary key <pkey>`
        :param dbstore: TODO
        :param bagFields: TODO"""
        queryargs = kwargs
        if pkey:
            queryargs = dict(where='$pkey=:pkey',pkey=pkey)
        records = self.query(addPkeyColumn=False,bagFields=bagFields,**queryargs).fetch()
        with self.db.tempEnv(storename=dbstore):
            if empty_before:
                self.empty()
            for rec in records:
                self.insertOrUpdate(rec)
                
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
                      
    def getReleases(self):
        prefix = '_release_'
        parslist = []
        extra_columns_list = []
        for fname in sorted(dir(self)):
             if fname.startswith(prefix):
                handler = getattr(self,fname)
                assert (int(fname[9:]) == len(parslist)+1) , 'Missing release'
                pars  = handler()
                updater = pars.pop('updater')
                extra_columns = pars.pop('extra_columns',None)
                if extra_columns:
                    extra_columns_list.extend(extra_columns.split(','))
                parslist.append((updater,pars))

        return parslist, ','.join(set(extra_columns_list))

    def updateRecordsToLastRelease_raw(self, commit=None, _wrapper=None, _wrapperKwargs=None):
        releases, extra_columns = self.getReleases()
        if not releases:
            return
        release = len(releases)
        toupdate = self.query(columns='*,%s' % extra_columns,
                             where='$__release IS NULL OR $__release < :release',
                            release=release , for_update=True,excludeLogicalDeleted=False,
                            excludeDraft=False).fetch()
        if _wrapper:
            _wrapperKwargs = _wrapperKwargs or dict()
            toupdate = _wrapper(toupdate, **(_wrapperKwargs or dict()))

        commit_frequency = commit if commit and isinstance(commit,int) else None
        n=0
        for record in toupdate:
            record = dict(record)
            oldrecord=dict(record)
            record_release = record['__release'] or 0
            for updater, kwargs in releases[record_release:]:
                updater(record, **kwargs)
            record['__release'] = release
            self.raw_update(record,oldrecord)
            if commit_frequency and n%commit_frequency==0:
                self.db.commit()
            n+=1
        if commit:
            self.db.commit()
                



    def relationExplorer(self, omit='', prevRelation='', dosort=True, pyresolver=False, 
                        relationStack='',checkPermissions=None,**kwargs):
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
                                     pyresolver=pyresolver,relationStack=relationStack, 
                                     **kwargs)
                                     
        def resultAppend(result, label, attributes, omit):
            if not self.db.application.allowedByPreference(**attributes):
                return
            if 'one_relation' in attributes or 'many_relation' in attributes:
                if not self.db.application.allowedByPreference(**self.db.model.column(attributes['one_relation']).table.attributes):
                    return
                if not self.db.application.allowedByPreference(**self.db.model.column(attributes['many_relation']).table.attributes):
                    return
            elif not attributes.get('virtual_column'):
                reltable = self.column(label).relatedTable()
                if reltable:
                    if not self.db.application.allowedByPreference(**reltable.attributes):
                        return
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
                
        def convertAttributes(result, relnode, prevRelation, omit,relationStack):
            attributes = dict(relnode.getAttr())
            attributes['fieldpath'] = gnrstring.concat(prevRelation, relnode.label)
            if 'joiner' in attributes:
                joiner = attributes.pop('joiner')
                attributes.update(joiner)
                attributes['name_long'] = self.relationName(relnode.label)
                if attributes['mode'] == 'M':
                    attributes['group'] = attributes.get('many_group') or 'zz'
                    attributes['dtype'] = 'RM'
                    relkey = '%(one_relation)s/%(many_relation)s' %attributes

                else:
                    attributes['group'] = attributes.get('one_group')
                    attributes['dtype'] = 'RO'
                    fkeyattr = dict(relnode.attr)
                    fkeyattr.pop('joiner')
                    attributes['fkey'] = fkeyattr
                    relkey = '%(many_relation)s/%(one_relation)s' %attributes
                relkey = str(hash(relkey) & 0xffffffff)
                if relkey in relationStack.split('|'):
                    return 
                attributes['relationStack'] = gnrstring.concat(relationStack, relkey,'|')
            else:
                if checkPermissions:
                    attributes.update(self.model.getColPermissions(relnode.label,**checkPermissions))
                attributes['name_long'] = attributes.get('name_long') or relnode.label
            return attributes
            
            
        tblmodel = self.model
        result = Bag()
        for relnode in tblmodel.relations: # add columns relations
            attributes = convertAttributes(result, relnode, prevRelation, omit,relationStack)
            if attributes:
                if not attributes.get('user_forbidden'):
                    resultAppend(result, relnode.label, attributes, omit)
            
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
                        if grplevel not in newresult:
                            newresult.setItem(grplevel, None, name_long=grdict.get(grplevel,grplevel.split('.')[-1]))
                    newresult.setItem('%s.%s' % ('.'.join(grplist), node.label), node.getValue(), node.getAttr())

                else:
                    newresult.setItem(node.label, node.getValue(), node.getAttr())
            return newresult
        else:
            return result

    def setQueryCondition(self,condition_name,condition):
        self.db.currentEnv['env_%s_condition_%s' %(self.fullname.replace('.','_'),condition_name)] = condition
    
    def onLogChange(self,evt,record,old_record=None):
        pass


    def updateTotalizers(self,record=None,old_record=None,evt=None,
                        _raw=None,_ignore_totalizer=None,**kwargs):
        if _raw and _ignore_totalizer:
            return
        totalizers = dictExtract(self.attributes,'totalizer_')
        if evt=='D':
            old_record = record
            record = None
        for tbl in totalizers.values():
            self.db.table(tbl).tt_totalize(record=record,old_record=old_record)
            
if __name__ == '__main__':
    pass