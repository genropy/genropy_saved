#!/usr/bin/env python
# encoding: utf-8

import datetime
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import splitAndStrip
from gnr.core.gnrdecorator import public_method

class GnrDboPackage(object):
    """Base class for packages"""
    def updateFromExternalDb(self,externaldb,empty_before=None):
        """TODO
        
        :param externaldb: TODO
        :param empty_before: TODO"""
        tables = self.attributes.get('export_order') or ''
        self.db.setConstraintsDeferred()
        for tbl in splitAndStrip(tables):
            self.db.table(tbl).copyToDb(externaldb,self.db,empty_before=empty_before)
            
    def getCounter(self, name, code, codekey, output, date=None, phyear=False, lastAssigned=0):
        """Generate a new number from the specified counter and return it.
        
        :param name: the counter name
        :param code: the counter code
        :param codekey: the codekey format (e.g. ``$YY`` for year)
        :param output: the output format (e.g. ``$YY.$NNNN`` for year)
        :param date: the current date
        :param phyear: the fiscal year
        :param lastAssigned: TODO"""
        return self.dbtable('counter').getCounter(name=name, pkg=self.name, code=code, codekey=codekey, output=output,
                                                  date=date, phyear=phyear, lastAssigned=lastAssigned)
                                                  
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
        
class TableBase(object):
    """TODO"""
    def sysFields(self, tbl, id=True, ins=True, upd=True, ldel=True, draftField=False, md5=False,
                  group='zzz', group_name='!!System'):
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
            tbl.column('id', size='22', group='_', readOnly='y', name_long='!!Id',_sendback=True)
            pkey = tbl.attributes.get('pkey')
            if not pkey:
                tbl.attributes['pkey'] = 'id'
            if group and group_name:
                tbl.attributes['group_%s' % group] = group_name
            else:
                group = '_'
        if ins:
            tbl.column('__ins_ts', dtype='DH', name_long='!!Insert date', onInserting='setTSNow', group=group)
        if ldel:
            tbl.column('__del_ts', dtype='DH', name_long='!!Logical delete date', group=group)
            tbl.attributes['logicalDeletionField'] = '__del_ts'
        if upd:
            tbl.column('__mod_ts', dtype='DH', name_long='!!Update date', onUpdating='setTSNow', onInserting='setTSNow',
                       group=group)
            lastTS = tbl.attributes.get('lastTS')
            if not lastTS:
                tbl.attributes['lastTS'] = '__mod_ts'
        if md5:
            tbl.column('__rec_md5', name_long='!!Update date', onUpdating='setRecordMd5', onInserting='setRecordMd5',
                       group='_')
        audit = tbl.attributes.get('audit')
        if audit:
            tbl.column('__version','L',name_long='Audit version',
                        onUpdating='setAuditVersionUpd', onInserting='setAuditVersionIns')
        diagnostic = tbl.attributes.get('diagnostic')
        if diagnostic:
            tbl.column('__warnings',name_long='!!Warnings',group=group)
            tbl.column('__errors',name_long='!!Errors',group=group)
        if draftField:
            draftField = '__is_draft' if draftField is True else draftField
            tbl.attributes['draftField'] =draftField
            tbl.column(draftField, dtype='B', name_long='!!Is Draft',group=group)
            
    def trigger_setTSNow(self, record, fldname):
        """This method is triggered during the insertion (or a change) of a record. It returns
        the insertion date as a value of the dict with the key equal to ``record[fldname]``,
        where ``fldname`` is the name of the field inserted in the record.
        
        :param record: the record
        :param fldname: the field name"""
        if not getattr(record, '_notUserChange', None):
            record[fldname] = datetime.datetime.today()
            
    def trigger_setAuditVersionIns(self, record, fldname):
        """TODO
        
        :param record: the record
        :param fldname: the field name"""
        record[fldname] = 0
        
    def trigger_setAuditVersionUpd(self, record, fldname):
        """TODO
        
        :param record: the record
        :param fldname: the field name"""
        record[fldname] = (record.get(fldname) or 0)+ 1
        
    def trigger_setRecordMd5(self, record, fldname):
        """TODO
        
        :param record: the record
        :param fldname: the field name"""
        pass
        
    def hasRecordTags(self):
        """TODO"""
        return self.attributes.get('hasRecordTags', False)

    def setMultidbSubscription(self,tblname):
        """TODO
        
        :param tblname: a string composed by the package name and the database :ref:`table` name
                        separated by a dot (``.``)"""
        pkg,tblname = tblname.split('.')
        model = self.db.model
        tbl = model.src['packages.%s.tables.%s' %(pkg,tblname)]
        subscriptiontbl =  model.src['packages.multidb.tables.subscription']
        pkey = tbl.parentNode.getAttr('pkey')
        pkeycolAttrs = tbl.column(pkey).getAttr()
        tblname = tbl.parentNode.label
        pkgName = tbl.parent.parentNode.label
        rel = '%s.%s.%s' % (pkg,tblname, pkey)
        fkey = rel.replace('.', '_')
        if subscriptiontbl:
            subscriptiontbl.column(fkey, dtype=pkeycolAttrs.get('dtype'),
                              size=pkeycolAttrs.get('size'), group='_').relation(rel, relation_name='subscriptions',
                                                                                 many_group='_', one_group='_')
                                                                                 
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
        
