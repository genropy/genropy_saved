.. _table:

=====
table
=====
    
    *Last page update*: |today|
    
    .. image:: ../../../_images/projects/packages/model_table.png
    
    add??? rewrite the following index!!!
    
    * :ref:`table_description`
    * :ref:`table_definition`
    * :ref:`table_creation`
    * :ref:`table_config_db`
    * :ref:`table_columns`, :ref:`table_validations`
    * :ref:`table_examples`
    
.. _table_description:

description
===========

    A table is one of the most important part of your project. In relational databases and
    flat file databases, a table is a set of data elements that is organized using a model
    of vertical :ref:`table_columns` (which are identified by their name) and horizontal
    rows. Each row is identified by the table's primary key (:ref:`pkey`).
    
.. _table_definition:

definition
==========

    .. automethod:: gnr.sql.gnrsqlmodel.DbModelSrc.table
    
.. _table_creation:
    
creation of a table
===================
    
    First write something like the following line::
    
        #!/usr/bin/env python
        
    ``/usr/bin/env`` is the address of the location of python (most of the time! Put your
    correct python location).
    
    Then write the following line for the utf-8 encoding::
    
        # encoding: utf-8
        
    Now we have to introduce the right class for a table.
    
    There are two options, that are:
    
    * :ref:`classes_table`
    * :ref:`classes_htable`
    
    Here we describe the most common table, that is the ``Table`` class::
    
        class Table(object):
        
    add???
    
.. _table_config_db:
        
config_db
=========
        
    To use a table you have to call the following method:
    
    .. automethod:: gnr.app.gnrdbo.Table_counter.config_db
    
    So, write inside your ``class Table(object):`` the following method::
        
            def config_db(self, pkg):
            
    Inside the ``config_db`` method you can create a table:
    
    * introduce a table::
        
        tbl = pkg.table('company', pkey='id', rowcaption='@registry_id.name',
                         name_long='Company', name_plural='Companies')
                         
    add??? automethod of table method!
                         
    * table attributes:
    
        * pkey
        * rowcaption
        * name_long
        * name_plural
        * audit='lazy' --> consente di visualizzare (DOVE??? Mi sembra una cosa di adm) le modifiche
                           ad un record. Non fa niente quando si crea un nuovo record.
        * _sendback: boolean. If ``True``, the value of the column is passed during the form save, even
          if it is not change.
          
          It is useful when you have to check a column value even if it doesn't change (using for
          example the :ref:`onloading_method` or the :ref:`onsaving_method` method).
          
        * indexed: boolan. If ``True``, create an SQL index.
          
.. _sysfields:

sysFields
---------
    
    .. automethod:: gnr.app.gnrdbo.TableBase.sysFields
    
    To call it in the table page, type::
        
        self.sysFields(tbl)
        
.. _htablefields:

htableFields
------------
    
    .. automethod:: gnr.app.gnrdbo.GnrHTable.htableFields
    
    To call it in the table page, type::
    
        self.htableFields(tbl)
    
.. _table_columns:

columns
=======

    There are a lot of columns type you can use:
    
    * the simple :ref:`table_column`
    * the :ref:`table_relation_column` (and the :ref:`table_relation`)
    * the :ref:`table_aliascolumn`
    * the :ref:`table_formulacolumn`
    * the :ref:`table_virtualcolumn`

.. _table_column:

column
------

    .. automethod:: gnr.sql.gnrsqlmodel.DbModelSrc.column
    
    **Example**::
        
        tbl.column('my_column',size=':15',name_long='!!My column')
        
    where ``tbl`` is the table object.
    
.. _table_relation_column:

relation column
---------------

    The relation column is a column that allows to build relations between tables.

    To create a relation column, you have to attach the :ref:`table_relation` to a :ref:`table_column`::
    
        tbl.column('my_column',size=':15',name_long='!!My column').relation(...)
        
    where ``tbl`` is the table object. In the next section we talk about the ``relation`` method.
    
.. _table_relation:

relation method
---------------

    .. automethod:: gnr.sql.gnrsqlmodel.DbModelSrc.relation
    
    For a full explanation of the relation method attributes, please check the
    :ref:`relation_attrs` page.
    
    **Example**::
    
        tbl.column('registry_id',size=':22',name_long='!!Registry id').relation('sw_base.registry.id',mode='foreignkey')
        
        add??? example explanation!
        
.. _table_aliascolumn:

aliasColumn
-----------

    The aliasColumn is a column through which you can give a different name to some columns of a related table.
    
        **Example**:
        
        add???
        
.. _table_formulacolumn:

formulaColumn
-------------

    add???
    
    ``#THIS``: you can use ``#THIS`` (only in a formulaColumn) to refer to the table itself.
    
    Example: if you some fields called ``change_date``, ``vat_rate`` and ``vat_rate_new``, and you are in the
    same table in which they are defined, you can make a formulaColumn::
    
        tbl.formulaColumn('current_vat_rate', """CASE WHEN
                                                 #THIS.change_date IS NULL
                                                 OR
                                                 #THIS.vat_rate_new IS NULL
                                                 OR
                                                 #THIS.change_date <:env_workdate
                                                 THEN
                                                 #THIS.vat_rate
                                                 ELSE #THIS.vat_rate_new
                                                 END""")
    
    .. note:: if you need to refer to another table, use the following syntax:
    
              ::
              
                tableName.tableName_columnName.tableField
                
    .. _table_virtualcolumn:

virtualColumn
-------------
    
    add???

.. _table_validations:

validations in a column
-----------------------

    add??? --> link to :ref:`validations`...
    
.. _bla_bla:
    
paragraph to revise
===================

.. _set_tagcolumn:

setTagColumn
------------

    add???
    
    .. automethod:: gnr.app.gnrdbo.TableBase.setTagColumn
    
.. _table_examples:

examples
========

    Let's see a first example::
    
        # encoding: utf-8
        
        class Table(object):
            def config_db(self, pkg):
                tbl = pkg.table('person',pkey='id',name_long='!!people',
                                 name_plural='!!People',rowcaption='$name')
                tbl.column('id',size='22',group='_',readOnly=True,name_long='Id')
                tbl.column('name', name_short='N.', name_long='Name')
                tbl.column('year', 'L', name_short='Yr', name_long='Birth Year')
                tbl.column('nationality', name_short='Ntl',name_long='Nationality')
                tbl.column('number','L',name_long='Number')