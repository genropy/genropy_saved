#!/usr/bin/env python
# encoding: utf-8

import datetime
import os
from gnr.core.gnrlang import boolean
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import splitAndStrip,encode36,templateReplace,fromJson,slugify
from gnr.core.gnrdecorator import public_method,extract_kwargs

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
        :param phyear: the fiscal year
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
        
    def getPreference(self, path, dflt=None):
        """Get a preference for the current package. Return the value of the specified
        preference, or *dflt* if it is missing
        
        :param path: a dotted name of the preference item
        :param dflt: the default value"""
        return self.db.table('adm.preference').getPreference(path, pkg=self.name, dflt=dflt)
        
    def setPreference(self, path, value):
        """Set a preference for the current package.
        
        :param path: a dotted name of the preference item
        :param value: the new value"""
        self.db.table('adm.preference').setPreference(path, value, pkg=self.name)
        
    def tableBroadcast(self,evt,autocommit=False,**kwargs):
        changed = False
        db = self.application.db
        for tname,tblobj in db.packages[self.id].tables.items():
            handler = getattr(tblobj.dbtable,evt,None)
            if handler:
                result = handler(**kwargs)
                changed = changed or result
        if changed and autocommit:
            db.commit()
        return changed

    def pickleAllData(self,basepath=None):
        pkgapp = self.db.application.packages[self.name]
        basepath = basepath or os.path.join(pkgapp.packageFolder,'data_pickled')
        if not os.path.isdir(basepath):
            os.mkdir(basepath)
        try:
            import cPickle as pickle
        except ImportError:
            import pickle
        file_list = []
        for tname,tblobj in self.tables.items():
            f = tblobj.dbtable.query(addPkeyColumn=False).fetch()
            z = os.path.join(basepath,'%s.pik' %tname)
            file_list.append(z)
            with open(z, 'w') as storagefile:
                pickle.dump(f, storagefile)

        import zipfile
        zipPath = '%s.zip' %basepath

        zipresult = open(zipPath, 'wb')
        zip_archive = zipfile.ZipFile(zipresult, mode='w', compression=zipfile.ZIP_DEFLATED,allowZip64=True)
        for fname in file_list:
            zip_archive.write(fname, os.path.basename(fname))
        zip_archive.close()
        zipresult.close()
        import shutil
        shutil.rmtree(basepath)

    def unpickleAllData(self,basepath=None,tables=None,btc=None):
        basepath = basepath or os.path.join(self.db.application.packages[self.name].packageFolder,'data_pickled')
        if not os.path.isdir(basepath):
            extractpath = '%s.zip' %basepath
            from zipfile import ZipFile
            myzip =  ZipFile(extractpath, 'r')
            myzip.extractall(basepath)
        db = self.db
        tables = tables or self.allTables()
        rev_tables =  list(tables)
        rev_tables.reverse()
        for t in rev_tables:
            db.table('%s.%s' %(self.name,t)).empty()
        db.commit()
        try:
            import cPickle as pickle
        except ImportError:
            import pickle
        tables = btc.thermo_wrapper(tables,'tables',message='Table') if btc else tables
        for tablename in tables:
            tblobj = db.table('%s.%s' %(self.name,tablename))
            with open(os.path.join(basepath,'%s.pik' %tablename), 'r') as storagefile:
                records = pickle.load(storagefile)
            records = records or []
            tblobj.insertMany(records)
            db.commit()

        import shutil
        shutil.rmtree(basepath)


    def allTables(self):
        return []

        
