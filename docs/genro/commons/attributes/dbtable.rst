.. _genro_dbtable:

=========
 dbtable
=========

    * :ref:`dbtable_def`
    * :ref:`dbtable_examples`

.. _dbtable_def:

Definition and description
==========================

    ::
    
        dbtable = None
        
    The *dbtable* attribute is used to specify a path for a database :ref:`genro_database_table` during a user query.
    
    The syntax is ``packageName.tableName.attributeName``, where:
    
        * ``packageName`` is the name of the package on which you're working [#]_ ;
        * ``tableName`` is the name of the :ref:`genro_database_table` on which is executed the user query.
        
    **Validity:** the *dbtable* attribute works on the following form widgets:
    
        * :ref:`genro_formbuilder`
        * :ref:`genro_field`
        * :ref:`genro_dbselect`
        * :ref:`genro_dbcombobox`

.. _dbtable_examples:

Examples
========

    Based on the form widget you're working on, there is a different use of *dbtable*:
    
        * For the :ref:`genro_formbuilder` and the :ref:`genro_field` form widgets, please check the :ref:`genro_field` page.
        * For the :ref:`genro_dbselect` and the :ref:`genro_dbcombobox` form widgets, please check the dbSelect and dbCombobox :ref:`db_examples` page.

**Footnotes:**

.. [#] For more information on a package, check the :ref:`genro_packages_index` paragraph.