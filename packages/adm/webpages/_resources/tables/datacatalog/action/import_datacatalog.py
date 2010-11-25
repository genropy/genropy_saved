# -*- coding: UTF-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.batch.btcaction import BaseResourceAction

caption = 'Import datacatalog'
tags = 'admin'
description='Import datacatalog element'

class Main(BaseResourceAction):
    batch_prefix = 'DC'
    batch_title = 'Datacatalog importer'
    batch_cancellable = False
    batch_delay = 0.5
    dialog_height = '300px'
    dialog_width = '200px'

    def do(self):
        pkgidx = 0
        for pkg,pkgobj in self.btc.thermo_wrapper(self.db.packages.items(),'pkg'):
            pkgcode = 'P%i' %(pkgidx)
            self.tblobj.insert(self.tblobj.package_record(pkgcode,name=pkg,attr=pkgobj.attributes))
            pkgidx+=1
            tblidx = 0
            for tbl,tblobj in self.btc.thermo_wrapper(pkgobj.tables.items(),'tbl'):
                tblcode = 'T%i' %(tblidx)
                self.tblobj.insert(self.tblobj.table_record(tblcode,parent_code=pkgcode,name=tbl,attr=tblobj.attributes))
                tblidx+=1
                colidx = 0
                for col,colobj in self.btc.thermo_wrapper(tblobj.columns.items(),'field'):
                    colcode = 'C%i' %(colidx)
                    self.tblobj.insert(self.tblobj.col_record(colcode,parent_code=tblcode,name=col,attr=colobj.attributes,obj=colobj))
                    colidx+=1
        self.db.commit()
                    
        
    def result_handler(self):
        return 'Execution completed'
            
    def table_script_parameters_pane(self,pane,**kwargs):
        pane.div('Import all model')