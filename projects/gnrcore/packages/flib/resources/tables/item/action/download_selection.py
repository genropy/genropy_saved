# -*- coding: UTF-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.batch.btcaction import BaseResourceAction
import time
import os

caption = '!!Download Selection'
description='!!Download selected files'

class Main(BaseResourceAction):
    batch_prefix = 'dwn_selection'
    batch_title = 'Download Selection'
    batch_cancellable = True
    batch_immediate = True
    batch_delay = 0.5
    dialog_height = '70px'
         
    def do(self):
        selection = self.get_selection()
        import zipfile
        self.zipNode = self.page.site.storageNode('page:output','%s.zip' % self.filename, autocreate=-1)
        self.zipurl = self.zipNode.url()
        with self.zipNode.open(mode='wb') as zipresult:
            zip_archive = zipfile.ZipFile(zipresult, mode='w', compression=zipfile.ZIP_DEFLATED)
            for item in self.btc.thermo_wrapper(selection,'!!Zip file',message=self.get_record_caption):
                item_path = item['path']
                if item_path:
                    item_node = self.page.site.storageNode(item_path)
                    with item_node.local_path() as i_path:
                        zip_archive.write(i_path, os.path.basename(item_path))
            zip_archive.close()
    

    def prepareFilePath(self, filename=None):
        if not filename:
            filename = self.maintable.replace('.', '_') if hasattr(self, 'maintable') else self.page.getUuid()
        filename = filename.replace(' ', '_').replace('.', '_').replace('/', '_')[:64]
        filename = filename.encode('ascii', 'ignore')
        self.filename = filename
        
    def result_handler(self):
        if self.batch_immediate:
            self.page.setInClientData(path='gnr.downloadurl',value=self.zipurl,fired=True)
        return 'Execution completed', dict(url=self.zipurl, document_name=self.batch_parameters['filename'])

    def _table_script_parameters_pane(self,pane,**kwargs):
        pass