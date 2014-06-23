# -*- coding: UTF-8 -*-

# valueattr.py
# Created by Francesco Porcari on 2012-05-04.
# Copyright (c) 2012 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return ''
         
    def test_0_valueattr(self,pane):
        """First test description"""
        fb = pane.formbuilder(cols=1, border_spacing='3px')
        
        fb.textbox(value='^.asfreddo.giusippo.testtxt',lbl='With valueattr',attr_pippo='^.pippo')
        fb.textbox(value='^.pippo',lbl='Pippo')