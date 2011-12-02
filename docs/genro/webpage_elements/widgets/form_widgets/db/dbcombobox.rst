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
    * :ref:`dbcombobox_examples`:
    
        * :ref:`dbcombobox_examples_simple`
        
.. _dbcombobox_def:

definition and description
==========================

    .. method:: pane.dbcombobox([**kwargs])
    
    The Genro ``dbCombobox`` is a :ref:`combobox` that conducts research on specific columns in a
    :ref:`database table <table>`. While user write in the dbCombobox, partially matched values will be
    shown in a pop-up menu below the input text box. The ``dbCombobox`` has got the same parameters of
    the :ref:`dbselect`, and allows to choose from values situated in the database AND from values that
    aren't in the database.
    
    The difference with the dbSelect is that the dbSelect allows to choose between records saved in a
    table through their IDs, while the dbCombobox allows to select a column of the record, not the
    complete record.
    
    To specify the table related to the dbCombobox you have to use the mandatory :ref:`dbtable` attribute
    
.. _dbcombobox_examples:

examples
========

.. _dbcombobox_examples_simple:

simple example
--------------

    * `dbComboBox [basic] <http://localhost:8080/webpage_elements/widgets/form_widgets/dbCombobox/1>`_
    
      .. note:: 
      
                #. Pay attention not to confuse *value* with *values*: *value* is used to allocate user
                   data in a well determined :ref:`datapath`, while *values* is used to fill the comboBox
                   
                #. Example elements' list:
                
                   * **classes**: :ref:`gnrcustomwebpage`
                   * **components**: :ref:`testhandlerfull`
                   * **webpage variables**: :ref:`webpages_py_requires`
                   * **widgets**: :ref:`formbuilder`
                   
    * **Code**::
    
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