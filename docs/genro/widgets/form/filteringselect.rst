	.. _form-filteringselect:

=================
 FilteringSelect
=================

.. currentmodule:: form

.. class:: filteringSelect -  Genropy filteringSelect

	- :ref:`filteringSelect-definition`
	
	- :ref:`filteringSelect-where`
	
	- :ref:`filteringSelect-description`
	
	- :ref:`filteringSelect-examples`
	
		- :ref:`bag-example`
		
		- :ref:`values-example`
		
	- :ref:`filteringSelect-attributes`
	
	- :ref:`filteringSelect-other-attributes`

	.. _filteringSelect-definition:
	
Definition
==========

	The filteringSelect is a text field who suggests to user the possible (and unique!) entries of his selection.
	
	.. _filteringSelect-where:

Where
=====

	#NISO ???
	
	.. _filteringSelect-description:

Description
===========

	FilteringSelect's values are composed by a key and a value (like the Python dictionary's elements): user can chooses from values, while in :ref:`genro-datastore` the user's choice is saved through keys. User can also freely type text and partially matched values will be shown in a pop-up menu below the input text box.
	
	If user types a wrong entry, that is a word that doesn't corresponds to any of the filteringSelect values, the key in :ref:`genro-datastore` will be saved as ``undefined``.

	.. _filteringSelect-examples:

Examples
========

	The main two modes to fill a filteringSelect are:
	
	* Filling a filteringSelect through a Bag
	* Filling a filteringSelect through "values" attribute
	
	.. _bag-example:
	
Filling a filteringSelect through a Bag
=======================================

	In this example we show you how to fill a filteringSelect through a Bag (for further explanations, check :ref:`bag-introduction`):
		::

			class GnrCustomWebPage(object):
				def main(self,root,**kwargs):
					fb = root.formbuilder(datapath='test1',cols=2)
					fb.filteringSelect(value='^.bag',storepath='bag')

				def sports(self,**kwargs):
					mytable=Bag()
					mytable['r1.pkey'] = 'SC'
					mytable['r1.Description'] = 'Soccer'
					mytable['r2.pkey'] = 'BK'
					mytable['r2.Description'] = 'Basket'
					mytable['r3.pkey'] = 'TE'
					mytable['r3.Description'] = 'Tennis'
					mytable['r4.pkey'] = 'HK'
					mytable['r4.Description'] = 'Hockey'
					mytable['r5.pkey'] = 'BB'
					mytable['r5.Description'] = 'Baseball'
					mytable['r6.pkey'] = 'SB'
					mytable['r6.Description'] = 'Snowboard'
					return mytable

	.. _values-example:

Filling a filteringSelect through "values" attribute
====================================================

		Example::

			class GnrCustomWebPage(object):
				def main(self,root,**kwargs):
					fb = root.formbuilder(datapath='test2',cols=2)
					fb.filteringSelect(value='^sports',
					                   values="""SC:Soccer,BK:Basket,HK:Hockey,
					                             TE:Tennis,BB:Baseball,SB:Snowboard""")
	
	Pay attention not to confuse ``value`` with ``values``: ``value`` is used to allocate user data in a well determined :ref:`common-datapath`, while ``values`` is used to fill the filteringSelect.
	
	Warning: unlike Dojo, actually filteringSelect doesn't warn user for its wrong insertion. You can add a warning for the user through a "validate" attribute (see :ref:`validations-validations`).
	
	Let's see a demo:
	
	#NISO add online demo!
	
	.. _filteringSelect-attributes:

Attributes
==========

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``ignoreCase``     | If True, user can write in filteringSelect      |  ``True``                |
	|                    | ignoring case                                   |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``values``         | Contains all the entries from which users       |  ``None``                |
	|                    | have to choose                                  |                          |
	+--------------------+-------------------------------------------------+--------------------------+

	.. _filteringSelect-other-attributes:

Common attributes
=================

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``disabled``       | If True, user can't act on the filteringSelect. |  ``False``               |
	|                    | For more details, see :ref:`common-disabled`    |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the filteringSelect.                       |  ``False``               |
	|                    | See :ref:`common-hidden`                        |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for filteringSelect's values.        |  ``None``                |
	|                    | For more details, see :ref:`common-datapath`    |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	