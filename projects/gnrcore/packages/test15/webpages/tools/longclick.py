# -*- coding: UTF-8 -*-

# dbselect_bug.py
# Created by Francesco Porcari on 2012-01-03.
# Copyright (c) 2012 Softwell. All rights reserved.

"Test page description"
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    dojo_source = True

    def windowTitle(self):
        return ''
         

    def test_0_longclick(self,pane):
        pane.div('Ciao',background='lime')
        pane.button('Bao',action='alert("pippo");',selfsubscribe_longclick='console.log("selflongclick")')
        pane.dataController("console.log('longclick target',target);",subscribe_longClick=True)