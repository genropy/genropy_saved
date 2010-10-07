	.. _database-table:

=======
 Table
=======

- :ref:`table-definition`

- :ref:`table-description`

- :ref:`table-examples`

	.. _table-definition:

Definition
==========

	???

	.. _table-description:

Description
===========

	??? Introdurre l'attributo rowcaption e mettere il link alla pagina relativa per maggiori informazioni (:ref:`database-rowcaption`).
	
	??? Descrivere bene il "@"!!!

	.. _table-examples:

Examples
========

	Let's see a first example::

		# encoding: utf-8
		
		class Table(object):
			def config_db(self, pkg):
				tbl = pkg.table('person',pkey='id',name_long='!!people',
				                 name_plural='!!People',rowcaption='$name')
				tbl.column('id',size='22',group='_',readOnly=True,name_long='Id')
				tbl.column('name', name_short='N.', name_long='Name')
				tbl.column('year', 'L', name_short='Yr', name_long='Birth Year')
				tbl.column('nationality', name_short='Ntl',name_long='Nationality')
				tbl.column('number','L',name_long='!!Number')
	 