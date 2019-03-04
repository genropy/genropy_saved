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


class LegacyTableMixins(object):
    def lgcy_addLegacyCode(self,pkey,legacy_code):
        self.db.table('lgcy.converter').insertConversionRow(self,pkey,legacy_code)
    

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='lgcy package',sqlschema='lgcy',
                name_short='Legacy', name_long='Legacy manager')

    def config_db(self, pkg):
        pass
    
    def onApplicationInited(self):
        self.mixinLgcyManager()

    def mixinLgcyManager(self):
        db = self.application.db
        for pkg,pkgobj in db.packages.items():
            for tbl,tblobj in pkgobj.tables.items():
                if tblobj.dbtable.attributes.get('legacy_code'):
                    instanceMixin(tblobj.dbtable, LegacyTableMixins)

    def onBuildingDbobj(self):
        for pkgNode in self.db.model.src['packages']:
            if not pkgNode.value:
                continue
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
        convertertbl.column(fkey, dtype=pkeycolAttrs.get('dtype'),_sysfield=True,name_long=tbl.parentNode.attr.get('name_long'),
                              size=pkeycolAttrs.get('size'), group='zz').relation(rel, relation_name='legacy',
                                                                                 many_group='zz', one_group='zz',deferred=True)
        tbl.aliasColumn('legacy_code' if legacy_code is True else legacy_code,'@legacy.code',name_long='Lgcy Legacy codes')



class Table(GnrDboTable):
    pass