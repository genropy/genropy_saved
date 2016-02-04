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
        return ''
         

    def test_0_shortcuts(self,pane):

        fb = pane.formbuilder(cols=1,border_spacing='3px')

        fb.textbox(value='^.suggestions',lbl='Suggestions')
        fb.simpleTextArea(value='^.test',width='40em',lbl='Test',suggestions='=gnr.app_preference.base.shortcuts.base__mainshortcuts_')

        fb.textbox(value='^.test_2',width='40em',lbl='Test 2',
            suggestions='=gnr.app_preference.base.shortcuts.base__mainshortcuts_')