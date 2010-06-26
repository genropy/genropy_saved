####################################################################
:mod:`gnr.core.gnrcmd` -- Strumenti per costruire command-line tools
####################################################################

.. automodule:: gnr.core.gnrcmd

Autodiscovery
*************

E' uno strumento per avere informazioni sui progetti, istanze, siti, packages
e comandi disponibili nell'ambiente run-time di GenroPy.

I risultati sono sensibili alla cartella corrente, rendendo semplice scrivere
intuitivi strumenti per l'esecuzione da linea di comando.

.. autoclass:: AutoDiscovery
	:members:

Utilities
*********

.. autofunction:: expandpath

.. autoclass:: ProgressBar
	:members: