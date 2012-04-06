# -*- coding: UTF-8 -*-

# checkboxgroup.py
# Created by Francesco Porcari on 2011-06-24.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return ''
         
    def test_0_mode_values(self,pane):
        """First test description"""
        pane.checkBoxText('Foo,Bar,Span',value='^.pluto',separator=' -     ')
        pane.textbox(value='^.pluto')
    
    def test_1_mode_codes(self,pane):
        """First test description"""
        pane.checkBoxText('foo:Foo,bar:Bar,span:Span',value='^.pluto',separator=' -     ')
        pane.textbox(value='^.pluto')
        pane.textbox(value='^.pluto?value_caption')

    def test_2_mode_numbcode(self,pane):
        """First test description"""
        pane.checkBoxText('0:Foo,1:Bar,2:Span',value='^.pluto',separator=' -     ')
        pane.textbox(value='^.pluto')
        pane.textbox(value='^.pluto?value_caption')