class TableBase(object):
    """TODO"""
    @extract_kwargs(counter=True)
    def sysFields(self, tbl, id=True, ins=True, upd=True, ldel=True, user_ins=False, user_upd=False, draftField=False, invalidFields=None,invalidRelations=None,md5=False,
                  counter=False,hierarchical=False,useProtectionTag=None,
                  group='zzz', group_name='!!System',
                  multidb=None,
                  df=None,counter_kwargs=None):
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
        if id:
            tbl.column('id', size='22', group=group, readOnly='y', name_long='!!Id',_sendback=True,_sysfield=True)
            pkey = tbl.attributes.get('pkey')
            if not pkey:
                tbl.attributes['pkey'] = 'id'
            if group and group_name:
                tbl.attributes['group_%s' % group] = group_name
            else:
                group = '_'
        if ins:
            tbl.column('__ins_ts', dtype='DH', name_long='!!Insert date', onInserting='setTSNow', group=group,_sysfield=True,indexed=True)
        if ldel:
            tbl.column('__del_ts', dtype='DH', name_long='!!Logical delete date', group=group,_sysfield=True,indexed=True)
            tbl.attributes['logicalDeletionField'] = '__del_ts'
        if upd:
            tbl.column('__mod_ts', dtype='DH', name_long='!!Update date', onUpdating='setTSNow', onInserting='setTSNow',
                       group=group,_sysfield=True,indexed=True)
            lastTS = tbl.attributes.get('lastTS')
            if not lastTS:
                tbl.attributes['lastTS'] = '__mod_ts'
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
                                             onInserting='hierarchical_before',_sysfield=True).relation('%s.id' %tblname,mode='foreignkey', 
                                                                                        onDelete='cascade',relation_name='_children',
                                                                                        one_name='!!Parent',many_name='!!Children',
                                                                                        deferred=True,
                                                                                        one_group=group,many_group=group)
            tbl.formulaColumn('child_count','(SELECT count(*) FROM %s.%s_%s AS children WHERE children.parent_id=#THIS.id)' %(pkg,pkg,tblname))
            tbl.formulaColumn('hlevel',"""length($hierarchical_pkey)-length(replace($hierarchical_pkey,'/',''))+1""")

            hfields = hierarchical.split(',')
            for fld in hfields:
                if fld=='pkey':
                    tbl.column('hierarchical_pkey',unique=True,group=group,_sysfield=True) 
                    tbl.column('_parent_h_pkey',group=group,_sysfield=True)
                else:
                    hcol = tbl.column(fld)
                    fld_caption=hcol.attributes.get('name_long',fld).replace('!!','')                   
                    tbl.column('hierarchical_%s'%fld,name_long='!!Hierarchical %s'%fld_caption,_sysfield=True)
                    tbl.column('_parent_h_%s'%fld,name_long='!!Parent Hierarchical %s'%fld_caption,group=group,_sysfield=True)
            tbl.attributes['hierarchical'] = hierarchical  
            if not counter:
                tbl.attributes.setdefault('order_by','$hierarchical_%s' %hfields[0] )
            broadcast = tbl.attributes.get('broadcast')
            broadcast = broadcast.split(',') if broadcast else []
            if not 'parent_id' in broadcast:
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
                tbl.formulaColumn('_h_sortcol',default_order_by,_sysfield=True)
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
                        onUpdating='setAuditVersionUpd', onInserting='setAuditVersionIns',_sysfield=True)
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
        if multidb:
            self.setMultidbSubscription(tbl,allRecords=(multidb=='*'),forcedStore=(multidb=='**'),group=group)
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
        sync = tbl.attributes.get('sync')
        if sync:
            tbl.column('__syncaux','B',group=group,
                        onUpdated='syncRecordUpdated',
                        onDeleting='syncRecordDeleting',
                        onInserted='syncRecordInserted',_sysfield=True)
        if df:
            self.sysFields_df(tbl)


    def sysFields_protectionTag(self,tbl,protectionTag=None,group=None):
        tbl.attributes['protectionTag'] = protectionTag
        tbl.attributes['protectionColumn'] = '__is_protected_row'
        tbl.column('__protection_tag', name_long='!!Protection tag', group=group,_sysfield=True,_sendback=True,onInserting='setProtectionTag')
        tbl.formulaColumn('__is_protected_row',""" $__protection_tag IS NOT NULL AND NOT (',' || :env_userTags || ',' LIKE '%%,'|| $__protection_tag || ',%%')""",dtype='B')
        
    def sysFields_df(self,tbl):
        tbl.column('df_fields',dtype='X',group='_')
        tbl.column('df_fbcolumns','L',group='_')
        tbl.column('df_custom_templates','X',group='_')
        tbl.column('df_colswith',group='_')

    def sysFields_counter(self,tbl,fldname,counter=None,group=None,name_long='!!Counter'):
        tbl.column(fldname, dtype='L', name_long=name_long, onInserting='setRowCounter',counter=True,
                            _counter_fkey=counter,group=group,_sysfield=True)

    def addPhonetic(self,tbl,column,mode=None,size=':5',group=None):
        mode = mode or 'dmetaphone'
        group = group or 'zzz'
        phonetic_column = '__phonetic_%s' %column
        tbl.column(column).attributes.update(phonetic=phonetic_column,_sendback=True,query_dtype='PHONETIC')
        tbl.column(phonetic_column,size=size,sql_value='%s(:%s)' %(mode,column),phonetic_mode=mode,group=group,_sendback=True)


    def invalidFieldsBag(self,record):
        if not record['__invalid_fields']:
            return
        result = Bag()
        invdict = fromJson(record['__invalid_fields'])
        for k,v in invdict.items():
            result.setItem(k,'%(fieldcaption)s:%(error)s' %v)
        return result

            
    def trigger_hierarchical_before(self,record,fldname,old_record=None,**kwargs):
        pkeyfield = self.pkey
        parent_id=record.get('parent_id')
        parent_record = None
        if parent_id:
            parent_record = self.query(where='$%s=:pid' %pkeyfield,pid=parent_id).fetch()
            parent_record = parent_record[0] if parent_record else None
        for fld in self.attributes.get('hierarchical').split(','):
            parent_h_fld='_parent_h_%s'%fld
            h_fld='hierarchical_%s'%fld
            v=record.get(pkeyfield if fld=='pkey' else fld) 
            record[parent_h_fld]= parent_record[h_fld] if parent_record else None
            record[h_fld]= '%s/%s'%( parent_record[h_fld], v) if parent_record else v
        if self.column('_row_count') is None:
            return 
        record['_parent_h_count'] = parent_record['_h_count'] if parent_record else None
        if old_record is None and record.get('_row_count') is None:
            #has counter and inserting a new record without '_row_count'
            where = '$parent_id IS NULL' if not record.get('parent_id') else '$parent_id =:p_id' 
            last_counter = self.readColumns(columns='$_row_count',where=where,
                                        order_by='$_row_count desc',limit=1,p_id=parent_id)
            record['_row_count'] = (last_counter or 0)+1
        if old_record is None or (record['_row_count'] != old_record['_row_count']) or (record['_parent_h_count'] != old_record['_parent_h_count']):
            record['_h_count'] = '%s%s' %(record.get('_parent_h_count') or '',encode36(record['_row_count'],2))

    def trigger_hierarchical_after(self,record,fldname,old_record=None,**kwargs):
        hfields=self.attributes.get('hierarchical').split(',')
        changed_hfields=[fld for fld in hfields if record.get('hierarchical_%s'%fld) != old_record.get('hierarchical_%s'%fld)]
        order_by = None
        changed_counter = False
        if '_row_count' in record:
            order_by = '$_row_count'
            changed_counter = (record['_row_count'] != old_record['_row_count']) or (record['_parent_h_count'] != old_record['_parent_h_count'])
        if changed_hfields or changed_counter:
            fetch = self.query(where='$parent_id=:curr_id',addPkeyColumn=False, for_update=True,curr_id=record[self.pkey],order_by=order_by).fetch()
            for k,row in enumerate(fetch):
                new_row = dict(row)
                for fld in changed_hfields:
                    new_row['_parent_h_%s'%fld]=record['hierarchical_%s'%fld]
                if changed_counter:
                    if new_row.get('_row_count') is None:
                        new_row['_row_count'] = k+1
                    new_row['_parent_h_count'] = record['_h_count']
                    new_row['_h_count'] = '%s%s' %(new_row['_parent_h_count'] or '',encode36(new_row['_row_count'],2))
                self.update(new_row, row)


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
        last_counter = self.readColumns(columns='$%s' %fldname,where=where,
                                    order_by='$%s desc' %fldname,limit=1,**wherekw)
        record[fldname] = (last_counter or 0)+1
        
    def trigger_setTSNow(self, record, fldname,**kwargs):
        """This method is triggered during the insertion (or a change) of a record. It returns
        the insertion date as a value of the dict with the key equal to ``record[fldname]``,
        where ``fldname`` is the name of the field inserted in the record.
        
        :param record: the record
        :param fldname: the field name"""
        if not getattr(record, '_notUserChange', None):
            record[fldname] = datetime.datetime.today()


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
        
    def hasRecordTags(self):
        """TODO"""
        return self.attributes.get('hasRecordTags', False)
    
    def isMultidbTable(self):
        return 'multidb_allRecords' in self.attributes

    def multidb_readOnly(self):
        return self.db.currentPage.dbstore and 'multidb_allRecords' in self.attributes

    
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
        if old_record and old_record.get(logicalDeletionField) and not record.get(logicalDeletionField) and record.get('__moved_related'):
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
                fullcaption = r['description']
                if df_field:
                    fieldpath='%s.%s' %(df_field,r['code'])
                    fullcaption='%s/%s' %(df_caption,r['description'])
                result.setItem(r['code'],None,caption=r['description'],dtype=r['data_type'],
                                fieldpath=fieldpath,fullcaption=fullcaption)
        return result
                     
    def multidbSubscribe(self,pkey,dbstore=None):
        self.db.table('multidb.subscription').addSubscription(table=self.fullname,pkey=pkey,dbstore=dbstore)
           
    def setMultidbSubscription(self,tbl,allRecords=False,forcedStore=False,group='zzz'):
        """TODO
        
        :param tblname: a string composed by the package name and the database :ref:`table` name
                        separated by a dot (``.``)"""
        pkg = tbl.attributes['pkg']
        tbl.attributes.update(multidb='*' if allRecords else True)

        tblname = tbl.parentNode.label
        tblfullname = '%s.%s' %(pkg,tblname)
        model = self.db.model
        subscriptiontbl =  model.src['packages.multidb.tables.subscription']
        pkey = tbl.parentNode.getAttr('pkey')
        pkeycolAttrs = tbl.column(pkey).getAttr()
        tblname = tbl.parentNode.label
        rel = '%s.%s.%s' % (pkg,tblname, pkey)
        fkey = rel.replace('.', '_')
        if subscriptiontbl:
            tbl.attributes.update(multidb_allRecords=allRecords,multidb_forcedStore=forcedStore)
            tbl.column('__multidb_flag',dtype='B',comment='!!Fake field always NULL',
                        onUpdated='multidbSyncUpdated',
                        onDeleting='multidbSyncDeleting',
                        onInserted='multidbSyncInserted',
                        group=group,_sysfield=True)
            if allRecords or forcedStore:
                return 
                
            tbl.column('__multidb_default_subscribed',dtype='B',_pluggedBy='multidb.subscription',
                    name_long='!!Subscribed by default',plugToForm=True,group=group,_sysfield=True)
            tbl.formulaColumn('__multidb_subscribed',"""EXISTS (SELECT * 
                                                        FROM multidb.multidb_subscription AS sub
                                                        WHERE sub.dbstore = :env_target_store 
                                                              AND sub.tablename = '%s'
                                                        AND sub.%s = #THIS.%s
                                                        )""" %(tblfullname,fkey,pkey),dtype='B',
                                                        name_long='!!Subscribed',_sysfield=True)
            subscriptiontbl.column(fkey, dtype=pkeycolAttrs.get('dtype'),_sysfield=True,
                              size=pkeycolAttrs.get('size'), group=group).relation(rel, relation_name='subscriptions',
                                                                                 many_group=group, one_group=group)
    def hasMultidbSubscription(self):
        return self.attributes.get('multidb')==True

    def _onUnifying(self,destRecord=None,sourceRecord=None,moved_relations=None,relations=None):
        if self.hasMultidbSubscription():
            relations.remove('@subscriptions')
            self.db.table('multidb.subscription').cloneSubscriptions(self.fullname,sourceRecord[self.pkey],destRecord[self.pkey])

    def trigger_multidbSyncUpdated(self, record,old_record=None,**kwargs):
        self.db.table('multidb.subscription').onSubscriberTrigger(self,record,old_record=old_record,event='U')
     
    def trigger_multidbSyncInserted(self, record,**kwargs):
        self.db.table('multidb.subscription').onSubscriberTrigger(self,record,event='I')
    
    def trigger_multidbSyncDeleting(self, record,**kwargs):        
        self.db.table('multidb.subscription').onSubscriberTrigger(self,record,event='D')
     
                                                               
    def setTagColumn(self, tbl, name_long=None, group=None):
        """TODO
        
        :param tbl: the :ref:`table` object
        :param name_long: the :ref:`name_long`
        :param group: a hierarchical path of logical categories and subacategories
                      the columns belongs to. For more information, check the :ref:`group` section"""
        name_long = name_long or '!!Tag'
        tagtbl = tbl.parentNode.parentbag.parentNode.parentbag.table('recordtag_link')
        tblname = tbl.parentNode.label
        tbl.parentNode.attr['hasRecordTags'] = True
        pkey = tbl.parentNode.getAttr('pkey')
        pkeycolAttrs = tbl.column(pkey).getAttr()
        rel = '%s.%s' % (tblname, pkey)
        fkey = rel.replace('.', '_')
        tagtbl.column(fkey, dtype=pkeycolAttrs.get('dtype'),
                      size=pkeycolAttrs.get('size'), group='_').relation(rel, mode='foreignkey',
                                                                         many_group='_', one_group='_')
        relation_path = '@%s_recordtag_link_%s.@tag_id' % (tbl.getAttr()['pkg'], fkey)
        tbl.aliasColumn('_recordtag_desc', relation_path='%s.description' % relation_path, group=group,
                        name_long=name_long, dtype='TAG')
        tbl.aliasColumn('_recordtag_tag', relation_path='%s.tag' % relation_path, name_long='!!Tagcode', group='_')


    def trigger_syncRecordUpdated(self,record,old_record=None,**kwargs):
        self.pkg.table('sync_event').onTableTrigger(self,record,old_record=old_record,event='U')

    def trigger_syncRecordInserted(self, record,**kwargs):
        self.pkg.table('sync_event').onTableTrigger(self,record,event='I')
    
    def trigger_syncRecordDeleting(self, record,**kwargs):        
        self.pkg.table('sync_event').onTableTrigger(self,record,event='D')

    #FUNCTIONS SQL
    def normalizeText(self,text):
        return """regexp_replace(translate(%s,'àèéìòù-','aeeiou '),'[.|,|;]', '', 'g')""" %text


    def templateColumn(self,record=None,field=None):
        template = self.column(field).attributes.get('template_name')
        tplpath = '%s:%s' %(self.fullname,template)
        tplkey = 'template_%s' %tplpath
        currEnv = self.db.currentEnv
        tpl = currEnv.get(tplkey)
        if not tpl:
            tpl = self.db.currentPage.loadTemplate(tplpath)
            currEnv[tplkey] = tpl
        r = Bag(dict(record))
        return templateReplace(tpl,r)


    def hosting_copyToInstance(self,source_instance=None,dest_instance=None,_commit=False,logger=None,onSelectedSourceRows=None,**kwargs):
        #attr = self.attributes
        #logger.append('** START COPY %(name_long)s **'%attr)
        source_db = self.db if not source_instance else self.db.application.getAuxInstance(source_instance).db 
        dest_db = self.db if not dest_instance else self.db.application.getAuxInstance(dest_instance).db 
        source_tbl = source_db.table(self.fullname)
        dest_tbl = dest_db.table(self.fullname)
        pkey = self.pkey
        source_rows = source_tbl.query(addPkeyColumn=False,**kwargs).fetch()
        if onSelectedSourceRows:
            onSelectedSourceRows(source_instance=source_instance,dest_instance=dest_instance,source_rows=source_rows)
        all_dest = dest_tbl.query(addPkeyColumn=False,for_update=True,**kwargs).fetchAsDict(pkey)
        existing_dest = dest_tbl.query(addPkeyColumn=False,for_update=True,where='$id IN :pk',pk=[r[pkey] for r in source_rows]).fetchAsDict(pkey)
        all_dest.update(existing_dest)
        if source_rows:
            fieldsToCheck = ','.join([c for c in source_rows[0].keys() if c not in ('__ins_ts','__mod_ts')])
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
        dest_db.table(self.fullname).deleteSelection(where='$%s IN :missing' %self.pkey,missing=missing)


    def getCustomFieldsMenu(self):
        data,metadata = self.db.table('adm.userobject').loadUserObject(code='%s_fieldstree' %self.fullname.replace('.','_'),objtype='fieldsmenu')
        return data,metadata

    ################## COUNTER SEQUENCE TRIGGER RELATED TO adm.counter ############################################

    def counterColumns(self):
        adm_counter = self.db.package('adm').attributes.get('counter')
        if adm_counter is not None and boolean(adm_counter) is False:
            return []
        return [k[8:] for k in dir(self) if k.startswith('counter_')]

    def trigger_releaseCounters(self,record=None):
        for field in self.counterColumns():
            self.db.table('adm.counter').releaseCounter(tblobj=self,field=field,record=record)

    def trigger_assignCounters(self,record=None,old_record=None):
        "Inside dbo"
        for field in self.counterColumns():
            self.db.table('adm.counter').assignCounter(tblobj=self,field=field,record=record)

    def _sequencesOnLoading(self,newrecord,recInfo=None):
        for field in self.counterColumns():
            pars = getattr(self,'counter_%s' %field)()
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
        mastertbl_multidb = mastertbl.attributes.get('multidb')
        
        tbl.attributes.setdefault('caption_field','description')
        tbl.attributes.setdefault('rowcaption','$description')
        tbl.attributes.setdefault('name_long','%s  Attachment' %mastertbl_name_long)
        tbl.attributes.setdefault('name_plural','%s Attachments' %mastertbl_name_long)

        self.sysFields(tbl,id=True, ins=False, upd=False,counter='maintable_id',multidb=mastertbl_multidb)
        tbl.column('id',size='22',group='_',name_long='Id')
        tbl.column('filepath' ,name_long='!!Filepath',onDeleted='onDeletedAtc',onInserted='convertDocFile')
        tbl.column('description' ,name_long='!!Description')
        tbl.column('mimetype' ,name_long='!!Mimetype')
        tbl.column('text_content',name_long='!!Content')
        tbl.column('info' ,'X',name_long='!!Additional info')
        tbl.column('maintable_id',size='22',group='_',name_long=mastertblname).relation('%s.%s.%s' %(pkgname,mastertblname,mastertbl.attributes.get('pkey')), 
                    mode='foreignkey', onDelete_sql='cascade', relation_name='atc_attachments',
                    one_group='_',many_group='_',deferred=True)
        tbl.formulaColumn('fileurl',"'/_vol/' || $filepath",name_long='Fileurl')

    @public_method
    def atc_importAttachment(self,pkey=None):
        site = self.db.application.site
        record = self.record(pkey=pkey,for_update=True).output('dict')
        old_record = dict(record)
        filepath = record['filepath']
        text_content = site.extractTextContent(site.getStaticPath('vol:%s' %filepath))
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
        if docConverter and os.path.splitext(attachment['filepath'])[1] in ('.doc','.docx'):
            pdf_staticpath = docConverter.convert(attachment['filepath'])
            if pdf_staticpath:
                pdf_record = dict(filepath=pdf_staticpath,
                        mimetype=attachment['mimetype'],
                        description=os.path.basename(pdf_staticpath),
                        maintable_id=attachment['maintable_id'])
                self.insert(pdf_record)
                return pdf_record

    def trigger_convertDocFile(self,record,**kwargs):
        p,ext = os.path.splitext(record['filepath'])
        if ext.lower() in ('.doc','.docx'):
            self.insertPdfFromDocAtc(record)

    def trigger_onDeletedAtc(self,record,**kwargs):
        site = self.db.application.site
        fpath = site.getStaticPath('vol:%s' %record['filepath'])
        try:
            if os.path.exists(fpath):
                os.remove(fpath)
        except Exception:
            return


