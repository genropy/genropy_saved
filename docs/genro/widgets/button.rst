=========
 Bottoni
=========

.. currentmodule:: widgets

.. class:: Buttons -  I bottoni in GenroPy

	Non si tratta di una vera e propria classe, ma solo di un modo per raggruppare i metodi della struct dell'interfaccia che implementano i bottoni.

.. method:: button(label[, fire=datapath][, action=javascript][, hidden=boolean or resolver])

	Costruisce un bottone usando il tag HTML ``button``.

.. method:: dropdownbutton(label)

	Costruisce un bottone che apre un ``menu`` o un ``tooltipdialog``.
	
	Esempio::
	
		def ddButtonPane(self, cp):
			dd = cp.dropdownbutton('prova')
			dd.tooltipdialog().div('Hello, world!')
