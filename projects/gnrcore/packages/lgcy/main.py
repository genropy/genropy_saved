#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage
from gnr.core.gnrdecorator import metadata
from gnr.core.gnrbag import Bag
from gnr.core.gnrlang import instanceMixin
#from gnrpkg.multidb.multidbtable import MultidbTable
from gnr.sql.gnrsql import GnrSqlException
import os
import datetime


class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='lgcy package',sqlschema='lgcy',
                name_short='Legacy', name_long='Legacy manager')

    def config_db(self, pkg):
        pass
    
   #def onApplicationInited(self):
   #    self.mixinLgcyManager()

   #def mixinLgcyManager(self):
   #    db = self.application.db
   #    tblconverter = db.table('lgcy.converter')
   #    for pkg,pkgobj in db.packages.items():
   #        for tbl,tblobj in pkgobj.tables.items():
   #            if tblobj.dbtable.attributes.get('legacy_code'):
   #                tblconverter.instanceMixin(tblobj.dbtable, MultidbTable)

    def onBuildingDbobj(self):
        for pkgNode in self.db.model.src['packages']:
            for tblNode in pkgNode.value['tables']:
                legacy_code = tblNode.attr.get('legacy_code')
                tbl = tblNode.value
                if legacy_code:
                    self._lgcy_configure(tbl,legacy_code)
       
    def _lgcy_configure(self,tbl,legacy_code):
        pkg = tbl.attributes['pkg']
        model = self.db.model
        convertertbl =  model.src['packages.lgcy.tables.converter']
        pkey = tbl.parentNode.getAttr('pkey')
        pkeycolAttrs = tbl.column(pkey).getAttr()
        tblname = tbl.parentNode.label
        rel = '%s.%s.%s' % (pkg,tblname, pkey)
        fkey = rel.replace('.', '_')
        convertertbl.column(fkey, dtype=pkeycolAttrs.get('dtype'),_sysfield=True,
                              size=pkeycolAttrs.get('size'), group='zz').relation(rel, relation_name='legacy',
                                                                                 many_group='zz', one_group='zz')
        tbl.aliasColumn('legacy_code' if legacy_code is True else legacy_code,'@legacy.code')


class Table(GnrDboTable):
    pass