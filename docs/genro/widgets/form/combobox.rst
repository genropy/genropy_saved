==========
 Combobox
==========

.. currentmodule:: form

.. class:: combobox -  Genropy combobox

Index
*****

	- :ref:`main-definition`
	
	- :ref:`where-is-it-?`
	
	- :ref:`A-brief-description`
	
	- :ref:`some-examples`
	
		- :ref:`Bag-way`
		- :ref:`values-attribute`
	
	- :ref:`main-attributes`

	.. _main-definition:

Definition
==========

	Genro checkbox is the combination between an HTML checkbox and a Dojo checkbox.

	.. _where-is-it-?:

Where
=====

	#NISO???

	.. _A-brief-description:

Description
===========

	Combobox is a graphical user widget that permits the user to select a value from multiple options.
	
	In combobox you have to provide a list of acceptable values (to upload these values, you can use two different ways: the Bag_-way and the values_-way). But like an input text field, user can also type whatever he wants. As the user types, partially matched values will be shown in a pop-up menu below the input text box.
	
	So, the combobox is like a filteringSelect, but combobox doesn't have keys.

	.. _some-examples:

Examples
========

	.. _Bag:

	.. _Bag-way:

Fill combobox through a Bag
===========================

	???

	Example::

		class
			def main(self,root,**kwargs):
				"""Checkbox filled through a Bag"""
				bc = pane.borderContainer(datapath='test2')
				bc.data('.values.sport',self.sports(),id='.pkey',caption='.Description')
				bc.combobox(value='^.record.Bag',storepath='.values.sport',
				lbl='loaded from Bag')

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
	.. _here:
		
	Let's see its graphical result:

	.. figure:: combobox.png

	.. _values:

	.. _values-attribute:

Fill combobox through "values" attribute
========================================

	???

	Example::

		pane.???(???)
		
	The graphical result is the same of the Bag-way (see it here_).

	.. _main-attributes:

Attributes
==========

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``default``        | For setting default combobox value              |  ``None``                |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``disabled``       | If True, user can't act on the combobox.        |  ``False``               |
	|                    | For more details, see :doc:`/common/disabled`   |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hasDownArrow``   | If True, create the selection arrow             |  ``True``                |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the combobox.                              |  ``False``               |
	|                    | See :doc:`/common/hidden`                       |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``ignoreCase``     | If True, user can write ignoring the case       |  ``True``                |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for combobox's values.               |  ``None``                |
	|                    | For more details, see :doc:`/common/datastore`  |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``values``         | Set all the possible values for user choice     |  ``None``                |
	|                    | Check here for explanation_.                    |                          |
	+--------------------+-------------------------------------------------+--------------------------+
