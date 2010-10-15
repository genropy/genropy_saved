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
        pane=pane.contentPane(height='400px',width='800px',position='relative')
        self.dropFileGrid(pane,uploaderId='foo_uploader',datapath='.uploader',
                      label='Upload here',footer=None,enabled=True,onResult='alert("Done")',
                      uploadPath='site:testuploader/foo_up',
                      preview=True)
        
    
    
        
    
        
        
