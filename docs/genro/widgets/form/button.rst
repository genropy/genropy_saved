=========
 Buttons
=========

.. currentmodule:: form

.. class:: Buttons -  Genropy buttons

**Index:**

	- Definition_
	
	- Where_
	
	- Description_
	
	- Examples_
	
	- Attributes_

.. _Definition:

**Definition**:

	Same definition of Dojo button (version 1.5). To show it, click here_.

	.. _here: http://docs.dojocampus.org/dijit/form/Button
	
.. _Where:

**Where:**

	#NISO ???

.. _Description:

**Description:**

	A simple button.

.. _Examples:

**Examples**:

	Example::

		pane.button('Click me!',value='^button')

	Let's see its graphical result:

	.. figure:: ???.png

.. _Attributes:

**Attributes**:

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``action``         | ???fa partire un comando javascript.            |  ``defaultValue``        |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``disabled``       | See :doc:`/common/attributes`                                              |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``fire``           | ???fire il datapath...                          |  ``defaultValue``        |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``label``          | Set button label                                |  ``None``                |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for button value                     |  ``None``                |
	+--------------------+-------------------------------------------------+--------------------------+



	This is not a real class, but only one way to combine the methods of the struct that implements interface **buttons**


	Button is a Dojo widget used as a representation of a normal button. You can act with it through "action" attribute, a js that is executed on mouse click.

	Example::

		pane.button('Button',action="alert('Hello!')")

	You can also use "FIRE" attribute within "action" attribute (action="FIRE 'javascript command'").

	Here is an example::

		pane.dataController('''alert(msg);''', msg='^msg')
		pane.button('Click me!',action="FIRE msg='Click!';")

	An alternative sintax is::

		pane.button('Click me!', fire_Click = 'msg')

    In Genro there are four macros used as a shortcut that you can use in place of a Javascript command.

	Here is the list: FIRE, GET, SET, PUT.