class DynamicFieldsTable(GnrDboTable):
    """CustomFieldsTable"""
    def config_db(self,pkg):
        tblname = self._tblname
        tbl = pkg.table(tblname,pkey='id')
        mastertbl = '%s.%s' %(pkg.parentNode.label,tblname.replace('_df',''))
        self.df_dynamicFormFields(tbl,mastertbl)

    def df_dynamicFormFields(self,tbl,mastertbl):
        pkgname,mastertblname = mastertbl.split('.')
        tblname = '%s_df' %mastertblname
        assert tbl.parentNode.label == tblname,'table name must be %s' %tblname
        model = self.db.model
        mastertbl =  model.src['packages.%s.tables.%s' %(pkgname,mastertblname)]
        mastertbl.attributes['df_fieldstable'] = '%s.%s' %(pkgname,tblname)
        mastertbl_name_long = mastertbl.attributes.get('name_long')
        mastertbl_multidb = mastertbl.attributes.get('multidb')
        mastertbl.column('df_fbcolumns','L',group='_')
        mastertbl.column('df_custom_templates','X',group='_')
        tbl.attributes.setdefault('caption_field','description')
        tbl.attributes.setdefault('rowcaption','$description')
        tbl.attributes.setdefault('name_long','%s dyn field' %mastertbl_name_long)
        tbl.attributes.setdefault('name_plural','%s dyn fields' %mastertbl_name_long)

        self.sysFields(tbl,id=True, ins=False, upd=False,counter='maintable_id',multidb=mastertbl_multidb)
        tbl.column('id',size='22',group='_',name_long='Id')
        tbl.column('code',name_long='!!Code')
        tbl.column('default_value',name_long='!!Default value')
        
        tbl.column('description',name_long='!!Description')
        tbl.column('data_type',name_long='!!Data Type')
        tbl.column('calculated','B',name_long='!!Enterable')

        tbl.column('wdg_tag',name_long='!!Wdg type')
        tbl.column('wdg_colspan','L',name_long='!!Colspan')
        tbl.column('wdg_kwargs','X',name_long='!!Wdg kwargs')

        tbl.column('source_combobox',name_long='!!Suggested Values')
        tbl.column('source_dbselect',name_long='!!Db Table')
        tbl.column('source_filteringselect',name_long='!!Allowed Values')
        tbl.column('source_checkboxtext',name_long='!!Checkbox Values')
        tbl.column('checkboxtext_cols','L',name_long='!!Checkbox cols')

        #tbl.column('source_multivalues',name_long='!!Multiple Values')
        
        tbl.column('field_style',name_long='!!Style')
        tbl.column('field_visible',name_long='!!Visible if')
        tbl.column('field_format',name_long='!!Format')
        tbl.column('field_placeholder',name_long='!!Placeholder')

        tbl.column('field_mask',name_long='!!Mask')
        tbl.column('field_tip',name_long='!!Tip')
    
        tbl.column('validate_case',size='1',values='!!u:Uppercase,l:Lowercase,c:Capitalize',name_long='!!Case')
        tbl.column('validate_range',name_long='!!Range')
        
        tbl.column('standard_range','N',name_long='!!Std range')
        tbl.column('formula',name_long='!!Formula')
        #tbl.column('do_summary','B',name_long='!!Do summary')
        tbl.column('mandatory','B',name_long='!!Mandatory')

        tbl.column('maintable_id',size='22',group='_',name_long=mastertblname).relation('%s.%s.%s' %(pkgname,mastertblname,mastertbl.attributes.get('pkey')), 
                    mode='foreignkey', onDelete_sql='cascade', relation_name='dynamicfields',
                    one_group='_',many_group='_')
        if mastertbl.attributes.get('hierarchical'):
            tbl.formulaColumn('hlevel',"""array_length(string_to_array(@maintable_id.hierarchical_pkey,'/'),1)""")

    def onSiteInited(self):
        if self.pkg.attributes.get('df_ok'):
            return
        mastertbl = self.fullname.replace('_df','')
        tblobj = self.db.table(mastertbl)
        if tblobj.column('df_fields') is not None:
            print 'IMPORTING DynamicFields FROM LEGACY',mastertbl
            tblobj.df_importLegacyScript()
            return True

        
              
