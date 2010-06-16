=========
 Bottoni
=========

.. function:: parent.button(label[, fire=datapath][, action=javascript][, hidden=boolean or resolver])

	Costruisce un bottone usando il tag HTML ``button``.

.. function:: parent.dropdownbutton(label)

	Costruisce un bottone che apre un ``menu`` o un ``tooltipdialog``.
	
	Esempio::
	
		def ddButtonPane(self, cp):
			dd = cp.dropdownbutton('prova')
			dd.tooltipdialog().div('Hello, world!')
