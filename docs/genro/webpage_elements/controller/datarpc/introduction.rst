	.. _genro-datarpc-introduction:

=========================
 Introduction to the Rpc
=========================

	:ref:`rpc-description`

	:ref:`rpc-common-attributes`

	.. _rpc-description:

Description
===========

	- The ``dataRpc`` belongs to :ref:`genro-server-side-controllers` family.

	The ``dataRpc`` is ...???

	.. _rpc-common-attributes:

Rpc common attributes
=====================

	+--------------------+----------------------------------------------------+--------------------------+
	|   Attribute        |          Description                               |   Default                |
	+====================+====================================================+==========================+
	| ``method``         | MANDATORY - name of the dataRpc                    |                          |
	+--------------------+----------------------------------------------------+--------------------------+
	| ``_onCalling``     | allows to execute a Javascript code BEFORE the     |  ``None``                |
	|                    | controller action                                  |                          |
	+--------------------+----------------------------------------------------+--------------------------+
	| ``_onResult``      | allows to execute a Javascript code AFTER that the |  ``None``                |
	|                    | controller have finished its action                |                          |
	+--------------------+----------------------------------------------------+--------------------------+
	| ``sync``           | boolean; if True, Genro stops every further action |  ``False``               |
	|                    | until the Rpc containing ``sync=True`` finishes.   |                          |
	+--------------------+----------------------------------------------------+--------------------------+