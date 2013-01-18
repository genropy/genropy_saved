# -*- coding: UTF-8 -*-

# dataremote.py
# Created by Francesco Porcari on 2010-10-29.
# Copyright (c) 2010 Softwell. All rights reserved.

"""dataRemote"""

import datetime
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
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


    def test_5_xx(self, pane):
        pane.textbox(value='^.testo')
        pane.div('^.risultato')
        pane.dataRemote('.risultato', self.piero, testo='^.testo')

    @public_method
    def piero(self,testo=None):
        return (testo or 'Ciao')+' Piero'

    def rpc_get_seconds(self, **kwargs):
        return datetime.datetime.now().second
    
    def rpc_get_time(self, **kwargs):
        return datetime.datetime.now()


    def test_9_remotepublish(self,pane):
        "aaaaa"
        pane.button('Test',action='FIRE .test')
        pane.dataRpc('dummy',self.remotePublishTest,_fired='^.test')
        pane.dataController("alert(number);",nodeId='ccc',selfsubscribe_test_node=True)
        pane.dataController("alert(number);",subscribe_test_public=True)
#
    #@public_method
    #def remotePublishTest(self):
    #    self.setInClientData('gnr.publisher',dict(topic='test_node',nodeId='ccc',kw=dict(number=4)),fired=True)
    #    self.setInClientData('gnr.publisher',dict(topic='test_public',kw=dict(number=36)),fired=True)



    @public_method
    def remotePublishTest(self):
        self.clientPublish('test_node',number=4,nodeId='ccc')
        self.clientPublish('test_public',number=36)

