.. _genro_query:

=====
query
=====
    
    *Last page update*: |today|
    
    add???
    
    In a query you can refer itself to the primary key with::
    
        where='$pkey=:pkey'
        
    example::
    
        >>> db.table('glbl.provincia').query(where='$pkey=:pkey',pkey='MI',addPkeyColumn=False).fetch()
        [[sigla=MI,regione=LOM,nome=Milano,codice_istat=013,ordine=22,ordine_tot=None,cap_valido=None]]