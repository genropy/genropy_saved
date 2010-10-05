	.. _form-dbcombobox:

============
 DbCombobox
============

.. currentmodule:: dbcombobox

.. class:: dbcombobox - Genropy dbcombobox

	- :ref:`dbcombobox-definition`

	- :ref:`dbcombobox-where`

	- :ref:`dbcombobox-description`

	- :ref:`dbcombobox-examples`

	- :ref:`dbcombobox-attributes`

	- :ref:`dbcombobox-other-attributes`

	- :ref:`dbcombobox-features`

		- :ref:`dbcombobox-first-reference`
		- :ref:`dbcombobox-second-reference`

	.. _dbcombobox-definition:

Definition
==========

	dbCombobox is a :ref:`form-combobox` that research values from a database table.

	.. _dbcombobox-where:

Where
=====

	You can find dbcombobox in *genro/gnrpy/...* ???

	.. _dbcombobox-description:

Description
===========

	The Genro dbCombobox is a :ref:`form-combobox` that conducts research on specific columns in a database table. As the user types, partially matched values will be shown in a pop-up menu below the input text box. The main feature is that dbCombobox, unlike the :ref:`form-dbselect`, permits to enter new values not yet in the database.

	.. _dbcombobox-examples:


	- attributi:
			auxColumns 		--> visualizza nella tendina i parametri di ricerca (vuole obbligato columns)
				       	    (campi di pura visualizzazione)
			columns		--> query fields
			limit='NUMBER'	--> pone il numero di campi visibili nel menu a scorrimento per la scelta
					    	    (di default è limit='10')
			alternatePkey=''	--> ???
			lbl='nome'		--> the label… (dbSelect doesn't have "label" attribute!!)
			zoom=True		--> serve per andare ad aprire il record collegato (all'id)
						    nella sua standard table (di default zoom è True!!)

	It's a filteringSelect that get data from a database's table.
    
    dbtable     The name of table you want to use as source
    columns     what fields you use for your search
    auxColumns  the columns you want to see but you don't want to search in


Examples
========

	Let's see a code example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				fb=pane.formbuilder(datapath='test1',cols=2)
				??

	Let's see a demo:

	#NISO add online demo!

	.. _dbcombobox-attributes:

Attributes
==========

	I parametri di dbCombobox sono:
	<i>dbtable</i> ovvero la table del database a cui si riferisce la ricerca, espressa col path package.table.<br/>
	<i>columns</i> ovvero le colonne sulle quali viene effettuata la ricerca.<br/>
	<i>auxColumns</i> le colonne aggiuntive che vengono mostrate nel menu popup delle opzioni trovate<br/>
	Inoltre è possibile aggiungere diversi parametri chiamati formati dal prefisso <i>selected_</i> 
	e dal nome di una colonna della table, nel quale specificare il datapath, dove salvare i rispettivi 
	dati del record selezionato con il dbCombobox.
	
	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``??``             | ??                                              |  ``??``                  |
	+--------------------+-------------------------------------------------+--------------------------+
	
	.. _dbcombobox-other-attributes:

Common attributes
=================

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``datapath``       | Set path for data.                              |  ``None``                |
	|                    | For more details, see :ref:`common-datapath`    |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``disabled``       | If True, user can't act on the dbcombobox.      |  ``False``               |
	|                    | For more details, see :ref:`common-disabled`    |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the dbcombobox.                            |  ``False``               |
	|                    | See :ref:`common-hidden`                        |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for dbcombobox's values.             |  ``None``                |
	|                    | For more details, see :ref:`common-datapath`    |                          |
	+--------------------+-------------------------------------------------+--------------------------+

	.. _dbcombobox-features:

Other features
==============

	.. _dbcombobox-first-reference:
	
?? Title first reference
===============================================
	
	??
	
	.. _dbcombobox-second-reference:
	
?? Title second reference
===============================================
	
	??