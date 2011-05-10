.. _genro_table:

=====
table
=====
    
    * :ref:`table_description`
    * :ref:`table_definition`
    * :ref:`table_creation`
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
    of vertical columns (which are identified by their name) and horizontal rows. Each row
    is identified by the table's primary key (pkey).
    
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
    
    Now we have to introduce the right class for a table; there are many options (that we will discuss
    in the :ref:`genro_table_class` documentation page). For now use the standard one::
    
        class Table(object):
        
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
    
    * introduce the sysFields::
        
        self.sysFields(tbl)
        
    .. automethod:: gnr.app.gnrdbo.TableBase.sysFields
    
    add self.htableFields(tbl)?

.. _table_columns:

Table columns
=============

    There are a lot of columns type you can use:
    
    * the simple :ref:`table_column` (and :ref:`table_relation`\s)
    * the :ref:`table_aliascolumn`
    * the :ref:`table_formulacolumn`
    * the :ref:`table_virtualcolumn`

.. _table_column:

column
------

    .. automethod:: gnr.sql.gnrsqlmodel.DbModelSrc.column
    
    * introduce column(s):
        
        tbl.column('tipologia',size=':22',name_long='!!Tipologia')
        
    * column attributes:
    
        * required (???)
        * unique (boolean)
        *  _sendback (boolean)
        
.. _table_relation:

relation
--------

    tbl.column('anagrafica_id',size=':22',name_long='!!Anagrafica id',group='_').relation('sw_base.anagrafica.id', mode='foreignkey')
    
    attributi di *relation*:
    
    * mode='foreignkey'
      se non si mette il mode='foreignkey', la relazione è puramente logica, ed è senza nessun controllo
      di integrità referenziale quando si vuole interagire con il database, mettere mode='foreignkey' -->
      diventa una relazione SQL. Nel 99% dei casi bisogna metterlo!
    * onDelete='cascade' add??? (altri attributi?)
    * one_one='*' add??? permette di rendere la relazione "simmetrica"
    * one_group add???
    * relation_name='nome' + storepath='nome' --> mi permette di non riscrivere tutta la relazione
      (@blabla.@bleble.nome) che è contenuta nella column con il relation...
      
.. _table_aliascolumn:

aliasColumn
-----------

    add???
    
.. _table_formulacolumn:

formulaColumn
-------------

    add???
    
.. _table_virtualcolumn:

virtualColumn
-------------
    
    add???

.. _table_validations:

validations in a column
-----------------------

    add??? --> link to :ref:`genro_validations` + speak about :ref:`validate_notnull`
    
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