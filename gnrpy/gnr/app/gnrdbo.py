#!/usr/bin/env python
# encoding: utf-8

import datetime
import warnings as warnings_module
import os
import shutil
import pytz
import mimetypes

from collections import defaultdict

from gnr.core.gnrlang import boolean
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import splitAndStrip,templateReplace,fromJson,slugify
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.core.gnrdict import dictExtract


mimetypes.init() # Required for python 2.6 (fixes a multithread bug)

class GnrDboPackage(object):
    """Base class for packages"""
    def updateFromExternalDb(self,externaldb,empty_before=None):
        """TODO
        
        :param externaldb: TODO
        :param empty_before: TODO"""
        tables = self.attributes.get('export_order')
        if not tables:
            return
        self.db.setConstraintsDeferred()
        for tbl in splitAndStrip(tables):
            self.db.table(tbl).copyToDb(externaldb,self.db,empty_before=empty_before)

    def partitionParameters(self):
        partition= self.attributes.get('partition')
        if not partition:
            return
        pkg,tbl,fld=partition.split('.')
        return dict(table='%s.%s' % (pkg,tbl),field='%s_%s' % (tbl,fld), path='current_%s_%s' % (tbl,fld))
    
            
    def getCounter(self, name, code, codekey, output, date=None, phyear=False, lastAssigned=0,**kwargs):
        """Generate a new number from the specified counter and return it.
        
        :param name: the counter name
        :param code: the counter code
        :param codekey: the codekey format (e.g. ``$YY`` for year)
        :param output: the output format (e.g. ``$YY.$NNNN`` for year)
        :param date: the current date
        :param phyear: the fisfcal year
        :param lastAssigned: TODO"""
        return self.dbtable('counter').getCounter(name=name, pkg=self.name, code=code, codekey=codekey, output=output,
                                                  date=date, phyear=phyear, lastAssigned=lastAssigned,**kwargs)
                                                  
    def getLastCounterDate(self, name, code, codekey, output,
                           date=None, phyear=False, lastAssigned=0):
        """TODO
        
        :param name: the counter name
        :param code: the counter code
        :param codekey: the codekey format (e.g. ``$YY`` for year)
        :param output: the output format (e.g. ``$YY.$NNNN`` for year)
        :param date: the current date
        :param phyear: the fiscal year
        :param lastAssigned: TODO"""
        return self.dbtable('counter').getLastCounterDate(name=name, pkg=self.name, code=code, codekey=codekey,
                                                          output=output,
                                                          date=date, phyear=phyear, lastAssigned=lastAssigned)
                                                          
    def setCounter(self, name, code, codekey, output,
                   date=None, phyear=False, value=0):
        """TODO
        
        :param name: the counter name
        :param code: the counter code
        :param codekey: the codekey format (e.g. ``$YY`` for year)
        :param output: the output format (e.g. ``$YY.$NNNN`` for year)
        :param date: the current date
        :param phyear: the fiscal year
        :param value: TODO"""
        return self.dbtable('counter').setCounter(name=name, pkg=self.name, code=code, codekey=codekey, output=output,
                                                  date=date, phyear=phyear, value=value)
                                                  
    def loadUserObject(self, pkg=None, **kwargs):
        """TODO
        
        :param pkg: the :ref:`package <packages>` object"""
        return self.dbtable('userobject').loadUserObject(pkg=pkg or self.name, **kwargs)
        
    def saveUserObject(self, data, pkg=None, **kwargs):
        """TODO
        
        :param data: TODO
        :param pkg: the :ref:`package <packages>` object"""
        return self.dbtable('userobject').saveUserObject(data, pkg=pkg or self.name, **kwargs)
        
    def deleteUserObject(self, id, pkg=None):
        """TODO
        
        :param id: the object id
        :param pkg: the :ref:`package <packages>` object"""
        return self.dbtable('userobject').deleteUserObject(pkg=pkg or self.name, id=id)
        
    def listUserObject(self, pkg=None, **kwargs):
        """TODO
        
        :param pkg: the :ref:`package <packages>` object"""
        return self.dbtable('userobject').listUserObject(pkg=pkg or self.name, **kwargs)
        
    def getPreference(self, path, dflt=None, mandatoryMsg=None):
        """Get a preference for the current package. Return the value of the specified
        preference, or *dflt* if it is missing
        
        :param path: a dotted name of the preference item
        :param dflt: the default value"""
        return self.db.table('adm.preference').getPreference(path, pkg=self.name, dflt=dflt, mandatoryMsg=mandatoryMsg)
        
    def setPreference(self, path, value):
        """Set a preference for the current package.
        
        :param path: a dotted name of the preference item
        :param value: the new value"""
        self.db.table('adm.preference').setPreference(path, value, pkg=self.name)
         
    @public_method
    def loadStartupData(self,basepath=None,empty_before=None):
        btc = self.db.currentPage.btc if self.db.currentPage else None
        if btc:
            btc.batch_create(title='%s Importer' %self.name,cancellable=True,delay=.5)
        self._loadStartupData_do(basepath=basepath,btc=btc,empty_before=empty_before)
        if btc:
            btc.batch_complete(result='ok', result_attr=dict())


    def _loadStartupData_do(self,basepath=None,btc=None,empty_before=True):
        bagpath = basepath or os.path.join(self.db.application.packages[self.name].packageFolder,'startup_data')
        if not os.path.isfile('%s.pik' %bagpath):
            import gzip
            with gzip.open('%s.gz' %bagpath,'rb') as gzfile:
                with open('%s.pik' %bagpath,'wb') as f:
                    f.write(gzfile.read())
        db = self.db
        s = Bag('%s.pik' %bagpath)
        tables = s['tables']
        rev_tables =  list(tables)
        rev_tables.reverse()
        if empty_before:
            for t in rev_tables:
                if t in self.tables:
                    db.table('%s.%s' %(self.name,t)).empty()
        
        tw = btc.thermo_wrapper(tables,'tables',message='Table') if btc else tables
        for tablename in tw:
            if tablename not in self.tables:
                continue
            tblobj = db.table('%s.%s' %(self.name,tablename))
            if tblobj.attributes.get('multidb')=='*' and not self.db.usingRootstore():
                continue
            currentRecords = tblobj.query().fetchAsDict('pkey')
            records = s[tablename]
            if not records:
                continue
            recordsToInsert = []
            pkeyField = tblobj.pkey
            hasSysCode = tblobj.column('__syscode') is not None
            if hasSysCode:
                currentSysCodes = [r['__syscode'] for r in currentRecords.values() if r['__syscode']]
            for r in records:
                if r[pkeyField] in currentRecords:
                    continue
                if hasSysCode and r.get('__syscode') in currentSysCodes:
                    continue
                recordsToInsert.append(r)
            if recordsToInsert:
                tblobj.insertMany(recordsToInsert)
        db.commit()

        self.db.table('adm.preference').initPkgPref(self.name,s['preferences'])
        db.commit()
        
        os.remove('%s.pik' %bagpath)


    def startupData_tables(self):
        return  [tbl for tbl in self.db.tablesMasterIndex()[self.name].keys() if self.table(tbl).dbtable.isInStartupData()]

    @public_method
    def createStartupData(self,basepath=None):
        btc = self.db.currentPage.btc if self.db.currentPage else None
        if btc:
            btc.batch_create(title='%s Exporter' %self.name,cancellable=True,delay=.5)
        self._createStartupData_do(basepath=basepath,btc=btc)
        if btc:
            btc.batch_complete(result='ok', result_attr=dict())

    def _createStartupData_do(self,basepath=None,btc=None):
        pkgapp = self.db.application.packages[self.name]
        tables = self.startupData_tables()
        if not tables:
            return
        bagpath = basepath or os.path.join(pkgapp.packageFolder,'startup_data')
        s = Bag()
        s['tables'] = tables
        tables = btc.thermo_wrapper(tables,'tables',message='Table') if btc else tables
        for tname in tables:
            tblobj = self.tables[tname]
            handler = getattr(tblobj.dbtable,'startupData',None)
            if handler:
                f = handler()
            else:
                qp_handler = getattr(tblobj.dbtable,'startupDataQueryPars',None)
                queryPars = dict(addPkeyColumn=False,bagFields=True)
                if qp_handler:
                    queryPars.update(qp_handler())
                f = tblobj.dbtable.query(**queryPars).fetch()
            s[tname] = f
        s['preferences'] = self.db.table('adm.preference').loadPreference()['data'][self.name]
        s.makePicklable()
        s.pickle('%s.pik' %bagpath)
        import gzip
        zipPath = '%s.gz' %bagpath
        with open('%s.pik' %bagpath,'rb') as sfile:
            with gzip.open(zipPath, 'wb') as f_out:
                f_out.writelines(sfile)
        os.remove('%s.pik' %bagpath)
        if os.path.isdir(bagpath):
            os.removedirs(bagpath)
        
