# -*- coding: UTF-8 -*-
"""simpleTextarea"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_simpleTextarea(self, pane):
        """simpleTextarea"""
        pane.simpleTextarea(value='^.simpleTextarea', height='80px', width='30em',
                            color='#605661', font_size='1.2em',
                            default='A simple area to contain text')