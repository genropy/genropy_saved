.. _genro_dbselect:

========
dbSelect
========

    * :ref:`dbselect_def`
    * :ref:`dbselect_attributes`
    * :ref:`dbselect_examples`

.. _dbselect_def:

Definition and Description
==========================

    .. method:: pane.dbSelect([**kwargs])
    
    dbSelect [#]_ is a :ref:`genro_filteringselect` that takes the values through a query on the database [#]_.
    
    User can choose between all the values contained into the linked :ref:`genro_database_table` (you have to specify the table from which user makes his selection), and dbSelect keep track into the :ref:`genro_datastore` of the ID of the record chosen by the user.
    
    While user write in the dbSelect, partially matched values will be shown in a pop-up menu below the input text box.
    
    To specify the table related to the dbSelect you have to use the mandatory :ref:`genro_dbtable` attribute.
    
.. _dbselect_examples:

Examples
========

    Let's see a code example::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb=pane.formbuilder(datapath='test1',cols=2)
                fb.dbSelect(dbtable='showcase.person',rowcaption='$name',
                            value='^.person_id',lbl='Star')

.. _dbselect_attributes:

dbSelect attributes
===================

    For the list of dbSelect attributes, please check :ref:`db_genro_attributes`.

**Footnotes**

.. [#] It should have been called "dbFilteringSelect", but it has been shortened in "dbSelect".
.. [#] To use dbSelect there must exist a database. For having information on a database creation, please check :ref:`genro_simple_introduction`.
