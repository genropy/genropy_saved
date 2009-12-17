#!/usr/bin/env python
# encoding: utf-8

import datetime
from gnr.core.gnrbag import Bag

class GnrDboPackage(object):
    def getCounter(self, name, code, codekey, output, 
                   date=None, phyear=False,lastAssigned=0):
        return self.dbtable('counter').getCounter(name=name, pkg=self.name, code=code, codekey=codekey, output=output, 
                                                date=date, phyear=phyear,lastAssigned=lastAssigned)
    def setCounter(self, name, code, codekey, output, 
                   date=None, phyear=False,value=0):
        return self.dbtable('counter').setCounter(name=name, pkg=self.name, code=code, codekey=codekey, output=output, 
                                                date=date, phyear=phyear,value=value)
                                                
    def loadUserObject(self, pkg=None, **kwargs):
        return self.dbtable('userobject').loadUserObject(pkg=pkg or self.name, **kwargs)
    
    def saveUserObject(self, data, pkg=None, **kwargs):
        return self.dbtable('userobject').saveUserObject(data, pkg=pkg or self.name, **kwargs)

    def deleteUserObject(self, id, pkg=None):
        return self.dbtable('userobject').deleteUserObject(pkg=pkg or self.name, id=id)

    def listUserObject(self, pkg=None, **kwargs):
        return self.dbtable('userobject').listUserObject(pkg=pkg or self.name, **kwargs)

class TableBase(object):
    def sysFields(self, tbl, id=True, ins=True, upd=True, ldel=True, md5=False, group='_'):
        if id:
            tbl.column('id',size='22',group='_',readOnly='y',name_long='!!Id')
            pkey = tbl.attributes.get('pkey')
            if not pkey:
                tbl.attributes['pkey'] = 'id'
        if ins:
            tbl.column('__ins_ts', dtype='DH', name_long='!!Insert date', onInserting='setTSNow', group=group)
        if ldel:
            tbl.column('__del_ts', dtype='DH', name_long='!!Logical delete date', group=group)
            tbl.attributes['logicalDeletionField'] = '__del_ts'
        if upd:
            tbl.column('__mod_ts', dtype='DH', name_long='!!Update date', onUpdating='setTSNow', onInserting='setTSNow', group=group)
            lastTS = tbl.attributes.get('lastTS')
            if not lastTS:
                tbl.attributes['lastTS'] = '__mod_ts'
        if md5:
            tbl.column('__rec_md5', name_long='!!Update date', onUpdating='setRecordMd5', onInserting='setRecordMd5', group='_')
             
    def trigger_setTSNow(self, record, fldname):
        if not getattr(record,'_notUserChange',None):
            record[fldname]=datetime.datetime.today()
            
    def trigger_setRecordMd5(self,record,fldname):
        pass
    
class GnrDboTable(TableBase):
       
    def dboLoad(self, pkey=None, **kwargs):
        """method to implement via mixin"""
        return self.dboDoLoad(dbo, pkey=pkey, **kwargs)
        
    def dboDoLoad(self, pkey=None, record=None, **kwargs):
        dbo = Bag()
        if pkey:
            record=self.record(pkey,mode='record',ignoreMissing=True)
        dbo.setItem('mainrecord', record, _pkey=record[self.pkey], _table=self.fullname, _opcode='U')
        return dbo
    
    def dboCreate(self, **kwargs):
        """method to implement via mixin"""
        return self.dboDoCreate()
        
    def dboDoCreate(self, **kwargs):
        dbo = Bag()
        rec = self.newrecord(True, **kwargs)
        dbo.setItem('mainrecord', rec, _pkey=rec[self.pkey], _table=self.fullname, _opcode='I')
        return dbo
    
    def dboProcess(self, dbo, **kwargs):
        pass
    
    def dboExecute(self, dbo, **kwargs):
        """method to implement via mixin
           @param mode: I (insert) U (update) IU (insert or update)"""
        self.dboDoExecute(dbo, **kwargs)
        
    def dboDoExecute(self, dbo, **kwargs):
        _opcode = dbo['mainrecord?_opcode']
        mainrecord = dbo['mainrecord']
        if _opcode=='D':
            self.delete(mainrecord)
            return
        if _opcode=='I':
            self.insert(mainrecord)
        elif _opcode=='U':
            self.update(mainrecord)
        elif _opcode=='IU':
            self.insertOrUpdate(mainrecord)
            
        children = dbo['children']
        for childrows, childtable, childcb in children.digest('#v,#a._table,#a._cb'):
            child_tblobj = self.db.table(childtable)
            if childrows:
                for row, rowop in childrows.digest('#v,#a._opcode'):
                    if childcb:
                        child_tblobj.getattr(childcb)(row, rowop)
                    else:
                        if rowop=='D':
                            child_tblobj.delete(row)
                        elif rowop=='I':
                            child_tblobj.insert(row)
                        elif rowop=='U':
                            child_tblobj.update(row)
                        elif rowop=='IU':
                            child_tblobj.insertOrUpdate(row)   
             

