# -*- coding: UTF-8 -*-

"""Radio Button Examples"""

from tutorlib import example
class GnrCustomWebPage(object):
    py_requires = "examplehandler:ExampleHandlerFull"


    @example(code=1,height=350,description='Textbox')
    def currency(self, pane):
        fb = pane.formbuilder()
        fb.TextBox(lbl='Name', value='^.name', currency='EUR', locale='it')

    def doc_currency(self):
        """The currencyTextbox widget will only allow numbers.
It will not accept letters.  A validation error will occur and a record will not be able to be saved,
if the data entered is not valid.
"""

    @example(code=1,height=350,description='currencyTextbox')
    def currency(self, pane):
        fb = pane.formbuilder()
        fb.currencyTextBox(lbl='Amount', value='^.amount', currency='EUR', locale='it')

    def doc_currency(self):
        """The currencyTextbox widget will only allow numbers.
It will not accept letters.  A validation error will occur and a record will not be able to be saved,
if the data entered is not valid.
"""
