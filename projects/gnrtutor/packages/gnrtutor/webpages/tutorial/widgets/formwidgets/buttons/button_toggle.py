# -*- coding: UTF-8 -*-


"""Toggle Button Example"""

from tutorlib import example
class GnrCustomWebPage(object):
    py_requires = "examplehandler:ExampleHandlerFull"


    @example(code=1,height='200',description='Slot Button')
    def togglebutton(self,pane):
        fb = pane.formbuilder(cols=2)     
        fb.togglebutton(value='^.toggle', iconClass="dijitRadioIcon", label='A togglebutton')
        fb.textBox(value='^.toggle',lbl='toggle value')

    def doc_togglebutton(self):
        """A toggle button alternates its value stored in the datastore between true and false, with repeated clicks.
We can display the value in a textBox by having an 'observer' (^) at the datastore path of the value.

A toggle button takes as its parameters
i. value - being the path in the datastore to the bag that will store the value true or false.
ii. iconClass.  In this example we use a dojo css class that defines the path to two radio buttons
iii. Label - the label of the button
"""

