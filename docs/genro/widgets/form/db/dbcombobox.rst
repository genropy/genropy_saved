	.. _genro-dbcombobox:

============
 dbCombobox
============

.. currentmodule:: dbcombobox

.. class:: dbCombobox - Genropy dbCombobox

	- :ref:`dbcombobox-definition-description`

	- :ref:`dbcombobox-examples`

	- :ref:`dbcombobox-attributes`

	We recommend you to read :ref:`genro-dbselect-dbcombobox` first.

	.. _dbcombobox-definition-description:

Definition and Description
==========================

	The Genro ``dbCombobox`` is a :ref:`genro-combobox` that conducts research on specific columns in a database table. While user write in the dbCombobox, partially matched values will be shown in a pop-up menu below the input text box. ``dbCombobox`` has got the same parameters of the :ref:`genro-dbselect`, and allows to choose from values situated in the database AND from values that aren't in the database. These "new" values aren't added in the database but they have being placed in the :ref:`genro-datastore`, so they can be handled from Genropy. [#]_

	The only way to specify the table related to the dbCombobox is using the :ref:`genro-dbtable` attribute.

	.. _dbcombobox-examples:

Examples
========

	Let's see a code example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				fb=pane.formbuilder(datapath='test1')
				fb.div("""In a "dbCombobox" you can draw record values from a database (not the ID!).
				          The difference with the "dbSelect" is the possibility to add NEW records.""",
				          font_size='.9em',text_align='justify')
				fb.div('For example, try to draw an actor from the first "dbCombobox"...',
				        font_size='.9em',text_align='justify')
				fb.dbCombobox(dbtable='showcase.person',value='^.person',lbl='Star')
				fb.div('... and then write a film not in the database.',
				          font_size='.9em',text_align='justify')
				fb.dbCombobox(dbtable='showcase.movie',value='^.movie',lbl='Movie')
				fb.div("""After that, check in the datasource your saved records (by clicking
				          ctrl+shift+D)""",font_size='.9em',text_align='justify')

	Let's see a demo:

	#NISO add online demo! ???

	.. _dbcombobox-attributes:

dbCombobox attributes
=====================

	For the list of dbCombobox attributes, please check :ref:`db-genro-attributes`.

**Footnotes**

.. [#] We remeber to you that ``dbCombobox`` supports only the values (not the keys!); so the main ``dbCombobox`` feature is that it permits to enter values in the :ref:`genro-datastore`, but they won't be stored in the database.