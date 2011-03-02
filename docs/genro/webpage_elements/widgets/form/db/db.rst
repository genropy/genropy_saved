.. _genro_db:

==================================================
filteringSelect, comboBox, dbSelect and dbCombobox
==================================================

    In this section we introduce four text field used to get a value chosen from a list of values or from a database.
    
        **Values from a list**:
            
            * :ref:`genro_filteringselect`: the filteringSelect is a text field who suggests to user the possible (and unique!) entries of his selection. FilteringSelect's values are composed by a key and a value (like the Python dictionary's elements): user can chooses from values, while in :ref:`genro_datastore` the user's choice is saved through its specific key.
            * :ref:`genro_combobox`: the comboBox is a graphical user widget that permits the user to select a value from multiple options (with combobox you have to provide a list of acceptable values).
        
        **Values from a database** [#]_:
        
            * :ref:`genro_dbselect`: The Genro dbSelect [#]_ is a :ref:`genro_filteringselect` that takes the values through a query on the database. User can choose between all the values contained into the linked :ref:`model_table` (you have to specify the table from which user makes his selection), and dbSelect keep track into the :ref:`genro_datastore` of the ID of the record chosen by the user.
            * :ref:`genro_dbcombobox`: The Genro ``dbCombobox`` is a :ref:`genro_combobox` that conducts research on specific columns in a database table.

**Footnotes:**

.. [#] It should have been called "dbFilteringSelect", but it has been shortened in "dbSelect".
.. [#] To use dbSelect there must exist a database. For having information on a database creation, please check :ref:`genro_simple_introduction`.