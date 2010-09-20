# -*- coding: UTF-8 -*-

# dropdownbutton.py
# Created by Niso on 2010-09-01.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Dropdownbutton"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    """
    =================
     dropdownbuttons
    =================

    .. currentmodule:: form

    .. class:: dropdownbuttons -  Genropy dropdownbuttons

    **Definition**: same definition of Dojo dropdownbuttons (version 1.5). To show it, click here_.

    .. _here: http://docs.dojocampus.org/dijit/form/DropDownButton

    .. method:: dropdownbutton(label)

    	Constructs a button that opens a ``menu`` or a ``tooltipdialog``.

    		Example::

    			def ddButtonPane(self, cp):
    				dd = cp.dropdownbutton('test')
    				dd.tooltipdialog().div('Hello, world!')
    """
    
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