class GnrHTable(GnrDboTable):
    """A hierarchical table. More information on the :ref:`classes_htable` section"""
    def htableFields(self, tbl):
        """:param tbl: the :ref:`table` object
        
        Create the necessary :ref:`columns` in order to use the :ref:`h_th` component.
        
        In particular it adds:
        
        * the "code" column: TODO
        * the "description" column: TODO
        * the "child_code" column: TODO
        * the "parent_code" column: TODO
        * the "level" column: TODO
        
        You can redefine the first three columns in your table; if you don't redefine them, they
        are created with the following features::
        
            tbl.column('code', name_long='!!Code', base_view=True)
            tbl.column('description', name_long='!!Description', base_view=True)
            tbl.column('child_code', name_long='!!Child code', validate_notnull=True,
                        validate_notnull_error='!!Required', base_view=True,
                        validate_regex='!\.', validate_regex_error='!!Invalid code: "." char is not allowed')"""
                        
        columns = tbl['columns'] or []
        broadcast = [] if 'broadcast' not in tbl.attributes else tbl.attributes['broadcast'].split(',')
        broadcast.extend(['code','parent_code','child_code'])
        tbl.attributes['broadcast'] = ','.join(list(set(broadcast)))
        if not 'code' in columns:
            tbl.column('code', name_long='!!Code', base_view=True,unique=True)
        if not 'description' in columns:
            tbl.column('description', name_long='!!Description', base_view=True)
        if not 'child_code' in columns:
            tbl.column('child_code', name_long='!!Child code', validate_notnull=True,
                        validate_notnull_error='!!Required', base_view=True,
                        validate_regex='!\.', validate_regex_error='!!Invalid code: "." char is not allowed'
                        #,unmodifiable=True
                        )
        tbl.column('parent_code', name_long='!!Parent code').relation('%s.code' % tbl.parentNode.label,onDelete='cascade')
        tbl.column('level', name_long='!!Level')
        pkgname = tbl.getAttr()['pkg']
        tblname = '%s.%s_%s' % (pkgname, pkgname, tbl.parentNode.label)
        tbl.formulaColumn('child_count',
                          '(SELECT count(*) FROM %s AS children WHERE children.parent_code=#THIS.code)' % tblname,
                           dtype='L', always=True)
        tbl.formulaColumn('hdescription',
                           """
                           CASE WHEN #THIS.parent_code IS NULL THEN #THIS.description
                           ELSE ((SELECT description FROM %s AS ptable WHERE ptable.code = #THIS.parent_code) || '-' || #THIS.description)
                           END
                           """ % tblname)
        
        tbl.formulaColumn('base_caption',"""CASE WHEN $description IS NULL OR $description='' THEN $child_code 
                                             ELSE $child_code ||'-'||$description END""")
        tbl.attributes.setdefault('caption_field','base_caption')
        if not 'rec_type'  in columns:
            tbl.column('rec_type', name_long='!!Type')
            
    
    def htableAutoCode(self,record=None,old_record=None,evt='I'):
        autocode = self.attributes.get('autocode')
        if not autocode:
            return
        
    def trigger_onInserting(self, record_data):
        """TODO
        
        :param record_data: TODO"""
        parent_code = record_data.get('parent_code')
        self.htableAutoCode(record=record_data,evt='I')
        self.assignCode(record_data)
        if not parent_code:
            return
        parent_children = self.readColumns(columns='$child_count',where='$code=:code',code=parent_code)
        if parent_children==0:
            self.touchRecords(where='$code=:code',code=parent_code)
        
    def trigger_onDeleted(self,record,**kwargs):
        parent_code = record.get('parent_code')
        self.htableAutoCode(record=record,evt='I')
        if not parent_code:
            return
        
       # children = self.query(where='$parent_code=:p',p=record['code'],for_update=True).fetch()
       # if children:
       #     for c in children:
       #         self.delete(c)
        
    def assignCode(self, record_data):
        """TODO
        
        :param record_data: TODO"""
        code_list = [k for k in (record_data.get('parent_code') or '').split('.') + [record_data['child_code']] if k]
        record_data['level'] = len(code_list) - 1
        record_data['code'] = '.'.join(code_list)
    
    @public_method
    def reorderCodes(self,pkey=None,into_pkey=None):
        record = self.record(pkey=pkey,for_update=True).output('record')
        oldrecord = dict(record)
        parent_code = self.record(pkey=into_pkey).output('record')['code'] if into_pkey else None
        code_to_test = '%s.%s' %(parent_code,record['child_code']) if parent_code else record['child_code']
        if not self.checkDuplicate(code=code_to_test):
            record['parent_code'] = parent_code
            self.update(record,oldrecord)
            self.db.commit()
            return True
        return False

    def trigger_onUpdating(self, record_data, old_record=None):
        """TODO
        :param record_data: TODO
        :param old_record: TODO"""
        if old_record and ((record_data['child_code'] != old_record['child_code']) or (record_data['parent_code'] != old_record['parent_code'])):
            old_code = old_record['code']
            self.assignCode(record_data)
            parent_code = record_data['code']
            self.batchUpdate(dict(parent_code=parent_code), where='$parent_code=:old_code', old_code=old_code)
            #if parent_code:
            #    parent_children = self.readColumns(columns='$child_count',where='$code=:code',code=parent_code)
            #    if parent_children==0:
            #        self.touchRecords(where='$code=:code',code=parent_code)

            
    def df_getFieldsRows(self,pkey=None,code=None):
        fieldstable = self.db.table(self.attributes.get('df_fieldstable'))
        code = self.readColumns(pkey=pkey,columns='code')
        return fieldstable.query(where="(:code=@maintable_id.code) OR (:code ILIKE @maintable_id.code || '.%%')",
                                    code=code,order_by='@maintable_id.code,$_row_count',columns='*,$wdg_kwargs').fetch()


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
            
