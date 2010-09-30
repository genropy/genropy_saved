==========
 Combobox
==========

.. currentmodule:: form

.. class:: combobox -  Genropy combobox

	- :ref:`combobox-definition`
	
	- :ref:`combobox-where`
	
	- :ref:`combobox-description`
	
	- :ref:`combobox-examples`
	
		- :ref:`Bag-way`
		- :ref:`values-attribute`
	
	- :ref:`combobox-attributes`
	
	- :ref:`combobox-other-attributes`

	.. _combobox-definition:

Definition
==========

	Genro checkbox is the combination between an HTML checkbox and a Dojo checkbox.

	.. _combobox-where:

Where
=====

	#NISO???

	.. _combobox-description:

Description
===========

	Combobox is a graphical user widget that permits the user to select a value from multiple options.
	
	In combobox you have to provide a list of acceptable values (to upload these values, you can use two different ways: the Bag_-way and the values_-way). But like an input text field, user can also type whatever he wants. As the user types, partially matched values will be shown in a pop-up menu below the input text box.
	
	So, the combobox is like a :doc:`filteringselect`; the difference is that combobox doesn't support keys.

	.. _combobox-examples:

Examples
========

	.. _explanation:

	.. _values:

	.. _combobox-attribute:

Fill combobox through "values" attribute
========================================

	You can add values to combobox using the "values" attribute; check this example for the correct sintax::

		class GnrCustomWebPage(object):
			def test_1_values(self,pane):
				bc = pane.borderContainer(datapath='test1')
				bc.combobox(value='^.record.values',values='Football,Golf,Karate',
					        lbl='loaded from values')

	.. _here:

	Let's see its graphical result:

	.. figure:: combobox.png

	.. _Bag:

	.. _Bag-way:

Fill combobox through a Bag
===========================

	Postponing all info of a ``Bag`` and of a ``data`` on the relative pages of documentation (:doc:`/bag/introduction` and :doc:`/datacontroller/data`), we'll show here how you can add values to ``combobox`` using a ``Bag``.
	
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
				
	The advantage of using a Bag is that you can add attributes to your records, while the info onto ``id`` are lost. For get an example, check ???METTERE IL LINK GIUSTO QUANDO C'E' LA PAGINA.

	The graphical result is the same of the values-way (see it here_).

	.. _combobox-attributes:

Attributes
==========

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``hasDownArrow``   | If True, create the selection arrow             |  ``True``                |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``ignoreCase``     | If True, user can write ignoring the case       |  ``True``                |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``values``         | Set all the possible values for user choice.    |  ``None``                |
	|                    | Check here for explanation_.                    |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	
	.. _`combobox-other-attributes`:
	
Common attributes
=================
	
	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``disabled``       | If True, user can't act on the combobox.        |  ``False``               |
	|                    | For more details, see :doc:`/common/disabled`   |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the combobox.                              |  ``False``               |
	|                    | See :doc:`/common/hidden`                       |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for combobox's values.               |  ``None``                |
	|                    | For more details, see :doc:`/common/datastore`  |                          |
	+--------------------+-------------------------------------------------+--------------------------+
