# -*- coding: UTF-8 -*-

# batch_handler.py
# Created by Francesco Porcari on 2010-10-01.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.core.gnrlist import XlsReader
from gnr.core.gnrbag import Bag, DirectoryResolver

"""Test drop uploader"""
class GnrCustomWebPage(object):
    py_requires = """gnrcomponents/testhandler:TestHandlerFull,
                   gnrcomponents/drop_uploader:DropUploader"""


    def test_1_uploader(self, pane):
        """File Uploader"""
        self.dropUploader(pane)


        #def test_2_dropFileGrid(self,pane):
        #    """dropFileGrid"""
        #    def footer(footer,**kwargs):
        #        footer.button('Upload',action='PUBLISH foo_uploader_upload',float='right')
        #    self.dropFileGrid(pane.contentPane(height='400px'),uploaderId='foo_uploader',datapath='.uploader',
        #                  label='Upload here',enabled=True,onResult='alert("Done")',
        #                  metacol_description=dict(name='!!Description',width='10em'),footer=footer,
        #                  uploadPath='site:testuploader/foo_up',
        #                  preview=True,uploadedFilesGrid=True)
        #

    def test_3_dropFileGridXLS(self, pane):
        """dropFileGrid xls"""
        bc = pane.borderContainer(height='400px')
        left = bc.borderContainer(region='left', width='40%', margin='5px')
        right = bc.borderContainer(region='right', width='40%', margin='5px')

        center = bc.borderContainer(region='center', margin='5px')

        def footer(footer, **kwargs):
            footer.button('Upload', action='PUBLISH foo_uploader_upload', float='right')

        self.dropFileGrid(left, uploaderId='foo_uploader', datapath='.uploader',
                          label='Upload here', enabled=True,
                          onResult='alert("Done"); FIRE test.test_3_dropFileGridXLS.update_loaded;',
                          metacol_description=dict(name='!!Description', width='10em'), footer=footer,
                          uploadPath='site:testuploader/foo_up',
                          preview=True, uploadedFilesGrid=True)

        pane.dataRpc('.loaded_content', 'getLoadedFiles', _fired='^.update_loaded',
                     uploadPath='site:testuploader/foo_up', _onStart=True)

        def struct(struct):
            r = struct.view().rows()
            r.cell('filename', name='Filename', width='10em')

        iv = self.includedViewBox(center, label='!!loaded content',
                                  datapath='test.test_3_dropFileGridXLS',
                                  storepath='.loaded_content',
                                  selected_filepath='.uploaded_filepath',
                                  hiddencolumns='filepath',
                                  struct=struct)
        pane.dataRpc('#xlsgrid.data', 'xlsRows', docname='^.uploaded_filepath', _onResult='FIRE #xlsgrid.reload;')

        iv = self.includedViewBox(right, label='!!Xls Rows',
                                  nodeId='xlsgrid',
                                  datapath='test.test_3_dropFileGridXLS.xlsgrid',
                                  storepath='.data.store', structpath='.data.struct',
                                  autoWidth=True)
        gridEditor = iv.gridEditor()

    def rpc_xlsRows(self, docname=None):
        result = Bag()
        reader = XlsReader(docname)
        headers = reader.headers
        result['struct'] = self.newGridStruct()
        r = result['struct'].view().rows()
        for colname in headers:
            r.cell(colname, name=colname, width='5em')
        for i, row in enumerate(reader()):
            result.setItem('store.r_%i' % i, None, dict(row))
        return result


    def rpc_getLoadedFiles(self, uploadPath=None, **kwargs):
        path = self.site.getStaticPath(uploadPath)
        result = Bag()
        b = DirectoryResolver(path)
        for i, n in enumerate(
                [(t[1], t[2]) for t in b.digest('#a.file_ext,#a.file_name,#a.abs_path') if t[0] == 'xls']):
            result.setItem('r_%i' % i, None, filename=n[0], filepath=n[1])
        return result


    def onUploading_foo_uploader(self, file_url=None, file_path=None,
                                 description=None, titolo=None, **kwargs):
        result = dict(file_url=file_url, file_path=file_path)
        #reader = XlsReader(file_path)
        #headers = reader.headers()
        #content = list(reader())
        print result
        return result
        
    
        
        
