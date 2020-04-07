#!/usr/bin/env python
# encoding: utf-8
from builtins import object
from gnr.core.gnrdecorator import public_method

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('tblinfo', pkey='tblid',
                    name_long='!!Table Info', name_plural='!!Table info',caption_field='tblid')
        self.sysFields(tbl,id=False)
        tbl.column('tblid' ,size=':50',name_long='!!Table')
        tbl.column('pkgid' ,size=':50',name_long='!!Package').relation('pkginfo.pkgid',relation_name='tables')
        tbl.column('description' ,size=':50',name_long='!!Description')

    def onDbSetup_populate(self):
        pkgtable = self.db.table('adm.pkginfo')
        currentPackages = pkgtable.query().fetchAsDict('pkgid')
        current = self.query().fetchAsDict('tblid')
        docommit =False
        for pkgId,pkg in list(self.db.packages.items()):
            if not pkgId in currentPackages:
                pkgtable.insert(dict(pkgid=pkgId))
                docommit = True
            for tbl in list(pkg.tables.values()):
                if not tbl.fullname in current:
                    self.insert(dict(pkgid=pkgId,tblid=tbl.fullname))
                docommit = True
        if docommit:
            self.db.commit()

    @public_method
    def getTblInfoCols(self,tbl=None,**kwargs):
        tblobj = self.db.table(tbl.split('/')[0])
        result = []
        for field,colobj in list(tblobj.model.columns.items()):
            result.append('%s:%s' %(field,field))
        return ','.join(result)