class Table_counter(TableBase):
    """This table is automatically created for every package that inherit from
       GnrDboPackage."""
   
    def config_db(self, pkg):
        tbl =  pkg.table('counter',  pkey='codekey', name_long='!!Counter', transaction=False)
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
                   
        self.getCounter(name,pkg,code,codekey=codekey,output=output,date=date,
                        phyear=phyear,lastAssigned=value-1)
                        
    def getCounter(self, name, pkg, code, 
                   codekey='$YYYY_$MM_$K', output='$K/$YY$MM.$NNNN', 
                   date=None, phyear=False, lastAssigned=0):
        """
        @param name: counter name
        @param pkg: package: the package involved.
        @param code: counter code.
        @param codekey: formatting string for the key.
        @param output: formatting output for the key.
        @param date: the date of counter attribution.
        @param phyear: phiscal year.
        """
        print lastAssigned
        ymd = self.getYmd(date, phyear=phyear)
        codekey = '%s_%s' % (pkg, self.counterCode(code, codekey, ymd))
        
        record = self.record(codekey, mode='record', for_update=True, ignoreMissing=True)
        if not record:
            print 'not existing %s try lock' % codekey
            self.lock()
            print 'locked %s' % codekey
            record = self.record(codekey, mode='record', for_update=True, ignoreMissing=True)
            if not record:
                record = self.createCounter(codekey,code, pkg,name,lastAssigned)
            
        counter = record['counter'] + 1
        record['counter'] = counter
        record['last_used'] = date
        self.update(record)
        return self.formatCode(code, output, ymd, counter)
    
    def createCounter(self,codekey,code,pkg,name,lastAssigned):
        record = Bag()
        record['name'] = '%s-%s' % (pkg, name)
        record['code'] = code
        record['pkg'] = pkg
        record['codekey'] = codekey
        record['counter'] = lastAssigned
        #print '---------------INSERTING COUNTER-----%s' % str(codekey) # commented out by Jeff 9/12/2009
        self.insert(record)
        return self.record(codekey, mode='record', for_update=True)
            
    def counterCode(self, code, codekey, ymd):
        """compose a counter code key"""
        codekey = codekey.replace('$YYYY', ymd[0])
        codekey = codekey.replace('$YY', ymd[0][2:])
        codekey = codekey.replace('$MM', ymd[1])
        codekey = codekey.replace('$DD', ymd[2])
        codekey = codekey.replace('$K', code)
        return codekey
        
    def formatCode(self, code, output, ymd, counter):
        x = '$N%s' % output.split('$N')[1]
        
        output = output.replace(x, str(counter).zfill(len(x)-1))

        output = output.replace('$YYYY', ymd[0])
        output = output.replace('$YY', ymd[0][2:])
        output = output.replace('$MM', ymd[1])
        output = output.replace('$DD', ymd[2])
        output = output.replace('$K', code)
        return output
    
    def getYmd(self, date, phyear=False):
        """
        it returns a tuple (y,m,d) of strings from a date. It should take in
        account the phiscal year flag.
        """
        if not date:
            return ('0000','00','00')
        if phyear:
            #to be completed
            pass
        else:
            return (str(date.year), str(date.month).zfill(2), str(date.day).zfill(2))

class Table_userobject(TableBase):

    def config_db(self, pkg):
        tbl =  pkg.table('userobject',  pkey='id', name_long='!!User Object', transaction=False)
        self.sysFields(tbl, id=True, ins=True, upd=True)
        tbl.column('code', size=':200', name_long='!!Code', indexed='y') # a code unique for the same type / pkg / tbl
        tbl.column('objtype', size=':24', name_long='!!Object Type', indexed='y')
        tbl.column('pkg', size=':24', name_long='!!Package') # package code
        tbl.column('tbl', size=':64', name_long='!!Package') # full table name: package.table
        tbl.column('userid', size=':32', name_long='!!User ID', indexed='y')
        tbl.column('description', 'T', name_long='!!Description', indexed='y')
        tbl.column('data', 'X', name_long='!!Data')
        tbl.column('authtags', 'T', name_long='!!Auth tags')
        tbl.column('private', 'B', name_long='!!Private')
        tbl.column('inside_shortlist', 'B', name_long='!!Shortlist')

    def saveUserObject(self, data, id=None, code=None, objtype=None, pkg=None, tbl=None, userid=None, 
                             description=None, authtags=None, private=None,inside_shortlist=None, **kwargs):
        if id:
            record = self.record(id, mode='record', for_update=True, ignoreMissing=True)
        else:
            record = self.record(code=code, objtype=objtype, pkg=pkg, tbl=tbl, mode='record', for_update=True, ignoreMissing=True)
        isNew = False
        if not record:
            record = Bag()
            isNew = True
            
        loc = locals()
        for k in ['code','objtype','pkg','tbl','userid','description','data','authtags','private','inside_shortlist']:
            record[k] = loc[k]
            
        if isNew:
            self.insert(record)
        else:
            self.update(record)
            
    def loadUserObject(self, id=None, code=None, objtype=None, pkg=None, tbl=None, userid=None):
        if id:
            record = self.record(id, mode='record', ignoreMissing=True)
        elif userid:
            record = self.record(code=code, objtype=objtype, pkg=pkg, tbl=tbl, userid=userid, mode='record', ignoreMissing=True)
        else:
            record = self.record(code=code, objtype=objtype, pkg=pkg, tbl=tbl, mode='record', ignoreMissing=True)
        data = record.pop('data')
        metadata = record.asDict(ascii=True)
        return data, metadata
        
    def deleteUserObject(self, id, pkg=None):
        self.delete({'id':id})
        
    def listUserObject(self, objtype=None, pkg=None, tbl=None, userid=None, authtags=None):
        def checkUserObj(r):
            if self.db.application.checkResourcePermission(r['authtags'], authtags):
                if (not r['private']) or (r['userid']==userid):
                    return True
        where = []
        
        if objtype:
            where.append('$objtype = :val_objtype')
        if tbl:
            where.append('$tbl = :val_tbl')
        where = ' AND '.join(where)
        sel = self.query(columns='$code, $objtype, $pkg, $tbl, $userid, $description, $authtags, $private', 
                    where=where, order_by='$code',
                    val_objtype=objtype, val_tbl=tbl).selection()
                    
        sel.filter(checkUserObj)
        return sel
    