class TableBase(object):
    """TODO"""

    @extract_kwargs(counter=True)
    def sysFields(self, tbl, id=True, ins=True, upd=True, full_upd=False, ldel=True, user_ins=None, user_upd=None, 
                  draftField=False, invalidFields=None,invalidRelations=None,md5=False,
                  counter=None,hierarchical=None,hierarchical_virtual_roots=False,
                    hierarchical_root_id=False,useProtectionTag=None,
                  group='zzz', group_name='!!System',
                  df=None,counter_kwargs=None,**kwargs):
        """Add some useful columns for tables management (first of all, the ``id`` column)
        
        :param tbl: the :ref:`table` object
        :param id: boolean. If ``True``, create automatically an ``id`` column. The ``id`` column is
                            normally used as the primary key (:ref:`pkey`) of a table
        :param ins: boolean. If ``True``, create the ``__ins_ts`` column.
                    Allow to know the time (date and hour) of a record entry
        :param upd: boolean. If ``True``, create the ``__mod_ts`` column.
                    Allow to know the time (date and hour) of a record modify
        :param ldel: boolean. If ``True``, create the ``__del_ts`` column.
                     Allow to know the time (date and hour) of a record delete
                     
        :param draftField: TODO
        :param md5: boolean. TODO
        :param group: a hierarchical path of logical categories and subacategories the columns belong to.
                      For more information, check the :ref:`group` section
        :param group_name: TODO"""
        user_ins,user_upd = self._sysFields_defaults(user_ins=user_ins,user_upd=user_upd)
        if id:
            tbl.column('id', size='22', group=group, readOnly='y', name_long='!!Id',_sendback=True,_sysfield=True)
            pkey = tbl.attributes.get('pkey')
            if not pkey:
                tbl.attributes['pkey'] = 'id'
        if group and group_name:
            tbl.attributes['group_%s' % group] = group_name
        else:
            group = '_'
        tsType = 'DHZ' if self.db.application.config['db?use_timezone'] else 'DH'
        if ins:
            tbl.column('__ins_ts', dtype=tsType, name_long='!!Insert date', onInserting='setTSNow', group=group,_sysfield=True,indexed=True)
        if ldel:
            tbl.column('__del_ts', dtype=tsType, name_long='!!Logical delete date', group=group,_sysfield=True,indexed=True)
            tbl.attributes['logicalDeletionField'] = '__del_ts'
        if upd:
            tbl.column('__mod_ts', dtype=tsType, name_long='!!Update date', onUpdating='setTSNow', onInserting='setTSNow',
                       group=group,_sysfield=True,indexed=True)
            lastTS = tbl.attributes.get('lastTS')
            if not lastTS:
                tbl.attributes['lastTS'] = '__mod_ts'
        if full_upd:
            tbl.column('__full_mod_ts', dtype=tsType, name_long='!!Full Update TS', group=group, _sysfield=True, indexed=True)

        if md5:
            tbl.column('__rec_md5', name_long='!!Update date', onUpdating='setRecordMd5', onInserting='setRecordMd5',
                       group=group,_sysfield=True)
        if useProtectionTag:
            self.sysFields_protectionTag(tbl,protectionTag=useProtectionTag,group=group)
        if hierarchical:
            hierarchical = 'pkey' if hierarchical is True else '%s,pkey' %hierarchical
            assert id,'You must use automatic id in order to use hierarchical feature in sysFields'
            tblname = tbl.parentNode.label
            pkg = tbl.attributes['pkg']
            tbl.column('parent_id',size='22',name_long='!!Parent id',
                                             onUpdating='hierarchical_before',
                                             onUpdated='hierarchical_after',
                                             onInserting='hierarchical_before',group='*',_sysfield=True).relation('%s.id' %tblname,mode='foreignkey', 
                                                                                        onDelete='cascade',relation_name='_children',
                                                                                        one_name='!!Parent',many_name='!!Children',
                                                                                        deferred=True,
                                                                                        one_group=group,many_group=group)
            tbl.formulaColumn('child_count','(SELECT count(*) FROM %s.%s_%s AS children WHERE children.parent_id=#THIS.id)' %(pkg,pkg,tblname),group='*')
            tbl.formulaColumn('hlevel',"""length($hierarchical_pkey)-length(replace($hierarchical_pkey,'/',''))+1""",group='*')
            if hierarchical_root_id:
                tbl.column('root_id',sql_value="substring(:hierarchical_pkey from 1 for 22)",
                            group='*',size='22').relation('%s.id' %tblname,relation_name='_grandchildren',mode='foreignkey',one_name='!!Root',many_name='!!Grandchildren',
                                                onDelete='ignore')
            if hierarchical_virtual_roots:
                tbl.column('_virtual_node',dtype='B',name_lomg="!!H.Virtual node",copyFromParent=True)

            hfields = []
            for fld in hierarchical.split(','):
                if fld=='pkey':
                    tbl.column('hierarchical_pkey',unique=True,group=group,_sysfield=True) 
                    tbl.column('_parent_h_pkey',group=group,_sysfield=True)
                    hfields.append(fld)
                else:
                    unique = False
                    if ':' in fld:
                        fld,mode = fld.split(':')
                        unique = mode=='unique'
                    hcol = tbl.column(fld)
                    fld_caption=hcol.attributes.get('name_long',fld).replace('!!','')  
                    hfields.append(fld)
                    tbl.column('hierarchical_%s'%fld,name_long='!!Hierarchical %s'%fld_caption,group=group,_sysfield=True,
                                unique=unique)
                    tbl.column('_parent_h_%s'%fld,name_long='!!Parent Hierarchical %s'%fld_caption,group=group,_sysfield=True)
            tbl.attributes['hierarchical'] = ','.join(hfields)
            if not counter:
                tbl.attributes.setdefault('order_by','$hierarchical_%s' %hfields[0] )
            
            broadcast = tbl.attributes.get('broadcast')
            broadcast = broadcast.split(',') if broadcast else []
            if 'parent_id' not in broadcast:
                broadcast.append('parent_id')
            tbl.attributes['broadcast'] = ','.join(broadcast)

        if counter:
            tbl.attributes['counter'] = counter
            if hierarchical:
                assert counter is True, 'in hierarchical counter is not relative to a foreignkey'
                tbl.column('_h_count',group=group,_sysfield=True)
                tbl.column('_parent_h_count',group=group,_sysfield=True) 
                tbl.column('_row_count', dtype='L', name_long='!!Counter', counter=True,group=group,_sysfield=True)
                default_order_by = '$_h_count' if hierarchical == 'pkey' else " COALESCE($_h_count,$%s) " %hierarchical.split(',')[0]
                tbl.formulaColumn('_h_sortcol',default_order_by,_sysfield=True, group=group)
                tbl.attributes.setdefault('order_by','$_h_sortcol')
            else:
                self.sysFields_counter(tbl,'_row_count',counter=counter,group=group,name_long='!!Counter')
                tbl.attributes.setdefault('order_by','$_row_count')
        if counter_kwargs:
            for k,v in counter_kwargs.items():
                self.sysFields_counter(tbl,'_row_count_%s' %k,counter=v,group=group,name_long='!!Counter %s' %k)
        audit = tbl.attributes.get('audit')
        if audit:
            tbl.column('__version','L',name_long='Audit version',
                        onUpdating='setAuditVersionUpd', onInserting='setAuditVersionIns',_sysfield=True,
                        group=group)
        diagnostic = tbl.attributes.get('diagnostic')
        unifyRecordsTag = tbl.attributes.get('unifyRecordsTag')
        if unifyRecordsTag:
            tbl.column('__moved_related','X',group=group,_sysfield=True)
        if diagnostic:
            tbl.column('__warnings',name_long='!!Warnings',group=group,_sysfield=True)
            tbl.column('__errors',name_long='!!Errors',group=group,_sysfield=True)
        if user_ins:
            tbl.column('__ins_user', name_long='!!User Insert', onInserting='setCurrentUser', group=group,_sysfield=True)
        if user_upd:
            tbl.column('__mod_user', name_long='!!User Modify', onUpdating='setCurrentUser', onInserting='setCurrentUser', group=group,_sysfield=True)
        if draftField:
            draftField = '__is_draft' if draftField is True else draftField
            tbl.attributes['draftField'] = draftField
            tbl.column(draftField, dtype='B', name_long='!!Is Draft',group=group,_sysfield=True)
        if invalidFields or invalidRelations:
            if invalidFields:
                tbl.attributes['invalidFields'] = '__invalid_fields'
                tbl.column('__invalid_fields',name_long='!!Invalids',group=group,_sysfield=True)
                r = ['( $__invalid_fields IS NOT NULL )']
            else:
                r = []
            if invalidRelations:
                for rel in invalidRelations.split(','):
                    r.append('%s.__is_invalid' %rel)
            tbl.formulaColumn('__is_invalid', ' ( %s ) '  %' OR '.join(r), dtype='B',aggregator='OR')
        if df:
            self.sysFields_df(tbl)
        tbl.formulaColumn('__protecting_reasons',sql_formula=True,group=group,name_long='!!Protecting reasons',_sysfield=True)
        tbl.formulaColumn('__is_protected_row',"$__protecting_reasons!=''",group=group,name_long='!!Row Protected',_sysfield=True)

        if filter(lambda r: r!='_release_' and r.startswith('_release_'), dir(self)):
            tbl.column('__release', dtype='L', name_long='Sys Version', group=group,_sysfield=True)
            
        if filter(lambda r: r!='sysRecord_' and r.startswith('sysRecord_'), dir(self)):
            tbl.column('__syscode',size=':20',unique=True,indexed=True,
                _sysfield=True,group=group,name_long='!!Internal code')
            tbl.formulaColumn('__protected_by_syscode',
                                """ ( CASE WHEN $__syscode IS NULL THEN NULL 
                                   ELSE NOT (',' || :env_userTags || ',' LIKE '%%,'|| :systag || ',%%')
                                   END ) """,
                                dtype='B',var_systag=tbl.attributes.get('syscodeTag') or 'superadmin',_sysfield=True,
                                group=group)
        self.sysFields_extra(tbl,_sysfield=True,group=group)
        

    def _sysFields_defaults(self,user_ins=None,user_upd=None):
        if user_ins is None:
            default_user_ins = self.db.application.config['sysfield?user_ins']
            user_ins = boolean(default_user_ins) if default_user_ins is not None else True
        if user_upd is None:
            default_user_upd = self.db.application.config['sysfield?user_upd']
            user_upd = boolean(default_user_upd) if default_user_upd is not None else False
        return user_ins,user_upd

    def sysFields_protectionTag(self,tbl,protectionTag=None,group=None):
        tbl.column('__protection_tag', name_long='!!Protection tag', group=group,_sysfield=True,_sendback=True,onInserting='setProtectionTag')
        tbl.formulaColumn('__protected_by_tag',""" ( CASE WHEN $__protection_tag IS NULL THEN NULL 
                                                    ELSE NOT (',' || :env_userTags || ',' LIKE '%%,'|| $__protection_tag || ',%%')
                                                    END ) """,dtype='B',_sysfield=True)
        #doctor,staff,superadmin               ,doctor,staff,superadmin, LIKE %%,admin,%%

    def sysFields_df(self,tbl):
        tbl.column('df_fields',dtype='X',group='_',_sendback=True)
        tbl.column('df_fbcolumns','L',group='_')
        tbl.column('df_custom_templates','X',group='_')
        tbl.column('df_colswidth',group='_')


    def sysFields_counter(self,tbl,fldname,counter=None,group=None,name_long='!!Counter'):
        tbl.column(fldname, dtype='L', name_long=name_long, onInserting='setRowCounter',counter=True,
                            _counter_fkey=counter,group=group,_sysfield=True)
    
    def sysFields_extra(self,tbl,**kwargs):
        for m in [k for k in dir(self) if k.startswith('sysFields_extra_') and not k[-1]=='_']:
            getattr(self,m)(tbl,**kwargs)

    def hasProtectionColumns(self):
        result = False
        if filter(lambda r: r.startswith('__protected_by_'), self.model.virtual_columns.keys()) or self.attributes.get('protectionColumn'):
            result = True
        return result

    def sql_formula___protecting_reasons(self,attr):
        protections= []
        if self.attributes.get('protectionColumn'):
            pcol = self.attributes['protectionColumn']
            protections.append("( CASE WHEN $%s IS NULL THEN NULL ELSE '%s' END ) " %(pcol,pcol))
        for field in filter(lambda r: r.startswith('__protected_by_'), self.model.virtual_columns.keys()):
            protections.append("""( CASE WHEN $%s IS TRUE THEN '%s' ELSE NULL END )  """ %(field,field[15:]))
        if protections:
            return "array_to_string(ARRAY[%s],',')"   %','.join(protections)
        else:
            return " NULL "

    def _isReadOnly(self,record):
        readOnly = False
        if self.attributes.get('readOnly'):
            readOnly = True
        elif record.get('__protecting_reasons'):
            readOnly = record.get('__protecting_reasons')
        elif record.get('__protection_tag'):
            readOnly = not (record['__protection_tag'] in self.db.currentEnv['userTags'].split(','))
        return readOnly

    def formulaColumn_allowedForPartition(self):

        partitionParameters = self.partitionParameters
        sql_formula = None
        if partitionParameters:
            sql_formula = "( $%(field)s IN :env_allowed_%(path)s )" %partitionParameters
        else:
            sql_formula = "TRUE"
        return [dict(name='__allowed_for_partition',sql_formula=sql_formula or 'FALSE',
                    dtype='B',name_long='!!Allowed for partition',group='_')]

    def getPartitionAllowedUsers(self,recordOrPkey):
        partitionParameters = self.partitionParameters
        usertbl = self.db.table('adm.user')
        if not partitionParameters:
            f = usertbl.query().fetch()
            return [r['id'] for r in f]
        else:
            record = self.recordAs(recordOrPkey)
            record_partition_fkey = record[self.partitionParameters['field']]
            f = usertbl.query(columns='$id,$allowed_%(field)s' %partitionParameters).fetch()
            allowedfield = 'allowed_%(field)s' %partitionParameters
            return [r['id'] for r in f if record_partition_fkey in r.get(allowedfield,'').split(',')]        

    def addPhonetic(self,tbl,column,mode=None,size=':5',group=None):
        mode = mode or 'dmetaphone'
        group = group or 'zzz'
        phonetic_column = '__phonetic_%s' %column
        tbl.column(column).attributes.update(phonetic=phonetic_column,_sendback=True,query_dtype='PHONETIC',_sysfield=True)
        tbl.column(phonetic_column,size=size,sql_value='%s(:%s)' %(mode,column),phonetic_mode=mode,group=group,_sendback=True,_sysfield=True)


    def invalidFieldsBag(self,record):
        if not record['__invalid_fields']:
            return
        result = Bag()
        invdict = fromJson(record['__invalid_fields'])
        for k,v in invdict.items():
            result.setItem(k,'%(fieldcaption)s:%(error)s' %v)
        return result

    def trigger_hierarchical_before(self,record,fldname,old_record=None,**kwargs):
        self.hierarchicalHandler.trigger_before(record,old_record=old_record)

    def trigger_hierarchical_after(self,record,fldname,old_record=None,**kwargs):
        self.hierarchicalHandler.trigger_after(record,old_record=old_record)

    @public_method
    def getHierarchicalData(self,caption_field=None,condition=None,caption=None,
                            dbstore=None,columns=None,related_kwargs=None,
                            resolved=False,**kwargs):
        related_kwargs = related_kwargs or dict()
        if hasattr(self,'hierarchicalHandler'):
            return self.hierarchicalHandler.getHierarchicalData(caption_field=caption_field,condition=condition,
                                                caption=caption,dbstore=dbstore,columns=columns,
                                                related_kwargs=related_kwargs,resolved=resolved,**kwargs)
        if related_kwargs.get('table') or kwargs.get('related_table'):
            return self.getHierarchicalDataBag(caption_field=caption_field,condition=condition,
                                                caption=caption,dbstore=dbstore,columns=columns,
                                                related_kwargs=related_kwargs,resolved=resolved,**kwargs)

    @public_method
    def hierarchicalSearch(self,seed=None,related_table=None,**kwargs):
        if hasattr(self,'hierarchicalHandler'):
            return self.hierarchicalHandler.hierarchicalSearch(seed=seed,related_table=related_table,**kwargs)


    @extract_kwargs(condition=True,related=True)
    def getHierarchicalDataBag(self,caption_field=None,condition=None,
                            condition_kwargs=None,caption=None,
                            dbstore=None,columns=None,related_kwargs=None,
                            resolved=False,**kwargs):
        b = Bag()
        caption = caption or self.name_plural
        condition_kwargs = condition_kwargs or dict()
        condition_kwargs.update(dictExtract(kwargs,'condition_'))
        caption_field = caption_field or self.attributes.get('caption_field') or self.pkey
        columns = columns or '*'
        f = self.query(where=condition,columns='%s,$%s' %(columns,caption_field),**condition_kwargs).fetch()
        related_tblobj = self.db.table(related_kwargs['table'])
        related_caption_field = related_kwargs.get('caption_field') or related_tblobj.attributes.get('caption_field')
        for r in f:
            pkey = r['pkey']
            value = Bag()
            relchidren = self._hdata_getRelatedChildren(fkey=pkey,related_tblobj=related_tblobj,
                                                              related_caption_field=related_caption_field,
                                                              related_kwargs = related_kwargs)
            for related_row in relchidren:
                related_row = dict(related_row)
                relpkey = related_row.pop('pkey',None)
                value.setItem(relpkey, None,
                                child_count=0,
                                caption=related_row[related_caption_field],
                                pkey=relpkey, treeIdentifier='%s_%s'%(pkey, relpkey),
                                node_class='tree_related',**related_row)    
            b.setItem(pkey.replace('.','_'),value,
                        pkey=pkey or '_all_',
                        caption=r[caption_field],child_count=len(value),
                        treeIdentifier = pkey,
                        parent_id=None,
                        hierarchical_pkey=pkey,
                       _record=dict(r))
        result = Bag()
        result.setItem('root',b,caption=caption,child_count=1,pkey='',treeIdentifier='_root_')
        return result

    def _hdata_getRelatedChildren(self,fkey=None,related_tblobj=None,related_caption_field=None,related_kwargs=None):
        related_kwargs = dict(related_kwargs)
        columns = related_kwargs.get('columns') or '*,$%s' %related_caption_field
        relation_path = related_kwargs['path']
        condition = related_kwargs.get('condition')
        condition_kwargs = dictExtract(related_kwargs,'condition_')
        wherelist = [' ($%s=:fkey) ' % relation_path]
        if condition:
            wherelist.append(condition)
        result = related_tblobj.query(where=' AND '.join(wherelist),columns=columns,
                                        fkey=fkey,**condition_kwargs).fetch()
        return result

    def onDbUpgrade_createSysRecords(self):
        self.createSysRecords()

    def createSysRecords(self,do_update=False):
        syscodes = []
        for m in dir(self):
            if m.startswith('sysRecord_') and m!='sysRecord_':
                method = getattr(self,m)
                if getattr(method,'mandatory',False):
                    syscodes.append(m[10:])
        commit = do_update
        if syscodes:
            f = self.query(where='$__syscode IN :codes',codes=syscodes,for_update=do_update).fetchAsDict('__syscode')
            for syscode in syscodes:
                if syscode not in f:
                    self.sysRecord(syscode)
                    commit = True
                elif do_update:
                    updated_version = getattr(self,'sysRecord_%s' %syscode)()
                    rec = f[syscode]
                    oldrecord = dict(rec)
                    for k,v in updated_version.items():
                        rec[k] = v
                    rec['__syscode'] = syscode
                    self.update(rec,oldrecord)
        if commit:
            self.db.commit()

    def sysRecord(self,syscode):
        return self.cachedRecord(syscode,keyField='__syscode',createCb=self._sysRecordCreateCb)

    def _sysRecordCreateCb(self,syscode,**extra_fields):
        sysRecord_masterfield = self.attributes.get('sysRecord_masterfield') or self.pkey
        with self.db.tempEnv(connectionName='system'):
            record = getattr(self,'sysRecord_%s' %syscode)()
            record['__syscode'] = syscode
            masterfield_value = record[sysRecord_masterfield]
            if masterfield_value is not None:
                oldrecord = self.query(where='$%s=:mv' %sysRecord_masterfield,mv=masterfield_value,
                                            addPkeyColumn=False).fetch()
                if oldrecord:
                    oldrecord = oldrecord[0]
                    record = dict(oldrecord)
                    record['__syscode'] = syscode
                    self.update(record,oldrecord)
                    self.db.commit()
                    return record
            record.update(extra_fields)
            self.insert(record)
            self.db.commit()
        return record

    def importerStructure(self):
        "override"
        pass

    def importerMatchIndex(self,reader,struct=None):
        importerStructure = struct or self.importerStructure() or dict()
        checkfields = importerStructure.get('fields')
        if not checkfields:
            return
        headers = set(reader.headers)
        convertdict = {}
        for k,v in checkfields.items():
            intersection =  headers.intersection(set(v.lower().replace(' ','_').replace('.','_').split(',')))
            if intersection:
                convertdict[list(intersection)[0]] = k
        return convertdict

    def importerCheck(self,reader):
        importerStructure = self.importerStructure() or dict()
        checkfields = importerStructure.get('fields')
        mandatories = importerStructure.get('mandatories')
        if not mandatories:
            return
        match_index = self.importerMatchIndex(reader)
        errors = []
        matched_cols =  match_index.values()
        for k in mandatories.split(','):
            if k not in matched_cols:
                errors.append(k)
        if errors:
            return 'Missing %s' %','.join(errors)
    
    def importerInsertRow(self,row,import_mode=None):
        if import_mode=='insert_or_update':
            self.insertOrUpdate(row)
        else:
            self.insert(row)


    @public_method
    def pathFromPkey(self,pkey=None,dbstore=None):
        return self.hierarchicalHandler.pathFromPkey(pkey=pkey,dbstore=dbstore)

    @public_method
    def getHierarchicalPathsFromPkeys(self,pkeys=None,related_kwargs=None,parent_id=None,dbstore=None,**kwargs):
        if hasattr(self,'hierarchicalHandler'):
            return self.hierarchicalHandler.getHierarchicalPathsFromPkeys(pkeys=pkeys,
                                                               related_kwargs=related_kwargs,parent_id=parent_id,
                                                              dbstore=dbstore,**kwargs)
        if related_kwargs['table']:
            related_tblobj = self.db.table(related_kwargs['table'])
            p = related_kwargs['path']
            f = related_tblobj.query(where='$%s IN :pkeys' %related_tblobj.pkey, 
                                pkeys=pkeys.split(','),columns='$%s' %p).fetch()
            return ','.join(['%s.%s' %(r[p].replace('.','_'),r['pkey']) for r in f])

    def trigger_setRowCounter(self,record,fldname,**kwargs):
        """field trigger used for manage rowCounter field"""
        if record.get(fldname) is not None:
            return
        counter_fkey = self.column(fldname).attributes.get('_counter_fkey')
        where = None
        wherekw = dict()       
        if counter_fkey is not True:
            filtered = filter(lambda n: record.get(n),counter_fkey.split(','))
            if not filtered:
                return
            counter_fkey = filtered[0]
            where = '$%s=:p_%s' %(counter_fkey,counter_fkey)
            wherekw['p_%s' %counter_fkey] = record[counter_fkey]
        last_counter_fetch = self.query(columns='$%s' %fldname,where=where,
                                    order_by='$%s desc' %fldname,limit=1,
                                    **wherekw).fetch()
        last_counter = last_counter_fetch[0].get(fldname) or 1 if last_counter_fetch else 0
        record[fldname] = last_counter +1
        
    def trigger_setTSNow(self, record, fldname,**kwargs):
        """This method is triggered during the insertion (or a change) of a record. It returns
        the insertion date as a value of the dict with the key equal to ``record[fldname]``,
        where ``fldname`` is the name of the field inserted in the record.
        
        :param record: the record
        :param fldname: the field name"""
         
        if not getattr(record, '_notUserChange', None):
            if self.column(fldname).dtype == 'DHZ':
                record[fldname] = datetime.datetime.now(pytz.utc)
            else:
                record[fldname] = datetime.datetime.now()
            if '__full_mod_ts' in self.columns:
                record['__full_mod_ts'] = record[fldname]

    def trigger_setProtectionTag(self,record,fldname,**kwargs):
        record[fldname] = self.getProtectionTag(record=record)

    def getProtectionTag(self,record=None):
        #override
        pass
    
    def trigger_setCurrentUser(self, record, fldname,**kwargs):
        """This method is triggered during the insertion (or a change) of a record. It returns
        the current user as a value of the dict with the key equal to ``record[fldname]``,
        where ``fldname`` is the name of the field inserted in the record.
        
        :param record: the record
        :param fldname: the field name"""
        if not getattr(record, '_notUserChange', None):
            record[fldname] = self.db.currentUser

    def trigger_setAuditVersionIns(self, record, fldname):
        """TODO
        
        :param record: the record
        :param fldname: the field name"""
        record[fldname] = 0
        
    def trigger_setAuditVersionUpd(self, record, fldname,**kwargs):
        """TODO
        
        :param record: the record
        :param fldname: the field name"""
        record[fldname] = (record.get(fldname) or 0)+ 1
        
    def trigger_setRecordMd5(self, record, fldname,**kwargs):
        """TODO
        
        :param record: the record
        :param fldname: the field name"""
        pass

    def inheritedFields(self):      
        return [field for field,colobj in self.columns.items() if colobj.attributes.get('inherited')]

    def getInheritedValues(self,record_source):      
        result = {}        
        for field,colobj in self.columns.items():
            doCopy = colobj.attributes.get('inherited')
            if doCopy:
                field_source = field if doCopy is True else doCopy
                if field_source in record_source:
                    result[field] = record_source[field_source]
        return result
        
    def hasRecordTags(self):
        """TODO"""
        return self.attributes.get('hasRecordTags', False)

    def checkDiagnostic(self,record):
        if self.attributes.get('diagnostic'):
            errors = self.diagnostic_errors(record)
            warnings = self.diagnostic_warnings(record)
            record['__errors'] = '\n'.join(errors) if errors else None
            record['__warnings'] = '\n'.join(warnings) if warnings else None

    def dbo_onInserting(self,record=None,**kwargs):
        self.checkDiagnostic(record)

    def dbo_onUpdating(self,record=None,old_record=None,pkey=None,**kwargs):
        self.checkDiagnostic(record)
        if self.draftField:
            if hasattr(self,'protect_draft'):
                record[self.draftField] = self.protect_draft(record)
        logicalDeletionField =self.logicalDeletionField
        if logicalDeletionField and old_record and self.fieldsChanged(logicalDeletionField,record,old_record):
            self.onArchivingRecord(record,record.get(logicalDeletionField))
            if not record.get(logicalDeletionField) and record.get('__moved_related'):
                self.restoreUnifiedRecord(record)

    def df_getQuerableFields(self,field,group=None,caption_field=None,grouped=False,**kwargs):
        column = self.column(field)
        df_field = column.attributes['subfields']
        df_column = column.table.column(df_field)
        df_table = df_column.relatedTable()
        querable = Bag()
        df_caption_field = caption_field or df_table.attributes.get('caption_field')
        fetch = df_table.dbtable.query(columns='$%s,$df_fields' %df_caption_field,**kwargs).fetch()
        typeconverter = {'T':'text','P':'text', 'N': 'numeric','B': 'boolean',
                         'D': 'date', 'H': 'time without time zone','L': 'bigint', 'R': 'real'}
        for r in fetch:
            df_fields = Bag(r['df_fields'])
            for v in df_fields.values():
                if v['querable']:
                    dtype = dtype=v['data_type']
                    sql_formula = """ (xpath('/GenRoBag/%s/text()', CAST($%s as XML) ) )[1] """ %(v['code'],field)
                    sql_formula = """CAST ( ( %s ) AS %s) """ %(sql_formula,typeconverter[dtype])
                    c = slugify(r[df_caption_field]).replace('-','_')
                    if grouped:
                        fcode ='%s_%s_%s' %(field,c,v['code'])
                        cgroup= group+'.%(df)s'
                        subgroup_df=r[df_caption_field]
                    else:
                        fcode ='%s_%s' %(field,v['code'])
                        subgroup_df = None
                        cgroup = group
                    querable.setItem(fcode,None,name=fcode,name_long=v['description'],dtype=dtype,
                                    sql_formula=sql_formula,
                                    group=cgroup ,
                                    subgroup_df=subgroup_df)
        return querable.digest('#a')


    def df_getFieldsRows(self,pkey=None,**kwargs):
        if self.column('df_fields') is None:
            fieldstable = self.attributes.get('df_fieldstable')
            return self.df_getFieldsRows_table(fieldstable,pkey=pkey,**kwargs)
        else:
            return self.df_getFieldsRows_bag(pkey,**kwargs)

    def df_importLegacyScript(self):
        updRecords = dict()
        pkeys = self.query().selection().output('pkeylist')
        for pkey in pkeys:
            self._df_importLegacyRec(pkey,updRecords=updRecords)
        def cb(row):
            row['df_fields'] = updRecords.get(row.get('id'))
        self.batchUpdate(cb,_pkeys=pkeys)

    def _df_importLegacyRec(self,pkey=None,updRecords=None):
        fieldstable = self.db.table(self.attributes.get('df_fieldstable'))
        f = fieldstable.query(where='$maintable_id=:m_id',m_id=pkey,bagFields=True,order_by='$_row_count').fetch()
        b = Bag()
        for r in f:
            c = dict(r)
            for k in ('id','__del_ts','_row_count','maintable_id','pkey'):
                c.pop(k)
            c['wdg_kwargs'] = Bag(c['wdg_kwargs'])
            c = Bag(c)
            b.setItem(c['code'],c)
        updRecords[pkey] = b

    def df_getFieldsRows_bag(self,pkey=None,**kwargs):
        hierarchical = self.attributes.get('hierarchical')
        where="$%s=:p" %self.pkey
        p = pkey
        order_by = '$__ins_ts'
        columns='*,$df_fields'

        if hierarchical:
            hpkey = self.readColumns(columns='$hierarchical_pkey' ,pkey=pkey)
            p = hpkey
            where =  " ( :p = $hierarchical_pkey ) OR ( :p ILIKE $hierarchical_pkey || :suffix) "
            order_by='$hlevel'
        result = []
        f = self.query(where=where,p=p,suffix='/%%',order_by=order_by,columns=columns).fetch()
        result = Bag()
        for r in f:
            for v in Bag(r['df_fields']).values():
                result.setItem(v['code'],v)
        return [v.asDict(ascii=True) for v in result.values()]

    def df_getFieldsRows_table(self,fieldstable,pkey=None,**kwargs):
        fieldstable = self.db.table(fieldstable)
        where="$maintable_id=:p"
        columns='*,$wdg_kwargs'
        hierarchical = self.attributes.get('hierarchical')
        p = pkey
        order_by='$_row_count'
        if hierarchical:
            hpkey = self.readColumns(columns='$hierarchical_pkey' ,pkey=pkey)
            p = hpkey
            where =  " ( :p = @maintable_id.hierarchical_pkey ) OR ( :p ILIKE @maintable_id.hierarchical_pkey || :suffix) "
            columns='*,$wdg_kwargs,@maintable_id.hierarchical_pkey AS type_hpkey'
            order_by = '$hlevel,$_row_count'
        result = fieldstable.query(where=where,p=p,suffix='/%%',order_by=order_by,columns=columns).fetch()
        
        return result
    
    @public_method
    def df_subFieldsBag(self,pkey=None,df_field='',df_caption=''):
        rows = self.df_getFieldsRows(pkey=pkey)
        result = Bag()
        if not rows:
            return result
        else:
            for r in rows:
                fieldpath = r['code']
                description = r.get('description') or fieldpath.title()
                fullcaption = description
                caption=description
                page = r.get('page')
                label = r['code']
                if df_field:
                    fieldpath='%s.%s' %(df_field,r['code'])
                    fullcaption='%s/%s' %(df_caption,r['description'])
                if page:
                    fullcaption = '%s/%s' %(page,fullcaption)
                    label ='%s.%s' %(page.replace('.','_'),label)

                result.setItem(label,None,caption=caption,dtype=r.get('data_type','T'),
                                fieldpath=fieldpath,fullcaption=fullcaption,page=page)
        return result
                     
    def setTagColumn(self, tbl, name_long=None, group=None):
        """TODO
        
        :param tbl: the :ref:`table` object
        :param name_long: the :ref:`name_long`
        :param group: a hierarchical path of logical categories and subacategories
                      the columns belongs to. For more information, check the :ref:`group` section"""
        warnings_module.warn(""" setTagColumn has been removed """, DeprecationWarning, 2) 

    #FUNCTIONS SQL
    def normalizeText(self,text):
        return """regexp_replace(translate(%s,'-',' '),'[.|,|;]', '', 'g')""" %text


    def templateColumn(self,record=None,field=None):
        template = self.column(field).attributes.get('template_name')
        tplpath = '%s:%s' %(self.fullname,template)
        tplkey = 'template_%s' %tplpath
        currEnv = self.db.currentEnv
        tpl = currEnv.get(tplkey)
        if not tpl:
            tpl = self.db.currentPage.loadTemplate(tplpath)
            currEnv[tplkey] = tpl
        kwargs = dict()
        if isinstance(tpl,Bag):
            kwargs['locale'] = self.db.currentPage.locale #tpl.getItem('main?locale')
            kwargs['masks'] = tpl.getItem('main?masks')
            kwargs['formats'] = tpl.getItem('main?formats')
            kwargs['df_templates'] = tpl.getItem('main?df_templates')
            kwargs['dtypes'] = tpl.getItem('main?dtypes')
            #virtual_columns = tpl.getItem('main?virtual_columns')
        r = Bag(dict(record))
        if not isinstance(record,Bag):
            tpl['main'] = tpl['main'].replace('@','_').replace('.','_')
        return templateReplace(tpl,r,**kwargs)


    def hosting_copyToInstance(self,source_instance=None,dest_instance=None,_commit=False,logger=None,onSelectedSourceRows=None,**kwargs):
        #attr = self.attributes
        #logger.append('** START COPY %(name_long)s **'%attr)
        source_db = self.db if not source_instance else self.db.application.getAuxInstance(source_instance).db 
        dest_db = self.db if not dest_instance else self.db.application.getAuxInstance(dest_instance).db 
        source_tbl = source_db.table(self.fullname)
        dest_tbl = dest_db.table(self.fullname)
        kwargs.setdefault('bagFields',True)
        pkey = self.pkey
        source_rows = source_tbl.query(addPkeyColumn=False,excludeLogicalDeleted=False,
              excludeDraft=False,**kwargs).fetch()
        onSelectedSourceRows = onSelectedSourceRows or getattr(self,'hosting_copyToInstance_onSelectedSourceRows',None)
        if onSelectedSourceRows:
            onSelectedSourceRows(source_instance=source_instance,dest_instance=dest_instance,source_rows=source_rows)
        all_dest = dest_tbl.query(addPkeyColumn=False,for_update=True,excludeLogicalDeleted=False,
              excludeDraft=False,**kwargs).fetchAsDict(pkey)
        existing_dest = dest_tbl.query(addPkeyColumn=False,for_update=True,excludeLogicalDeleted=False,
              excludeDraft=False,where='$%s IN :pk' %pkey,pk=[r[pkey] for r in source_rows]).fetchAsDict(pkey)
        all_dest.update(existing_dest)
        if source_rows:
            fieldsToCheck = ','.join([c for c in source_rows[0].keys() if c not in ('__ins_ts','__mod_ts','__ins_user','__mod_user')])
            for r in source_rows:
                r = dict(r)
                if r[pkey] in all_dest:
                    oldr = dict(all_dest[r[pkey]])
                    if self.fieldsChanged(fieldsToCheck,r,oldr):
                        #logger.append('\t\t ** UPDATING LINE %s **' %r['id'])
                        dest_tbl.raw_update(r,oldr)
                    all_dest.pop(r[pkey])
                else:
                    #logger.append('\t\t ** INSERTING LINE %s **' %r['id'])
                    dest_tbl.raw_insert(r)  
            #self.hosting_removeUnused(dest_db,all_dest.keys())
            if _commit:
                dest_db.commit()
        return source_rows

    def hosting_removeUnused(self,dest_db,missing=None):
        dest_db.table(self.fullname).deleteSelection(where='$%s IN :missing' %self.pkey,missing=missing,
            excludeLogicalDeleted=False,excludeDraft=False)


    def getCustomFieldsMenu(self):
        data,metadata = self.db.table('adm.userobject').loadUserObject(code='%s_fieldstree' %self.fullname.replace('.','_'),objtype='fieldsmenu')
        return data,metadata


    def isInStartupData(self):
        inStartupData = self.attributes.get('inStartupData')
        if inStartupData is False:
            return False
        elif inStartupData is not None:
            return True
        for t,isdeferred in self.model.dependencies:
            if not self.db.table(t).isInStartupData():
                return False
        return True

    ################## COUNTER SEQUENCE TRIGGER RELATED TO adm.counter ############################################

    def counterColumns(self):
        return [k[8:] for k in dir(self) if k.startswith('counter_') and not k[-1]=='_']

    def getCounterPars(self,field,record=None):
        return getattr(self,'counter_%s' %field)(record=record)


    def trigger_releaseCounters(self,record=None,backToDraft=None):
        for field in self.counterColumns():
            if record.get(field):
                counter_pars = self.getCounterPars(field,record) 
                if not counter_pars or not counter_pars.get('recycle') or (backToDraft and counter_pars.get('assignIfDraft')):
                    continue
                self.db.table('adm.counter').releaseCounter(tblobj=self,field=field,record=record)

    def trigger_assignCounters(self,record=None,old_record=None):
        "Inside dbo"
        if old_record and self.isDraft(record) and not self.isDraft(old_record):
            self.trigger_releaseCounters(record,backToDraft=True)
        else:
            for field in self.counterColumns():
                self.db.table('adm.counter').assignCounter(tblobj=self,field=field,record=record)

    @public_method
    def guessCounter(self,record=None,field=None,**kwargs):
        sequence,sequenceInfo = self.db.table('adm.counter').guessNextSequence(tblobj=self,field=field,record=record)
        result = dict(promised=True,wdg_color='green',sequence=sequence)
        pars = getattr(self,'counter_%s' %field)(record=record)
        if sequenceInfo.get('recycled'):
            result['wdg_color'] = 'darkblue'
            fieldname = self.column(field).name_long or field
            fieldname.replace('!!','')
            message = pars.get('message_recycle','!!%(fieldname)s promised value (recycled)')
            message = message %dict(fieldname=fieldname,sequence=sequence) 
            result['wdg_tip'] = message
        return result

    def _sequencesOnLoading(self,newrecord,recInfo=None):
        for field in self.counterColumns():
            pars = getattr(self,'counter_%s' %field)(record=newrecord)
            if not pars:
                continue
            if self.isDraft(newrecord) and not pars.get('assignIfDraft'):
                continue
            if pars.get('showOnLoad'):
                sequence,sequenceInfo = self.db.table('adm.counter').guessNextSequence(tblobj=self,field=field,record=newrecord)
                kw = dict(promised=True,wdg_color='green')
                if sequenceInfo.get('recycled'):
                    kw['wdg_color'] = 'darkblue'
                    fieldname = self.column(field).name_long or field
                    fieldname.replace('!!','')
                    message = pars.get('message_recycle','!!%(fieldname)s promised value (recycled)')
                    loaded_message = recInfo.setdefault('loaded_message',[])
                    if not isinstance(loaded_message,list):
                        loaded_message = [loaded_message]
                    message = message %dict(fieldname=fieldname,sequence=sequence) 
                    loaded_message.append(dict(message=message,messageType='warning',duration_out=5))
                    kw['wdg_tip'] = message
                    recInfo['loaded_message'] = loaded_message
                newrecord.setItem(field,sequence,**kw)


