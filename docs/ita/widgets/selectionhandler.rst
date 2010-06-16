Selection Handler
=================

**TODO:** inserire la documentazione autogenerata di selectionhandler()

Datastore
*********
Relativi al ``datapath``.

``.reload``
	usare FIRE per ricaricare i dati dal server

``.status.locked``
	stato del lucchetto (vedi anche parametro ``parentLock``)

``.selection``
	selezione corrente, le varie righe della griglia

``.dlg``
	I dati relativi al ``recordDialog``

``.dlg.record``
	il record corrente

``.selectedId``
	elemento selezionato correntemente. Negli attributi ha tutte le colonne del record corrente (è possibile passare ``hiddenColumns`` a ``selectionhandler()`` per aggiungere altre colonne).

``.struct``
	Struttura della griglia. Può essere cambiata a run-time per aggiungere, togliere o modificare colonne.

``.can_add`` e ``.can_del``
	flag booleani (trattare come sola lettura, leggere il codice del component per vedere come modificarli).

Nomi
****

Dato un ``nodeId`` uguale a ``foo``, i vari componenti vengono nominati nel modo seguente:

# ``foo_frm`` per la form
# ``foo_dlg`` nodeId della finestra di dialogo

