.. _genro_menu:

====
menu
====

	.. note:: To create a menu, you have to use the ``dropdownbutton`` widget. Go the :ref:`genro_dropdownbutton` page for further details on it.
	
	- :ref:`menu_definition_description`
	
	- :ref:`menu_syntax`
	
	- :ref:`menu_examples`
	
	- :ref:`menu_attributes`
	
.. _menu_definition_description:
	
Definition and Description
==========================

	Constructs a button that opens a :ref:`genro_menu` or a ``tooltipdialog``.

.. _menu_syntax:

Syntax
======

	* You can create a *menu* with::

		dropdownbutton('NameOfTheMenu')

	* Every *menuline* is created through the ``menuline`` attribute:

	.. method:: menuline(label,[params])

		ddb=pane.dropdownbutton('Menù')
		dmenu=ddb.menu()
		dmenu.menuline('Open...', action="FIRE msg='Opening!';")
		dmenu.menuline('Close', action="FIRE msg='Closing!';")
		dmenu.menuline('-')
		submenu=dmenu.menuline('I have submenues').menu()
		submenu.menuline('To do this', action="alert('Doing this...')")
		submenu.menuline('Or to do that', action="alert('Doing that...')")
		dmenu.menuline('-')
		dmenu.menuline('Quit',action="alert('Quitting...')")

	 where the first parameter is the label, ::

		menuline('Open...',action="alert('Opening...')")
		menuline('')


	* To create a dividing line use ``-`` in a ``menuline``::

		menuline('-')

.. _menu_examples:

Examples
========

	**Example**::

		def main(self,root,**kwargs):
			ddb=root.dropdownbutton('Menu')    # Same meaning: ddb=root.dropdownbutton(label='Menu')
			dmenu=ddb.menu()
			dmenu.menuline('Open...',action="alert('Opening...')")
			dmenu.menuline('Close',action="alert('Closing...')")
			dmenu.menuline('-')
			submenu=dmenu.menuline('I have submenues').menu() # With this line you create a submenu
			submenu.menuline('To do this',action="alert('Doing this...')")
			submenu.menuline('Or to do that',action="alert('Doing that...')")
			dmenu.menuline('-')
			dmenu.menuline('Quit',action="alert('Quitting...')").

Common attributes
=================

	Here we list all the attributes that belong both to dropdownbutton, to menu and to other widgets. Click on them for a complete documentation:
	
	* :ref:`genro-disabled`
	* :ref:`genro-hidden`
	* :ref:`genro-label`
