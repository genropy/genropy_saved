#!/usr/bin/env python
# encoding: utf-8
from gnr.core.gnrdecorator import public_method

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('tblinfo', pkey='tbl', pkey_columns_joiner='/',
                    name_long='!!Table Info', name_plural='!!Table info',caption_field='tbl')
        self.sysFields(tbl,id=False)
        tbl.column('pkg' ,size=':50',name_long='!!Package').relation('pkginfo.pkg',relation_name='tables')
        tbl.column('tbl' ,size=':50',name_long='!!Table')
        tbl.column('description' ,size=':30',name_long='!!Description')

    def createSysRecords(self):
        pkgtable = self.db.table('adm.pkginfo')
        currentPackages = pkgtable.query().fetchAsDict('pkg')
        current = self.query().fetchAsDict('tbl')
        docommit =False
        for pkgId,pkg in self.db.packages.items():
            if not pkgId in currentPackages:
                pkgtable.insert(dict(pkg=pkgId))
                docommit = True
            for tbl in pkg.tables.values():
                if not tbl.fullname in current:
                    self.insert(dict(pkg=pkgId,tbl=tbl.fullname))
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

    @public_method
    def getTblInfoCols(self,tbl=None,**kwargs):
        tblobj = self.db.table(tbl.split('/')[0])
        result = []
        for field,colobj in tblobj.model.columns.items():
            result.append('%s:%s' %(field,field))
        return ','.join(result)

