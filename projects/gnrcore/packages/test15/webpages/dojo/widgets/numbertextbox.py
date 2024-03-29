# -*- coding: utf-8 -*-

# tree.py
# Created by Filippo Astolfi on 2011-12-02.
# Copyright (c) 2011 Softwell. All rights reserved.

"""numberTextBox"""

from builtins import object
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    
    def windowTitle(self):
        return 'NumberTextBox'
        

    def test_0_base(self, pane):
        fb = pane.formbuilder(cols=2,datapath='.data')
        fb.numberTextBox(value='^.number.blu')
        fb.numberTextBox(value='^.number.inattr?val')

        fb.button('TEST',fire='.colors')
        fb.dataRpc('.number',self.testblu,_fired='^.colors')

    @public_method
    def testblu(self):
        a = Bag()
        a.setItem('blu',3,wdg_color='navy')
        a.setItem('inattr',None,val=44,wdg_val_color='red')
        return a

    def test_1_focus(self, pane):
        fb = pane.formbuilder(cols=2,datapath='.data')
        fb.textbox('^.txtval',lbl='Txt')
        fb.textbox('^.txtval_2',lbl='Txt 2')
        fb.data('.txtval_2','test')
        fb.data('.number',0)
        fb.numberTextBox('^.number',lbl='Number',format='#.00') #_autoselect=True

    def test_2_dotcomma(self, pane):
        fb = pane.formbuilder(cols=2,datapath='.data')
        fb.numberTextBox('^.number',lbl='Number',format='#,###.00') #_autoselect=True
