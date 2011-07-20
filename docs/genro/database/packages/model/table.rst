.. _genro_table:

=====
table
=====
    
    *Last page update*: |today|
    
    .. image:: ../../../_images/projects/packages/model_table.png
    
    * :ref:`table_description`
    * :ref:`table_definition`
    * :ref:`table_creation`
    * :ref:`table_config_db`
    * :ref:`table_columns`
    
        * the simple :ref:`table_column` (and :ref:`table_relation`\s)
        * the :ref:`table_aliascolumn`
        * the :ref:`table_formulacolumn`
        * the :ref:`table_virtualcolumn`
        
        * :ref:`table_validations`
        
    * :ref:`table_examples`
    
.. _table_description:

Description
===========

    A table is one of the most important part of your project. In relational databases and
    flat file databases, a table is a set of data elements that is organized using a model
    of vertical :ref:`table_columns` (which are identified by their name) and horizontal
    rows. Each row is identified by the table's primary key (pkey).
    
.. _table_definition:

Definition
==========

    .. automethod:: gnr.sql.gnrsqlmodel.DbModelSrc.table
    
.. _table_creation:
    
Creation of a table
===================
    
    To autocreate a table header, you have to install Textmate_ with :ref:`textmate_bundle`.
    
    .. _Textmate: http://macromates.com/
    
    If you have them, then you can write "table" and then press the "Tab" key.
    
    Alternatively, you can write by yourself the header lines:
    
    * First write the following line for the utf-8 encoding::
    
        # encoding: utf-8
    
    Now we have to introduce the right class for a table; there are many options (that we
    discuss in the :ref:`genro_table_classes` documentation page). We use now the standard
    method::
    
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
          
    * introduce the sysFields::
        
        self.sysFields(tbl)
        
    .. automethod:: gnr.app.gnrdbo.TableBase.sysFields
    
    * introduce the htableField::
    
        add??? self.htableFields(tbl)

.. _table_columns:

columns
=======

    There are a lot of columns type you can use:
    
    * the simple :ref:`table_column` (and :ref:`table_relation`\s)
    * the :ref:`table_relation`
    * the :ref:`table_aliascolumn`
    * the :ref:`table_formulacolumn`
    * the :ref:`table_virtualcolumn`

.. _table_column:

column
------

    .. automethod:: gnr.sql.gnrsqlmodel.DbModelSrc.column
    
    * introduce column(s):
        
      ::
        
        tbl.column('tipologia',size=':22',name_long='!!Tipologia')
        
    * column attributes:
    
        * size
        * :ref:`genro_name_long`
        * :ref:`genro_name_plural`
        * :ref:`genro_name_short`
        * required (???)
        * unique (boolean)
        *  _sendback (boolean) add???
        
.. _table_relation:

relation column
---------------

    Allow to create a relation from table to table.

    ::
    
        tbl.column('registry_id',size=':22',name_long='!!Registry id').relation('sw_base.registry.id',mode='foreignkey')
        
    attributi di *relation*:
    
    * first parameter: the path of the relation field
    
      ::
      
        packageName.tableName.columnName
        
    * mode='foreignkey'
      se non si mette il mode='foreignkey', la relazione è puramente logica, ed è senza nessun controllo
      di integrità referenziale quando si vuole interagire con il database, mettere mode='foreignkey' -->
      diventa una relazione SQL. Nel 99% dei casi bisogna metterlo!
      
    * one_one='*' / True / ... add??? permette di rendere la relazione "simmetrica"
    * one_group add???
    * relation_name='STRING'; 
      allow to use the relation parameter in a :ref:`genro_th` component. For more
      information on the relation parameter, please check the :ref:`th_relation_condition` example.
      NON SOLO!
      correggere: spiegare che è l'attributo che semplifica la sintassi standard del path di relazione inverso...
      linkare al paragrafo in cui si spiegano i path di relazioni inversi (esiste?)
      
    SQL attributes:
    * onDelete='cascade'
    * deferred boolean
    * others? add???
      
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
    same table in which they are defined, you can make a formulColumn::
    
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

    add??? --> link to :ref:`genro_validations`...
    
.. _table_examples:

Examples
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