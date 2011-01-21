.. _genro_dbtable:

=========
 dbtable
=========

	* :ref:`dbtable_def`
	* :ref:`dbtable_validity`
	* :ref:`dbtable_examples`

.. _dbtable_def:

Definition and description
==========================
	
	The ``dbtable`` attribute is used to specify a path for a database :ref:`genro_database_table` during a user query.
	
	The syntax is ``packageName.tableName.attributeName``, where:
	
		- ``packageName`` is the name of the package on which you're working [#]_ ;
		
		- ``tableName`` is the name of the :ref:`genro_database_table` on which is executed the user query.

.. _dbtable_validity:

Validity and default value
==========================

	**Validity:** the ``dbtable`` attribute works on the following form widgets:
	
		* :ref:`genro_formbuilder`
		
		* :ref:`genro_field`
		
		* :ref:`genro_dbselect`
		
		* :ref:`genro_dbcombobox`

	**default value:** the default value of ``dbtable`` is ``None``::

		dbtable=None

.. _dbtable_examples:

Examples
========

	Based on the form widget you're working on, there is a different use of ``dbtable``:
	
		- If you are working on :ref:`genro_formbuilder` and :ref:`genro_field` form widgets, then check the :ref:`genro_field` page for all the details.
		
		- If you are working on :ref:`genro_dbselect` and :ref:`genro_dbcombobox` form widgets, then check the dbSelect and dbCombobox :ref:`db_examples` for all the details.
		

**Footnotes:**

.. [#] For more information on a package, check the :ref:`genro_packages` paragraph.