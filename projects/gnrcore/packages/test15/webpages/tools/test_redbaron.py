# -*- coding: UTF-8 -*-

# messages.py
# Created by Francesco Porcari on 2010-08-26.
# Copyright (c) 2010 Softwell. All rights reserved.

"""RedBaron"""

from gnr.core.gnrdecorator import public_method
from time import sleep
from random import randint
class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    
    def windowTitle(self):
        return 'RedBaron'
        
    def test_1_redbaron(self,pane):
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.numberTextBox(value='^.module',lbl='Module')
        fb.button('ADD',action="""var current = (current || 0)+1;
                                SET .module = current;
                                SET .current = current""",current='=.current')
        fb.dataRpc('.result',self.redBaronIndex,httpMethod='WSK',module='^.module',
                    _onCalling='SET .module=null',_if='module')
        fb.div('^.result')

    def test_2_testLog(self,pane):
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.button('Log',action="""var current = (current || 0)+1;
                                SET .number = current;
                                SET .current = current""",current='=.current')
        fb.dataRpc('.result',self.testLog,number='^.number',
                    _onCalling='SET .number=null',_if='number')
        fb.div('^.result')

    @public_method
    def testLog(self,number=None):
        self.log('Il mio numero %s' %number)



    @public_method
    def redBaronIndex(self,module=None):
        self.log('Prova %s' %module)
        with self.sharedData('status',list) as shared:
            s = randint(0,5)
            if module=='*':
                shared[:] = []
            else:
                txt = 'SET %s . Waited %s' %(module,s)
                shared.append(txt) 
            sleep(s)
            return '<br/>'.join(shared)
