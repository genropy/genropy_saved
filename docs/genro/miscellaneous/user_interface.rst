==============
User interface
==============

Building Server-side pages
**************************

For building server-side pages, please see :mod:`gnr.core.gnrhtml`.

==========================
Building Client-side pages
==========================

Events
======

Load record
===========

.. method:: page.onLoading(self, record, newrecord, loadingParameters, recInfo)
.. method:: page.onLoading_package_table(self, record, newrecord, loadingParameters, recInfo)

	:param record: |Bag|
	:param newrecord: boolean
	:param loadingParameters: |Bag| or dict
	:param recInfo: dict

	The bag ``record`` can be manipulated to alter the data being supplied to the client.

 	The ``Recinfo`` record contains metadata that is used by the framework to determine which behavior is determined in various situations.  ``RecInfo`` may contain the following values:
	
		``_alwaysSaveRecord`` -- controls the behavior during the rescue.
			* ``False`` (default) -- When a user inserts a new record and immediately saves (without change),
			  then there is no record saved or stored in the database.
			* ``True`` -- if the user inserts a new record then save without making changes, always created a new record.
