# -*- coding: UTF-8 -*-
"""Textbox"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_textbox(self, pane):
        """Textbox"""
        fb = pane.formbuilder()
        fb.textbox(value='^.name', lbl='Name')
        fb.textbox(value='^.surname', lbl='Surname')
        fb.textbox(value='^.address', lbl='Address')
        fb.textbox(value='^.email', lbl='e-mail')

    def test_2_validation(self, pane):
        """Validation on a textbox"""
        fb = pane.formbuilder(datapath='test2', cols=2)
        fb.textbox(value='^.textBox')
        fb.div("A \"no validations\" textbox")
        fb.textbox(value='^.textBox_2', validate_len='4:')
        fb.div("""A textbox with "validate_len" validation: try to write a text with less than
                  4 characters to invalidate the field""")
        fb.textbox(value='^.textBox_2', validate_email=True)
        fb.div("""A textbox with "validate_email" validation. Try to type an email""")