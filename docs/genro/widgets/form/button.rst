========
 Button
========

.. currentmodule:: form

.. class:: button -  Genropy button

	- :ref:`main-definition`

	- :ref:`where-is-it-?`

	- :ref:`A-brief-description`

	- :ref:`some-examples`

	- :ref:`main-attributes`

	- :ref:`common-attributes`

	.. _main-definition:

Definition
==========

	Same definition of Dojo button (version 1.5). To show it, click here_.

	.. _here: http://docs.dojocampus.org/dijit/form/Button
	
	.. _where-is-it-?:

Where
=====

	#NISO ???

	.. _A-brief-description:

Description
===========

	Button is a Dojo widget used as a representation of a normal button.
	
	You can act with it through "action" attribute, a javascript executed on mouse click.

	.. _some-examples:

Examples
========

	Example::

		pane.button('Button',action="alert('Hello!')")

	Let's see its graphical result:

	.. figure:: button.png
	
	You can also use "FIRE" attribute within "action" attribute: `action="FIRE 'javascript command'"`

	Example::

		pane.dataController('''alert(msg);''', msg='^msg')
		pane.button('Click me!',action="FIRE msg='Click!';")

	An alternative sintax is::

		pane.button('Click me!', fire_Click = 'msg')

    In Genro there are four macros used as a shortcut that you can use in place of a Javascript command. They are FIRE, GET, SET, PUT. For more details, see :doc:`/common/datastore`.

	.. _main-attributes:

Attributes
==========

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``action``         | Starts a Javascript command                     |  ``#NISO???``            |
	+--------------------+-------------------------------------------------+--------------------------+
	
	.. _`common-attributes`:
	
Common attributes
=================

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``disabled``       | If True, user can't act on the object.          |  ``False``               |
	|                    | For more details, see :doc:`/common/disabled`   |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the button.                                |  ``False``               |
	|                    | See :doc:`/common/hidden`                       |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``label``          | Set button label.                               |  ``None``                |
	|                    | For more details, see :doc:`/common/label`      |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for button's values.                 |  ``None``                |
	|                    | For more details, see :doc:`/common/datastore`  |                          |
	+--------------------+-------------------------------------------------+--------------------------+
