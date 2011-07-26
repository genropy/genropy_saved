.. _query:

=====
query
=====
    
    *Last page update*: |today|
    
    add???
    
    In a query you can refer itself to the primary key of the table with the
    following syntax::
    
        where='$pkey=:pkey'
        
    where :ref:`pkey` is the name for the primary key.
    
        **Example**:
        
        >>> db.table('location.province').query(where='$pkey=:pkey',pkey='MI',addPkeyColumn=False).fetch()
        [initials=MI,region=LOM,name=Milan,istat_code=013,order=22,total_order=None,valid_vat=None]