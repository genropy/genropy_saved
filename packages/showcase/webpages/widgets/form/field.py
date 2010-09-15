# -*- coding: UTF-8 -*-

# field.py
# Created by Niso on 2010-09-15.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Field"""

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    """ "Field" is used to view data included in a database (and, eventually, is used to modify them).
    Its type is defined from data that you request (for example if field catches data from a numberTextbox,
    its type is actually a numberTextbox, and so on).
    
    - MANDATORY formbuilder and datapath:
        Field MUST be a formbuilder's son, and formbuilder itself MUST have a datapath (for inner relative path
        gears);
        
        example:
            def main(self,root,**kwargs):
                fb = root.formbuilder(datapath='myform')
                fb.field()
    
    - field's attribute:
        - name of column (MANDATORY):
        The first parameter is the name of the column. You have to specify the route folder; for doing this you
        have two options:
        
            1) 'tableName.fileModelName.columnName'
            This is the COMPLETE sintax, and this allows to not specify a maintable of the webpage.
            
            example:
                def main(self,root,**kwargs):
                    fb = root.formbuilder(datapath='myform')
                    fb.field('showcase.cast.person_id')
                    
                    "showcase" is the package name, "cast" is the database file name (that lies in
                    model folder) and "person_id" is the field to which we are referring.
            
            2) 'columnName'
            This is the SHORTER sintax; for using this you have to specify the main table to which formbuilder
            will be linked.
            
            example:
                maintable='showcase.table'
                
                def main(self,root,**kwargs):
                    fb = root.formbuilder(datapath='myform')
                    fb.field('person_id')
        
        - lbl: "lbl" is properly a formbuilder's son attribute, so "field" inherit from it. If you don't specify
        it, Field will take the "name_long"" attribute of the requested data.
        - limit (default=10): The max number of rows displayed in a field as response to user request.
        The last line is always a line with no characters, so user can choose it to undo his request.
        
        - zoom:
        With zoom attribute you can move yourself to the database page and you can modify the database.???GIUSTO?
        The default is: "True".
        zoomURL ???
        
        - rowcaption:
        ???
        
    """
    
    #   - Other forms, attributes and items:
    #       In this section we report forms/attributes that have been used in this example
    #       despite they didn't strictly belonging to ???.
    #       We also suggest you the file (if it has been created!) where you can find
    #       some documentation about them.
    #
    #       ## name ##          --> ## file ##
    #       datapath            --> webpages/tutorial/datapath.py
    #       formbuilder         --> formbuilder.py
    #       lbl                 --> formbuilder.py
    
    def test_1_basic(self,pane):
        """Basic field"""
        pane.div("""In this basic test you see a simple field.""",
                 font_size='.9em',text_align='justify')
        pane.div("""1) Search for file model from which field draws going "in showcase/model/cast.py",
                 and search for the column labeled as "person_id".""",
                 font_size='.9em',text_align='justify')
        pane.div("""2) It looks like there is a "lbl" attribute, but if you see in the code you won't find it.
                 That's because if "lbl" is not defined, then field takes the label directly from file model.""",
                 font_size='.9em',text_align='justify')
        fb = pane.formbuilder(datapath='test1',cols=2)
        fb.field('showcase.cast.person_id',zoom=False)
        pane.div("""The sintax of this field is "fb.field('showcase.cast.person_id',zoom=False)", but you could
                 write "fb.field('person_id',zoom=False)", adding in the file requirments the following line:
                 "maintable='showcase.cast'". So it's your choice to specify the main table at the beginning of
                 the code, or to specify it in the sintax of field ("showcase.cast").""",
                 font_size='.9em',text_align='justify')
        
        