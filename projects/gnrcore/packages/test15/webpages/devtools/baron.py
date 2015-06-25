# -*- coding: UTF-8 -*-
"""Red Baron test"""

import sys
from gnr.core.gnrdecorator import public_method
from redbaron import RedBaron
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_readcode(self, pane):
        """Basic button"""
        bc=pane.borderContainer(height='500px')
        top=bc.contentPane(region='top',height='60px',background='silver')
        left=bc.contentPane(region='left',width='250px')
        center=bc.contentPane(region='center')
        fb=top.formbuilder(cols=3)
        fb.textBox(value='^.modulepath',lbl='Module path')
        fb.button('Read',fire='.readcode')
        top.dataRpc('.codeTree',self.readCode,modulepath='=.modulepath',_fired='^.readcode')
        left.tree(storepath='.codeTree')
        
        
    @public_method
    def readCode(self,modulepath=None):
        result=Bag()
        modulepath=modulepath or sys.modules[self.__module__].__file__
        with open(modulepath, "r") as source_code:
            red = RedBaron(source_code.read())
        result.fromJson(red.fst())
        return result
            
