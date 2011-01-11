	.. _genro-filteringselect:

=================
 filteringSelect
=================

	- :ref:`filteringselect-definition-description`
	
	- :ref:`filteringSelect_attributes`
	
	- :ref:`filteringselect-examples`: :ref:`bag_example`, :ref:`values_example`, :ref:`filteringselect_label`
	
	.. _filteringselect-definition-description:

Definition and Description
==========================

	.. note:: The Genro filteringSelect has been taken from Dojo without adding any modifies. In this page you will find some interesting features that we want to point up. For more information, check the Dojo's filteringSelect_ documentation.
	
	.. _filteringSelect: http://docs.dojocampus.org/dijit/form/FilteringSelect

	.. method:: pane.filteringSelect([values='key:value'[, storepath=path[, ignoreCase=True]]])

	The filteringSelect is a Dojo widget who suggests to user the possible (and unique!) entries of his selection.

	FilteringSelect's values are composed by a key and a value (like the Python dictionary's elements): user can chooses from values, while in :ref:`genro-datastore` the user's choice is saved through keys. User can also freely type text and partially matched values will be shown in a pop-up menu below the input text box.
	
	If user types a wrong entry (that is a word that doesn't corresponds to any of the filteringSelect values) the key in :ref:`genro-datastore` will be saved as ``undefined``.

.. _filteringSelect_attributes:

Attributes
==========

	**filteringSelect attributes**:
	
	* *ignoreCase*: If True, user can write in filteringSelect ignoring the case. Default value is ``True``.
	* *values*: Set all the possible values for user choice. Default value is ``None``. For more information, check the example below_.
	
	**Common attributes**:
		
	* *disabled*: if True, allow to disable this widget. Default value is ``None``. For more information, check the :ref:`genro-disabled` documentation page
	* *hidden*: if True, allow to hide this widget. Default value is ``None``. For more information, check the :ref:`genro-hidden` documentation page
	* *label*: You can't use the ``label`` attribute; if you want to give a label to your filteringSelect, check the :ref:`filteringselect_label` example
	* *value*: specify the path of the widget's value. For more information, check the :ref:`genro_datapath` documentation page
	
	You can't use the ``label`` attribute; if you want to give a label to your filteringSelect you have to:

	.. _filteringselect-examples:

Examples
========

	The main two modes to fill a filteringSelect are:
	
	* :ref:`bag_example`
	* :ref:`values_example`
	
.. _bag_example:
	
Filling a filteringSelect through a Bag
=======================================

	In this example we show you how to fill a filteringSelect through a :ref:`genro-bag-intro`:
		::

			class GnrCustomWebPage(object):
				def main(self,root,**kwargs):
					root.data('bag_storepath', self.sports(), id='.pkey', caption='.Description')
					bc = root.borderContainer()
					bc.filteringSelect(value='^bag_value', storepath='bag_storepath')

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
		
		First we fill (and create) a Bag with the "sports" function, then the filteringSelect let the user choose a Bag's value through the storepath, that define the path from which the filteringSelect must to take values. Finally, the user choice will be save at the path: "bag_value".

.. _below:
.. _values_example:

Filling a filteringSelect through "values" attribute
====================================================

	Just add some keys and values with the syntax::
	
		values='key1:value1,key2:value2,...,keyN:valueN'
	
	**Example**::

		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				root.filteringSelect(value='^sport',
				                     values="""SC:Soccer,BK:Basket,HK:Hockey,
				                               TE:Tennis,BB:Baseball,SB:Snowboard""")
	
	.. note:: Pay attention not to confuse ``value`` with ``values``: ``value`` is used to allocate user data in a well determined :ref:`genro_datapath`, while ``values`` is used to fill the filteringSelect.
	
	.. warning:: Unlike Dojo, actually filteringSelect doesn't warn user for its wrong insertion. You can add a warning for the user through a "validate" attribute (see :ref:`genro-validations`).

.. _filteringselect_label:

To label a filteringSelect
==========================

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
