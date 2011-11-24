# -*- coding: UTF-8 -*-

# validations.py
# Created by Filippo Astolfi on 2011-03-29.
# Copyright (c) 2011 Softwell. All rights reserved.

"""Validations"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_0_form(self,pane):
        """Validations"""
        fs='1.2em'
        fs_small='1em'
        ta='justify'
        fb = pane.formbuilder(cols=2,lbl_color='teal')
        fb.textbox(value='^.no_val',lbl='no validations here')
        fb.div("""This is a simple field: you can write anything, there is no
                  validation that check any type of correct form""",
                  font_size=fs_small,text_align=ta)
        fb.div("""The following four validations check if their condition is satisfied,
                  and if not, they correct the value (so they will not give any kind of error).""",
                  font_size=fs,text_align=ta,colspan=2)
        fb.textbox(value='^.c',lbl='validate_case=\'c\'',validate_case='c')
        fb.div('Correct the field if it is not capitalized into a capitalized value',
                font_size=fs_small,text_align=ta)
        fb.textbox(value='^.u',lbl='validate_case=\'u\'',validate_case='u')
        fb.div('Correct the field if it is not uppercased into a uppercased value',
                font_size=fs_small,text_align=ta)
        fb.textbox(value='^.l',lbl='validate_case=\'l\'',validate_case='l',
                   validate_notnull=True,validate_notnull_error='!!Required field')
        fb.div('Correct the field if it is not lowercased into a lowercased value',
                font_size=fs_small,text_align=ta)
        fb.textbox(value='^.t',lbl='validate_case=\'t\'',validate_case='t')
        fb.div('Correct the field if it is not titled into a titled value',
                font_size=fs_small,text_align=ta)
        fb.div("""From now on the fields have real validations: if you don't satisfy
                  rightly their condition, the border field will become red and when
                  you return on the uncorrected field, you will get an hint on your
                  error through a tip (or a tooltip)""",
                  font_size=fs,text_align=ta,colspan=2)
        fb.textbox(value='^.fiscal_code',lbl='validate_len=\'16\'',
                   validate_len='16',
                   validate_len_error="""Wrong lenght: the field accept only a string
                                         of 16 characters""")
        fb.div("""This field have a precise lenght string (16 characters) to satisfy.
                  In addition, there is an uppercase validation""",
                  font_size=fs_small,text_align=ta)
        fb.textBox(value='^.short',lbl='validate_len=\':5\'',validate_len=':5')
        fb.div('In this field you have to write a string with 5 characters max',
                font_size=fs_small,text_align='justify')
        fb.textBox(value='^.long',lbl='validate_len=\'6:\'',validate_len='6:',
                   validate_onReject='alert("The string "+"\'"+value+"\'"+" is too short")')
        fb.div('In this field you have to write a string with 6 characters or more',
                font_size=fs_small,text_align=ta)
        fb.textBox(value='^.email_error',lbl="validate_email=True",
                   validate_email=True,validate_onAccept='alert("Correct email format")')
        fb.div('This field validate an email string with regex.',
                font_size=fs_small,text_align=ta)
        fb.textBox(value='^.email_warning',lbl="validate_email=True (warning)",
                   validate_email=True,validate_email_warning='Uncorrect email format')
        fb.div("""This field validate an email string with regex. On user error,
                  the \"validate_email_warning\" don't prevent the form to be correct.""",
                  font_size=fs_small,text_align=ta)
        fb.textbox(value='^.notnull',lbl='validate_notnull=True',
                   validate_notnull=True)
        fb.div('A mandatory field', font_size=fs_small,text_align=ta)