class GnrDboTable(TableBase):
    """TODO"""
    def use_dbstores(self,**kwargs):
        """TODO"""
        return self.attributes.get('multidb')


    def populateFromMasterDb(self,master_db=None,from_table=None,**kwargs):
        print 'populating %s from %s' %(self.fullname,from_table or '')
        descendingRelations = self.model.manyRelationsList(cascadeOnly=True)
        ascendingRelations = self.model.oneRelationsList(foreignkeyOnly=True)
        onPopulatingFromMasterDb = getattr(self,'onPopulatingFromMasterDb',None)

        if onPopulatingFromMasterDb:
            onPopulatingFromMasterDb(master_db=master_db,from_table=from_table,query_kwargs=kwargs)
        f = master_db.table(self.fullname).query(bagFields=True,addPkeyColumn=False,**kwargs).fetch()
        valuesset = self._getTableCache(self.fullname)
        for r in f:
            r = dict(r)
            self.populateAscendingRelationsFromMasterDb(r,master_db=master_db,ascendingRelations=ascendingRelations)
            if r[self.pkey] in valuesset:
                continue
            self.raw_insert(r)
            print '.',
            valuesset.add(r[self.pkey])
            for tbl,fkey in descendingRelations:
                if tbl!=from_table and tbl!=self.fullname:
                    self.db.table(tbl).populateFromMasterDb(master_db,where='$%s=:fkey' %fkey, fkey=r[self.pkey])
        print '\n'


    def populateAscendingRelationsFromMasterDb(self,record,master_db=None,ascendingRelations=None,foreignkeyOnly=None):
        currentEnv = self.db.currentEnv
        if not ascendingRelations:
            p = '%s_one_relations' %self.fullname.replace('.','_')
            ascendingRelations = currentEnv.get(p)
            if not ascendingRelations:
                ascendingRelations = self.model.oneRelationsList(foreignkeyOnly=foreignkeyOnly)
                currentEnv[p] = ascendingRelations
                self.db.currentEnv = currentEnv
        for table,pkey,fkey in ascendingRelations:
            valuesset = self._getTableCache(table)
            tblobj= self.db.table(table)
            fkeyvalue = record[fkey]
            if fkeyvalue and not fkeyvalue in valuesset:
                tblobj.populateFromMasterDb(master_db=master_db,where='$%s=:f' %pkey,f=fkeyvalue,from_table=self.fullname)
            

    def _getTableCache(self,table):
        currentEnv = self.db.currentEnv
        p = 'cached_%s' %table.replace('.','_')
        valuesset = currentEnv.get(p)
        if valuesset is None:
            tblobj = self.db.table(table)
            f = tblobj.query(columns='%s' %tblobj.pkey).fetch()
            valuesset = set([r['pkey'] for r in f])
            currentEnv[p] = valuesset
        return valuesset

    def deferredUpdateParentFullTs(self, record, relation_field):
        parent_id=record[relation_field]
        self.db.deferToCommit(self.updateParentFullTs, relation_field=relation_field, parent_id=parent_id, _deferredId=parent_id)

    def updateParentFullTs(self, relation_field, parent_id=None):
        relatedTbl = self.column(relation_field).relatedTable().dbtable
        relatedTbl.batchUpdate(dict(), pkey=parent_id)
           


        
