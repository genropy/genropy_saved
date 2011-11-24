.. _query:

=====
query
=====
    
    *Last page update*: |today|
    
    TODO
    
    In a query you can refer itself to the :ref:`primary key <pkey>` of a :ref:`database table <table>`
    with the following syntax::
    
        where='$pkey=:pkey'
        
    **Example**:
    
    >>> db.table('location.province').query(where='$pkey=:pkey',pkey='MI',addPkeyColumn=False).fetch()
    [initials=MI,region=LOM,name=Milan,istat_code=013,order=22,total_order=None,valid_vat=None]