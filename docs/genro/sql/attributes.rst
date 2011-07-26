.. _sql_attributes:

==============
sql attributes
==============

    * :ref:`sql_attributes`:
    
        * :ref:`sql_columns`
        * :ref:`sql_deferred`
        * :ref:`sql_distinct`
        * :ref:`sql_group_by`
        * :ref:`sql_having`
        * :ref:`sql_order_by`
        * :ref:`sql_where`
        
.. _sql_columns:

columns
-------

    .. module:: gnr.sql.gnrsqldata.SqlQueryCompiler
    
    The ``columns`` attribute represents the :ref:`table_columns` to be returned
    by the "SELECT" clause in the traditional sql query.
    
    It is a string of column names and :ref:`relation paths <relation_path>`
    separated by comma (you can use a list or a tuple, too).
    
    It is a standard sql column clause and may contain sql functions and the "AS" operator.
    In addition to sql expressions, a column can be called through the following syntaxes:
    
    * ``$colname``: a column of the main table or a key of the :ref:`relationdict`
    * ``@relname.colname``: a related column
    * ``sqlfunction($colname, @relname.colname)``: ``$`` and ``@`` syntax can be used inside
      sql functions too 
    * ``*``: all the columns of the main table (with or without the bagFields)
    * ``*filter``: all columns of the main table filtered (check the :meth:`expandMultipleColumns`
      method)
    * ``*@relname.filter``: all columns of a related table filtered (check the
      :meth:`expandMultipleColumns` method)
    
    To select all the columns use the char ``*``
    
    The ``columns`` parameter also accepts special statements such as "COUNT", "DISTINCT"
    and "SUM".
    
    Example::
    
        columns='*'
        
        add??? (other examples...)
        
.. _sql_deferred:

deferred
--------

    The sql "DEFERRED" clause.
    
    Boolean, ``True`` to get... add???
    
    Example::
    
        add???
        
.. _sql_distinct:

distinct
--------

    The sql "DISTINCT" clause.
    
    Boolean, ``True`` for getting a "SELECT DISTINCT".
    
    Example::
    
        add???
        
.. _sql_group_by:

group_by
--------

    The sql "GROUP BY" clause. Database columns can use one of the following syntaxes:
    
    * ``$colname``
      
      where ``colname`` is the name a table column
    * ``@relname.colname``
      
      where ``relname`` is a :ref:`relation_path`, ``colname`` is the name of the column.
      
    Use ``group_by='*'`` when all columns are aggregate (add???) functions in order to avoid
    the automatic insertion of the :ref:`pkey` field in the columns.
    
    Example::
    
        add???
    
.. _sql_having:

having
------

    The sql "HAVING" clause. Database columns can use one of the following syntaxes:
    
    * ``$colname``
      
      where ``colname`` is the name a table column
    * ``@relname.colname``
      
      where ``relname`` is a :ref:`relation_path`, ``colname`` is the name of the column.
      
.. _sql_order_by:

order_by
--------

    The sql "ORDER BY" clause. A clause that returns the result set in a sorted order
    based on specified columns.
    
    Database columns can use one of the following syntaxes:
    
    * ``$colname``
      
      where ``colname`` is the name a table column
    * ``@relname.colname``
      
      where ``relname`` is a :ref:`relation_path`, ``colname`` is the name of the column.
    
    Example::
    
        add???
    
.. _sql_where:

where
-----

    The ``where`` attribute represents the table :ref:`table_columns` to be returned by the
    "SELECT" clause in the traditional sql query.
    
    Database columns can use one of the following syntaxes:
    
    * ``$colname``
      
      where ``colname`` is the name a table column
    * ``@relname.colname``
      
      where ``relname`` is a :ref:`relation_path`, ``colname`` is the name of the column.
    
    Query parameters have to start with colon (``:``), like::
    
        ``@relname.colname=:param1``.
        
    where ``param1`` is the query parameter.
    
    .. note:: we suggest not to use hardcoded values into the where clause, but refer to
              variables passed to the selection method as kwargs.
              
              Examples::
              
                where="$date BETWEEN :mybirthday AND :christmas", mybirthday=mbd, christmas=xmas
                