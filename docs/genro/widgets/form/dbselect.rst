	.. _form-dbselect:

==========
 DbSelect
==========

.. currentmodule:: dbSelect

.. class:: dbSelect - Genropy dbSelect

	- :ref:`dbselect-definition`

	- :ref:`dbselect-where`

	- :ref:`dbselect-description`

	- :ref:`dbselect-examples`

	- :ref:`dbselect-attributes`

	- :ref:`dbselect-other-attributes`

	- :ref:`dbselect-features`

		- :ref:`dbselect-zoom-example`

	.. _dbselect-definition:

Definition
==========
		
	Here we report dbselect's definition::
		
		def nameOfObject(args): ???
			

	.. _dbselect-where:

Where
=====

	You can find dbSelect in *genro/gnrpy/...* ???

	.. _dbselect-description:

Description
===========

	dbSelect [#]_ is a :ref:`form-filteringselect` that takes the values through a query on the database. While user write in the dbSelect, partially matched values will be shown in a pop-up menu below the input text box.
	
	dbSelect keep track into the :ref:`genro-datastore` of the ID of the record chosen by the user.
	
	To use dbSelect there must exist a database. For having information on a database creation, please check :ref:`database-introduction`.

	.. _dbselect-examples:

Examples
========

	Let's see a code example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				fb=pane.formbuilder(datapath='test1',cols=2)
				fb.dbSelect(value='^.query',)

	Let's see a demo:

	#NISO add online demo!

	.. _dbselect-attributes:

Attributes
==========
	
	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``alternatePkey``  | ???                                             |  ``???``                 |
	|                    | ???                                             |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``auxColumns``     | Show in a pop-up menu below the input textbox   |  ``???``                 |
	|                    | i parametri di ricerca (vuole obbligato columns)|                          |
	|                    | (campi di pura visualizzazione) ???             |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``columns``        | Query fields ???                                |  ``???``                 |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``dbtable``        | Select the database :ref:`database-table` for   |  ``None``                |
	|                    | dbSelect query. For further details, see        |                          |
	|                    | :ref:`common-dbtable`                           |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``limit``          | Set the number of visible choices on the pop-up |  ``10``                  |
	|                    | menu below the input textbox during user typing |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``zoom=True``      | It allows to open the linked record in its      |  ``True``                |
	|                    | :ref:`database-table`. For further              |                          |
	|                    | details, check :ref:`dbselect-zoom-example`     |                          |
	+--------------------+-------------------------------------------------+--------------------------+

	.. _dbselect-other-attributes:

Common attributes
=================

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``disabled``       | If True, user can't act on the dbselect.        |  ``False``               |
	|                    | For more details, see :ref:`common-disabled`    |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the dbselect.                              |  ``False``               |
	|                    | See :ref:`common-hidden`                        |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for dbselect's values.               |  ``None``                |
	|                    | For more details, see :ref:`common-datapath`    |                          |
	+--------------------+-------------------------------------------------+--------------------------+

	.. _dbselect-features:

Attributes description
======================

	.. _dbselect-zoom-example:
	
zoom example
============
	
	??
	
**Footnotes**
	
.. [#] It should have been called "dbFilteringSelect", but it has been shortened in "dbSelect"
