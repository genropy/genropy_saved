# -*- coding: UTF-8 -*-

# textbox.py
# Created by Filippo Astolfi on 2010-09-17.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Textbox"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    # For an exhaustive documentation, please see http://docs.genropy.org/widgets/form/textboxes/textbox.html
    
    def test_1_textbox(self,pane):
        """Textbox"""
        pane.div("Some simple textboxes.",font_size='.9em',text_align='justify')
        fb = pane.formbuilder(datapath='test1',cols=2)
        fb.textbox(value='^.name',lbl='Name')
        fb.textbox(value='^.surname',lbl='Surname')
        fb.textbox(value='^.address',lbl='Address')
        fb.textbox(value='^.email',lbl='e-mail')
        
    def test_2_validation(self,pane):
        """Validation on a textbox"""
        fb = pane.formbuilder(datapath='test2',cols=2)
        fb.textbox(value='^.textBox')
        fb.div("A simple textbox.",font_size='.9em',text_align='justify')
        fb.textbox(value='^.textBox_2',nodeId='name',
                   validate_len='4:',
                   validate_onReject='alert(value+" is too short (minimum 4 characters)")',
                   validate_onAccept='alert("Correct lenght of "+value)')
        fb.div(""" A textbox with "validate" attributes. Here you have to write a text
                   with 4 or more characters.""",
                   font_size='.9em',text_align='justify')
                   
    def test_3_validationTextBoxAttributes(self,pane):
        """Some validationTextBox features"""
        fb = pane.formbuilder(datapath='test3',cols=2)
        fb.textbox(value='^.name',lbl='Name',colspan=2,
                   required=True,
                   promptMessage="""Write something!(regExp='casa')""",
                   regExp='casa'
                   )
                    
        fb.textbox(value='^.surname',lbl='Surname',
                   invalidMessage='You MUST write something!', #Filippo Astolfi Questo non funziona, però di default esiste
                                                               #     un invalidMessage, che dice: "Il valore
                                                               #     immesso non è valido." Strano!
                   tooltipPosition='top',
                   constraints='???')
        fb.div("""In the following textbox I (Filippo Astolfi) write all the attributes that doesn't work
                  in Dojo 1.1, and that have to be tested for Dojo 1.5""",
                  font_size='.9em',text_align='justify')
        