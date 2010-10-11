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
    
    
        
        
