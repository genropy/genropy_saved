# -*- coding: UTF-8 -*-

# rpcurl.py
# Created by Francesco Porcari on 2011-11-12.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
import datetime
from gnr.core.gnrdecorator import public_method
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return ''
         

    def test_1_errordebug(self,pane):
        pane.button('test',action='3+pino;');

    def test_0_firsttest(self,pane):
        """First test description"""
        pane.button('Action',action="""genro.rpcDownload('oraCorrente',{title:'sono le ore',_download_name_:'pippone'});""")
    
    @public_method
    def oraCorrente(self,title=None,**kwargs):
        
        return '%s %s' %(title,datetime.datetime.now())