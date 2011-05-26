.. _genro_sql:

===
SQL
===

    .. warning:: completely to do !!
    
    add???
    
.. _sql_relation:

sql relation
============

    add??? (explain that: the "@ path" call a resolver to resolv a sql relation)
    
    DEF: a path with @ is called 
    
.. _sql_relation_field:

relation field
==============

    add??? A relation field is path ... e.g: ``@agenda_id.staff``
    
    Relation fields uses a syntax based on the char '@' and 'dot notation'. (e.g. "@member_id.name").
    
.. _sql_attributes:

sql attributes
==============
    
.. _sql_columns:

columns
-------

    Represent the "SELECT" clause in the traditional sql query.
    
    It is a string of column names and :ref:`sql_relation_field`\s separated by comma
    (you can use a list or a tuple, too). Each column's name has to be prefixed with '$'.
    To select all the columns use the char '*'. The ``columns`` parameter also accepts
    special statements such as "COUNT", "DISTINCT" and "SUM".
    
    Example::
    
        columns='*'
        
        add??? (other examples...)
        
.. _sql_where:

where
-----

    add???
    