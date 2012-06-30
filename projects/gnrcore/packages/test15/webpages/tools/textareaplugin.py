# -*- coding: UTF-8 -*-
"""simpleTextarea"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"

    def test_0_simpleTextareaSpeech(self, pane):
        """simpleTextarea"""
        pane.simpleTextarea(value='^.simpleTextarea', height='80px', width='30em',
                            color='#605661', font_size='1.2em',speech=True)

    def test_1_simpleTextareaFullEditor(self, pane):
        """simpleTextarea"""
        pane.simpleTextarea(value='^.simpleTextarea', height='80px', width='30em',
                            color='#605661', font_size='1.2em',editor=True)