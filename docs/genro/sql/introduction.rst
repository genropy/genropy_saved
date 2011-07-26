.. _sql_introduction:

============
introduction
============
    
    *Last page update*: |today|
    
    * :ref:`relation_path`
    * :ref:`inv_rel_path`
        
    add??? introduction...
    
.. _relation_path:

relation path
=============

    You can create relations between database :ref:`tables <table>`. For doing this, you have to relate
    a column in your table to the primary key of the table to relate to.
    
    **Example**:
    
    add???
    
    **Syntax**:
    
    To create a relation path you have to specify a foreign key in the model table
    
    Relation paths uses a syntax based on the char '@' and 'dot notation'. (e.g. "@member_id.name").
    
    The syntax is::
    
        tbl.column('anagrafica_id',size='22',name_long='!!Anagrafica',group='_').relation('sw_base.anagrafica.id',
                                                                                           mode='foreignkey',
                                                                                           one_name='!!Anagrafica')
                                                                                           
.. _inv_rel_path:

inverse relation path
=====================

    add??? --> relation_name...
    
    add an image!
    
    CLIPBOARD::
    
        un path di relazione inverso permette di risalire un path di relazione diretta AL CONTRARIO.
        Se non specificato altrimenti la sintassi di questo path è::
        
            nomePackage_nomeTable_NomeDellaForeignKey
            
        con NomeDellaForeignKey si intende il nome della column con cui si è creata la relazione.
        
        es::
        
            polimed_specialita_medico_medico_id
            
        (package=polimed;nomeTable='specialita_medico';nomeForeignKey='medico_id')
        
        Si può specificare una sintassi alternativa con il relation_name
        