class HostedTable(GnrDboTable):
    def hosting_config(self,tbl,mode=None):
        if mode=='slave' and self.db.application.hostedBy:
            tbl.attributes['readOnly'] = True

class AttachmentTable(GnrDboTable):
    """AttachmentTable"""

    def config_db(self,pkg):
        tblname = self._tblname
        tbl = pkg.table(tblname,pkey='id')
        mastertbl = '%s.%s' %(pkg.parentNode.label,tblname.replace('_atc',''))

        pkgname,mastertblname = mastertbl.split('.')
        tblname = '%s_atc' %mastertblname
        assert tbl.parentNode.label == tblname,'table name must be %s' %tblname
        model = self.db.model
        mastertbl =  model.src['packages.%s.tables.%s' %(pkgname,mastertblname)]
        mastertbl.attributes['atc_attachmenttable'] = '%s.%s' %(pkgname,tblname)
        mastertbl_name_long = mastertbl.attributes.get('name_long')        
        tbl.attributes.setdefault('caption_field','description')
        tbl.attributes.setdefault('rowcaption','$description')
        tbl.attributes.setdefault('name_long','%s  Attachment' %mastertbl_name_long)
        tbl.attributes.setdefault('name_plural','%s Attachments' %mastertbl_name_long)

        self.sysFields(tbl,id=True, ins=False, upd=False,counter='maintable_id')
        tbl.column('id',size='22',group='_',name_long='Id')
        tbl.column('filepath' ,name_long='!!Filepath',onDeleted='onDeletedAtc',onInserted='convertDocFile',onInserting='checkExternalUrl')
        tbl.column('external_url', name_long='!!External url')
        tbl.column('description' ,name_long='!!Description')
        tbl.column('mimetype' ,name_long='!!Mimetype')
        tbl.column('text_content',name_long='!!Content')
        tbl.column('info' ,'X',name_long='!!Additional info')
        tbl.column('maintable_id',size='22',group='*',name_long=mastertblname).relation('%s.%s.%s' %(pkgname,mastertblname,mastertbl.attributes.get('pkey')), 
                    mode='foreignkey', onDelete_sql='cascade',onDelete='cascade', relation_name='atc_attachments',
                    one_group='_',many_group='_',deferred=True)
        tbl.formulaColumn('adapted_url',"""CASE WHEN position('\:' in $filepath)>0 THEN '/'||$filepath
             ELSE '/_vol/' || $filepath
            END""",group='_')
                    
        tbl.formulaColumn('fileurl',"COALESCE($external_url,$adapted_url)",name_long='Fileurl')
        if hasattr(self,'atc_types'):
            tbl.column('atc_type',values=self.atc_types())
        if hasattr(self,'atc_download'):
            tbl.column('atc_download',dtype='B',name_lomg='DL')
        self.onTableConfig(tbl)

    def onArchiveExport(self,records,files=None):
        site = self.db.application.site
        for r in records:
            filepath = r['filepath']
            if  ':' not in filepath:
                filepath = 'home:%s' %filepath
            files[r['id']].append(self._atcStorageNode(r))
    
    def _atcStorageNode(self,record):
        filepath = record['filepath']
        if ':' not in filepath:
            filepath = 'home:%s' %filepath
        return self.db.application.site.storageNode(filepath)

    def onTableConfig(self,tbl):
        pass

    @public_method
    def atc_importAttachment(self,pkey=None):
        site = self.db.application.site
        record = self.record(pkey=pkey,for_update=True).output('dict')
        old_record = dict(record)
        text_content = site.extractTextContent(self._atcStorageNode(record))
        if text_content:
            record['text_content'] = text_content
            self.update(record,old_record=old_record)
            self.db.commit()

    def insertPdfFromDocAtc(self, attachment):
        """Creates a pdf version of a .doc/.docx attachment and inserts the a sibling record referring to it.
            Returns the new pdf attachment record
        :param attachment: source attachment record or pket"""

        if isinstance(attachment, basestring):
            attachment = self.recordAs(attachment, mode='dict')
        site = self.db.application.site
        docConverter = site.getService('doctopdf')
        pdf_record = None
        snode = self._atcStorageNode(attachment)
        if docConverter and snode.ext in ('doc','docx'):
            pdf_staticpath = docConverter.convert(snode)
            if pdf_staticpath:
                pdf_record = dict(filepath=pdf_staticpath,
                        mimetype=attachment['mimetype'],
                        description=os.path.basename(pdf_staticpath),
                        maintable_id=attachment['maintable_id'])
                self.insert(pdf_record)
                return pdf_record

    def _getDestAttachmentNode(self,maintable_id=None,filename=None):
        description,ext = os.path.splitext(filename)
        description = slugify(description)
        maintable = self.fullname[0:-4]
        maintableobj = self.db.table(maintable)
        destFolder = None
        if hasattr(maintableobj,'atc_getAttachmentPath'):
            destFolder = maintableobj.atc_getAttachmentPath(pkey=maintable_id)
        if not destFolder:
            destFolder = '%s/%s' %(maintable.replace('.','_'),maintable_id)
        if not ':' in destFolder:
            destFolder = 'home:%s' %destFolder
        site = self.db.application.site
        destFilename = '%s%s' %(description,ext)
        destStorageNode = site.storageNode(destFolder,destFilename)
        counter = 0
        while destStorageNode.exists:
            counter += 1
            description = '%s_%02i' %(description,counter)
            destFilename = '%s%s' %(description,ext)
            destStorageNode = site.storageNode(destFolder,destFilename)
        return destStorageNode
        
    def addAttachment(self,maintable_id=None,origin_filepath=None,destFolder=None,
                            description=None,mimetype=None,moveFile=False,copyFile=True,**kwargs):
        site = self.db.application.site
        originStorageNode = site.storageNode(origin_filepath)
        mimetype = mimetype or mimetypes.guess_type(originStorageNode.path)[0]
        filename = originStorageNode.basename
        if copyFile or moveFile:
            if destFolder:
                destStorageNode = site.storageNode(destFolder,filename)
            else:
                destStorageNode = self._getDestAttachmentNode(maintable_id=maintable_id,filename=filename)
            if moveFile:
                originStorageNode.move(destStorageNode)
            else:
                originStorageNode.copy(destStorageNode)
        else:
            destStorageNode = originStorageNode
        record = self.newrecord(maintable_id=maintable_id,
                        mimetype=mimetype,
                        description=destStorageNode.cleanbasename,
                        filepath=destStorageNode.fullpath,**kwargs)
        self.insert(record)
        return record
    
    def trigger_checkExternalUrl(self,record,**kwargs):
        if not record.get('description') and 'external_url' in record:
            record['description'] = record['external_url']


    def trigger_convertDocFile(self,record,**kwargs):
        if not record.get('filepath'):
            return
        else:
            p,ext = os.path.splitext(record['filepath'])
            if ext.lower() in ('.doc','.docx'):
                self.insertPdfFromDocAtc(record)

    def trigger_onDeletedAtc(self,record,**kwargs):
        if not record['filepath']:
            return
        snode = self._atcStorageNode(record)
        try:
            if snode.exists:
                snode.delete()
        except Exception:
            return

