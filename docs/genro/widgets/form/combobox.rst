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

	Checkbox is a graphical user widget that permits the user to select a value from multiple options. The checkbox must have some values between user can choose. To upload these values, you can use two different ways: the Bag-way and the Attribute-way

	.. _some-examples:

Examples
========

	.. _Bag-way:

Fill combobox through a Bag
===========================

	???

	.. _values-attribute:

Fill combobox through "values" attribute
========================================

	???

	Example::

		pane.???(???)
		
	Let's see its graphical result:

	.. figure:: combobox.png


	.. _main-attributes:

Attributes
==========

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
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

	Like a SELECT combo-box, you provide a list of acceptable values. But like an INPUT text field, the user can also type whatever they want. As the user types, partially matched values will be shown in a pop-up menu below the INPUT text box.
    
	On FORM submit, the displayed text value of a non-disabled ComboBox widget is submitted using a native INPUT text box if the name attribute was specified at widget creation time.
    
	ComboBox widgets are dojo.data-enabled. This means rather than embedding all the OPTION tags within the page, you can have dojo.data fetch them from a server-based store. The unified dojo.data architecture can get its data from various places such as databases and web services. See the dojo.data section for complete details.
    
    note: ComboBox only has a single value that matches what is displayed while FilteringSelect incorporates a hidden value that corresponds to the displayed value.
