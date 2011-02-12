# -*- coding: UTF-8 -*-

# deferred.py
# Created by Francesco Porcari on 2011-02-12.
# Copyright (c) 2011 Softwell. All rights reserved.
from time import sleep

"Test page description"
class GnrCustomWebPage(object):
    user_polling=0
    auto_polling=0
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return ''
         
        
    def test_0_deferred(self, pane):
        pane.numberTextBox(value='^.x',default_value=10)
        pane.button('Cb',action="""genro.testDeferred('give_me_five',{x:x});""",x='^.x')
    
    def test_1_deferred(self, pane):
        pane.numberTextBox(value='^.x',default_value=10)
        pane.button('Cbtxt',action="""genro.testDeferred('give_me_five',{x:x},'text');""",x='^.x')

    def test_2_dataRpc(self, pane):
        pane.numberTextBox(value='^.x',default_value=5)
        pane.numberTextBox(value='^.k',default_value=4)
        pane.button('Go',fire='^.go')
        dr = pane.dataRpc('.res','give_me_five',x='=.x',_fired='^.go')
        dr.addCallback('console.log(result);return result+z+k',z=26,k='=.k')
        dr.addCallback('console.log(result)')


    def rpc_give_me_five(self, x=None, **kwargs):
        sleep(x)
        return x