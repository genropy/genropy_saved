.. _dbselect:

========
dbSelect
========
    
    *Last page update*: |today|
    
    .. note:: dbSelect features:
              
              * **Type**: :ref:`Genro form widget <genro_form_widgets>`
              * **Common attributes**: you can check:
              
                * the :ref:`widget common attributes section <attributes_index>`
                * the :ref:`dbSelect and dbCombobox common attributes section <db_attributes>`
              
    * :ref:`dbselect_def`
    * :ref:`dbselect_examples`:
    
        * :ref:`dbselect_examples_simple`
        * :ref:`dbselect_examples_condition`

.. _dbselect_def:

Definition and Description
==========================

    .. method:: pane.dbSelect([**kwargs])
    
    dbSelect [#]_ is a :ref:`filteringselect` that takes the values through a query on the database [#]_.
    
    User can choose between all the values contained into the linked :ref:`table` (you have to specify
    the table from which user makes his selection), and dbSelect keep track into the :ref:`datastore`
    of the ID of the record chosen by the user.
    
    While user write in the dbSelect, partially matched values will be shown in a pop-up menu below the
    input text box.
    
    To specify the table related to the dbSelect you have to use the mandatory :ref:`dbtable` attribute.
    
.. _dbselect_examples:

Examples
========

.. _dbselect_examples_simple:

simple example
--------------

    Let's see a code example::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb=pane.formbuilder(datapath='test1',cols=2)
                fb.dbSelect(dbtable='showcase.person',rowcaption='$name',
                            value='^.person_id',lbl='Star')
                            
.. _dbselect_examples_condition:

condition example
-----------------

    add??? (an example with the condition...)
                            
**Footnotes**

.. [#] It should have been called "dbFilteringSelect", but it has been shortened in "dbSelect"
.. [#] To use dbSelect there must exist a database. For having information on a database creation, please check :ref:`tutorial_index`
