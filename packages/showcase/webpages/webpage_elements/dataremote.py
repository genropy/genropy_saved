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
        pane = pane.contentPane()
        pane.button('Show seconds', action='alert(seconds);', seconds='=.time.seconds')
        pane.dataRemote('.time.seconds', 'get_time', cacheTime=10)

    def test_2_ondiv(self, pane):
        """dataRemote basic example"""
        pane = pane.contentPane()
        pane.div('^.quantic_time')
        pane.dataFormula(".quantic_time", "time", time="=.time.seconds", _timing=1)
        pane.dataRemote('.time.seconds', 'get_time', cacheTime=10)

    def test_3_ondiv(self, pane):
        """dataRemote basic example"""
        pane = pane.contentPane()
        pane.div('^.quantic_time')
        pane.numberTextbox(value='^.b')

        pane.data('.cachetime', 5)
        pane.dataFormula(".quantic_time", "time", time="=.time.seconds", _timing=1)
        pane.dataRemote('.time.seconds', 'get_time', cacheTime=5, b='=.b')

    def rpc_get_time(self, b=None, **kwargs):
        if b:
            return b
        return datetime.datetime.now().second