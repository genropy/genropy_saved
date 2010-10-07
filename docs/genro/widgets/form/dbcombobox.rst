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

	.. _dbcombobox-definition:

Definition
==========

	Here we report dbCombobox's definition::
		
		def nameOfObject(args): #NISO ???

	.. _dbcombobox-where:

Where
=====

	You can find dbcombobox in *genro/gnrpy/...* #NISO ???

	.. _dbcombobox-description:

Description
===========

	The Genro dbCombobox is a :ref:`form-combobox` that conducts research on specific columns in a database table.

	The main feature is that dbCombobox, unlike the :ref:`form-dbselect`, permits to enter new values not yet in the database.

	While user write in the dbCombobox, partially matched values will be shown in a pop-up menu below the input text box.

	The only way to specify the table related to the dbCombobox is using the :ref:`common-dbtable` attribute.
	
	???
	< #NISO >
	Inoltre è possibile aggiungere diversi parametri chiamati formati dal prefisso "selected" e dal nome di una colonna della table, nel quale specificare il datapath, dove salvare i rispettivi dati del record selezionato con il dbCombobox.
	</ #NISO>
	
	
	la dbcombobox ha gli stessi parametri della dbselect, però permette di scegliere tra elementi anche non previsti nel database (NON è che i valori che non sono nel database vengonno aggiunti nel database, PERO' dà la possibilità di metterli! Tanto salva per valori, non ha le chiavi! Quindi è una figata, magari mettere un esempio in cui nel database ci sono tutte le città italiane, e uno può aggiungere una località strana cazzuta che non è contemplata nel databse)

	.. _dbcombobox-examples:

Examples
========

	Let's see a code example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				fb=pane.formbuilder(datapath='test1',cols=2)
				???

	Let's see a demo:

	#NISO add online demo! ???

	.. _dbcombobox-attributes:

Attributes
==========

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``alternatePkey``  | #NISO                                           |  ``None``                |
	|                    | ???                                             |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``auxColumns``     | Show in a pop-up menu below the input textbox   |  ``None``                |
	|                    | i parametri di ricerca (vuole obbligato columns)|                          |
	|                    | (campi di pura visualizzazione) ???             |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``columns``        | Specify the columns on which will be made the   |  ``None``                |
	|                    | query ???                                       |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``dbtable``        | MANDATORY - Select the database                 |  ``None``                |
	|                    | :ref:`database-table` for dbCombobox query. For |                          |
	|                    | further details, see :ref:`common-dbtable`      |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``limit``          | Set the number of visible choices on the pop-up |  ``10``                  |
	|                    | menu below the input textbox during user typing |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``rowcaption``     | Allow user to view records through              |  ``None``                |
	|                    | :ref:`name-name_long` value.                    |                          |
	|                    | Without ``rowcaption``, user will see value ID. |                          |
	|                    | Check for more information on                   |                          |
	|                    | :ref:`database-rowcaption` page                 |                          |
	+--------------------+-------------------------------------------------+--------------------------+

	??? <i>auxColumns</i> le colonne aggiuntive che vengono mostrate nel menu popup delle opzioni trovate<br/>

	.. _dbcombobox-other-attributes:

Common attributes
=================

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``disabled``       | If True, user can't act on the dbcombobox.      |  ``False``               |
	|                    | For more details, see :ref:`common-disabled`    |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the dbcombobox.                            |  ``False``               |
	|                    | See :ref:`common-hidden`                        |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for dbcombobox's values.             |  ``None``                |
	|                    | For more details, see :ref:`common-datapath`    |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	
