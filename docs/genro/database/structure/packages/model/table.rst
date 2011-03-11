.. _model_table:

=====
table
=====
    
    * :ref:`table_definition`
    * :ref:`table_description`
    * :ref:`table_relation`
    * :ref:`table_examples`
    
.. _table_definition:

Definition
==========

    A table allows to manage the database. add???(here I need an help for documentation...)
    
    * introduce the following lines::
    
        # encoding: utf-8
        
        class Table(object): # add???(a mixin class?)
        
        class TableBase
        
    .. automethod:: gnr.app.gnrdbo.Table_counter.config_db
        
            def config_db(self, pkg):
            
    * introdurre la table::
        
        tbl = pkg.table('azienda', pkey='id', rowcaption='@anagrafica_id.ragione_sociale',
                              name_long='!!Azienda', name_plural='!!Aziende')
    
    * introdurre il sysFields::
        
        self.sysFields(tbl, group='_')
        
    .. automethod:: gnr.app.gnrdbo.TableBase.sysFields
    
    * introdurre le column(s):
        
        tbl.column('tipologia',size=':22',name_long='!!Tipologia')
        
    * parlare delle column con la relation...
        
        tbl.column('anagrafica_id',size=':22',name_long='!!Anagrafica id',group='_').relation('sw_base.anagrafica.id', mode='foreignkey')
        
    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc.column
    
.. _table_description:

Description
===========

    * introduce the rowcaption attribute and put the link to the relative page for further details (:ref:`genro_database_rowcaption`).
    * speak about column 
    
.. _table_relation:

relation
========

    ??? HERE EXPLAIN OF THE RELATION!
    
..??? Explain of the possibility to create a Table with the relation attribute; make an example of:

    table1 + table2 + table3 (in relation with table 1 and table2)

..(use OmniGraffle!!)

    Suppose to create a database of directors and films. In this database you have created a :ref:`model_table` for the directors (called ``person.py``), a ``table`` for the films (called ``movie.py``) and a :ref:`table_relation` table between directors and films (called ``cast.py``).

..add a figure...

    Suppose now that you want to create a webpage containing two ``dbselect``: the first one will be used by the user to choose a director, and the second one will be used to choose a film of the chosen director.
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