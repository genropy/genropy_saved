# -*- coding: utf-8 -*-

# dbselect_bug.py
# Created by Francesco Porcari on 2012-01-03.
# Copyright (c) 2012 Softwell. All rights reserved.

"Test page description"
from builtins import object
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    dojo_source = True

    def windowTitle(self):
        return ''
         

    def test_0_shortcuts(self,pane):

        fb = pane.formbuilder(cols=1,border_spacing='3px')

        fb.simpleTextArea(value='^.test_1',width='40em',lbl='Test 1',shortcuts='Pippo,Nonna Papera,Ciccio')
        fb.simpleTextArea(value='^.test_2',width='40em',lbl='Test 2',shortcuts='p:Pippo,np:Nonna Papera,n:Nemo')
        fb.simpleTextArea(value='^.test_3',width='40em',lbl='Test 3',shortcuts=True)


