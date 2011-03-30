# -*- coding: UTF-8 -*-

# validations.py
# Created by Filippo Astolfi on 2011-03-29.
# Copyright (c) 2011 Softwell. All rights reserved.

"""Validations"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_0_form(self,pane):
        """Validations"""
        fb = pane.formbuilder(cols=2)
        fb.textbox(value='^.name',lbl='Name', validate_case='c')
        fb.div('Capitalized field')
        fb.textbox(value='^.surname',lbl='Surname', validate_case='c')
        fb.div('Capitalized field')
        fb.textbox(value='^.job',lbl='Profession',
                   validate_case='l',
                   validate_notnull=True,validate_notnull_error='!!Required field')
        fb.div('Not null field; lowercase field')
        fb.textbox(value='^.address', lbl='!!Address')
        fb.div('No validation is required')
        fb.textbox(value='^.fiscal_code',lbl='!!Fiscal code',
                   validate_len='16',validate_case='u')
        fb.div('Uppercased field; Precise length field [16]')
        fb.textBox(value='^.long',lbl='Long string',validate_len='6:',
                   validate_onReject='alert("The string "+"\'"+value+"\'"+" is too short")')
        fb.div('Insert 6 or more characters (wrong input notification)')
        fb.textBox(value='^.email', lbl="email", validate_email=True,
                   validate_onAccept='alert("Correct email format")',
                   validate_notnull=True)
        fb.div('required correct e-mail form (correct input notification)')