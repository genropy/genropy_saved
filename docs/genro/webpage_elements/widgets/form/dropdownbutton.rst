	.. _genro-dropdownbutton:

================
 dropdownbutton
================

	- :ref:`dropdownbutton-definition-description`
	
	- :ref:`dropdownbutton-syntax`

	- :ref:`dropdownbutton-examples`

	- :ref:`dropdownbutton_attributes`

	.. _dropdownbutton-definition-description:

Definition and Description
==========================

	Same definition of Dojo dropdownbuttons (version 1.5). To show it, click here_.

	.. _here: http://docs.dojocampus.org/dijit/form/DropDownButton

	.. _dropdownbutton-where:

	Constructs a button that opens a ``menu`` or a ``tooltipdialog``.

	.. _dropdownbutton-syntax:

Syntax
======

	* You can create a menu with one of the following two lines::
	
		dropdownbutton(label='NameOfTheMenu')
		dropdownbutton('NameOfTheMenu')

	* Every menu row is created through the ``menuline`` attribute::
		
		menuline('Open...',action="alert('Opening...')")
	
	* To create a dividing line use ``-`` in a ``menuline``::

		menuline('-')

	.. _dropdownbutton-examples:

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
			dmenu.menuline('Quit',action="alert('Quitting...')")

.. _dropdownbutton_attributes:

Common attributes
=================

	Here we list all the attributes that belong both to menu and to other widgets. Click on them for a complete documentation:
	
	* :ref:`genro-disabled`
	* :ref:`genro-hidden`
	* :ref:`genro-label`
