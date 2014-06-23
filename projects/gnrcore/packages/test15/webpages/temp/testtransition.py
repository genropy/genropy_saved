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
        """dbselect with auxcol"""
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        d = fb.div(height='30px',width='30px',border='1px solid silver',style='^.mystyle')
        fb.simpleTextArea(value='^.buffer',width='300px',height='100px')
        fb.dataController('SET .mystyle = b; SET .buffer =null;',b='^.buffer')