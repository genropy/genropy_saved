# -*- coding: UTF-8 -*-

# dropdownbutton.py
# Created by Niso on 2010-09-01.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Dropdownbutton"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    """
    ================
     Dropdownbutton
    ================
    
    .. currentmodule:: widgets

    .. class:: dropdown buttons -  Genropy dropdown buttons
    
    ???TO DO!!!!
    """
        
        #   - Other forms and attributes:
        #       In this section we report forms/attributes that have been used in this example
        #       despite they didn't strictly belonging to button.
        #       We also suggest you the file (if it has been created!) where you can find
        #       some documentation about them.
        #
        #       ## name ##      --> ## file ##
        #       datapath        --> datapath.py
        #       formbuilder     --> formbuilder.py
        #       menu            --> menu.py
        #       menuline        --> menu.py
        #       numberTextbox   --> textbox.py
        #       textbox         --> textbox.py
        #       value           --> datapath.py

    def test_1_dropdownbutton(self,pane):
        """Dropdown button"""
        pane.div(""" Here we show you an example of dropdown button, using also "action" attribute
                (for further details, check "menu.py").""",
                font_size='.9em',text_align='justify')
        ddb=pane.dropdownbutton('Menù')
        dmenu=ddb.menu()
        dmenu.menuline('Open...', action="FIRE msg='Opening!';")
        dmenu.menuline('Close', action="FIRE msg='Closing!';")
        dmenu.menuline('-')
        submenu=dmenu.menuline('I have submenues').menu()
        submenu.menuline('To do this', action="alert('Doing this...')")
        submenu.menuline('Or to do that', action="alert('Doing that...')")
        dmenu.menuline('-')
        dmenu.menuline('Quit',action="alert('Quitting...')")