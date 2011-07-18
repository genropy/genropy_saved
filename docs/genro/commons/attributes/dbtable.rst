.. _genro_dbtable:

=======
dbtable
=======

    * :ref:`dbtable_def`
    * :ref:`dbtable_syntax`
    * :ref:`dbtable_validity`
    * :ref:`dbtable_examples`

.. _dbtable_def:

definition and description
==========================

    ::
    
        dbtable = 'STRING'
        
    The *dbtable* attribute belongs to many :ref:`genro_webpage_elements_intro` and
    it is used to specify the :ref:`genro_table` to which the webpage elements is
    linked.
    
    If you have defined in your :ref:`webpages_webpages` a :ref:`webpages_maintable`,
    then you have a default ``dbtable`` value for all the elements of your page.
    Obviously, if you have a maintable AND a dbtable value, the dbtable value will
    prevail on the maintable value.
    
.. _dbtable_syntax:

syntax
======
    
    ::
    
        dbtable='packageName.tableName.columnName'
        
    where:
    
    * ``packageName`` is the name of the :ref:`package <genro_packages_index>` on which you're working;
    * ``tableName`` is the name of the :ref:`genro_table` on which is executed the user query;
    * ``columnName`` is the name of the database :ref:`table_column`.
    
    .. note:: you can omit the ``packageName`` if the dbtable is used on a :ref:`webpages_webpages` that
              belongs to the package you should specify.
        
.. _dbtable_validity:

validity
========
    
    the *dbtable* attribute works on:
    
    * :ref:`genro_dbcombobox`
    * :ref:`genro_dbselect`
    * :ref:`genro_field`
    * :ref:`genro_formbuilder`
    
.. _dbtable_examples:

examples
========

    Based on the form widget you're working on, there is a different use of *dbtable*:
    
        * For the :ref:`genro_formbuilder` and the :ref:`genro_field` form widgets,
          please check the :ref:`genro_field` page.
        * For the :ref:`genro_dbselect` and the :ref:`genro_dbcombobox` form widgets,
          please check the dbSelect and dbCombobox :ref:`db_examples` page.