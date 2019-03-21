# -*- coding: utf-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.batch.btcaction import BaseResourceAction
from gnr.core.gnrbag import Bag
import gzip
import os

caption = 'Import archive file'
tags = '_DEV_,superadmin'
description =  'Import archive file'

class Main(BaseResourceAction):
    batch_prefix = 'iaf'
    batch_title =  'Import archive file'
    batch_cancellable = False
    batch_delay = 0.5
    batch_immediate = True
    #batch_steps = 'get_dependencies,archive,delete_archived'

    def do(self):
        filepath = self.batch_parameters.get('filepath')
        if filepath:
            path = self.page.site.getStaticPath(filepath)
        else:
            path = self.page.site.getStaticPath('page:archive_to_import','last_archive.pik')
        archive = Bag(path)
        self.db.importArchive(archive,thermo_wrapper=self.btc.thermo_wrapper)
        self.db.commit()
        
        

    def table_script_parameters_pane(self, pane, table=None,**kwargs):
        fb = pane.div(padding='10px').formbuilder(cols=1,border_spacing='3px')
        fb.textbox(value='^.filepath',lbl='Filepath')
        
        fb.dropUploader(label='Drop the archive here',width='230px',
                        uploadPath='page:archive_to_import',
                        filename='last_archive.pik',
                        progressBar=True)

