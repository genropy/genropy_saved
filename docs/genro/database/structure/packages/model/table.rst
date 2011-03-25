.. _genro_table:

=====
table
=====
    
    .. warning:: to be completed!!
    
    * :ref:`table_definition`
    * :ref:`table_creation`
    * :ref:`table_relation`
    * :ref:`table_examples`
    
.. _table_definition:

Definition
==========

    In relational databases and flat file databases, a table is a set of data elements (values)
    that is organized using a model of vertical columns (which are identified by their name) and
    horizontal rows. A table has a specified number of columns, while the number of rows is equal
    to the records inserted. Each row is identified by the values appearing in a particular
    column subset which has been identified as a candidate key.
    
    A table allows to manage the database. add???(here I need an help for documentation...)
    
.. _table_creation:
    
Creation of a table
===================

    To autocreate a table header, you have to install Textmate_ with :ref:`textmate_bundle`.
    
    .. _Textmate: http://macromates.com/
    
    If you have them, then you can write "table" and then press the "Tab" key.
    
    Alternatively, you can write by yourself the header lines:
    
    * First write::
    
        # encoding: utf-8
    
    Explain...
    
    ::
    
        class Table(object): # add???(a mixin class?)
        
        class TableBase ???
        
    .. automethod:: gnr.app.gnrdbo.Table_counter.config_db
        
            def config_db(self, pkg):
            
    * introduce a table::
        
        tbl = pkg.table('azienda', pkey='id', rowcaption='@anagrafica_id.ragione_sociale',
                         name_long='!!Azienda', name_plural='!!Aziende') # in English!!!!add???
                         
    * table attributes:
        
        * pkey
        * rowcaption
        * name_long
        * name_plural
        * audit='lazy' --> consente di visualizzare (DOVE??? Mi sembra una cosa di adm) le modifiche ad un record.
                           Non fa niente quando si crea un nuovo record.
    
    * introduce the sysFields::
        
        self.sysFields(tbl, group='_')
        
    .. automethod:: gnr.app.gnrdbo.TableBase.sysFields

.. _table_column:

column
------

    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc.column
    
    * introduce column(s):
        
        tbl.column('tipologia',size=':22',name_long='!!Tipologia')
        
    * column attributes:
    
        * required
        * unique
        
.. _table_relation:

relation
--------

    tbl.column('anagrafica_id',size=':22',name_long='!!Anagrafica id',group='_').relation('sw_base.anagrafica.id', mode='foreignkey')
    
    attributi di *relation*:
    
    * mode='foreignkey'
      se non si mette il mode='foreignkey', la relazione è puramente logica, ed è senza nessun controllo di integrità referenziale
      quando si vuole interagire con il database, mettere mode='foreignkey' --> diventa una relazione 
    * onDelete='cascade' add??? (altri attributi?)
    * one_one='*' add??? permette di rendere la relazione "simmetrica"
    * one_group add???
    * relation_name='nome' + storepath='nome' --> mi permette di non riscrivere tutta la relazione (@blabla.@bleble.nome) che è
      contenuta nella column con il relation...
      
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
                tbl.column('number','L',name_long='!!Number')