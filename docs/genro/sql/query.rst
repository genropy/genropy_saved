.. _query:

=====
query
=====
    
    *Last page update*: |today|
    
    TODO
    
.. _query_intro:

introduction
============

    .. automethod:: gnr.sql.gnrsql.GnrSqlDb.query
    
    TODO
    
    CLIPBOARD::
        
        In a query you can refer itself to the :ref:`primary key <pkey>` of a :ref:`database table <table>`
        with the following syntax::
        
            where='$pkey=:pkey'
            
        **Example**:
        
        >>> db.table('location.province').query(where='$pkey=:pkey',pkey='MI',addPkeyColumn=False).fetch()
        [initials=MI,region=LOM,name=Milan,istat_code=013,order=22,total_order=None,valid_vat=None]
    
.. _query_methods:

query methods
=============

.. _query_count:

count
-----

    .. automethod:: gnr.sql.gnrsqldata.SqlQuery.count
    
    TODO
    
.. _query_fetch:

fetch
-----

    .. automethod:: gnr.sql.gnrsqldata.SqlQuery.fetch
    
    TODO
    
.. _query_fetchasbag:

fetchAsBag
----------

    .. automethod:: gnr.sql.gnrsqldata.SqlQuery.fetchAsBag
    
    TODO
    
.. _query_fetchasdict:

fetchAsDict
-----------

    .. automethod:: gnr.sql.gnrsqldata.SqlQuery.fetchAsDict
    
    TODO
    
.. _query_fetchgrouped:

fetchGrouped
------------

    .. automethod:: gnr.sql.gnrsqldata.SqlQuery.fetchGrouped
    
    TODO
    
.. _query_selection:

selection
---------

    .. automethod:: gnr.sql.gnrsqldata.SqlQuery.selection
    
    TODO
    