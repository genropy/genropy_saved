# -*- coding: UTF-8 -*-
"""dbCombobox"""

from tutorlib import example

class GnrCustomWebPage(object):
    py_requires = "examplehandler:ExampleHandlerFull"



    @example(code=1,height=350,description='dbComboBox')
    def dbCombobox(self, pane):
        """Basic dbCombobox"""
        fb = pane.formbuilder()

        fb.dbCombobox(dbtable='gnrtutor.person', value='^.name_full',lbl='Artist',hasDownArrow=True)
        fb.dbCombobox(dbtable='gnrtutor.music', value='^.movie',lbl='Title', width='25em',hasDownArrow=True)



    def doc_dbCombobox(self, pane):
        """In a \"dbCombobox\" you populate the menu from record values in a database and save the value and not the 'ID'
of the record.
        
With a dbSelect, the menu is populated with the record values, but the ID is saved.

With a dbComboBox you have the possibility to type a value that is not in the table that populates the menu

For example, try to draw an actor from the first "dbCombobox"...
... and then write a film not in the database.
After that, check your saved records in the datasource.  You will find the new values have not been added.
"""