# -*- coding: UTF-8 -*-

# deferred.py
# Created by Francesco Porcari on 2011-02-12.
# Copyright (c) 2011 Softwell. All rights reserved.

"deferred"

from time import sleep

class GnrCustomWebPage(object):
    user_polling=0
    auto_polling=0
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    
    def windowTitle(self):
        return 'deferred'
        
    def test_0_deferred(self, pane):
        pane.numberTextBox(value='^.x',default=10)
        pane.button('Cb',action="""genro.testDeferred('give_me_five',{x:x});""",x='^.x')
        
    def test_1_deferred(self, pane):
        pane.numberTextBox(value='^.x',default=10)
        pane.button('Cbtxt',action="""genro.testDeferred('give_me_five',{x:x},'text');""",x='^.x')
        
    def test_2_dataRpc(self, pane):
        pane.numberTextBox(value='^.x',default=5)
        pane.numberTextBox(value='^.k',default=4)
        pane.button('Somma',fire='^.go')
        pane.textbox(value='^.deferred_res')
        pane.textbox(value='^.res')
        dr = pane.dataRpc('.res','give_me_five',x='=.x',_fired='^.go',_onResult='result')
        dr.addCallback('result+z+k',z=26,k='=.k')
       # dr.addCallback('SET .deferred_res = result;')
        
    def test_2_syncdata(self, pane):
        pane.numberTextBox(value='^.x',default=5)
        pane.numberTextBox(value='^.k',default=4)
        pane.button('Somma',fire='^.go')
        dr = pane.dataController("""var deferred = genro.testDeferredSum(x,k);
                                    deferred.addCallback(function(result){
                                        result = result*100;
                                        return result;
                                    });
                                    deferred.addCallback(function(result){
                                        alert(result);
                                        return result;
                                    });
                                    """,x='=.x',k='=.k',_fired='^.go',sync=True)
        #dr.addCallback('return result+z+k',z=26,k='=.k')
        #dr.addCallback('console.log(result)')
        
    def rpc_give_me_five(self, x=None, **kwargs):
        sleep(x)
        return x