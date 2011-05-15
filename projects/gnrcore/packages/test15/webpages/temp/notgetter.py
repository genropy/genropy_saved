# -*- coding: UTF-8 -*-

# notgetter.py
# Created by Francesco Porcari on 2011-05-14.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    user_polling=0
    auto_polling=0
    def windowTitle(self):
        return ''
         
    def test_0_firsttest(self,pane):
        """First test description"""
        pane.textbox(value='^.foo')
        pane.button('pippo',disabled='^.foo?=!#v')
        pane.button(label='^.foo::aaaa')
