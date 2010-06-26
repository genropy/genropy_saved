Selection Handler
=================


.. method:: selectionHandler(self, bc, nodeId, table, datapath, struct, label, selectionPars, dialogPars, ...)

	Un componente che mostra records in una griglia e ne consente la modifica tramite una finestra di dialogo.

	:param bc:			borderContainer -- parent
	:param nodeId:		string
	
		- the dialog ID will be *nodeId* + ``_dlg``
		- the form ID will be *nodeId* + ``_form``
		
	:param table:		table name
	:param datapath:	datapath
	:param struct:		struct or callable
	:param label:		string or callable
	:param selectionPars:		dict -- selection parameters
	:param dialogPars:			dict -- dialog parameters
	:param reloader:			datapath
	:param externalChanges:
	:param hiddencolumns:
	:param custom_addCondition:
	:param custom_delCondition:
	:param askBeforeDelete:
	:param checkMainRecord:
	:param onDeleting:
	:param dialogAddRecord:
	:param onDeleted:
	:param add_enable:
	:param del_enable:
	:param parentSave:
	:param parentId:
	:param parentLock:
	:param **kwargs:

..  def selectionHandler(self,bc,nodeId=None,table=None,datapath=None,struct=None,label=None,
                         selectionPars=None,dialogPars=None,reloader=None,externalChanges=None,
                         hiddencolumns=None,custom_addCondition=None,custom_delCondition=None,
                         askBeforeDelete=True,checkMainRecord=True,onDeleting=None,dialogAddRecord=True,
                         onDeleted=None,add_enable=True,del_enable=True,
                         parentSave=False,parentId=None,parentLock='^status.locked',
                         **kwargs):

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

	* ``foo_frm`` per la form	
	* ``foo_dlg`` nodeId della finestra di dialogo

