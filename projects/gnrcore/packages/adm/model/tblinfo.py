#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('tblinfo', pkey='tbl', name_long='!!Table Info', name_plural='!!Table info',caption_field='tbl')
        self.sysFields(tbl)
        tbl.column('tbl' ,size=':50',name_long='!!Table')
        tbl.column('pkg' ,size=':50',name_long='!!Package').relation('pkginfo.pkg',relation_name='tables')
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
