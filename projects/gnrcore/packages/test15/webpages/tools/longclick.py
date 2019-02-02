# -*- coding: utf-8 -*-

# dbselect_bug.py
# Created by Francesco Porcari on 2012-01-03.
# Copyright (c) 2012 Softwell. All rights reserved.

"Test page description"
from builtins import object
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    dojo_source = True

    def windowTitle(self):
        return ''
         

    def test_0_longclick(self,pane):
        pane.div('Ciao',background='lime',connect_onclick="if($1._longClick){alert('long '+$1._clickDuration)}")
        pane.div('Click and hold',background='pink',selfsubscribe_clickAndHold="alert('clickAndHold');",
                selfsubscribe_longMouseDown="alert('longMouseDown');")
