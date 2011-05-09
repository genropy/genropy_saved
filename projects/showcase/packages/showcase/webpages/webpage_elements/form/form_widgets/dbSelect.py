#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

"""dbSelect"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    def test_1_basic(self, pane):
        """Basic test"""
        fb = pane.formbuilder(cols=2, border_spacing='10px', datapath='test1')
        fb.div("""In this test you can see the basic funcionalities of the dbSelect attribute:
                  the "dbtable" attribute allows to search from a database table,""",
                  font_size='.9em', text_align='justify', colspan=2)
        fb.div("""saving the ID of the chosen record.""",
                  font_size='.9em', text_align='justify', colspan=2)
        fb.div('Star (value saved in "test1/person_id")',color='#94697C', colspan=2)
        fb.dbSelect(dbtable='showcase.person', value='^test1.person_id', limit=10, colspan=1)
        fb.div("""Default values for a dbSelect: limit=10 (number of viewed records scrolling the
                  dbSelect), hasDownArrow=False, ignoreCase""",
                  font_size='.9em', text_align='justify', colspan=1)
        fb.div('Star (value saved in "test1/person_id_2")',color='#94697C', colspan=2)
        fb.dbSelect(dbtable='showcase.person', value='^test1.person_id_2', hasDownArrow=True)
        fb.div("""The hasDownArrow=True override the limit=10, and let the user see all the entries""",
                  font_size='.9em', text_align='justify', colspan=1)
                    
    def test_2_selected(self, pane):
        """"Selected" attribute"""
        fb = pane.formbuilder(border_spacing='10px', datapath='test2')
        fb.div("""If you want to save some record attributes (in addition to the ID),
                you have to use the "selected" attribute:""",
               font_size='.9em', text_align='justify')
        fb.div("""check in datasource (ctrl+shift+D) the values added by your choice
                in the "name" and in the "year" folders.""",
               font_size='.9em', text_align='justify')
        fb.div("""Please note that "name" and "year" folders will be created
                AFTER you made your choice.""",
               font_size='.9em', text_align='justify')
        fb.dbSelect(dbtable='showcase.person', value='^.person_id', lbl='Star',
                    selected_name='.name', selected_year='.year')
                    
    def test_3_advanced(self, pane):
        """"Condition" attribute"""
        fb = pane.formbuilder(border_spacing='10px', datapath='test3')
        fb.div("""If you have created two or more database tables for a single entry,
                you can allows the user to choose a record for a first "dbSelect"... """,
               font_size='.9em', text_align='justify')
        fb.dbSelect(dbtable='showcase.person', value='^.person_id', lbl='Star',
                    selected_name='.selected_name', selected_year='.selected_year')#, auxColumns='$nationality')
        fb.div("""... and then you can make the user choose an attribute relative to the
                first record selected:""",
               font_size='.9em', text_align='justify')
        fb.dbSelect(dbtable='showcase.cast', value='^.movie_id', lbl='Movie',
                    condition='$person_id=:pid', condition_pid='=.person_id',
                    alternatePkey='movie_id')