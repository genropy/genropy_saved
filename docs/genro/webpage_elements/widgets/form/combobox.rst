	.. _genro-combobox:

==========
 combobox
==========

	- :ref:`combobox-definition-description`

	- :ref:`combobox-examples`: :ref:`Bag-way`, :ref:`values-attribute`

	- :ref:`combobox-attributes`
	
	- :ref:`combobox-other-attributes`

	.. _combobox-definition-description:

Definition and Description
==========================

	Genro checkbox is the combination between an HTML checkbox and a Dojo checkbox.

	Combobox is a graphical user widget that permits the user to select a value from multiple options.
	
	In combobox you have to provide a list of acceptable values: to upload them, you can use a Bag_ or you can use the values_ attribute. As the user types, partially matched values will be shown in a pop-up menu below the input text box. Like an input text field, user can also type values that doesn't belong to the list of accetable ones.
	
	The combobox looks like a :ref:`genro-filteringselect`: the only difference is that it doesn't support keys.

	.. _combobox-examples:

Examples
========

	.. _explanation:
	
	.. _values:
	
	.. _values-attribute:

Fill combobox through "values" attribute
========================================

	You can add values to combobox using the "values" attribute; check this example for the correct syntax::
	
		class GnrCustomWebPage(object):
			def test_1_values(self,pane):
				bc = pane.borderContainer(datapath='test1')
				fb = bc.formbuilder()
				fb.combobox(value='^.record.values',values='Football,Golf,Karate',
					        lbl='loaded from values')

	.. _here:
	
	.. _Bag:
	
	.. _Bag-way:

Fill combobox through a Bag
===========================

	Postponing all info of a ``Bag`` and of a ``data`` on the relative pages of documentation (:ref:`genro-bag-intro` introduction page and :ref:`genro-data` page), we'll show here how you can add values to ``combobox`` using a ``Bag``.
	
	Example::

		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				bc = root.borderContainer(datapath='test1')
				bc.data('.values.sport',self.sports(),id='.pkey',caption='.Description')
				bc.combobox(value='^.record.Bag',storepath='.values.sport',lbl='loaded from Bag')

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
				
	The advantage of using a Bag is that you can add attributes to your records, but you lose the keys (they aren't supported from combobox).
	
	.. _combobox-attributes:

Combobox attributes
===================

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``hasDownArrow``   | If True, create the selection arrow             |  ``True``                |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``ignoreCase``     | If True, user can write ignoring the case       |  ``True``                |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``values``         | Set all the possible values for user choice.    |  ``None``                |
	+--------------------+-------------------------------------------------+--------------------------+
	
	.. _`combobox-other-attributes`:
	
Common attributes
=================
	
	Here we list all the attributes that belong both to combobox and to other widgets. Click on them for a complete documentation:
	
	* :ref:`genro-disabled`
	* :ref:`genro-hidden`
	* value: check the :ref:`genro-datapath` page
	
	You can't use the ``label`` attribute; so if you want to give a label to your combobox you have to use a :ref:`genro-formbuilder`, then you have to insert the combobox in the formbuilder using the formbuilder's ``lbl`` attribute on your combobox.
	