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

	.. _dbselect-definition:

Definition
==========
		
	Here we report dbSelect's definition::
		
		def nameOfObject(args): #NISO ???

	.. _dbselect-where:

Where
=====

	You can find dbSelect in *genro/gnrpy/...* #NISO ???

	.. _dbselect-description:

Description
===========

	dbSelect [#]_ is a :ref:`form-filteringselect` that takes the values through a query on the database [#]_.
	
	User can choose between all the values contained into the linked :ref:`database-table`. You have to specify the table from which user makes his selection.
	
	dbSelect keep track into the :ref:`genro-datastore` of the ID of the record chosen by the user.
	
	While user write in the dbSelect, partially matched values will be shown in a pop-up menu below the input text box.
	
	The only way to specify the table related to the dbSelect is using the :ref:`common-dbtable` attribute.
	
	.. _dbselect-examples:

Examples
========

	Let's see a code example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				fb=pane.formbuilder(datapath='test1',cols=2)
				fb.dbSelect(dbtable='showcase.person',rowcaption='$name',
				            value='^.person_id',lbl='Star')

	Let's see a demo:

	#NISO add online demo!

	.. _dbselect-attributes:

Attributes
==========
	
	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``alternatePkey``  | #NISO                                           |  ``None``                |
	|                    | ???                                             |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``auxColumns``     | Show in a pop-up menu below the input textbox   |  ``None``                |
	|                    | i parametri di ricerca (vuole obbligato columns)|                          |
	|                    | (campi di pura visualizzazione) ???             |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``columns``        | Specify the columns on which will be made the   |  ``None``                |
	|                    | query ???                                       |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``dbtable``        | MANDATORY - Select the database                 |  ``None``                |
	|                    | :ref:`database-table` for dbSelect query. For   |                          |
	|                    | further details, see :ref:`common-dbtable`      |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``limit``          | Set the number of visible choices on the pop-up |  ``10``                  |
	|                    | menu below the input textbox during user typing |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``rowcaption``     | Allow user to view records through              |  ``None``                |
	|                    | :ref:`name-name_long` value.                    |                          |
	|                    | Without ``rowcaption``, user will see value ID. |                          |
	|                    | Check for more information on                   |                          |
	|                    | :ref:`database-rowcaption` page                 |                          |
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

	
**Footnotes**
	
.. [#] It should have been called "dbFilteringSelect", but it has been shortened in "dbSelect"
.. [#] To use dbSelect there must exist a database. For having information on a database creation, please check :ref:`database-introduction`.

