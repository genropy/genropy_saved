# -*- coding: UTF-8 -*-

# serverpath.py
# Created by Francesco Porcari on 2010-09-03.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Serverpath"""
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    def test_1_serverpath(self,pane):
        self.autopolling = 0
        fb = pane.formbuilder(cols=1, border_spacing='3px',datapath='test1')
        fb.data('.mysync','',_serverpath='mytest1.mirror')
        fb.textbox(value='^.mydata',lbl='Data')
        fb.div('^.mysync',lbl='Answer')
        fb.dataRpc('dummy','setval',value='^.mydata',
                    serverpath='mytest1.mirror')

    def test_2_serverpath(self,pane):
        self.autopolling = 0
        fb = pane.formbuilder(cols=1, border_spacing='3px',datapath='test2')
        fb.data('.mysync','',_serverpath='mytest2.mirror.ppp')
        fb.textbox(value='^.mydata',lbl='Data')
        fb.div('^.mysync',lbl='Answer')
        fb.dataRpc('dummy','setval',value='^.mydata',
                    serverpath='mytest2.mirror.ppp')
                    
    def test_3_serverpath(self,pane):
        self.autopolling = 0
        fb = pane.formbuilder(cols=1, border_spacing='3px',datapath='test3')
        fb.data('.mysync','',_serverpath='mytest3.mirror')
        fb.textbox(value='^.mydata',lbl='Data')
        fb.div('^.mysync.answer.1.2.3',lbl='Answer')
        fb.dataRpc('dummy','setval',value='^.mydata',
                    serverpath='mytest3.mirror.answer.1.2.3')
    
    def rpc_setval(self,serverpath=None,value=None):
        with self.pageStore() as store:
            print 'setting at %s value %s' %(serverpath,value)
            store.setItem(serverpath,value)
        