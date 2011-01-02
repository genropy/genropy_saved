# -*- coding: UTF-8 -*-

# dropdownbutton.py
# Created by Filippo Astolfi on 2010-09-01.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Dropdownbutton"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage

    def test_1_dropdownbutton(self, pane):
        """Dropdown button"""
        pane.div(""" Here we show you an example of dropdown button, using also "action" attribute
                (for further details, check "menu.py").""",
                 font_size='.9em', text_align='justify')
        ddb = pane.dropdownbutton('Menù')
        dmenu = ddb.menu()
        dmenu.menuline('Open...', action="FIRE msg='Opening!';")
        dmenu.menuline('Close', action="FIRE msg='Closing!';")
        dmenu.menuline('-')
        submenu = dmenu.menuline('I have submenues').menu()
        submenu.menuline('To do this', action="alert('Doing this...')")
        submenu.menuline('Or to do that', action="alert('Doing that...')")
        dmenu.menuline('-')
        dmenu.menuline('Quit', action="alert('Quitting...')")