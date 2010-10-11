	.. _genro-dbselect-dbcombobox:

==========================================
 dbSelect and dbCombobox: common features
==========================================

.. currentmodule:: form

.. class:: dbFormWidgets -  Genropy dbFormWidgets

	- :ref:`db-description`
	
	- :ref:`db-common-attributes`
	
	- :ref:`db-examples`: :ref:`db-selected`, :ref:`db-condition`, :ref:`db-columns` and :ref:`db-auxColumns`

	.. _db-description:

Description
===========

	dbSelect and dbCombobox are form widgets used to handle database user queries.

	- :ref:`form-dbselect`

	- :ref:`form-dbcombobox`

	.. _db-common-attributes:

Common attributes
=================

	Here we show the attributes that belong both to dbSelect than to dbCombobox:

	+--------------------+---------------------------------------------------+--------------------------+
	|   Attribute        |          Description                              |   Default                |
	+====================+===================================================+==========================+
	| ``alternatePkey``  | Alternate primary key: allow to save user choice  |  ``None``                |
	|                    | through a different parameter respect to the      |                          |
	|                    | default ID. You can set any other field's         |                          |
	|                    | parameter as alternatePkey                        |                          |
	+--------------------+---------------------------------------------------+--------------------------+
	| ``auxColumns``     | Show in a pop-up menu below the input textbox     |  ``None``                |
	|                    | query parameters (``columns`` is MANDATORY).      |                          |
	|                    | Check :ref:`db-auxColumns` example for further    |                          |
	|                    | details                                           |                          |
	+--------------------+---------------------------------------------------+--------------------------+
	| ``columns``        | Check :ref:`db-columns` for further details       |  ``None``                |
	+--------------------+---------------------------------------------------+--------------------------+
	| ``condition``      | Start a SQL query. Check :ref:`db-condition`      |  ``None``                |
	|                    | example for further details                       |                          |
	+--------------------+---------------------------------------------------+--------------------------+
	| ``dbtable``        | MANDATORY - Select the database                   |  ``None``                |
	|                    | :ref:`database-table` for database widget query.  |                          |
	|                    | For further details, see :ref:`common-dbtable`    |                          |
	+--------------------+---------------------------------------------------+--------------------------+
	| ``disabled``       | If True, user can't act on the form widget.       |  ``False``               |
	|                    | For more details, see :ref:`common-disabled`      |                          |
	+--------------------+---------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the form widget. See :ref:`common-hidden`    |  ``False``               |
	+--------------------+---------------------------------------------------+--------------------------+
	| ``limit``          | Set the number of visible choices on the pop-up   |  ``10``                  |
	|                    | menu below the input textbox during user typing   |                          |
	+--------------------+---------------------------------------------------+--------------------------+
	| ``rowcaption``     | Allow user to view records through                |  ``None``                |
	|                    | :ref:`name-name_long` value.                      |                          |
	|                    | Without ``rowcaption``, user will see value ID.   |                          |
	|                    | Check for more information the                    |                          |
	|                    | :ref:`database-rowcaption` page                   |                          |
	+--------------------+---------------------------------------------------+--------------------------+
	| ``selected``       | You can add different parameters with the sintax: |  ``None``                |
	|                    | ``selected_nameOfATableColumn='datapathFolder'``. |                          |
	|                    | See :ref:`db-selected` example for further details|                          |
	+--------------------+---------------------------------------------------+--------------------------+
	| ``value``          | Set a path for widget's values.                   |  ``None``                |
	|                    | For more details, see :ref:`common-datapath`      |                          |
	+--------------------+---------------------------------------------------+--------------------------+

	.. _db-examples:
	
Examples
========

	.. _db-selected:

