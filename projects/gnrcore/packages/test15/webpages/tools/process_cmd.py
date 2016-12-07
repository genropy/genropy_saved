# -*- coding: UTF-8 -*-

"""process_cmd tester"""
from gnr.core.gnrdecorator import public_method
import os

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    
    def test_1_process_cmd(self, pane):
        pane.button('Run Test',fire='.run')
        pane.dataRpc(None,self.runTestCommand,_fired='^.run')

    @public_method
    def runTestCommand(self):
        self.log('process id',os.getpid())
        self.site.process_cmd.test(p1='test')