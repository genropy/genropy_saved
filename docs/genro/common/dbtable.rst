	.. _genro-dbtable:

=========
 Dbtable
=========
	
	The ``dbtable`` attribute is used to specify a path for a database :ref:`genro-database_table` during a user query.
	
	The syntax is ``packageName.tableName.attributeName``, where:
	
		* ``packageName`` is the name of the package on which you're working;
		* ``tableName`` is the name of the :ref:`genro-database_table` on which is executed the user query.

	Based on the form widget you're using, there is a different usage of ``dbtable``:
	
		* If you are using :ref:`genro-formbuilder` and :ref:`genro-field` widgets, then check the :ref:`genro-field` page for all the details.
		
		* If you are using :ref:`genro-dbselect` and :ref:`genro-dbcombobox` widgets, then check the dbSelect and dbCombobox :ref:`db-examples` for all the details.