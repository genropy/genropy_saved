.. _sql_commons:

====================
SQL common attibutes
====================

    *Last page update*: |today|

    * :ref:`pkey`
    * :ref:`relationdict`
    
.. _pkey:

pkey
====

    The primary key of a :ref:`table`.
    
    CLIPBOARD::
    
        TODO parlare del fatto che si può usare l'id come una qualsiasi altra
        colonna attraverso il sysFields...

.. _relationdict:

relationDict
============

    A dict to assign a symbolic name to a :ref:`relation <relations>`.
    
    Example::
    
        dict(myname='@relname.colname')
        
    ``myname`` can be used as ``$myname`` in all clauses to refer to the related column ``@relname.colname``.
    ``myname`` is also the name of the related column in the result of the select (relatedcol AS myname).