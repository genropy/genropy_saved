=================
 dropdownbuttons
=================

.. currentmodule:: form

.. class:: dropdownbuttons -  Genropy dropdownbuttons

**Definition**: same definition of Dojo dropdownbuttons (version 1.4). To show it, click here_.

.. _here: http://docs.dojocampus.org/dijit/form/DropDownButton


.. method:: dropdownbutton(label)

	Constructs a button that opens a ``menu`` or a ``tooltipdialog``.
			
		Example::
	
			def ddButtonPane(self, cp):
				dd = cp.dropdownbutton('test')
				dd.tooltipdialog().div('Hello, world!')