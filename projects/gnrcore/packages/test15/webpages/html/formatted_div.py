#!/usr/bin/python
# -*- coding: utf-8 -*-

"genro.dom.centerOn"

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    
    
    def test_0_boolean(self, pane):
        pane.data('.bool_value', True)
        pane.lightbutton('^.bool_value',action="""SET .bool_value=event.shiftKey?null:!val;""",val='=.bool_value',
                            format='<div class="checkboxOn">&nbsp;</div>,<div class="checkboxOff">&nbsp;</div>,<div class="checkboxOnOff">&nbsp;</div>',
                            dtype='B')
        pane.div(value='^.bool_value', format='semaphore', dtype='B')
        pane.semaphore('^.bool_value')

    def test_2_cb(self,pane):
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.div(_class='').checkbox(value='^.pippo',validate_notnull=True)


    def test_1_boolean(self, pane):
        pane.div(format=dict(isbutton=True,))
