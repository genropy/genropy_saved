:mod:`gnr.core.gnrhtml` -- Server-side HTML generations (web pages and printable reports)
*****************************************************************************************

In GenroPy le pagine vengono generalmente costruite lato client: la struttura della pagina viene trasferita come |Bag| e poi la parte Javascript del framework si occupa di costruire il DOM ed i widgets necessari. In questo modo è possibile modificare completamente la pagina semplicemente alterando la |Bag| che la descrive.

E' però possibile costruire completamente la pagina lato server. Risulta utile per far indicizzare le pagine dai motori di ricerca e, soprattutto, per implementare :doc:`/print/index`.

E' ancora possibile utilizzare nelle pagine costruite lato server gli widgets di Dojo, ma in modalità nativa e senza le estenzioni di GenroPy (e.g. le ``dbselect`` non funzionano).

.. automodule:: gnr.core.gnrhtml
	:members:
