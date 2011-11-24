.. _dbtable:

=======
dbtable
=======
    
    *Last page update*: |today|
    
    .. note:: **validity** - the *dbtable* attribute is supported by the following :ref:`form_widgets`:
              
              * :ref:`dbcombobox`
              * :ref:`dbselect`
              * :ref:`field`
              * :ref:`formbuilder`
              
    * :ref:`dbtable_def`
    * :ref:`dbtable_syntax`
    * :ref:`dbtable_examples`

.. _dbtable_def:

definition and description
==========================

    The *dbtable* attribute is used to specify the database :ref:`table` to which
    the object including the *dbtable* attribute belongs to.
    
    * To define a default ``dbtable`` value for all the elements of your page that supports
      it you can use the :ref:`webpage variable <webpages_variables>` called :ref:`maintable`.
      Clearly, if you define a *dbtable* attribute in a object, it prevails on the *maintable*
      
.. _dbtable_syntax:

syntax
======

    ::
    
        dbtable='packageName.tableName'
        
    where:
    
    * ``packageName`` is the name of the :ref:`package <packages>` on which you're working;
    * ``tableName`` is the name of the :ref:`table` on which is executed the user query;
    
    .. note:: you can omit the ``packageName`` if the dbtable is used on a :ref:`webpage` that
              belongs to the package you should specify.
              
.. _dbtable_examples:

examples
========

    Based on the form widget you're working on, there is a different use of *dbtable*:
    
        * For the :ref:`formbuilder` and the :ref:`field` form widgets,
          please check the :ref:`field` page.
        * For the :ref:`dbselect` and the :ref:`dbcombobox` form widgets,
          please check the dbSelect and dbCombobox :ref:`db_examples` page.