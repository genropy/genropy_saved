# -*- coding: UTF-8 -*-

# dataremote.py
# Created by Francesco Porcari on 2010-10-29.
# Copyright (c) 2010 Softwell. All rights reserved.

"""dataRemote"""

import datetime

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage

    def test_1_basic(self, pane):
        """dataRemote basic example"""
        fb = pane.formbuilder(datapath='test1')
        pane.button('Show time', action='alert(time);', time='=.time')
        pane.dataRemote('.time', 'get_time', cachetime=10)
        
    def test_2_cc(self, pane):
        pane.button('Show seconds', action='FIRE dammi_ora;')
        pane.dataRpc('.time.seconds', 'get_seconds', _fired='^dammi_ora')
        pane.dataController("alert(seconds)",seconds="^.time.seconds")

    def test_3_ondiv(self, pane):
        """dataRemote basic example"""
        pane = pane.contentPane()
        pane.div('^.quantic_time')
        pane.dataFormula(".quantic_time", "time", time="=.time.seconds", _timing=1)
        pane.dataRemote('.time.seconds', 'get_seconds', cacheTime=10)

    def test_4_ondiv(self, pane):
        """dataRemote basic example"""
        pane = pane.contentPane()
        pane.div('^.quantic_time')
        pane.numberTextbox(value='^.b')

        pane.data('.cachetime', 5)
        pane.dataFormula(".quantic_time", "time", time="=.time.seconds", _timing=1)
        pane.dataRemote('.time.seconds', 'get_seconds', cacheTime=5, b='=.b')

    def rpc_get_seconds(self, **kwargs):
        return datetime.datetime.now().second
    
    def rpc_get_time(self, **kwargs):
        return datetime.datetime.now()