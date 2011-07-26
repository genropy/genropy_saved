.. _db:

============
Introduction
============
    
    *Last page update*: |today|
    
    In this section we introduce four input field used to get a value chosen from a list of values or from a database.
    
    **Values from a list**:
            
    * :ref:`filteringselect`: the Dojo filteringSelect suggests to user the possible (and unique!)
      entries of his selection. FilteringSelect's values are composed by a "key" and a "value", like in
      a dictionary. The users can choose between "values", while in the :ref:`datastore` the users
      choice is saved through its specific "key".
    * :ref:`combobox`: the Dojo comboBox is a graphical user widget that permits the user to select
      a value from multiple options (you have to provide this list of acceptable values). Like an input
      text field, user can also type values that doesn't belong to the list of accetable ones.
        
    **Values from a database** [#]_:
        
    * :ref:`dbselect`: The Genro dbSelect [#]_ is a :ref:`filteringselect` that takes the values
      through a query on the database. User can choose between all the values contained into the linked
      :ref:`table` (you have to specify the table from which user makes his selection), and dbSelect
      keep track into the :ref:`datastore` of the ID of the record chosen by the user.
    * :ref:`dbcombobox`: The Genro ``dbCombobox`` is a :ref:`combobox` that conducts research on
      specific columns in a database table.
      
**Footnotes:**

.. [#] It should have been called "dbFilteringSelect", but it has been shortened in "dbSelect".
.. [#] To use dbSelect there must exist a database. For having information on a database creation, please check :ref:`simple_introduction`.