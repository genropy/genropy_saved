# -*- coding: utf-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2011 Softwell. All rights reserved.



from gnr.web.batch.btcaction import BaseResourceAction
caption = '!!Import localization file'
tags = 'superadmin,_DEV_'
description = '!!Import localization file'

class Main(BaseResourceAction):
    batch_prefix = 'icnt'
    batch_title = '!!Import localization file'
    batch_cancellable = False
    batch_delay = 0.5
    batch_immediate = True
    
    def do(self):
        package = self.batch_parameters['package']
        package_identifier = '%s/%s'%(self.db.application.packages[package].project,package)
        with self.page.site.storageNode('pkg:%s'%package,'localization.xml').open() as localizationfile:
            self.tblobj.importLocalizationFile(package_identifier=package_identifier,filepath=localizationfile)
        self.db.commit()

    def table_script_parameters_pane(self, pane, table=None,**kwargs):
        fb = pane.formbuilder(cols=1,border_spacing='10px')
        fb.filteringSelect(value='^.package',lbl='!!Package identifier',
                        values=','.join(list(self.db.packages.keys())))





