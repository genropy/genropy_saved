# -*- coding: UTF-8 -*-

# filtering.py
# Created by Francesco Porcari on 2011-10-19.
# Copyright (c) 2011 Softwell. All rights reserved.

"FilteringSelect"
class GnrCustomWebPage(object):
    dojo_source=True
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return ''

    def isDeveloper(self):
        return True
         

    def test_1_filtering(self,pane):
        "FilteringSelect"
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.data('.code','1')
        fb.button('Reset value',action='SET .pluto=null;')
        fb.filteringSelect(value='^.code',values='0:Zero,1:One,2:Two',lbl='With code')
        fb.filteringSelect(value='^.description',values='Zero,One,Two',lbl='No code')

    def test_2_combobox(self,pane):
        "combobox"
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.comboBox(value='^.description',values='Zero,One,Two',lbl='Combo')

