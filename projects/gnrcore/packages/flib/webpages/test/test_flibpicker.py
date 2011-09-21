# -*- coding: UTF-8 -*-

# test_flibpicker.py
# Created by Saverio Porcari on 2010-10-15.
# Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"FlibPicker test"
class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,item_picker:FlibPicker"


    def test_1_flibpicker(self, pane):
        self.flibPicker(pane, pickerId='test_picker', datapath='.picker', rootpath=None,
                        current_items=None, selected_items=None)
        pane.button('Open picker', action='PUBLISH test_picker_open')

