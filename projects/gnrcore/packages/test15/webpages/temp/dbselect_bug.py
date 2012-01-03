# -*- coding: UTF-8 -*-

# dbselect_bug.py
# Created by Francesco Porcari on 2012-01-03.
# Copyright (c) 2012 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    dojo_source = True

    def windowTitle(self):
        return ''
         
    def test_0_firsttest(self,pane):
        """First test description"""
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.dbSelect(dbtable='glbl.nazione',value='^.nazione',lbl='Nazione')
        fb.div('^.nazione')