class Table_userobject(TableBase):
    """TODO"""
    def use_dbstores(self,**kwargs):
        """TODO"""
        return False
        
    def config_db(self, pkg):
        """Configure the database, creating the database :ref:`table` and some :ref:`columns`
        
        :param pkg: the :ref:`package <packages>` object"""
        tbl = pkg.table('userobject', pkey='id', name_long='!!User Object', transaction=False)
        self.sysFields(tbl, id=True, ins=True, upd=True)
        tbl.column('code', name_long='!!Code', indexed='y') # a code unique for the same type / pkg / tbl
        tbl.column('objtype', name_long='!!Object Type', indexed='y')
        tbl.column('pkg', name_long='!!Package') # package code
        tbl.column('tbl', name_long='!!Table') # full table name: package.table
        tbl.column('userid', name_long='!!User ID', indexed='y')
        tbl.column('description', 'T', name_long='!!Description', indexed='y')
        tbl.column('notes', 'T', name_long='!!Notes')
        tbl.column('data', 'X', name_long='!!Data')
        tbl.column('authtags', 'T', name_long='!!Auth tags')
        tbl.column('private', 'B', name_long='!!Private')
        tbl.column('quicklist', 'B', name_long='!!Quicklist')
        tbl.column('flags', 'T', name_long='!!Flags')

        
    def saveUserObject(self, data, id=None, code=None, objtype=None, pkg=None, tbl=None, userid=None,
                       description=None, authtags=None, private=None, inside_shortlist=None, **kwargs):
        """TODO
        
        :param data: TODO
        :param id: TODO
        :param code: TODO
        :param objtype: TODO
        :param pkg: the :ref:`package <packages>` object
        :param tbl: the :ref:`table` object
        :param userid: TODO
        :param description: TODO
        :param authtags: TODO
        :param private: TODO
        :param inside_shortlist: TODO"""
        if id:
            record = self.record(id, mode='record', for_update=True, ignoreMissing=True)
        else:
            record_pars = dict(code=code, objtype=objtype)
            if tbl:
                record_pars['tbl'] = tbl
            if pkg:
                record_pars['pkg'] = pkg
            record = self.record(mode='record', for_update=True, ignoreMissing=True, **record_pars)
        isNew = False
        if not record:
            record = Bag()
            isNew = True
            
        loc = locals()
        for k in ['code', 'objtype', 'pkg', 'tbl', 'userid', 'description', 'data', 'authtags', 'private']:
            record[k] = loc[k]
            
        if isNew:
            self.insert(record)
        else:
            self.update(record)
        return record
        
    def loadUserObject(self, id=None, objtype=None, **kwargs):
        """TODO
        
        :param id: TODO
        :param objtype: TODO"""
        if id:
            record = self.record(id, mode='record', ignoreMissing=True)
        else:
            record = self.record(objtype=objtype, mode='record', ignoreMissing=True, **kwargs)
        data = record.pop('data')
        metadata = record.asDict(ascii=True)
        return data, metadata
        
    def deleteUserObject(self, id, pkg=None):
        """TODO
        
        :param id: TODO
        :param pkg: the :ref:`package <packages>` object"""
        self.delete({'id': id})
        
    def listUserObject(self, objtype=None,pkg=None, tbl=None, userid=None, authtags=None, onlyQuicklist=None, flags=None):
        """TODO
        
        :param objtype: TODO
        :param pkg: the :ref:`package <packages>` object
        :param tbl: the :ref:`table` object
        :param userid: TODO
        :param authtags: TODO
        :param onlyQuicklist: TODO
        :param flags: TODO"""
        onlyQuicklist = onlyQuicklist or False
        
        def checkUserObj(r):
            condition = (not r['private']) or (r['userid'] == userid)
            if onlyQuicklist:
                condition = condition and r['quicklist']
            if self.db.application.checkResourcePermission(r['authtags'], authtags):
                if condition:
                    return True
        where = []
        if objtype:
            where.append('$objtype = :val_objtype')
        if tbl:
            where.append('$tbl = :val_tbl')
        if flags:
            where.append(' position(:_flags IN $flags)>0 ')
        where = ' AND '.join(where)
        sel = self.query(columns='$id, $code, $objtype, $pkg, $tbl, $userid, $description, $authtags, $private, $quicklist, $flags',
                         where=where, order_by='$code',
                         val_objtype=objtype, val_tbl=tbl,_flags=flags).selection()
                         
        sel.filter(checkUserObj)
        return sel
        
