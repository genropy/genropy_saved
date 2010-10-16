# -*- coding: UTF-8 -*-

# batch_handler.py
# Created by Francesco Porcari on 2010-10-01.
# Copyright (c) 2010 Softwell. All rights reserved.


"""Test drop uploader"""
class GnrCustomWebPage(object):
    py_requires="""gnrcomponents/testhandler:TestHandlerFull,
                   gnrcomponents/drop_uploader:DropUploader"""

        
    def test_1_uploader(self,pane):
        """File Uploader"""
        self.dropUploader(pane)
    
    
    def test_2_dropFileGrid(self,pane):
        """dropFileGrid"""
        def footer(footer,**kwargs):
            footer.button('Upload',action='PUBLISH foo_uploader_upload',float='right')
        self.dropFileGrid(pane.contentPane(height='400px'),uploaderId='foo_uploader',datapath='.uploader',
                      label='Upload here',enabled=True,onResult='alert("Done")',
                      metacol_description=dict(name='!!Description',width='10em'),footer=footer,
                      uploadPath='site:testuploader/foo_up',
                      preview=True,uploadedFilesGrid=True)
        
    
    def onUploading_foo_uploader(self,file_url=None,file_path=None,
                                description=None,titolo=None,**kwargs):
        result =  dict(file_url=file_url,file_path=file_path)
        print result
        return result
        
    
        
        
