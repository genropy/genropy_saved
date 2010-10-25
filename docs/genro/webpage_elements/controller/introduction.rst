	.. _genro-controllers-introduction:

=================================
 Introduction to the controllers
=================================

	The Genro controllers allow to execute a script. Follow these links to see the relaative documentation:
	
	- :ref:`genro-datacontroller`
	- :ref:`genro-dataformula`
	- :ref:`genro-datarpc`
	- :ref:`genro-datascript`

Common attributes
=================

	+--------------------+----------------------------------------------------+--------------------------+
	|   Attribute        |          Description                               |   Default                |
	+====================+====================================================+==========================+
	| ``_init``          | Boolean; if True, ... ???                          |  ``None``                |
	|                    |                                                    |                          |
	+--------------------+----------------------------------------------------+--------------------------+
	| ``_onresult``      | Boolean; if True, ... ???                          |  ``None``                |
	|                    |                                                    |                          |
	+--------------------+----------------------------------------------------+--------------------------+
	| ``_onstart``       | Boolean; if True, ... ???                          |  ``None``                |
	|                    |                                                    |                          |
	+--------------------+----------------------------------------------------+--------------------------+
	| ``_timing``        | ... ???                                            |  ``None``                |
	|                    |                                                    |                          |
	+--------------------+----------------------------------------------------+--------------------------+

	???
	_init =    viene eseguita un'azione quando nel codice si arriva a leggere
	           la determinata riga in cui è definito l'init stesso
	_onstart = prima viene letta tutta la pagina, subito dopo viene eseguita l'azione relativa all'onstart;
	           vantaggi rispetto all'init: può essere che l'azione che scatta con l'init utilizzi anche righe che non sono
	           ancora state lette; con "_onstart" si legge tutta la pagina e poi si esegue l'azione
	_timing = 'NUMBER'
	           aggiorna l'operazione di un numero di secondi pari a NUMBER