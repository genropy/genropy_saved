# -*- coding: UTF-8 -*-

"""Radio Button Examples"""

from tutorlib import example
class GnrCustomWebPage(object):
    py_requires = "examplehandler:ExampleHandlerFull"


    @example(code=1,height=150,description='textbox')
    def textbox(self, pane):
        fb = pane.formbuilder()
        fb.textBox(lbl='Name', value='^.name')

    def doc_textbox(self):
        """The standard text box is able to receive any character from the keyboard. Validations can be applied.  For example
validation='uppercase'
"""


    @example(code=2,height=150,description='currencyTextbox')
    def currency(self, pane):
        fb = pane.formbuilder()
        fb.currencyTextBox(lbl='Amount', value='^.amount', currency='EUR', locale='it')

    def doc_currency(self):
        """The currencyTextbox widget will only allow numbers. You can set the currency and the locale.
It expects input to include either no cents or 2 digits for cents.
It will not accept letters.  A validation error will occur.
"""

    @example(code=3,height=150,description='dateTextbox')
    def datetextbox(self, pane):
        fb = pane.formbuilder()
        fb.dateTextbox(value='^.date', lbl='Date')
    def doc_datetextbox(self,pane):
        """You can enter a date or click on the icon to display the date widget.  You can set the parameter popup=False
to remove the date icon that invokes the date calendar.  By default it is True.
"""

    @example(code=4,height=150,description='numberTextbox')
    def numberTextbox(self, pane):
        fb = pane.formbuilder()
        fb.numberTextBox(value='^.number', lbl='Number', places=3)

    def doc_numberTextbox(self):
        """The numberTextbox widget will only allow numbers. Any trailing zeros in the display will be removed.
It will not accept letters.  A validation error will occur (and a record will not be able to be saved
if the data entered is not valid).

The parameter places=3 means that this number text box MUST have a number with 3 decimal places else a validation error will occur.
"""

    @example(code=5,height=200,description='timeTextbox')
    def timeTextbox(self, pane):
        fb = pane.formbuilder()
        fb.timeTextBox(value='^.timeTextbox', lbl='Appointment')

    def doc_timeTextbox(self):
        """The timeTextbox widget provides an grahical interface to set time. You can either type directly or select from the widget.
The data entered must be in an acceptable format or a validation error will occur. eg. 8:00 PM
"""

    @example(code=6,height=200,description='textbox')
    def textbox2(self, pane):
        fb = pane.formbuilder()
        fb.textBox(value='^.textbox', lbl='speech entry',speech=True)

    def doc_textbox2(self):
        """Any text box can contain the parameter speech=True.  This takes advantage of chrome version 9's speech recnognition.
By clicking the icon you can then speak and the text will be dictated.
"""