class TotalizeTable(GnrDboTable):
    def totalize_exclude(self,record=None,old_record=None):
        return 
    
    def sysFields_extra_totalize(self,tbl,**kwargs):
        tbl.column('_refcount',dtype='L',name_long='!!Ref.Count',totalize_value=1,**kwargs)

    def tt_totalize_pars(self):
        tot_keys = {}
        tot_fields = {}
        for colname,colobj in self.columns.items():
            attr =  colobj.attributes
            for attr_key,dest in (('totalize_key',tot_keys),('totalize_value',tot_fields)):
                if not attr_key in attr:
                    continue
                attr_val = attr[attr_key]
                result = {}
                if attr_val == '*':
                    result['cb'] = getattr(self,'%s_%s' %(attr_key,colname))
                elif attr_val is True:
                    result['field'] = colname
                elif isinstance(attr_val,basestring):
                    result['field'] = attr_val
                else:
                    result['const'] = attr_val
                dest[colname] = result

        return tot_keys,tot_fields

    def tt_record(self,record,tot_keys):
        result = {}
        for k,pars in tot_keys.items():
            result[k] = self.tt_getvalue(record,pars)
        return result

    def tt_getvalue(self,record,pars):
        if 'cb' in pars:
            return pars['cb'](record)
        if 'field' in pars:
            return record[pars['field']]
        return pars['const']

    def _tt_has_changes(self,record=None,old_record=None,tot_fields=None):
        for totalizer_field,pars in tot_fields.items():
            if self.tt_getvalue(record,pars) != self.tt_getvalue(old_record,pars):
                return True
        return False
            

    def tt_totalize(self,record=None,old_record=None,local_records=None):
        tot_keys,tot_fields = self.tt_totalize_pars()
        tot_record_new = self.tt_record(record,tot_keys) if record else None
        tot_record_old = self.tt_record(old_record,tot_keys) if old_record else None
        handler = self.tt_totalize_memory if local_records is not None else self.tt_totalize_record
        if tot_record_new == tot_record_old:
            if self._tt_has_changes(record=record,old_record=old_record,tot_fields=tot_fields):
                handler(record=record,old_record=old_record,
                    tot_fields=tot_fields,
                    tot_record=tot_record_new,local_records=local_records)
            return
        if record is not None:
            handler(record=record,old_record=None,
                    tot_fields=tot_fields,
                    tot_record=tot_record_new,local_records=local_records)
        if old_record is not None:
            handler(record=None,old_record=old_record,
                    tot_fields=tot_fields,
                    tot_record=tot_record_old,local_records=local_records)

    def tt_totalize_record(self,record=None,old_record=None,
                                        tot_fields=None,
                                        tot_record=None,**kwargs):
        addFromCurrent = (record is not None) and (self.totalize_exclude(record) is not True)
        subtractFromOld = (old_record is not None) and (self.totalize_exclude(old_record) is not True)
        self.tt_totalize_allowed(record,old_record=old_record)
        with self.recordToUpdate(self.pkeyValue(tot_record),insertMissing=True,**tot_record) as tot:
            for totalizer_field,pars in tot_fields.items():
                if addFromCurrent:
                    value = self.tt_getvalue(record,pars) 
                    tot[totalizer_field] = (tot[totalizer_field] or value.__class__(0)) + value
                if subtractFromOld:
                    old_value = self.tt_getvalue(old_record,pars)
                    tot[totalizer_field] = (tot[totalizer_field] or old_value.__class__(0)) - old_value
            if tot['_refcount']<=0:
                tot[self.pkey] = False
    
    def tt_totalize_allowed(self,record=None,old_record=None):
        pass

    def tt_totalize_memory(self,record=None,old_record=None,
                                        tot_fields=None,
                                        tot_record=None,
                                        local_records=None):
        keyprim = ','.join(['%s_%s' %(k,tot_record[k]) for k in sorted(tot_record.keys())])
        tot = local_records[keyprim]
        if not tot:
            tot.update(tot_record)
            tot[self.pkey] = self.newPkeyValue(tot)
        for totalizer_field,pars in tot_fields.items():
            value = self.tt_getvalue(record,pars) 
            tot[totalizer_field] = (tot.get(totalizer_field) or value.__class__(0)) + value

    def tt_realign_block(self,records):
        local_records = defaultdict(dict)
        for r in records:
            self.tt_totalize(record=r,local_records=local_records)
        self.insertMany(local_records.values())


    def tt_realign(self,empty=False):
        if empty:
            self.empty()
            self.db.commit()
        maintable = self.db.table(self.attributes['totalize_maintable'])
        maincolumn = self.attributes['totalize_maincolumn']
        blocks = maintable.query(columns='$%s' %maincolumn,distinct=True).fetch()
        for b in blocks:
            f = maintable.query(columns='*',addPkeyColumn=False,where='$%s=:bval' %maincolumn,
                                bval=b[maincolumn]).fetch()
            self.tt_realign_block(f)
            self.db.commit()
                    