Selected
========

	With ``selected`` attribute you can draw multiple attributes to the :ref:`genro-datastore` through a single ``dbSelect`` or ``dbCombobox``; the sintax is ``selected_nameOfATableColumn='datapathFolder'``.

	Example: let's consider a database :ref:`database-table` that includes a list of actors::
	
		# encoding: utf-8

		class Table(object):
			def config_db(self, pkg):
				tbl = pkg.table('person',pkey='id',rowcaption='$name',
				                 name_long='!!people',name_plural='!!People')
				tbl.column('id',size='22',group='_',readOnly=True,name_long='Id')
				tbl.column('name',name_short='N.',name_long='Name')
				tbl.column('year','L',name_short='Yr',name_long='Birth Year')
				tbl.column('nationality',name_short='Ntl',name_long='Nationality')
				tbl.column('number','L',name_long='!!Number')
	
	let's consider also this Genro webpage::

		class GnrCustomWebPage(object):
			def main(self,root):
				fb = root.formbuilder(cols=2,border_spacing='10px',datapath='myform')
				fb.dbSelect(dbtable='showcase.person',value='^.person_id',lbl='Star',
				            selected_name='.name',selected_year='.year')
	
	This dbSelect allows user to choose from the ``table`` "person" an actor; after user choice, this dbSelect will do these things:
	
	- a save of the auctor's ID into the ``Datastore`` at the path: ``/myform/person_id``;
	
	- through the sintax ``selected_name='.name'``, dbSelect will do a save of the value of the actor's column named "name" into the path: ``/myform/name``;
	
	- through the sintax ``selected_year='.year'``, dbSelect will do a save of the value of the actor's column named "year" into the path: ``/myform/year``;
	
	So, for example, if user will choose "Cate Blanchett" from the actors' list, Genro will save the following values in the following folders:

	``/myform/person_id/EuSy8OPJP_Kax4yGokSauw``
	
	``/myform/name/"Cate Blanchett"``
	
	``/myform/year/1969``

	.. _db-condition:
	
Condition
=========

	With ``condition`` attribute you can write a SQL query; let's make an example starting from the previous example (:ref:`db-selected`), so we have a list of actors into a ``table`` called "person"; let's introduce a "movie" ``table`` that contains a lot of title films on which the actors have participated::
	
		# encoding: utf-8
		
		class Table(object):
			def config_db(self, pkg):
				tbl = pkg.table('movie',pkey='id',name_long='!!Movie',
				                 name_plural='!!Movies')#,rowcaption='$title')
				tbl.column('id',size='22',group='_',readOnly=True,name_long='Id')
				tbl.column('title',name_short='Ttl.',name_long='Title',
				            validate_case='capitalize',validate_len='3,40')
				tbl.column('genre',name_short='Gnr',name_long='Genre',
				            validate_case='upper',validate_len='3,10',indexed=True)
				tbl.column('year', 'L', name_short='Yr',name_long='Year',indexed=True)
				tbl.column('nationality', name_short='Ntl', name_long='Nationality')
				tbl.column('description', name_short='Dsc', name_long='Movie description')
				tbl.column('number','L',name_long='!!Number')
	
	The two tables ("movie" and "person") will be linked through a :ref:`database-relation_table` called "cast"::
	
		# encoding: utf-8
		
		class Table(object):
			def config_db(self, pkg):
				tbl = pkg.table('cast',pkey='id',rowcaption='@movie_id.title',
				                 name_long='!!Cast',name_plural='!!Casts')
				tbl.column('id',size='22',group='_',readOnly=True,name_long='Id')
				tbl.column('movie_id',size='22', name_short='Mid', 
				            name_long='Movie id').relation('movie.id',mode='foreignkey')
				tbl.column('person_id',size='22',name_short='Prs', 
				            name_long='Person id').relation('person.id',mode='foreignkey')
				tbl.column('role', name_short='Rl.',name_long='Role')
				tbl.column('prizes', name_short='Priz.',name_long='Prizes', size='40')
				tbl.column('number','L',name_long='!!Number')
		
	Finally, let's introduce a Genro webpage made like this one::
	
		class GnrCustomWebPage(object):
			def main(self,root):
				fb = root.formbuilder(cols=2,border_spacing='10px',datapath='myform')
				fb.dbSelect(dbtable='showcase.person',value='^.person_id',lbl='Star')
				fb.dbSelect(dbtable='showcase.movie',value='^.movie_id',lbl='Movie',
				            condition='$person_id=:pid',condition_pid='=.person_id',
				            alternatePkey='movie_id')
	
	The first dbSelect allows the user to choose an actor from the database. The second dbSelect allows the user to choose from a movie made exclusively by the chosen actor.

	So, ``condition`` has the same meaning of the SQL ``WHERE``. The sintax is:
	
		``condition='$tableColumnName'=:'something'``, where 'something' is the SQL condition, expressed through:
		
		``condition_something='=PathOfValue'``
	
	.. _db-columns:

Columns
=======

	??? se non c'è columns, allora la dbselect ricerca E visualizza attraverso i parametri del rowcaption,
	??? se c'è columns allora ricerca SOLAMENTE per columns, e visualizza SOLO per rowcaption.

	.. _db-auxColumns:

auxColumns
==========

	??? auxColumns: campi di pura visualizzazione aggiunti a quello primario
