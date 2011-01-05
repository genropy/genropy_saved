	.. _genro-filteringselect:

=================
 filteringSelect
=================

	- :ref:`filteringselect-definition-description`

	- :ref:`filteringselect-examples`: :ref:`bag-example`, :ref:`values-example`

	- :ref:`filteringSelect_attributes`

	- :ref:`filteringselect-other-attributes`

	.. _filteringselect-definition-description:

Definition and Description
==========================

	The filteringSelect is a text field who suggests to user the possible (and unique!) entries of his selection.

	FilteringSelect's values are composed by a key and a value (like the Python dictionary's elements): user can chooses from values, while in :ref:`genro-datastore` the user's choice is saved through keys. User can also freely type text and partially matched values will be shown in a pop-up menu below the input text box.
	
	If user types a wrong entry (that is a word that doesn't corresponds to any of the filteringSelect values) the key in :ref:`genro-datastore` will be saved as ``undefined``.

	.. _filteringselect-examples:

Examples
========

	The main two modes to fill a filteringSelect are:
	
	* Filling a filteringSelect through a :ref:`genro-bag-intro`
	* Filling a filteringSelect through "values" attribute
	
	.. _bag-example:
	
Filling a filteringSelect through a Bag
=======================================

	In this example we show you how to fill a filteringSelect through a Bag:
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
					root.filteringSelect(value='^sport',
					                     values="""SC:Soccer,BK:Basket,HK:Hockey,
					                               TE:Tennis,BB:Baseball,SB:Snowboard""")
	
	.. note:: Pay attention not to confuse ``value`` with ``values``: ``value`` is used to allocate user data in a well determined :ref:`genro-datapath`, while ``values`` is used to fill the filteringSelect.
	
	.. warning:: Unlike Dojo, actually filteringSelect doesn't warn user for its wrong insertion. You can add a warning for the user through a "validate" attribute (see :ref:`genro-validations`).

	.. _filteringSelect_attributes:

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

	.. _filteringselect-other-attributes:

Common attributes
=================
	
	Here we list all the attributes that belong both to filteringSelect and to other widgets. Click on them for a complete documentation:
	
	* :ref:`genro-disabled`
	* :ref:`genro-hidden`
	* value: check the :ref:`genro-datapath` page
	
	You can't use the ``label`` attribute; if you want to give a label to your filteringSelect you have to:
	
		#. create a form (use the :ref:`genro-formbuilder` form widget)
		#. append the filteringSelect to the formbuilder
		#. use the formbuilder's ``lbl`` attribute on your filteringSelect.
	
		**Example**::
			
			class GnrCustomWebPage(object):
				def main(self,root,**kwargs):
					fb = root.formbuilder(cols=2)
					fb.filteringSelect(value='^sport',lbl='Sport',
					                   values="""SC:Soccer,BK:Basket,HK:Hockey,
					                             TE:Tennis,BB:Baseball,SB:Snowboard""")
