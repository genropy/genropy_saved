	.. _form-dbcombobox:

============
 DbCombobox
============

.. currentmodule:: dbcombobox

.. class:: dbcombobox - Genropy dbcombobox

	- :ref:`dbcombobox-definition`

	- :ref:`dbcombobox-where`

	- :ref:`dbcombobox-description`

	- :ref:`dbcombobox-examples`

	- :ref:`dbcombobox-attributes`

	We recommend you to read :ref:`genro-dbselect-dbcombobox` first.

	.. _dbcombobox-definition:

Definition
==========

	Here we report dbCombobox's definition::
		
		def nameOfObject(args): #NISO ???

	.. _dbcombobox-where:

Where
=====

	You can find dbcombobox in *genro/gnrpy/...* #NISO ???

	.. _dbcombobox-description:

Description
===========

	The Genro ``dbCombobox`` is a :ref:`form-combobox` that conducts research on specific columns in a database table. While user write in the dbCombobox, partially matched values will be shown in a pop-up menu below the input text box. ``dbCombobox`` has got the same parameters of the :ref:`form-dbselect`, and allows to choose from values situated in the database AND from values that aren't in the database. These "new" values aren't added in the database but they have being placed in the :ref:`genro-datastore`, so they can be handled from Genropy [#]_.

	The only way to specify the table related to the dbCombobox is using the :ref:`common-dbtable` attribute.

	.. _dbcombobox-examples:

Examples
========

	Let's see a code example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				fb=pane.formbuilder(datapath='test1',cols=2)
				???

	Let's see a demo:

	#NISO add online demo! ???

	.. _dbcombobox-attributes:

dbCombobox attributes
=====================

	For the list of dbCombobox attributes, please check :ref:`db-common-attributes`.

**Footnotes**

.. [#] We remeber to you that ``dbCombobox`` supports only the values (not the keys!); so the main ``dbCombobox`` feature is that it permits to enter values in the :ref:`genro-datastore`, but they won't be stored in the database.
