# -*- coding: UTF-8 -*-

# mixed.py
# Created by Niso on 2010-09-08.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Mixed"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    #   - Other forms, attributes and items:
    #       In this section we report forms/attributes that have been used in this example
    #       despite they didn't strictly belonging to boxes.
    #       We also suggest you the file (if it has been created!) where you can find
    #       some documentation about them.
    #
    #       ## name ##          --> ## file ##
    #       cols                --> formbuilder.py
    #       datapath            --> datapath.py
    #       formbuilder         --> formbuilder.py
    #       popup               --> dateTextbox.py
    #       value               --> datapath.py
    
    def test_1_basic(self,pane):
        """Mixed"""
        fb = pane.formbuilder(datapath='test1',cols=3,fld_width='100%',width='100%')
        fb.textBox(value='^.r0.name',lbl='Name')
        fb.textBox(value='^.r0.surname',lbl='Surname',colspan=2)
        fb.dateTextBox(value='^.r0.birthday',lbl='Birthday')
        fb.dateTextBox(value='^.r0.date',popup=False,lbl='Date (no popup)')
        fb.div('remember: date format is GG/MM/AAAA',
                font_size='.9em',text_align='justify')
        fb.numberTextBox(value='^.r0.age',lbl='Age')
        fb.textBox(value='^.r0.text',width='5em',lbl='Text')