class Table_sync_event(TableBase):
    def config_db(self, pkg):
        tbl =  pkg.table('sync_event',pkey='id',name_long='!!Sync event',
                      name_plural='!!Sync event')
        self.sysFields(tbl)
        tbl.column('tablename',name_long='!!Table') #uke.help
        tbl.column('event_type',name_long='!!Event',values='I,U,D')
        tbl.column('event_pkey',name_long='!!Pkey')
        tbl.column('event_data','X',name_long='!!Data')
        tbl.column('event_check_ts','H',name_long='!!Event check ts')
        tbl.column('status','L',name_long='!!Status') #0 updated, 1 to send, -1 conflict
        tbl.column('topic',name_long='!!Topic')
        tbl.column('author',name_long='!!Author')
        tbl.column('server_user',name_long='User')
        tbl.column('server_ts','DH',name_long='!!Server timestamp')

    def onTableTrigger(self,tblobj,record,old_record=None,event=None):
        event_check_ts = None
        tsfield = tblobj.lastTs
        if tsfield and event != 'I':
            event_check_ts = old_record[tsfield] if event=='U' else record[tsfield]
        print 'TABLE TRIGGER SYNC'
        event_record = dict(tablename=tblobj.fullname,event_type=event,
                    event_pkey=record[tblobj.pkey],
                    event_data=Bag(record),
                    event_check_ts=event_check_ts,status='to_send',
                    topic=record.get(tblobj.attributes.get('sync_topic')))
        self.insert(event_record)

        
