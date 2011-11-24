# -*- coding: UTF-8 -*-
"""dbCombobox"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_basic(self, pane):
        """Basic dbCombobox"""
        fb = pane.formbuilder(datapath='test1_movie')
        fb.div("""In a "dbCombobox" you can draw record values from a database (not the ID!).
                  The difference with the "dbSelect" is the possibility to add NEW records.""",
                  font_size='.9em', text_align='justify')
        fb.div('For example, try to draw an actor from the first "dbCombobox"...',
                font_size='.9em', text_align='justify')
        fb.dbCombobox(dbtable='showcase.person', value='^.person', lbl='Star')
        fb.div('... and then write a film not in the database.',
               font_size='.9em', text_align='justify')
        fb.dbCombobox(dbtable='showcase.movie', value='^.movie', lbl='Movie')
        fb.div("""After that, check in the datasource your saved records (by clicking
                  ctrl+shift+D)""", font_size='.9em', text_align='justify')