================
 Dropdownbutton
================

.. currentmodule:: form

.. class:: dropdownbutton -  Genropy dropdownbutton

	- :ref:`dropdownbutton-definition`
	
	- :ref:`dropdownbutton-where`
	
	- :ref:`dropdownbutton-description`
	
	- :ref:`dropdownbutton-examples`
	
	- :ref:`dropdownbutton-attributes`

	.. _dropdownbutton-definition:

Definition
==========

	Same definition of Dojo dropdownbuttons (version 1.5). To show it, click here_.

	.. _here: http://docs.dojocampus.org/dijit/form/DropDownButton

	.. _dropdownbutton-where:

Where
=====

	#NISO???

	.. _dropdownbutton-description:

Description
===========

	Constructs a button that opens a ``menu`` or a ``tooltipdialog``.

	.. _dropdownbutton-examples:

Examples
========

	First example::
	
		def main(self,root,**kwargs):
			ddb=root.dropdownbutton('Menu')    # Same meaning: ddb=root.dropdownbutton(label='Menu')
			dmenu=ddb.menu()
			
	Every menu row is created through "menuline"::
			
			dmenu.menuline('Open...',action="alert('Opening...')")
			dmenu.menuline('Close',action="alert('Closing...')")
			
	For creating a dividing line use the following sintax::
			
			dmenu.menuline('-')
		
	You can also create a menu inside a menu::
		
			submenu=dmenu.menuline('I have submenues').menu()
			submenu.menuline('To do this',action="alert('Doing this...')")
			submenu.menuline('Or to do that',action="alert('Doing that...')")
			dmenu.menuline('-')
			dmenu.menuline('Quit',action="alert('Quitting...')")

	Let's see its graphical result:

	.. figure:: dropdownbutton.png
	
	.. _dropdownbutton-attributes:

Common Attributes
=================

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``disabled``       | If True, user can't act on the dropdownbutton.  |  ``False``               |
	|                    | For more details, see :doc:`/common/disabled`   |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the dropdownbutton.                        |  ``False``               |
	|                    | See :doc:`/common/hidden`                       |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``label``          | Set dropdownbutton label.                       |  ``None``                |
	|                    | For more details, see :doc:`/common/label`      |                          |
	+--------------------+-------------------------------------------------+--------------------------+
