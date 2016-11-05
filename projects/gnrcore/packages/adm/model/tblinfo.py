#!/usr/bin/env python
# encoding: utf-8
from gnr.core.gnrdecorator import public_method

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('tblinfo', pkey='tblid', pkey_columns_joiner='/',
                    name_long='!!Table Info', name_plural='!!Table info',caption_field='tbl')
        self.sysFields(tbl,id=False)
        tbl.column('pkgid' ,size=':50',name_long='!!Package').relation('pkginfo.pkgid',relation_name='tables')
        tbl.column('tblid' ,size=':50',name_long='!!Table')
        tbl.column('description' ,size=':30',name_long='!!Description')

    def createSysRecords(self):
        pkgtable = self.db.table('adm.pkginfo')
        currentPackages = pkgtable.query().fetchAsDict('pkgid')
        current = self.query().fetchAsDict('tblid')
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

    @public_method
    def getTblInfoCols(self,tbl=None,**kwargs):
        tblobj = self.db.table(tbl.split('/')[0])
        result = []
        for field,colobj in tblobj.model.columns.items():
            result.append('%s:%s' %(field,field))
        return ','.join(result)

