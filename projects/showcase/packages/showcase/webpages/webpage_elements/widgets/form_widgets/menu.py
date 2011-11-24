# -*- coding: UTF-8 -*-
"""menu"""

class GnrCustomWebPage(object):
    py_requires = 'gnrcomponents/testhandler:TestHandlerFull'
    
    def test_1_basic(self,pane):
        """simple menu"""
        fb = pane.formbuilder(cols=3)
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
        
    def test_2_alert(self, pane):
          """menu with alert attribute"""
          menudiv = pane.dropdownbutton('Menu')
          menu = menudiv.menu(action='alert($1.foo)')
          menu.menuline('menuline n.1', foo=36)
          menu.menuline('I\'m disabled', foo=60, disabled=True)
          menu.menuline('menuline n.3', action='alert("I\'m different")',checked=True)
          menu.menuline('-')
          submenu = menu.menuline('Sub').menu(action='alert("sub "+$1.bar)')
          submenu.menuline('submenuline n.1', bar=36)
          submenu.menuline('submenuline n.2', bar=60)