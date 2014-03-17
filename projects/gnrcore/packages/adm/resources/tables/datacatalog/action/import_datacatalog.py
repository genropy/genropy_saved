# -*- coding: UTF-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.batch.btcaction import BaseResourceAction

caption = 'Import datacatalog'
tags = 'admin'
description = 'Import datacatalog element'

class Main(BaseResourceAction):
    batch_prefix = 'DC'
    batch_title = 'Datacatalog importer'
    batch_cancellable = False
    batch_delay = 0.5
    dialog_height = '200px'
    dialog_width = '300px'

    def do(self):
        pkgidx = 0
        rootname = self.batch_parameters.get('root_code') or 'db_0'
        root_rec = dict(parent_code=None, child_code=rootname,
                        description=self.batch_parameters.get('root_description') or 'Imported Db',
                        rec_type='db_root')
        self.tblobj.insert(root_rec)

        for pkg, pkgobj in self.btc.thermo_wrapper(self.db.packages.items(), 'pkg'):
            pkgrec = self.tblobj.make_record_db_pkg(idx=pkgidx, parent_id=root_rec['id'], name=pkg,
                                                    attr=pkgobj.attributes)
            self.tblobj.insert(pkgrec)
            pkgidx += 1
            tblidx = 0
            for tbl, tblobj in self.btc.thermo_wrapper(pkgobj.tables.items(), 'tbl'):
                tblrec = self.tblobj.make_record_db_tbl(idx=tblidx, parent_id=pkgrec['id'], name=tbl,
                                                        attr=tblobj.attributes)
                self.tblobj.insert(tblrec)
                tblidx += 1
                colidx = 0
                for col, colobj in self.btc.thermo_wrapper(tblobj.columns.items(), 'field'):
                    colrec = self.tblobj.make_record_db_col(idx=colidx, parent_id=tblrec['id'],
                                                            name=col, attr=colobj.attributes, obj=colobj)
                    self.tblobj.insert(colrec)
                    colidx += 1
        self.db.commit()


    def result_handler(self):
        return 'Execution completed', dict()

    def table_script_parameters_pane(self, pane, **kwargs):
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.textbox(value='^.root_code', lbl='Root Code')
        fb.textbox(value='^.root_desc', lbl='Root Description')
