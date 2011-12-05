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

    The *dbtable* attribute is used in all those widgets that allows the user to perform
    a selection on database through a query. In the *dbtable* attribute you have to specify
    the :ref:`database table <table>` in association with the query
    
    * To define a default dbtable value for all the elements of your page that supports
      it you can use the :ref:`webpage variable <webpages_variables>` called :ref:`maintable`.
      If you define a *dbtable* attribute in a object, it prevails on the *maintable* value
      
.. _dbtable_syntax:

syntax
======

    ::
    
        dbtable='packageName.tableName'
        
    where:
    
    * ``packageName`` is the name of the :ref:`package <packages>` on which you're working;
    * ``tableName`` is the name of the :ref:`table` on which is executed the user query;
    
.. _dbtable_examples:

examples
========

    TODO
    