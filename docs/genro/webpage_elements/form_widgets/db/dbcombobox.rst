.. _dbcombobox:

==========
dbCombobox
==========
    
    *Last page update*: |today|
    
    .. note:: dbCombobox features:
              
              * **Type**: :ref:`Genro form widget <genro_widgets>`
              * **Common attributes**: you can check:

                  * the :ref:`widget common attributes section <attributes_index>`
                  * the :ref:`dbSelect and dbCombobox common attributes section <db_attributes>`
                  
    * :ref:`dbcombobox_def`
    * :ref:`dbcombobox_examples`

.. _dbcombobox_def:

Definition and Description
==========================

    .. method:: pane.dbcombobox([**kwargs])
    
    The Genro ``dbCombobox`` is a :ref:`combobox` that conducts research on specific columns in a database
    table. While user write in the dbCombobox, partially matched values will be shown in a pop-up menu below
    the input text box. The ``dbCombobox`` has got the same parameters of the :ref:`dbselect`, and allows
    to choose from values situated in the database AND from values that aren't in the database. These "new"
    values aren't added in the database but they have being placed in the :ref:`datastore`, so they can be
    handled from Genropy. [#]_
    
    To specify the table related to the dbCombobox you have to use the mandatory :ref:`dbtable` attribute.
    
.. _dbcombobox_examples:

Examples
========

    Let's see a code example::
        
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb=root.formbuilder(datapath='test1')
                fb.div("""In a "dbCombobox" you can draw record values from a database (not the ID!).
                          The difference with the "dbSelect" is the possibility to add NEW records.""")
                fb.div('For example, try to draw an actor from the first "dbCombobox"...')
                fb.dbCombobox(dbtable='showcase.person',value='^.person',lbl='Star')
                fb.div('... and then write a film not in the database.')
                fb.dbCombobox(dbtable='showcase.movie',value='^.movie',lbl='Movie')
                fb.div('After that, check in the datasource your saved records')

**Footnotes**

.. [#] We remember to you that ``dbCombobox`` supports only the values (not the keys!); so the main ``dbCombobox`` feature is that it permits to enter values in the :ref:`datastore`, but they won't be stored in the database.