	.. _genro-button:

========
 button
========

	- :ref:`button-definition-description`

	- :ref:`button-examples`

	- :ref:`button-attributes`

	- :ref:`button-other-attributes`

	.. _button-definition-description:

Definition and Description
==========================

	Same definition of Dojo button (version 1.5). To show it, click here_.

	.. _here: http://docs.dojocampus.org/dijit/form/Button

	Button is a Dojo widget used as a representation of a normal button. You can act with it through "action" attribute, a javascript executed on mouse click.

	.. _button-examples:

Examples
========

	Example::

		pane.button('Button',action="alert('Hello!')")

	Let's see a demo:

	#NISO add online demo!
	
	You can also use "FIRE" attribute within "action" attribute: `action="FIRE 'javascript command'"`

	Example::

		pane.dataController('''alert(msg);''', msg='^msg')
		pane.button('Click me!',action="FIRE msg='Click!';")

	An alternative syntax is::

		pane.button('Click me!', fire_Click = 'msg')
	
	Example::
	
		top.button('Unleash the dataController!',fire='.add')
        top.dataController("""put some Javascript code here...
                           """,_fired="^.add")
	
	Please note that the ``fire`` attribute in :ref:`genro-button` is a shortcut for a script that puts 'true' in the destination path and then put again false. So for a little while we have a true in that location, that allows to trigger the action of the button.

    In Genro there are four macros used as a shortcut that you can use in place of a Javascript command. They are FIRE, GET, SET, PUT. For more details, see :ref:`genro-datastore`.

	.. _button-attributes:

Attributes
==========

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``action``         | Starts a Javascript command                     |  ``#NISO???``            |
	+--------------------+-------------------------------------------------+--------------------------+
	
	.. _button-other-attributes:
	
Common attributes
=================

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``disabled``       | If True, user can't act on the object.          |  ``False``               |
	|                    | For more details, see :ref:`genro-disabled`     |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the button.                                |  ``False``               |
	|                    | See :ref:`genro-hidden`                         |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``label``          | Set button label.                               |  ``None``                |
	|                    | For more details, see :ref:`genro-label`        |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for button's values.                 |  ``None``                |
	|                    | For more details, see :ref:`genro-datapath`     |                          |
	+--------------------+-------------------------------------------------+--------------------------+
