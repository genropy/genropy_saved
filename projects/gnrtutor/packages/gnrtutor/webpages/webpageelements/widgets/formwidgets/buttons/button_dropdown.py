# -*- coding: UTF-8 -*-


"""Buttons Examples Advanced"""

from tutorlib import example
class GnrCustomWebPage(object):
    py_requires = "examplehandler:ExampleHandlerFull"


    @example(code=1,height='200',description='A dropdownbutton with a label')
    def dropdown1(self,pane):
        fb = pane.formbuilder(margin='5px')
        ddb = fb.dropdownbutton(label='Save')
        dmenu = ddb.menu()
        dmenu.menuline('Save', action="alert('Saved')")
        dmenu.menuline('Save as...', action="alert('Saved as...')")

    def doc_dropdown1(self):
        """The DropDownButton is usually used to display a menu items so we use it in conjunction with menu.
In order to create the menu, you must reference the dropdownbutton object, then call the menu() function on it.
You then can make multiple calls on the menu object.
"""


    @example(code=1,height='250',description='DropDownButton with iconClass attribute')
    def dropdown2(self,pane):
        fb = pane.formbuilder(margin='5px')
        ddb = fb.dropdownbutton(label='Load', height='30px', width='7em', iconClass='iconbox storage')
        dmenu = ddb.menu()
        dmenu.menuline('Load template', action="alert('Loaded from template')")
        dmenu.menuline('Load from file', action="alert('Loaded from file')")

    def doc_dropdown2(self):
        """You can also give to the dropdownbutton the iconClass attribute and CSS attributes (like in this case, the\"height\" attribute)"""
        