class Table_recordtag(TableBase):
    def config_db(self, pkg):
        """Configure the database, creating the database :ref:`table` and some :ref:`columns`
        
        :param pkg: the :ref:`package <packages>` object"""
        tbl = pkg.table('recordtag', pkey='id', name_long='!!Record tags', transaction=False)
        self.sysFields(tbl, id=True, ins=False, upd=False)
        tbl.column('tablename', name_long='!!Table name')
        tbl.column('tag', name_long='!!Tag', validate_notnull=True, validate_notnull_error='!!Required')
        tbl.column('description', name_long='!!Description', validate_notnull=True, validate_notnull_error='!!Required')
        tbl.column('values', name_long='!!Values')
        tbl.column('maintag', name_long='!!Main tag')
        tbl.column('subtag', name_long='!!Sub tag')
        
    def trigger_onInserting(self, record_data):
        """TODO
        
        :param record_data: TODO"""
        if record_data['values']:
            self.setTagChildren(record_data)
            
    def setTagChildren(self, record_data, old_record_data=None):
        """TODO
        
        :param record_data: TODO
        :param old_record_data: TODO"""
        tablename = record_data['tablename']
        parentTag = record_data['tag']
        parentDescription = record_data['description']
        
        oldChildren = {}
        if old_record_data:
            #updating
            parentTag_old = old_record_data['tag']
            parentDescription_old = old_record_data['description']
            if parentTag_old != parentTag:
                #updating if change parentTag
                def cb_tag(row):
                    row['tag'] = row['tag'].replace('%s_' % parentTag_old, '%s_' % parentTag)
                    row['maintag'] = parentTag
                    
                self.batchUpdate(cb_tag, where='$maintag =:p_tag AND tablename=:t_name',
                                 p_tag=parentTag_old, t_name=tablename)
        if old_record_data and old_record_data['values']:
            #updating if change change values
            for item in splitAndStrip(old_record_data['values'], ','):
                tag, description = splitAndStrip('%s:%s' % (item, item), ':', n=2, fixed=2)
                oldChildren['%s_%s' % (parentTag, tag)] = description
            
        for item in splitAndStrip(record_data['values'], ','):
            tag, description = splitAndStrip('%s:%s' % (item, item), ':', n=2, fixed=2)
            fulltag = '%s_%s' % (parentTag, tag)
            if fulltag in oldChildren:
                if description != oldChildren[fulltag]:
                    def cb_desc(row):
                        row['description'] = description

                    self.batchUpdate(cb_desc, where='$tag=:c_tag', c_tag=fulltag)
                oldChildren.pop(fulltag)
            else:
                self.insert(Bag(
                        dict(tablename=tablename, tag=fulltag, description=description, maintag=parentTag, subtag=tag)))
        tagsToDelete = oldChildren.keys()
        if tagsToDelete:
            self.deleteSelection('tag', tagsToDelete, condition_op='IN')
            
    def trigger_onDeleting(self, record):
        """TODO
        
        :param record: TODO"""
        if record['values']:
            self.deleteSelection('tag', '%s_%%' % record['tag'], condition_op='LIKE')
            
    def trigger_onUpdating(self, record_data, old_record):
        """TODO
        
        :param record_data: TODO
        :param old_record: TODO"""
        if not record_data['maintag']:
            self.setTagChildren(record_data, old_record)

            
