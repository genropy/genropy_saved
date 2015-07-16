# -*- coding: UTF-8 -*-

# dbselect_bug.py
# Created by Francesco Porcari on 2012-01-03.
# Copyright (c) 2012 Softwell. All rights reserved.

"Test page description"
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    dojo_source = True

    def windowTitle(self):
        return 'setInClientData'
         
    def test_0_setInClientData(self,pane):
        """dbselect with auxcol"""
        bc = pane.borderContainer(height='500px')
        left = bc.contentPane(region='left',width='50%',datapath='.pars')
        pane.data('.pars',Bag(dict(destpath='foo.bar',value='44')))
        fb = left.formbuilder(cols=1, border_spacing='4px')
        fb.textbox(value='^.destpath',lbl='Path')
        fb.textbox(value='^.value',lbl='Value')
        bc.contentPane(region='center',datapath='.pars').multiValueEditor(value='^.attributes')
        fb.textbox(value='^._nodeId',lbl='NodeId')
        fb.textbox(value='^._fired',lbl='Fired')
        fb.textbox(value='^._reason',lbl='Reason')
        fb.button('Send RPC',fire='.#parent.send_rpc')
        fb.button('Send WSK',fire='.#parent.send_wsk')

        fb = bc.contentPane(region='bottom',nodeId='mybox',datapath='.mybox.data',background='yellow').formbuilder(cols=3,border_spacing='3px')
        fb.div('^.foo.bar',lbl='foo.bar',width='10em')
        fb.div('^.spam',lbl='spam',width='10em')
        fb.div('^.alpha',lbl='alpha',width='10em')

        pane.dataRpc('dummy',self.testSetInClientDataSimple,pars='=.pars',_fired='^.send_rpc')        
        pane.dataRpc('dummy',self.testSetInClientDataSimple,pars='=.pars',_fired='^.send_wsk',httpMethod='WSK')        

    @public_method
    def testSetInClientDataSimple(self,pars=None):
        attributes = pars['attributes']
        if attributes:
            attributes = attributes.asDict(ascii=True)
        self.setInClientData(pars['destpath'],value=pars['value'],attributes=attributes,nodeId=pars['_nodeId'],fired=pars['_fired'])



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
        self.log('Il mio numero',number,prova=33,test={'aaa':99})
