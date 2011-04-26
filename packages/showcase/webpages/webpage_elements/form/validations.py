# -*- coding: UTF-8 -*-

# validations.py
# Created by Filippo Astolfi on 2011-03-29.
# Copyright (c) 2011 Softwell. All rights reserved.

"""Validations"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_0_form(self,pane):
        """Validations"""
        fb = pane.formbuilder(lbl_color='teal')
        fb.textbox(value='^.no_val', lbl='No validations')
        fb.textbox(value='^.capitalized',lbl='Capitalized field', validate_case='c')
        fb.textbox(value='^.lowercased',lbl='Lowercased field - required',validate_case='l',
                   validate_notnull=True,validate_notnull_error='!!Required field')
        fb.textbox(value='^.titled',lbl='Titled field',validate_case='t')
        fb.textbox(value='^.fiscal_code',lbl='Uppercased + precise length field [16]',validate_len='16',validate_case='u')
        fb.textBox(value='^.short',lbl='Short string [<=5]',validate_len=':5')
        fb.textBox(value='^.long',lbl='Long string [>=6]',validate_len='6:',
                   validate_onReject='alert("The string "+"\'"+value+"\'"+" is too short")')
        fb.textBox(value='^.email_error',lbl="Email validation + error",
                   validate_email=True,validate_onAccept='alert("Correct email format")',validate_notnull=True)
        fb.textBox(value='^.email_warning',lbl="Email validation + warning",
                   validate_email=True,validate_email_warning='Uncorrect email format')
        fb.textbox(value='^.notnull',lbl='Notnull validation',
                   validate_notnull=True)
        fb.textbox(value='^.empty',lbl='Empty validation',
                   validate_empty=True)
    #    fb.textBox(value='^.email2',lbl="secondary email",
    #               validate_remote=pippo,
    #               validate_remote_niso='3',
    #               validate_remote_warning='Uncorrect email format')
    #    fb.div('warning on wrong insertion')
    #    
    #def remote_pippo(self,niso):
        
        