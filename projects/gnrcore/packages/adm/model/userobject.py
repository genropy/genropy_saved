# encoding: utf-8
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method
class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('userobject', pkey='id', name_long='!!User Object',name_plural='!!User Objects',rowcaption='$code,$objtype')
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
                
    def listUserObject(self, objtype=None,pkg=None, tbl=None, userid=None, authtags=None, onlyQuicklist=None, flags=None):
        onlyQuicklist = onlyQuicklist or False
        def checkUserObj(r):
            condition = (not r['private']) or (r['userid'] == userid)
            if onlyQuicklist:
                condition = condition and r['quicklist']
            if self.db.application.checkResourcePermission(r['authtags'], authtags):
                if condition:
                    return True
        where = []
        _flags = None
        if objtype:
            where.append('$objtype = :val_objtype')
        if tbl:
            where.append('$tbl = :val_tbl')
        if flags:
            where.append(' ($flags LIKE :_flags)  ')
            _flags = '%%'+flags+'%%'
        where = ' AND '.join(where)
        sel = self.query(columns='$id, $code, $objtype, $pkg, $tbl, $userid, $description, $authtags, $private, $quicklist, $flags',
                         where=where, order_by='$code',
                         val_objtype=objtype, val_tbl=tbl,_flags=_flags).selection()
        sel.filter(checkUserObj)
        return sel.output('records')

    #PUBLIC METHODS 
    
    @public_method
    def loadUserObject(self, id=None, objtype=None, **kwargs):
        if id:
            record = self.record(id, mode='record', ignoreMissing=True)
        else:
            record = self.record(objtype=objtype, mode='record', ignoreMissing=True, **kwargs)
        if not record:
            return None,None
        data = record.pop('data')
        metadata = record.asDict(ascii=True)
        metadata['pkey'] = metadata['id']
        return data, metadata
    
    
    @public_method
    def deleteUserObject(self, pkey):
        self.delete({'id': pkey})
        self.db.commit()

    @public_method
    def userObjectMenu(self,table=None, objtype=None,**kwargs): #th_listUserObject
        result = Bag()
        userobjects = self.listUserObject(objtype=objtype,userid=self.db.currentPage.user, tbl=table,
                                                authtags=self.db.currentPage.userTags,**kwargs)
        i = 0
        if len(userobjects)>0:
            for r in userobjects:
                r.pop('data')
                r['pkey'] = r.pop('id')
                r['caption'] = r['description'] or r['code']
                r['draggable'] = True
                r['onDrag'] = """dragValues['dbrecords'] = {table:'adm.userobject',pkeys:['%(pkey)s'],objtype:'%(objtype)s',reftable:"%(tbl)s"}""" %r
                result.setItem(r['code'] or 'r_%i' % i, None, **dict(r))
                i+=1
        return result
            
    @public_method
    def saveUserObject(self, table=None,objtype=None,data=None,metadata=None,**kwargs):
        pkg,tbl = table.split('.')
        pkey = metadata['pkey'] or metadata['id']
        if not metadata or not (metadata['code'] or pkey):
            return
        record = dict(data=data,objtype=objtype,
                    pkg=pkg,tbl=table,userid=self.db.currentPage.user,id=pkey,
                    code= metadata['code'],description=metadata['description'],private=metadata['private'] or False,
                    notes=metadata['notes'],flags=metadata['flags'])
        self.insertOrUpdate(record)
        self.db.commit()
        return record['id'],record    

    def importOld(self):
        currpkeys = self.query().selection().output('pkeylist')
        where = ' $id NOT IN :currpkeys '  if currpkeys else None
        for pkg in self.db.packages.values():
            if pkg.name=='adm':
                continue
            pkguserobject = pkg.tables.get('userobject')
            if pkguserobject:
                pkguserobject = pkguserobject.dbtable
                f = pkguserobject.query(where=where,currpkeys=currpkeys,addPkeyColumn=False).fetch()
                for r in f:
                    self.insert(r)
        self.db.commit()
                
        
