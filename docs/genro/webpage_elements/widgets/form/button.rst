	.. _genro-button:

========
 button
========

	- :ref:`button-definition-description`

	- :ref:`button-examples`: :ref:`button_example_action`, :ref:`button_example_fire`

	- :ref:`button-attributes`

	- :ref:`button-other-attributes`

	.. _button-definition-description:

Definition and Description
==========================

	Same definition of Dojo button. To show it, click here_.

	.. _here: http://docs.dojocampus.org/dijit/form/Button

	Button is a Dojo widget used as a representation of an html button. You may define its purpose through the "action" attribute (explained below), a javascript command executed by clicking on the button itself.

	.. _button-examples:

Examples
========

.. _button_example_action:

The action attribute
====================

	We show here a simple button::

		pane.button('Button',action="alert('Hello!')")

.. _button_example_fire:

The FIRE command
================
	
	You can also use ``FIRE`` within "action" attribute: it will launch an alert message. The syntax is::
	
		action="FIRE 'javascript command'"
	
	So, you can create an example using a button with the ``FIRE`` command combined with a dataController, using the following syntax::
	
		pane.dataController('write-JS-Here!',_fired="^startJS")     # in place of "write-JS-here" you have
		                                                            #     to write some Javascript code
		pane.button('Unleash the dataController!',fire='^startJS')  # when this button is clicked, the JS wrote in the
		                                                            #     dataController will be executed
		
	We now show you two different syntax to do the same thing:

	**syntax 1**::

		pane.dataController('''alert(msg);''', msg='^msg')
		pane.button('Click me!',action="FIRE msg='Click!';")

	**syntax 2**::

		pane.dataController('''alert(msg);''', msg='^msg')
		pane.button('Click me!', fire_Click = 'msg')
	
	It is important for you to know that the ``FIRE`` command in the button is a shortcut for a script that puts ``True`` in the destination path (allowing to the action of the button to be executed) and then put again ``False`` (allowing to the button to be reusable!).

	In Genro there are four macros used as a shortcut that you can use in place of a Javascript command. They are ``FIRE``, ``GET``, ``SET``, ``PUT``. For more details, check the :ref:`genro-datastore` page.

	.. _button-attributes:

Button attributes
=================

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``action``         | Starts a Javascript command                     |  ``#NISO???``            |
	+--------------------+-------------------------------------------------+--------------------------+
	
	.. _button-other-attributes:
	
Common attributes
=================

	Here we list all the attributes that belong both to button and to other widgets. Click on them for a complete documentation:
	
	* :ref:`genro-disabled`
	* :ref:`genro-hidden`
	* :ref:`genro-label`
	* value: check the :ref:`genro-datapath` page
	