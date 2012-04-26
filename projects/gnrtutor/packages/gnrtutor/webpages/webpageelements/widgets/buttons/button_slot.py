# -*- coding: UTF-8 -*-


"""Slot Button Example"""

from tutorlib import example
class GnrCustomWebPage(object):
    py_requires = "examplehandler:ExampleHandlerFull"


    @example(code=1,height='200',description='Slot Button')
    def slotbutton(self,pane):
        fb = pane.formbuilder(cols=3)
        fb.slotButton('I\'m the label, but I work as a tooltip', iconClass="icnBuilding", action='alert("Hello!")',colspan=2)

    def doc_slotbutton(self):
        """This is the standard usage of a slotButton: the label works as a tooltip. 
"""