class Table_recordtag_link(TableBase): 
    def config_db(self, pkg):
        """Configure the database, creating the database :ref:`table` and some :ref:`columns`
        
        :param pkg: the :ref:`package <packages>` object"""
        tbl = pkg.table('recordtag_link', pkey='id', name_long='!!Record tag link', transaction=False)
        self.sysFields(tbl, id=True, ins=False, upd=False)
        tbl.column('tag_id', name_long='!!Tag id', size='22').relation('recordtag.id', onDelete='cascade',
                                                                       mode='foreignkey')
        tbl.aliasColumn('tag', relation_path='@tag_id.tag')
        tbl.aliasColumn('description', relation_path='@tag_id.description')
        
    def getTagLinks(self, table, record_id):
        """TODO
        
        :param table: the :ref:`database table <table>` name, in the form ``packageName.tableName``
                      (packageName is the name of the :ref:`package <packages>` to which the table
                      belongs to)
        :param record_id: the record id"""
        where = '$%s=:record_id' % self.tagForeignKey(table)
        return self.query(columns='@tag_id.tag,@tag_id.description',
                          where=where, record_id=record_id).fetchAsDict(key='@tag_id.tag')
                            
    def getTagTable(self):
        """TODO"""
        return self.db.table('%s.recordtag' % self.pkg.name)
        
    def getTagDict(self, table):
        """TODO
        
        :param table: the :ref:`database table <table>` name, in the form ``packageName.tableName``
                      (packageName is the name of the :ref:`package <packages>` to which the table
                      belongs to)"""
        currentEnv = self.db.currentEnv
        cachename = '_tagDict_%s' % table.replace('.', '_')
        tagDict = currentEnv.get(cachename)
        if not tagDict:
            tagDict = self.getTagTable().query(where='$tablename =:tbl', tbl=table).fetchAsDict(key='tag')
            currentEnv[cachename] = tagDict
        return tagDict
        
    def assignTagLink(self, table, record_id, tag, value):
        """TODO
        
        :param table: the :ref:`database table <table>` name, in the form ``packageName.tableName``
                      (packageName is the name of the :ref:`package <packages>` to which the table
                      belongs to)
        :param record_id: the record id
        :param tag: TODO
        :param value: TODO"""
        fkey = self.tagForeignKey(table)
        tagDict = self.getTagDict(table)
        tagRecord = tagDict[tag]
        if tagRecord.get('values', None):
            if value == 'false':
                self.sql_deleteSelection(where='@tag_id.maintag=:mt AND $%s=:record_id' % fkey,
                                         mt=tagRecord['tag'], record_id=record_id)
                return
            tagRecord = tagDict['%s_%s' % (tag, value)]
        existing = self.query(where='$%s=:record_id AND $tag_id=:tag_id' % fkey, record_id=record_id,
                              tag_id=tagRecord['id'], for_update=True, addPkeyColumn=False).fetch()
        if existing:
            if value == 'false':
                self.delete(existing[0])
            return
        if value != 'false':
            if tagRecord['maintag']:
                self.sql_deleteSelection(where='@tag_id.maintag=:mt AND $%s=:record_id' % fkey,
                                         mt=tagRecord['maintag'], record_id=record_id)
            record = dict()
            record[fkey] = record_id
            record['tag_id'] = tagRecord['id']
            self.insert(record)
        return
        
    def getTagLinksBag(self, table, record_id):
        """TODO
        
        :param table: the :ref:`database table <table>` name, in the form ``packageName.tableName``
                      (packageName is the name of the :ref:`package <packages>` to which the table
                      belongs to)
        :param record_id: the record id"""
        result = Bag()
        taglinks = self.query(columns='@tag_id.maintag AS maintag, @tag_id.subtag AS subtag, @tag_id.tag AS tag',
                              where='$%s=:record_id' % self.tagForeignKey(table), record_id=record_id).fetch()
        for link in taglinks:
            if link['maintag']:
                tagLabel = '%s.%s' % (link['maintag'], link['subtag'])
            else:
                tagLabel = '%s.true' % link['tag']
            result[tagLabel] = True
        return result
        
    def getCountLinkDict(self, table, pkeys):
        """TODO
        
        :param table: the :ref:`database table <table>` name, in the form ``packageName.tableName``
                      (packageName is the name of the :ref:`package <packages>` to which the table
                      belongs to)
        :param pkeys: TODO"""
        return self.query(columns='@tag_id.tag as tag,count(*) as howmany', group_by='@tag_id.tag',
                          where='$%s IN :pkeys' % self.tagForeignKey(table), pkeys=pkeys).fetchAsDict(key='tag')
                          
    def tagForeignKey(self, table):
        """TODO
        
        :param table: the :ref:`database table <table>` name"""
        tblobj = self.db.table(table)
        return '%s_%s' % (tblobj.name, tblobj.pkey)
