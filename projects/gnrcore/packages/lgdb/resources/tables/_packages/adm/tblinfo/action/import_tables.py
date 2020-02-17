# -*- coding: utf-8 -*-
import os
from shutil import copyfile

from gnr.web.batch.btcaction import BaseResourceAction
from gnr.lib.services.storage import StorageNode

caption = 'Import legacy tables'
description = 'Import legacy tables'

class Main(BaseResourceAction):
    batch_prefix = 'mb'
    batch_title = 'Import Legacy tables'
    batch_cancellable = True
    batch_immediate = True
    batch_delay = 0.5

    def do(self):
        pkg_code = None
        pkg_table = self.db.table('lgdb.lg_pkg')
        tbl_table = self.db.table('lgdb.lg_table')
        import_mode = self.batch_parameters.get('import_mode')
        
        
        for t in self.btc.thermo_wrapper(self.get_selection(), 'TABLES'):
            pkg = t['pkgid']
            if pkg != pkg_code:
                if not pkg_table.query(where='$code=:pkg', pkg=pkg).fetch():
                    pkg_table.insert(dict(code=pkg))
                pkg_code=pkg
            pkgobj = self.db.package(pkg_code)
            tbl_name = t['tblid'].split('.')[-1]
            if tbl_name in pkgobj.tables.keys():
                tblobj = pkgobj.table(tbl_name)
                tbl_table.importTable(pkg_code = pkg_code, 
                                  tblobj=tblobj, 
                                  import_mode = import_mode)
        self.db.commit()


    def table_script_parameters_pane(self, pane, **kwargs):
        fb = pane.formbuilder(cols=1)
        fb.filteringSelect('.import_mode', lbl='Mode', values='restart,update,add_only')

        
            

