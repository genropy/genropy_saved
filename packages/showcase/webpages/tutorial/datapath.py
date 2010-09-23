# -*- coding: UTF-8 -*-

# datapath.py
# Created by Niso on 2010-09-06.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Datapath"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    """ Datapath is an attribute used to create a hierarchy of your data's addresses.
    You can give "datapath" attribute to each object (widget, etc), but it is useful give this attribute only to the
    objects that contain other object (let's call them "containers").
    
    Let's see an example:
        box = pane.div(datapath='father')   (this div is the father, and datapath carries an absolute path)
        box.textbox(value='^.son')          (this textbox is the son)
        
    If you want to create a son with an absolute path, you simply mustn't write the dot at the
    beginning of son's datapath, like:
        box.textbox(value='^.another_son',datapath='father_2') (this datapath will have an absolute path)
        
    You can also create a datapath with a relative path; for doing this you have to put the dot at
    the beginning of son's datapath, like:
        box.textbox(value='^.another_son',datapath='.father_2') (this datapath will inherit from the previous datapath)
                                                                
    Pay attention to not create a relative path without an absolute path as father!"""
    
    #   - attributes of datapath's sons:
    #       value: set item's address.
    #
    #   - Other forms, attributes and items:
    #       In this section we report forms/attributes that have been used in this example
    #       despite they didn't strictly belonging to datapath.
    #       We also suggest you the file (if it has been created!) where you can find
    #       some documentation about them.
    #
    #       ## name ##      --> ## file ##
    #       datasource      --> datasource.py
    #       textbox         --> textbox.py
    
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
                 