# -*- coding: utf-8 -*-

"""Context tester"""
from __future__ import print_function

from builtins import object
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method
from datetime import datetime

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    dojo_version = '11'
    dojo_theme = 'tundra'

    
    def test_2_rpc_ts(self, pane):
        """Context rpc """
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.div("^.result.server_ts",lbl='Server ts')
        fb.div("^.result2.server_ts",lbl='ts 2')

        fb.button('Get server ts',action="FIRE .get_ts;")
        fb.button('Send',action="FIRE .send_ts;")

        fb.dataRpc('.result',self.serverTransmission,_fired='^.get_ts')

        fb.dataRpc('.result2',self.checkTransmission,previeousResult='=.result',_fired='^.send_ts')


    @public_method
    def serverTransmission(self):
        result = Bag()
        ts = datetime.now()
        result.setItem('server_ts',ts,dtype='DH',ts=ts)
        return result


    @public_method
    def checkTransmission(self,previeousResult=None):
        print('previeousResult',previeousResult)
        print(previeousResult['server_ts'])
        return previeousResult

