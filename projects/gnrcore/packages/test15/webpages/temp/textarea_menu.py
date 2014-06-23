# -*- coding: UTF-8 -*-

# textarea_menu.py
# Created by Francesco Porcari on 2012-04-13.
# Copyright (c) 2012 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return ''
 
    def test_0_firsttest(self,pane):
        """First test description"""
        pane.simpleTextArea(value='^.piero').menu(action="""genro.dom.setTextInSelection($2,($1.fullpath.indexOf('caption_')==0?$1.label:$1.fullpath));""",
                                                    values='^.mario')
        #m.menuline('pippo',caption='Pippo')
        #m.menuline('paperino',caption='Paperino')
        pane.simpleTextArea(value='^.mario')
    
 
    def test_1_firsttest(self,pane):
        """First test description"""
        pane.simpleTextArea(value='^.piero',suggestions='pippo:Pippo,paperino:Paperino')
        #m.menuline('pippo',caption='Pippo')
        #m.menuline('paperino',caption='Paperino')
        #pane.simpleTextArea(value='^.mario')