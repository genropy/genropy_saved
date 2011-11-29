# -*- coding: UTF-8 -*-
"""dbCombobox"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_basic(self, pane):
        """Basic dbCombobox"""
        fb = pane.formbuilder()
        fb.div("""In a \"dbCombobox\" you can draw record values from a database (not the ID!).
                  The difference with the "dbSelect" is the possibility to type values
                  that don't belong to """)
        fb.div('For example, try to draw an actor from the first \"dbCombobox\"...')
        fb.dbCombobox(dbtable='showcase.person', value='^.person',
                      lbl='Artist')
        fb.div('... and then write a film not in the database.')
        fb.dbCombobox(dbtable='showcase.music', value='^.movie',
                      lbl='Title', width='25em')
        fb.div('After that, check in the datasource your saved records')