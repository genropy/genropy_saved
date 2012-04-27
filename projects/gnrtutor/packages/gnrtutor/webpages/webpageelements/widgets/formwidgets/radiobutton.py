# -*- coding: UTF-8 -*-


"""Radio Button Examples"""

from tutorlib import example
class GnrCustomWebPage(object):
    py_requires = "examplehandler:ExampleHandlerFull"    
    
    @example(code='1',height=350,description='Radio Button')
    def radiobutton(self, pane):
        fb = pane.formbuilder(datapath='.radio', cols=1, margin='5px')

        fb.div("""We show you here a simple radio buttons set.
                  The "group" attribute is used to create radiobuttons related each other.""")
        fb.div("""You can specify a default selection with \"default_value=True\"""")
        fb.radiobutton(value='^.jazz', group='genre', label='Jazz',default_value=True)
        fb.radiobutton(value='^.rock', group='genre', label='Rock')
        fb.radiobutton(value='^.blues', group='genre', label='Blues')

        pane.div('Another group', margin_left='12px')
        fb2 = pane.formbuilder(datapath='.sex', cols=3, lbl_width='3em', fld_width='4em')
        fb2.div('Gender')
        fb2.radiobutton(value='^.male', group='gender', label='M', default_value=True)
        fb2.radiobutton(value='^.female', group='gender', label='F')

    def doc_radiobutton(self):
        """This example shows two simple radio buttons sets.
The "group" attribute is used to create radiobuttons related each other.

Note the use of datapath='.radio' in the formbuilder.  This datapath attribute in this example is a relative path (the dot prefix)
but you can use static paths or symbolic paths too.  The datapath is used to specify where the data will be stored in the hierarchical datastore bag.
"""

