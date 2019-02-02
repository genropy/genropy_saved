# -*- coding: utf-8 -*-

# gettemplate.py
# Created by Francesco Porcari on 2011-05-11.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
from builtins import object
from gnr.core.gnrdecorator import public_method
import mimetypes


class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def test_1_download_text(self,pane):
        """First test description"""
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.textbox(value='^.name',lbl='Name')
        fb.data('.name',"hello")
        fb.button('Download file',action='genro.rpcDownload(rpcmethod,{name:name+".txt"})',
                    rpcmethod=self.testDownloadFile,
                    name='=.name')


    def test_2_download_button(self,pane):
        """First test description"""
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.textbox(value='^.name',lbl='Name')
        fb.data('.name',"hello")
        fb.downloadButton(label='Download file',
                    cursor='pointer',
                    text_decoration='underline',
                    rpc_method=self.testDownloadFile,
                    rpc_name='=.name')

    @public_method
    def testDownloadFile(self,name=None,**kwargs):
        self.download_name = name or 'pippo.txt'
        return 'Hello to everybody \n paraponzi'

