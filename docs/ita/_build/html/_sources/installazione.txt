***************
 Installazione
***************

Prerequisiti
============

Per utilizare GenroPy, avrete bisogno almeno di:

- sistema operativo Mac o Linux (non ho esperienza con Windows)
- Python 2.6
- Postgres 8
- subversion (e magari git)

Se non l'avete già, installate **easy_install** così::

	curl -O http://peak.telecommunity.com/dist/ez_setup.py
	sudo python ez_setup.py
	# oppure in Ubuntu
	sudo apt-get install python-setuptools

Serviranno anche **psycopg2** e **paver**, installabili con *easy_install*::

	sudo easy_install -U -Z psycopg2
	# oppure in Ubuntu
	sudo apt-get install python-psycopg2

Per installare *paver*::

	sudo easy_install -U -Z paver

(``-U`` = upgrade, ``-Z`` = always unzip)

Ottenere GenroPy
================

Il repository di GenroPy è basato su subversion, però vi consiglio di usare git così da poter tener traccia delle modifiche fatte localmente. Per ottenere genropy, scrivete::

	svn co http://svn.genropy.org/genro/trunk genro

In alternativa, usando git (se avete tanto tempo a disposizione)::

	git svn clone http://robertolupi@svn.genropy.org/genro/trunk genro

Installare GenroPy
==================

Il grosso è fatto, ora meglio lasciar il campo libero a *paver*::

	cd genro
	cd gnrpy
	sudo paver develop

Configurare GenroPy
===================

GenroPy utilizza ``.gnr`` per la configurazione::

	cd ../example_configuration/
	cp -a moveto.gnr $HOME/.gnr

Utilizzate poi il vostro editor preferito per modificare ``environment.xml``, ``siteconfig/default.xml`` e ``instanceconfig/default.xml``.

Provare l'installazione
=======================

GenroPy include alcuni progetti di prova:

- Una raccolta un po' disorganizzata ma completa di esempi (package: **showcase**, istanza: **showcase**, sito: **testgarden**)
- Un semplice programma di fatturazione (package: **invoices**, istanza e sito: **fatture1**)

Il primo è stato un po' trascurato, il codice ha bisogno di essere sistemato (per quanto, vi consiglio di dare un'occhaita alla sezione tutorial).

Ad esempio, per provare il secondo potete procedere così per creare il database e poi lanciare un webserver di sviluppo::

	gnrdbsetup -i fatture1
	gnrwsgiserve -s fatture1
