# -*- coding: UTF-8 -*-

# dropdownbutton.py
# Created by Niso on 2010-09-28.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Dropdownbutton"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    """
    =================
     dropdownbuttons
    =================
    
    SEE DROPDOWNBUTTON.RST
    
    """
    
    def test_1_dropdownbutton(self,pane):
        """Dropdown button"""
        #pane.div(""" Here we show you an example of dropdown button, using also "action" attribute
        #        (for further details, check "menu.py").""",
        #        font_size='.9em',text_align='justify')
        ddb=pane.dropdownbutton(label='Menù')
        dmenu=ddb.menu()
        dmenu.menuline('Open...',action="alert('Opening...')")
        dmenu.menuline('Close',action="alert('Closing...')")
        dmenu.menuline('-')
        submenu=dmenu.menuline('I have submenues').menu()
        submenu.menuline('To do this',action="alert('Doing this...')")
        submenu.menuline('Or to do that',action="alert('Doing that...')")
        dmenu.menuline('-')
        dmenu.menuline('Quit',action="alert('Quitting...')")