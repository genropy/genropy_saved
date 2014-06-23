# -*- coding: UTF-8 -*-
"""simpleTextarea"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"

    def test_0_simpleTextareaSpeech(self, pane):
        """simpleTextarea"""
        pane.simpleTextarea(value='^.simpleTextarea', height='200px', width='400px',speech=True,editor=True)


    def test_2_simpleTextareaSpeech(self, pane):
        """simpleTextarea"""
        pane.formbuilder(cols=1,border_spacing='3px').simpleTextarea(value='^.simpleTextarea', height='200px', width='400px')

    def test_3_simpleTextareaSpeechFb(self, pane):
        fb = pane.formbuilder(cols=1,border_spacing='3px',fld_width='100%',width='400px')
        fb.simpleTextarea(value='^.simpleTextarea', height='200px',speech=True,lbl='Prova',editor=True)



   #def test_1_simpleTextareaFullEditor(self, pane):
   #    """simpleTextarea"""
   #    pane.simpleTextarea(value='^.simpleTextarea', height='80px', width='30em',
   #                        color='#605661', font_size='1.2em',editor=True)