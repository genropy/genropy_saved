# -*- coding: UTF-8 -*-

# test_flibpicker.py
# Created by Saverio Porcari on 2010-10-15.
# Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"FlibPicker test"
class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,flib:FlibPicker"


    def test_1_flibpicker(self, pane):
        pane.flibPicker(dockButton=True)


