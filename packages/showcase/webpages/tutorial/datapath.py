# -*- coding: UTF-8 -*-

# datapath.py
# Created by Filippo Astolfi on 2010-09-06.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Datapath"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    def test_1_basic(self,pane):
        """Standard datapath"""
        pane.div("""Simple example of datapath. In the first line "datapath='father'" is
        an absolute path; in the following two rows there are two textbox with
        a relative path linked to "father" ("value" attribute).
        The last four rows (that begins with "box2") described a similar example:
        even in this case the "datapath='job'" is an absolute path.
        Try to type something in textbox and retrieve it in Datasource (to open Datasource use 
        "SHIFT+CTRL+D".)""",
        font_size='.9em',text_align='justify')
        box = pane.div(datapath='father')
        box.textbox(value='^.son')
        box.textbox(value='^.son_2')
        pane.br()
        box2 = pane.div(datapath='job')
        box2.textbox(value='^.profession')
        box2.textbox(value='^.company_name')
        box2.textbox(value='^.fiscal_code')
        
    def test_2_abs_rel(self,pane):
        """Absolute and relative paths"""
        pane.div("""In this test you can see how datapath can build a relative path or an absolute
        path (use datasource).
        In the first two lines, like test_1, there is a datapath with an absolute path
        (datapath='goofy') and a son of the datapath (textbox with mario's value).
        In the third line we use datapath ('pancrazio') in a textbox with the meaning of
        absolute path, WHILE in the forth line we use datapath with the meaning of rela-
        tive path, and that's caused by the dot that precedes the address ('.luigi') """,
        font_size='.9em',text_align='justify')
        box = pane.div(datapath='goofy')
        box.textbox(value='^.mario')
        box.textbox(value='^.anthony',datapath='luigi')
        box.textbox(value='^.anthony',datapath='.luigi')
                 