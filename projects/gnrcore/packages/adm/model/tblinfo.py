#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('tblinfo', pkey='tbl_key', pkey_columns_joiner='/',
                    pkey_columns='tbl,branch',
                    name_long='!!Table Info', name_plural='!!Table info',caption_field='tbl')
        self.sysFields(tbl,id=False)
        tbl.column('tbl_key', size=':50', readOnly='y', name_long='!!Tbl key', indexed='y')
        tbl.column('pkg' ,size=':50',name_long='!!Package').relation('pkginfo.pkg',relation_name='tables')
        tbl.column('tbl' ,size=':50',name_long='!!Table')
        tbl.column('branch',size=':40',name_long='!!Branch')
        tbl.column('description' ,size=':30',name_long='!!Description')

    def createSysRecords(self):
        pkgtable = self.db.table('adm.pkginfo')
        currentPackages = pkgtable.query().fetchAsDict('pkg')
        current = self.query().fetchAsDict('tbl_key')
        docommit =False
        for pkgId,pkg in self.db.packages.items():
            if not pkgId in currentPackages:
                pkgtable.insert(dict(pkg=pkgId))
                docommit = True
            for tbl in pkg.tables.values():
                if not tbl.fullname in current:
                    self.insert(dict(pkg=pkgId,tbl=tbl.fullname)) 
                branches = tbl.dbtable.tableBranches
                for b in branches: 
                    if not '%s/%s' %(tbl.fullname,b) in current:
                        self.insert(dict(pkg=pkgId,tbl=tbl.fullname,branch=b))
                docommit = True
        if docommit:
            self.db.commit()


    def loadItem(self,table=None,item_type=None,name=None,branch=None,group_code=None):
        where = ['$tbl=:t','$item_type=:it']
        wherekw = dict(tbl=table,item_type=item_type)
        if name:
            where.append('$name=:n')
            wherekw['n'] = name
        if branch:
            where.append('$branch=:b')
            wherekw['b'] = branch



       #group_code = 
       #if self.avatar.group_code:
       #    where

       #item_type = 'QTREE' if item_type=='quick' else 'FTREE'
       #qtree_records = self.db.table('adm.tblinfo_item').query(where=where,bagFields=True,
       #                                                        t=table,it=item_type,branch=branch).fetch()

       #getTableResourceContent