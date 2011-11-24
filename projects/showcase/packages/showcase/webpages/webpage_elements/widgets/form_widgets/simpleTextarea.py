# -*- coding: UTF-8 -*-
"""simpleTextarea"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_simpleTextarea(self, pane):
        """simpleTextarea"""
        bc = pane.borderContainer(height='100px')
        fb = bc.formbuilder(datapath='test1')
        fb.simpleTextarea(value='^.simpleTextarea', height='80px', width='30em',
                          colspan=2, color='blue', font_size='1.2em',
                          default='A simple area to contain text.', lbl='Textarea')