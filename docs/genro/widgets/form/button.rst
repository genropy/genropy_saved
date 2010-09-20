=========
 Buttons
=========

.. currentmodule:: widgets

.. class:: Buttons -  Genropy buttons

**Definition**: same definition of Dojo buttons (version 1.4). To show it, click here_.

.. _here: http://docs.dojocampus.org/dijit/form/Button

	This is not a real class, but only one way to combine the methods of the struct that implements interface **buttons**

.. method:: button(label[, fire=datapath][, action=javascript][, hidden=boolean or resolver])

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
