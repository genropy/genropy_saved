.. _sql_commons:

=======
commons
=======

    *Last page update*: |today|

    * :ref:`pkey`
    * :ref:`relationdict`
    
.. _pkey:

pkey
====

    The primary key of a :ref:`table`.
    
    add??? parlare del fatto che si può usare l'id come una qualsiasi altra colonna + sysFields

.. _relationdict:

relationDict
============

    A dict to assign a symbolic name to a :ref:`relation_path`.
    
    Example::
    
        dict(myname='@relname.colname')
        
    ``myname`` can be used as ``$myname`` in all clauses to refer to the related column ``@relname.colname``.
    ``myname`` is also the name of the related column in the result of the select (relatedcol AS myname).
    
    RIMUOVO I TEXTMATE DA _BUILD...
    METTO A POSTO IL PKEY...