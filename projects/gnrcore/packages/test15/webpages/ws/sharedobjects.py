# -*- coding: UTF-8 -*-

# sharedobjects.py
# Created by Francesco Porcari on 2012-01-03.
# Copyright (c) 2012 Softwell. All rights reserved.

from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
"Test sharedobjects"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    dojo_source = True

    def windowTitle(self):
        return ''
         
    def test_0_firsttest(self,pane):
        pane.sharedObject('mydata',shared_id='so_test1')
        fb=pane.formbuilder(cols=1, datapath='mydata')
        fb.textbox('^.name', lbl='Name')
        fb.textbox('^.address', lbl='Address')
        fb.numbertextbox('^.age', lbl='Age')

    @public_method
    def testDebug(self):
        return Bag(dict(pipo='pipo'))
    