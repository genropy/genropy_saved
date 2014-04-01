# -*- coding: UTF-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag


from gnr.web.batch.btcaction import BaseResourceAction
caption = '!!Initialize counter'
tags = 'superadmin,_DEV_'
description = '!!Initialize counter'

class Main(BaseResourceAction):
    batch_prefix = 'icnt'
    batch_title = 'Initialize counter'
    batch_cancellable = False
    batch_delay = 0.5
    batch_immediate = True
    
    def do(self):
        package = self.batch_parameters['package']
        table = self.batch_parameters['table']
        thermo_wrapper=self.btc.thermo_wrapper
        if not package:
            self.tblobj.initializeApplicationSequences(thermo_wrapper=thermo_wrapper)
        elif not table:
            self.tblobj.initializePackageSequences(self.db.package(package),thermo_wrapper=thermo_wrapper)
        else:
            self.tblobj.initializeTableSequences(self.db.table(table),thermo_wrapper=thermo_wrapper)
        self.db.commit()

    def table_script_parameters_pane(self, pane, table=None,**kwargs):
        fb = pane.formbuilder(cols=1,border_spacing='10px')
        packages = Bag()
        tables = Bag()
        for pkg in self.db.packages.values():
            attr = pkg.attributes
            if attr.get('_syspackage'):
                continue
            pkgtables = Bag()
            for t in pkg['tables'].values():
                t = t.dbtable
                if t.counterColumns():
                    pkgtables.setItem(t.name,Bag(code=t.fullname,description=t.name_long))
            if pkgtables:
                tables.setItem(pkg.name,pkgtables)
                packages.setItem(pkg.name,Bag(code=pkg.name,description=pkg.attributes.get('name_long') or pkg))

        fb.data('.packages',packages)
        fb.data('.tables',tables)
        fb.dataFormula('.pkgtables',"tables.getItem(currPkg).deepCopy()",tables='=.tables',currPkg='^.package')
        fb.filteringSelect(value='^.package',lbl='!!Package',storepath='.packages',storeid='.code', width='30em',
                            storecaption='.description',validate_onAccept='SET .table=null;')
        fb.filteringSelect(value='^.table',lbl='!!Tables',storepath='.pkgtables',storeid='.code', width='30em',
                            storecaption='.description',row_hidden='^.package?=!#v')





