# -*- coding: UTF-8 -*-

# validations.py
# Created by Filippo Astolfi on 2011-03-29.
# Copyright (c) 2011 Softwell. All rights reserved.

"""Validations"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_0_form(self,pane):
        """Validations"""
        fb = pane.formbuilder(cols=2,lbl_color='teal')
        fb.div('In this example we explain you the Genro validations',
                text_align='justify',colspan=2)
        fb.textbox(value='^.no_val',lbl='no validations here')
        fb.div("""This is a simple field: you can write anything, there is no
                  validation that check any type of correct form""",
                  font_size='0.9em',text_align='justify')
        fb.div("""The following three fields are not basic validations: they check
                  if their condition is satisfied, and if not, they correct
                  the value (so they will not give any kind of error).""",
                  text_align='justify',colspan=2)
        fb.textbox(value='^.capitalized',lbl='validate_case=\'c\'',validate_case='c')
        fb.div('Correct the field if it is not capitalized into a capitalized value',
                font_size='0.9em',text_align='justify')
        fb.textbox(value='^.lowercased',lbl='validate_case=\'l\'',validate_case='l',
                   validate_notnull=True,validate_notnull_error='!!Required field')
        fb.div('Correct the field if it is not lowercased into a lowercased value',
                font_size='0.9em',text_align='justify')
        fb.textbox(value='^.titled',lbl='validate_case=\'t\'',validate_case='t')
        fb.div('Correct the field if it is not titled into a titled value',
                font_size='0.9em',text_align='justify')
        fb.div("""From now on the fields have real validations: if you don't satisfy
                  rightly their condition, the border field will become red and when
                  you return on the uncorrected field, you will get an hint on your
                  error through a tip (or a tooltip)""",
                  text_align='justify',colspan=2)
        fb.textbox(value='^.fiscal_code',lbl='validate_len=\'16\' validate_case=\'u\'',
                   validate_len='16',validate_case='u',
                   validate_len_error="""Wrong lenght: the field accept only a string
                                         of 16 characters""")
        fb.div("""This field have a precise lenght string (16 characters) to satisfy.
                  In addition, there is an uppercase validation""",
                  font_size='0.9em',text_align='justify')
        fb.textBox(value='^.short',lbl='validate_len=\':5\'',validate_len=':5')
        fb.div('In this field you have to write a string with 5 characters max',
                font_size='0.9em',text_align='justify')
        fb.textBox(value='^.long',lbl='validate_len=\'6:\'',validate_len='6:',
                   validate_onReject='alert("The string "+"\'"+value+"\'"+" is too short")')
        fb.div('In this field you have to write a string with 6 characters or more',
                font_size='0.9em',text_align='justify')
        fb.textBox(value='^.email_error',lbl="validate_email=True",
                   validate_email=True,validate_onAccept='alert("Correct email format")')
        fb.div('This field validate an email string with regex.',
                font_size='0.9em',text_align='justify')
        fb.textBox(value='^.email_warning',lbl="validate_email=True (warning)",
                   validate_email=True,validate_email_warning='Uncorrect email format')
        fb.div("""This field validate an email string with regex. On user error,
                  the \"validate_email_warning\" don't prevent the form to be correct.""",
                  font_size='0.9em',text_align='justify')
        fb.textbox(value='^.notnull',lbl='validate_notnull=True',
                   validate_notnull=True)
        fb.div('This validation ...add???',
                font_size='0.9em',text_align='justify')
        fb.textbox(value='^.empty',lbl='validate_empty=True',
                   validate_empty=True)
        fb.div('This validation ...add???',
                font_size='0.9em',text_align='justify')
        #fb.textBox(value='^.email2',lbl="secondary email",
        #           validate_remote_warning='Uncorrect email format')
        #fb.div('warning on wrong insertion',
        #        font_size='0.9em',text_align='justify')
        
        # add??? Add the remote validations...
                