class Table_counter(TableBase):
    """This table is automatically created for every package that inherit from GnrDboPackage."""
        
    def config_db(self, pkg):
        """Configure the database, creating the database :ref:`table` and some :ref:`columns`
        
        :param pkg: the :ref:`package <packages>` object"""
        tbl = pkg.table('counter', pkey='codekey', name_long='!!Counter', transaction=False)
        self.sysFields(tbl, id=False, ins=True, upd=True)
        tbl.column('codekey', size=':32', readOnly='y', name_long='!!Codekey', indexed='y')
        tbl.column('code', size=':12', readOnly='y', name_long='!!Code')
        tbl.column('pkg', size=':12', readOnly='y', name_long='!!Package')
        tbl.column('name', name_long='!!Name')
        tbl.column('counter', 'L', name_long='!!Counter')
        tbl.column('last_used', 'D', name_long='!!Counter')
        tbl.column('holes', 'X', name_long='!!Holes')
        
    def setCounter(self, name, pkg, code,
                   codekey='$YYYY_$MM_$K', output='$K/$YY$MM.$NNNN',
                   date=None, phyear=False, value=0,**kwargs):
        """TODO
        
        :param name: the counter name
        :param pkg: the :ref:`package <packages>` object
        :param code: the counter code
        :param codekey: the codekey format (e.g. ``$YY`` for year)
        :param output: the output format (e.g. ``$YY.$NNNN`` for year)
        :param date: the current date
        :param phyear: the fiscal year
        :param value: TODO"""
        self.getCounter(name, pkg, code, codekey=codekey, output=output, date=date,
                        phyear=phyear, lastAssigned=value - 1,**kwargs)
                        
    def getCounter(self, name, pkg, code,
                   codekey='$YYYY_$MM_$K', output='$K/$YY$MM.$NNNN',
                   date=None, phyear=False, lastAssigned=0,**kwargs):
        """Generate a new number from the specified counter and return it as a string
        
        :param name: the counter name
        :param pkg: the :ref:`package <packages>` object
        :param code: the counter code
        :param codekey: the formatting string for the key
        :param output: the formatting output for the key
        :param date: the the date of counter attribution
        :param phyear: the fiscal year
        :param lastAssigned: TODO"""
        ymd = self.getYmd(date, phyear=phyear)
        codekey = '%s_%s' % (pkg, self.counterCode(code, codekey, ymd))
        
        record = self.record(codekey, mode='record', for_update=True, ignoreMissing=True)
        if not record:
            self.lock()
            record = self.record(codekey, mode='record', for_update=True, ignoreMissing=True)
            if not record:
                record = self.createCounter(codekey, code, pkg, name, lastAssigned)
                
        counter = record['counter'] + 1
        record['counter'] = counter
        record['last_used'] = date
        self.update(record)
        return self.formatCode(code, output, ymd, counter)
        
    def getLastCounterDate(self, name, pkg, code,
                           codekey='$YYYY_$MM_$K', output='$K/$YY$MM.$NNNN',
                           date=None, phyear=False, lastAssigned=0):
        """TODO
        
        :param name: the counter name
        :param pkg: the :ref:`package <packages>` object
        :param code: the counter code
        :param codekey: the formatting string for the key
        :param output: the formatting output for the key
        :param date: the the date of counter attribution
        :param phyear: the fiscal year
        :param lastAssigned: TODO"""
        ymd = self.getYmd(date, phyear=phyear)
        codekey = '%s_%s' % (pkg, self.counterCode(code, codekey, ymd))
        record = self.record(codekey, mode='record', for_update=True, ignoreMissing=True)
        if record:
            return record['last_used']
            
    def createCounter(self, codekey, code, pkg, name, lastAssigned):
        """Create a counter. The counter is built through a :ref:`bag`
        
        :param codekey: the formatting string for the key
        :param code: the counter code
        :param pkg: the :ref:`package <packages>` object
        :param name: the counter name
        :param lastAssigned: TODO"""
        record = Bag()
        record['name'] = '%s-%s' % (pkg, name)
        record['code'] = code
        record['pkg'] = pkg
        record['codekey'] = codekey
        record['counter'] = lastAssigned
        self.insert(record)
        return self.record(codekey, mode='record', for_update=True)
        
    def counterCode(self, code, codekey, ymd):
        """Compose a counter code key and return it
        
        :param code: the counter code
        :param codekey: the formatting string for the key
        :param ymd: a tuple including year, month and day as strings"""
        codekey = codekey.replace('$YYYY', ymd[0])
        codekey = codekey.replace('$YY', ymd[0][2:])
        codekey = codekey.replace('$MM', ymd[1])
        codekey = codekey.replace('$DD', ymd[2])
        codekey = codekey.replace('$K', code)
        return codekey
        
    def formatCode(self, code, output, ymd, counter):
        """Create the output for the code and return it
        
        :param code: the counter code
        :param output: the formatting output for the key
        :param ymd: a tuple including year, month and day as strings
        :param counter: the long integer counter"""
        x = '$N%s' % output.split('$N')[1]
        
        output = output.replace(x, str(counter).zfill(len(x) - 1))
        output = output.replace('$YYYY', ymd[0])
        output = output.replace('$YY', ymd[0][2:])
        output = output.replace('$MM', ymd[1])
        output = output.replace('$DD', ymd[2])
        output = output.replace('$K', code)
        return output
        
    def getYmd(self, date, phyear=False):
        """Return a tuple (year, month, date) of strings from a date.
        
        :param date: the datetime
        :param phyear: the fiscal year (not yet implemented)"""
        if not date:
            return ('0000', '00', '00')
        if phyear:
            #to be completed
            pass
        else:
            return (str(date.year), str(date.month).zfill(2), str(date.day).zfill(2))
            

