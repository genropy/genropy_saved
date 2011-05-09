# -*- coding: UTF-8 -*-

# togglebutton.py
# Created by Filippo Astolfi on 2010-10-13.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Radio buttons"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage

    def test_1_basic(self, pane):
        """Simple test"""
        fb = pane.contentPane(title='Buttons', datapath='test1').formbuilder(cols=4, border_spacing='10px')

        fb.div("""We show you here a simple radio buttons set; (add to your radiobuttons
                  the "group" attribute).""", font_size='.9em', text_align='justify')
        fb.radiobutton(value='^.radio.jazz', group='genre1', label='Jazz')
        fb.radiobutton(value='^.radio.rock', group='genre1', label='Rock')
        fb.radiobutton(value='^.radio.blues', group='genre1', label='Blues')

        fb.div("""Here we show you an other radio buttons set.""",
               font_size='.9em', text_align='justify')
        fb.div('Sex')
        fb.radiobutton(value='^.sex.male', group='genre2', label='M')
        fb.radiobutton(value='^.sex.female', group='genre2', label='F')