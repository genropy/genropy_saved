================
 dropdownbutton
================

.. currentmodule:: form

.. class:: dropdownbutton -  Genropy dropdownbutton

	- :ref:`main-definition`
	
	- :ref:`where-is-it-?`
	
	- :ref:`A-brief-description`
	
	- :ref:`some-examples`
	
	- :ref:`main-attributes`

	.. _main-definition:

Definition
==========

	same definition of Dojo dropdownbuttons (version 1.5). To show it, click here_.

	.. _here: http://docs.dojocampus.org/dijit/form/DropDownButton

	.. _where-is-it-?:

Where
=====

	#NISO???

	.. _A-brief-description:

Description
===========

	Constructs a button that opens a ``menu`` or a ``tooltipdialog``.

	.. _some-examples:

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

	.. _main-attributes:

Attributes
==========

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
