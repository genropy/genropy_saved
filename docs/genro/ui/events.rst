Eventi
======

Caricamento dei record
**********************

.. method:: page.onLoading(self, record, newrecord, loadingParameters, recInfo)
.. method:: page.onLoading_package_table(self, record, newrecord, loadingParameters, recInfo)

	:param record: |Bag|
	:param newrecord: boolean
	:param loadingParameters: |Bag| or dict
	:param recInfo: dict

	La bag ``record`` può essere manipolata per alterare i dati che vengono forniti al client.

 	``recInfo`` contiene i metadati del record, è utilizzata dal framework per determinare quale comportamento
	adottare in varie situazioni. ``recInfo`` può contenere i seguenti valori:
	
		``_alwaysSaveRecord`` -- controlla il comportamento durante il salvataggio.
			* ``False`` (default) -- quando l'utente inserice un nuovo record e subito dopo salva (senza fare modifiche),
			  non viene salvato alcun record nel database.
			* ``True`` -- se l'utente inserisce un nuovo record poi salva senza apportare modifiche, viene sempre
			  creato un nuovo record.