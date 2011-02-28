.. _genro_filteringselect:

===============
filteringSelect
===============

    .. note:: The Genro filteringSelect has been taken from Dojo without adding any modifies. In this page you will find some interesting features that we want to point up. For more information, check the Dojo's filteringSelect_ documentation.

    .. _filteringSelect: http://docs.dojocampus.org/dijit/form/FilteringSelect

	* :ref:`filteringselect_def`
	* :ref:`filteringselect_description`
	* :ref:`filteringSelect_attributes`
	* :ref:`filteringselect_examples`: :ref:`bag_example`, :ref:`values_example`
	
.. _filteringselect_def:

Definition
==========

	.. method:: pane.filteringSelect([**kwargs])

.. _filteringselect_description:

Description
===========

	The filteringSelect is a Dojo widget who suggests to user the possible (and unique!) entries of his selection.

	FilteringSelect's values are composed by a key and a value (like the Python dictionary's elements): user can chooses from values, while in :ref:`genro_datastore` the user's choice is saved through keys. User can also freely type text and partially matched values will be shown in a pop-up menu below the input text box.
	
	If user types a wrong entry (that is a word that doesn't corresponds to any of the filteringSelect values) the key in :ref:`genro_datastore` will be saved as ``undefined``.

.. _filteringSelect_attributes:

Attributes
==========

	**filteringSelect attributes**:
	
	* ``ignoreCase``: If True, user can write in filteringSelect ignoring the case. Default value is ``True``.
	
	To fill a filteringSelect, you can use one of these two attributes:
	
	* ``storepath``: specify a path from which the filteringSelect will get values. For more information, check the :ref:`bag_example` example.
	* ``values``: Set all the possible values for user choice. For more information, check the example below_.
	
	**Common attributes**:
		
	* ``disabled``: if True, allow to disable this widget. Default value is ``False``. For more information, check the :ref:`genro_disabled` documentation page
	* ``hidden``: if True, allow to hide this widget. Default value is ``False``. For more information, check the :ref:`genro_hidden` documentation page
	* ``label``: You can't use the ``label`` attribute; if you want to give a label to your widget, check the :ref:`lbl_formbuilder` example
	* ``value``: specify the path of the widget's value. For more information, check the :ref:`genro_datapath` documentation page
	* ``visible``: if False, hide the widget (but keep a place in the :ref:`genro_datastore` for it). For more information, check the :ref:`genro_visible` documentation page

	You can't use the ``label`` attribute; if you want to give a label to your filteringSelect you have to:

.. _filteringselect_examples:

Examples
========

	The main two modes to fill a filteringSelect are:
	
	* :ref:`bag_example`
	* :ref:`values_example`
	
.. _bag_example:
	
Filling a filteringSelect through a Bag
=======================================

	In this example we show you how to fill a filteringSelect through a :ref:`genro_bag_intro`:
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
	
	.. warning:: Unlike Dojo, actually filteringSelect doesn't warn user for its wrong insertion. You can add a warning for the user through a "validate" attribute (see :ref:`genro_validations`).