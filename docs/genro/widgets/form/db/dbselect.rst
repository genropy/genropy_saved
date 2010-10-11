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

	We recommend you to read :ref:`genro-dbselect-dbcombobox` first.

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
	
	User can choose between all the values contained into the linked :ref:`database-table` (you have to specify the table from which user makes his selection), and dbSelect keep track into the :ref:`genro-datastore` of the ID of the record chosen by the user.
	
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

dbSelect attributes
===================

	For the list of dbSelect attributes, please check :ref:`db-common-attributes`.

**Footnotes**
	
.. [#] It should have been called "dbFilteringSelect", but it has been shortened in "dbSelect".
.. [#] To use dbSelect there must exist a database. For having information on a database creation, please check :ref:`database-introduction`.

