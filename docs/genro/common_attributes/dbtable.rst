	.. _genro-dbtable:

=========
 dbtable
=========

	- :ref:`dbtable-definition-description`

	- :ref:`dbtable-validity`

	- :ref:`dbtable_examples`

	.. _dbtable-definition-description:

Definition and description
==========================
	
	The ``dbtable`` attribute is used to specify a path for a database :ref:`genro-database_table` during a user query.
	
	The syntax is ``packageName.tableName.attributeName``, where:
	
		- ``packageName`` is the name of the package on which you're working [#]_ ;
		
		- ``tableName`` is the name of the :ref:`genro-database_table` on which is executed the user query.

	.. _dbtable-validity:

Validity and default value
==========================

	**Validity:** the ``dbtable`` attribute works on the following form widgets:
	
		- :ref:`genro-formbuilder`
		
		- :ref:`genro-field`
		
		- :ref:`genro-dbselect`
		
		- :ref:`genro-dbcombobox`

	**default value:** the default value of ``dbtable`` is ``None``::

		dbtable=None

.. _dbtable_examples:

Examples
========

	Based on the form widget you're working on, there is a different use of ``dbtable``:
	
		- If you are working on :ref:`genro-formbuilder` and :ref:`genro-field` form widgets, then check the :ref:`genro-field` page for all the details.
		
		- If you are working on :ref:`genro-dbselect` and :ref:`genro-dbcombobox` form widgets, then check the dbSelect and dbCombobox :ref:`db-examples` for all the details.
		

**Footnotes:**

.. [#] For more information on a package, check the :ref:`genro-packages` paragraph.