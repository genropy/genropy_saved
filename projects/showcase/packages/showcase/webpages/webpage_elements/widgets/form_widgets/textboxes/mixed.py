# -*- coding: UTF-8 -*-
"""Mixed"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_basic(self, pane):
        """Textboxes"""
        fb = pane.formbuilder(fld_width='18em', cols=2)
        fb.textBox(value='^.name', lbl='Name')
        fb.div('textBox')
        fb.textBox(value='^.surname', lbl='Surname')
        fb.div('textBox')
        fb.dateTextbox(value='^.birthday', lbl='Birthday')
        fb.div('dateTextbox')
        fb.dateTextBox(value='^.date', popup=False, lbl='Date (no popup)',
                       tooltip='remember: date format depends on your \"locale\" browser setting')
        fb.div('dateTextbox')
        fb.numberTextBox(value='^.age', lbl='Age')
        fb.div('numberTextbox')
        fb.textBox(value='^.text', lbl='Text')
        fb.div('textbox')