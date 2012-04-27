# -*- coding: UTF-8 -*-
"""menu"""

from tutorlib import example
class GnrCustomWebPage(object):
    py_requires = "examplehandler:ExampleHandlerFull"


    @example(code='1',height=450,description='Simple Menu')
    def menu1(self,pane):
        fb = pane.formbuilder(cols=3,margin='5px')
        ddb = fb.dropdownbutton(iconClass='iconbox print', showLabel=False)
        dmenu = ddb.menu()
        dmenu.menuline('Print...', action="alert('Printing...')")
        dmenu.menuline('-')
        submenu = dmenu.menuline('Advanced options').menu() # With this line you create a submenu
        submenu.menuline('Preview', action="alert('Creating preview...')")
        submenu.menuline('PDF', action="alert('Making PDF...')")
        dmenu.menuline('-')
        dmenu.menuline('Cancel', action="alert('Abort print...')")

        ddb = fb.dropdownbutton('Save', iconClass='iconbox save')
        dmenu = ddb.menu()
        dmenu.menuline('Save', action="alert('Saved')")
        dmenu.menuline('Save as...', action="alert('Saved as...')")

        ddb = fb.dropdownbutton('Load', height='22px')
        dmenu = ddb.menu()
        dmenu.menuline('Load template', action="alert('Loaded')")
        dmenu.menuline('Load from file', action="alert('Loaded')")

    def doc_menu1(self):
        """This example shows that a menu item can have an action parameter.  This is the js that will be executed when the menu item
is selected.  In this example it is a simple alert, but of course you can use the macros FIRE, and SET.

There is an alternative syntax to get the parameter from the menu item and to have it trigger the action js parameter in the menu object.
"""



    @example(code='2',height=250,description='Menu and submenus. How to pass a parameter from the menu item to the menu')
    def menu2(self, pane):
          menudiv = pane.dropdownbutton('Menu')
          menu = menudiv.menu(action='alert($1.foo)')
          menu.menuline('menuline n.1', foo=36)
          menu.menuline('I\'m disabled', foo=60, disabled=True)
          menu.menuline('menuline n.3', action='alert("I\'m different")',checked=True)
          menu.menuline('-')
          submenu = menu.menuline('Sub').menu(action='alert("sub "+$1.bar)')
          submenu.menuline('submenuline n.1', bar=36)
          submenu.menuline('submenuline n.2', bar=60)

    def doc_menu2(self):
        """This example shows how to create the menu and furthermore the sub menu.  keyword parameter foo=36
will be passed to $1.foo in the menu object action javascript.
"""