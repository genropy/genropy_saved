.. _genro_menu:

====
menu
====

	.. note:: To create a menu, you have to use the ``dropdownbutton`` widget. Go the :ref:`genro_dropdownbutton` page for further details on it.
	
	- :ref:`menu_definition_description`
	
	- :ref:`menu_attributes`
	
	- :ref:`menu_examples`
	
.. _menu_definition_description:
	
Definition and Description
==========================

	.. method:: dropdownbutton.menu()

	Constructs a button that opens a :ref:`genro_menu` or a ``tooltipdialog``.

	* You can create a *menu* with::

		ddb = pane.dropdownbutton('NameOfTheMenu')
		menu = ddb.menu()

	* Every *menuline* is created through the ``menuline`` attribute:

		.. method:: menu.menuline(label, action='JavascriptCode'[,**kwargs])

	 where the first parameter is the label, whie the second one is the :ref:`button_action` attribute (an attribute of the :ref:`genro_button` widget) ::

		menuline('Open...',action="alert('Opening...')")

	* To create a dividing line use ``-`` in a ``menuline`` in place of its label::

		menuline('-')

.. _menu_attributes:

Attributes
==========
	
	**menu attributes**:
	
		There aren't particular attributes.
	
	**common attributes**:
	
	* *disabled*: if True, allow to disable this widget. Default value is ``None``. For more information, check the :ref:`genro-disabled` documentation page
	* *hidden*: if True, allow to hide this widget. Default value is ``None``. For more information, check the :ref:`genro-hidden` documentation page
	* *label*: You can't use the ``label`` attribute; if you want to give a label to your widget, you have to give it to the dropdownbutton. Check the following_ example.

.. _menu_examples:

Examples
========

.. _following:

	**Example**::

		def main(self,root,**kwargs):
			ddb = pane.dropdownbutton('Menu')    # Same meaning: ddb=pane.dropdownbutton(label='Menu')
			dmenu = ddb.menu()
			dmenu.menuline('Open...',action="alert('Opening...')")
			dmenu.menuline('Close',action="alert('Closing...')")
			dmenu.menuline('-')
			submenu = dmenu.menuline('I have submenues').menu() # With this line you create a submenu
			submenu.menuline('To do this',action="alert('Doing this...')")
			submenu.menuline('Or to do that',action="alert('Doing that...')")
			dmenu.menuline('-')
			dmenu.menuline('Quit',action="alert('Quitting...')")
	