class GnrHTable(TableBase):
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
            tbl.column('code', name_long='!!Code', base_view=True)
        if not 'description' in columns:
            tbl.column('description', name_long='!!Description', base_view=True)
        if not 'child_code' in columns:
            tbl.column('child_code', name_long='!!Child code', validate_notnull=True,
                        validate_notnull_error='!!Required', base_view=True,
                        validate_regex='!\.', validate_regex_error='!!Invalid code: "." char is not allowed'
                        #,unmodifiable=True
                        )
        tbl.column('parent_code', name_long='!!Parent code').relation('%s.code' % tbl.parentNode.label)
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
        if not 'rec_type'  in columns:
            tbl.column('rec_type', name_long='!!Type')
            
    def trigger_onInserting(self, record_data):
        """TODO
        
        :param record_data: TODO"""
        parent_code = record_data['parent_code']
        parent_children = self.readColumns(columns='$child_count',where='$code=:code',code=parent_code)
        self.assignCode(record_data)
        if parent_children==0:
            self.touchRecords(where='$code=:code',code=parent_code)
        
    def trigger_onDeleted(self,record,**kwargs):
        parent_code = record['parent_code']
        parent_children = self.readColumns(columns='$child_count',where='$code=:code',code=parent_code)
        if parent_children==0:
            self.touchRecords(where='$code=:code',code=parent_code)
        
        
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
        parent_record = self.record(pkey=into_pkey).output('record')
        parent_code = parent_record['code']
        code_to_test = '%s.%s' %(parent_code,record['child_code'])
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
            self.batchUpdate(dict(parent_code=record_data['code']), where='$parent_code=:old_code', old_code=old_code)
            
class GnrDboTable(TableBase):
    """TODO"""
    def use_dbstores(self):
        """TODO"""
        return True
        
class Table_counter(TableBase):
    """This table is automatically created for every package that inherit from GnrDboPackage."""
    def use_dbstores(self):
        """TODO"""
        return True
        
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
                   date=None, phyear=False, value=0):
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
                        phyear=phyear, lastAssigned=value - 1)
                        
    def getCounter(self, name, pkg, code,
                   codekey='$YYYY_$MM_$K', output='$K/$YY$MM.$NNNN',
                   date=None, phyear=False, lastAssigned=0):
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
    def use_dbstores(self):
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
    """TODO"""
    def use_dbstores(self):
        """TODO"""
        return True
        
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
    """TODO"""
    def use_dbstores(self):
        """TODO"""
        return True
        
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
