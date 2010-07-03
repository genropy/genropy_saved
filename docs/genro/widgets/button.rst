=========
 Bottoni
=========

.. currentmodule:: widgets

.. class:: Buttons -  Genropy buttones

	This is not a real class, but only one way to combine the methods of the struct that implements interface **buttons**

.. method:: button(label[, fire=datapath][, action=javascript][, hidden=boolean or resolver])

	Construct a button using the HTML tag ``button``.

.. method:: dropdownbutton(label)

	Constructs a button that opens a ``menu`` or a ``tooltipdialog``.
	
	Example::
	
		def ddButtonPane(self, cp):
			dd = cp.dropdownbutton('test')
			dd.tooltipdialog().div('Hello, world!')
